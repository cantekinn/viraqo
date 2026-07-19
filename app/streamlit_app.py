"""Tarim Asistani - kullanici arayuzu (Sprint 2).

Urun odakli tasarim: soldan tarla sec -> ustte aktif tarla banneri ->
sekmelerde uzman danisman (urun onerisi, sulama, iklim riski, zararli,
hastalik teshisi, serbest soru). Her uzman agent orkestrator uzerinden
calisir; sonuclar yapilandirilmis kart/metrik olarak gosterilir ve oturum
boyunca korunur (sekme degistirince kaybolmaz).

Calistirma:
    streamlit run app/streamlit_app.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from core.schemas import ClimateData, FarmProfile, Parcel, SoilData
from data.open_meteo import get_climate
from data.parcel_files import load_parcels
from data.soilgrids import get_soil
from memory.farm_profile_db import find_by_parcel, list_profiles, save_profile
from models import disease
from models.crop_reco import gbdt_available, gbdt_second_opinion, recommend

# Antalya varsayilan (Serik ovasi - toprak verisi olan bir tarim koordinati)
DEFAULT_LAT, DEFAULT_LON = 37.05, 31.05

CROPS = {
    "domates": "Domates",
    "biber": "Biber",
    "patates": "Patates",
    "narenciye": "Narenciye",
    "zeytin": "Zeytin",
    "muz": "Muz",
}

st.set_page_config(page_title="Tarım Asistanı", layout="wide")

# --- Gorsel stil (urun hissi: yumusak kartlar, rozetler, banner) ---
st.markdown(
    """
    <style>
      .block-container {padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1120px;}
      h1 {font-weight: 800; letter-spacing: -0.02em;}
      .stButton>button {border-radius: 10px; font-weight: 600;}
      .parcel-banner {background: linear-gradient(90deg,#1b5e20,#2e7d32);
        color:#fff; padding:14px 18px; border-radius:14px; margin:2px 0 14px;}
      .parcel-banner b {color:#fff;}
      .badge {display:inline-block; padding:2px 11px; border-radius:999px;
        font-size:0.78rem; font-weight:700; margin-right:6px; letter-spacing:.01em;}
      .badge-yuksek {background:#fdecec; color:#c0392b;}
      .badge-orta {background:#fff4e0; color:#b9770e;}
      .badge-dusuk {background:#e7f6ea; color:#2e7d32;}
      .hint {color:#8a94a6; font-size:0.9rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------ veri/altyapi
@st.cache_data(show_spinner="Toprak ve iklim verisi getiriliyor...")
def _fetch(lat: float, lon: float):
    """Koordinat icin toprak + iklim verisi. Kaynaklar bagimsiz; biri duserse
    digeri yine gelir ve uyari dondurulur."""
    warnings: list[str] = []
    try:
        soil = get_soil(lat, lon)
    except Exception as exc:
        soil = SoilData()
        warnings.append(f"Toprak verisi alınamadı (SoilGrids): {exc}")
    try:
        climate = get_climate(lat, lon)
    except Exception as exc:
        climate = ClimateData()
        warnings.append(f"İklim verisi alınamadı (Open-Meteo): {exc}")
    return soil, climate, warnings


@st.cache_resource(show_spinner=False)
def _graph():
    from agents.orchestrator import build_graph

    return build_graph()


def _active_profile() -> dict:
    return {
        "parcel": st.session_state.get("parcel"),
        "soil": st.session_state.get("soil"),
        "climate": st.session_state.get("climate"),
    }


def _invoke(query: str, image_path: str | None = None) -> dict:
    state_in = {"query": query, "farm_profile": _active_profile()}
    if image_path:
        state_in["image_path"] = image_path
    return _graph().invoke(state_in).get("result", {})


def _has_location() -> bool:
    p = st.session_state.get("parcel") or {}
    return p.get("lat") is not None and p.get("lon") is not None


# ------------------------------------------------------------------ renderers
def render_irrigation(res: dict) -> None:
    data = res.get("data") or {}
    if not data.get("planlar"):
        st.info(res.get("message", ""))
        return
    et0 = data["et0_mm_gun"]
    yagis = data["yagis_mm_donem"]
    asama = {"ini": "Başlangıç (fide/dikim)", "mid": "Gelişme", "end": "Hasat/olgunluk"}[data["stage"]]
    st.caption(
        f"Bu günlerde hava günde ~{et0} mm su buharlaştırıyor, önümüzdeki hafta "
        f"~{yagis} mm yağış bekleniyor. Aşama: {asama}."
    )
    for p in data["planlar"]:
        with st.container(border=True):
            urun = p["urun"].capitalize()
            net = p["net_mm_gun"]
            st.markdown(f"### {urun}")
            if net <= 0.05:
                st.markdown("**Kısaca: şu an ek sulamaya gerek yok.**")
                st.markdown(
                    "Beklenen yağış bu aşamada bitkinin su ihtiyacını karşılıyor. "
                    "Yağış beklentisi düşerse ya da hava ısınırsa yeniden kontrol et."
                )
            else:
                if "litre_gun" in p:
                    litre = p["litre_gun"]
                    uc_gun = litre * 3
                    st.markdown(f"**Kısaca: bu tarlaya günde ortalama {litre:,.0f} litre su gerekiyor.**")
                    st.markdown(
                        f"Her gün uğraşmak yerine **3 günde bir yaklaşık {uc_gun:,.0f} litre** verebilirsin."
                    )
                else:
                    st.markdown(f"**Kısaca: her metrekareye günde {net:.1f} litre su gerekiyor.**")
                    st.caption("Parsel alanını girersen toplam litreyi de hesaplarım.")
                st.markdown(
                    "- Damla sulama: toprağın 20-30 cm derinliği nemlenene kadar çalıştır.\n"
                    "- Salma/karık sulama: 3-4 günde bir toplu ver.\n"
                    "- Yağmur yağarsa o kadar suyu düş; çok sıcak/rüzgarlı günlerde biraz artır."
                )
            with st.expander("Teknik detay (nasıl hesaplandı)"):
                k1, k2, k3 = st.columns(3)
                k1.metric("Net sulama", f"{net} mm/gün")
                k2.metric("Bitki su isteği (ETc)", f"{p['etc_mm_gun']} mm/gün")
                k3.metric("Ürün katsayısı (Kc)", p["kc"])
                st.caption(
                    f"ET0 {et0} mm x Kc {p['kc']} = ETc {p['etc_mm_gun']} mm; "
                    f"net = ETc - etkili yağış. Yöntem: FAO-56 Penman-Monteith. "
                    "(mm = metrekareye düşen litre; 1 mm = 1 L/m2.)"
                )


def render_climate(res: dict) -> None:
    data = res.get("data") or {}
    riskler = data.get("riskler")
    if not riskler:
        st.info(res.get("message", ""))
        return
    st.caption(f"{data.get('gun', 16)} günlük tahmine göre ürün bazlı risk.")
    order = {"yuksek": 0, "orta": 1, "dusuk": 2}
    etiket_map = {"yuksek": "YÜKSEK", "orta": "ORTA", "dusuk": "DÜŞÜK"}
    for crop, risks in riskler.items():
        with st.container(border=True):
            st.markdown(f"**{crop.capitalize()}**")
            for r in sorted(risks, key=lambda x: order[x["seviye"]]):
                st.markdown(
                    f"<span class='badge badge-{r['seviye']}'>{etiket_map[r['seviye']]}</span> "
                    f"{r['aciklama']}",
                    unsafe_allow_html=True,
                )


def render_pest(res: dict) -> None:
    data = res.get("data") or {}
    durumlar = data.get("durumlar")
    if not durumlar:
        st.info(res.get("message", ""))
        return
    st.caption(f"Biofix 1 Mart'tan bugüne {data.get('gun', 0)} gün sıcaklık birikimi (GDD).")
    for r in durumlar:
        with st.container(border=True):
            st.markdown(f"**{r['zararli']}**")
            m1, m2, m3 = st.columns(3)
            m1.metric("Nesil", f"{r['nesil']}.")
            m2.metric("Yaşam evresi", r["evre"])
            m3.metric("Toplam GDD", r["toplam_gdd"])
            if r["sonraki_evre"]:
                ad, kalan = r["sonraki_evre"]
                st.caption(f"Sonraki evre: {ad} (yaklaşık {kalan} GDD sonra)")
            st.caption(r["not"])


def render_diagnosis(res: dict) -> None:
    data = res.get("data") or {}
    teshis = data.get("teshis")
    seviye = teshis.get("seviye") if teshis else None
    if seviye == "tanimsiz":
        st.warning("Bu yaprak domates, biber veya patates yaprağına benzemiyor "
                   "(başka bir bitki ya da net olmayan fotoğraf). Teşhis vermiyorum.")
    elif seviye == "belirsiz":
        st.warning(f"Kesin teşhis çıkmadı (en yüksek güven %{teshis['guven'] * 100:.0f}). "
                   "Aşağıdaki ihtimalleri ve öneriyi inceleyin.")
    elif seviye == "olasi":
        if teshis.get("urun"):
            st.caption(f"Tespit edilen ürün: {disease.CROP_TR.get(teshis['urun'], teshis['urun'].capitalize())} "
                       f"(%{teshis.get('urun_guven', 0) * 100:.0f})")
        st.info(f"En olası teşhis: {disease.label_display(teshis['etiket'])} "
                f"(güven %{teshis['guven'] * 100:.0f}, kesin değil).")
    elif teshis:
        if teshis.get("urun"):
            st.caption(f"Tespit edilen ürün: {disease.CROP_TR.get(teshis['urun'], teshis['urun'].capitalize())} "
                       f"(%{teshis.get('urun_guven', 0) * 100:.0f})")
        st.metric("Teşhis", disease.label_display(teshis["etiket"]), f"güven %{teshis['guven'] * 100:.0f}")
    st.write(res.get("message", ""))
    gc = data.get("gradcam")
    if gc and Path(gc).exists():
        st.image(gc, caption="Grad-CAM ısı haritası - teşhisi sürükleyen bölge")


# ------------------------------------------------------------------ kenar cubugu
with st.sidebar:
    st.header("Tarla Seçimi")

    dosya_parselleri = load_parcels()
    if dosya_parselleri:
        etiket_map = {k["etiket"]: k["parcel"] for k in dosya_parselleri}
        secim_dosya = st.selectbox("Kayıtlı parsellerden seç", ["(seç)"] + list(etiket_map))
        if secim_dosya != "(seç)" and st.button("Seç ve getir", type="primary", use_container_width=True):
            parcel = etiket_map[secim_dosya]
            st.session_state["parcel"] = parcel.model_dump()
            soil, climate, warnings = _fetch(parcel.lat, parcel.lon)
            st.session_state["soil"] = soil.model_dump()
            st.session_state["climate"] = climate.model_dump()
            for w in warnings:
                st.warning(w)

    kayitli = list_profiles()
    if kayitli:
        etiketler = {
            f"{p['il']}/{p['ilce']} ada {p['ada']} parsel {p['parsel']}": p for p in kayitli
        }
        secim = st.selectbox("Hafızadan tarla yükle", ["(yeni)"] + list(etiketler))
        if secim != "(yeni)" and st.button("Yükle", use_container_width=True):
            p = etiketler[secim]
            prof = find_by_parcel(p["il"], p["ada"], p["parsel"])
            if prof:
                st.session_state["parcel"] = prof.parcel.model_dump()
                if prof.soil is None and prof.parcel.lat is not None:
                    soil, climate, warnings = _fetch(prof.parcel.lat, prof.parcel.lon)
                    st.session_state["soil"] = soil.model_dump()
                    st.session_state["climate"] = climate.model_dump()
                    for w in warnings:
                        st.warning(w)
                else:
                    st.session_state["soil"] = (prof.soil or SoilData()).model_dump()
                    st.session_state["climate"] = (prof.climate or ClimateData()).model_dump()

    with st.expander("Elle koordinat gir"):
        il = st.text_input("İl", value="Antalya")
        ilce = st.text_input("İlçe", value="Serik")
        ada = st.text_input("Ada", value="120")
        parsel = st.text_input("Parsel", value="7")
        lat = st.number_input("Enlem", value=DEFAULT_LAT, format="%.4f")
        lon = st.number_input("Boylam", value=DEFAULT_LON, format="%.4f")
        if st.button("Veriyi getir", use_container_width=True):
            soil, climate, warnings = _fetch(lat, lon)
            st.session_state["soil"] = soil.model_dump()
            st.session_state["climate"] = climate.model_dump()
            st.session_state["parcel"] = Parcel(
                il=il, ilce=ilce, mahalle="", ada=ada, parsel=parsel, lat=lat, lon=lon
            ).model_dump()
            for w in warnings:
                st.warning(w)

    st.divider()
    st.caption("Veri kaynakları: Open-Meteo (iklim/ET0), SoilGrids (toprak), TKGM/MEGSIS (parsel). Tümü açık ve ücretsiz.")


# ------------------------------------------------------------------ baslik + banner
st.title("Tarım Asistanı")
st.caption("Küçük çiftçi için çok agentli yapay zeka tarım danışmanı")

parcel_d = st.session_state.get("parcel") or {}
if parcel_d:
    p = Parcel(**parcel_d)
    adres = f"{p.il} / {p.ilce}".strip(" /")
    alan = f" · {p.alan_m2:,.0f} m2" if p.alan_m2 else ""
    st.markdown(
        f"<div class='parcel-banner'>Aktif tarla: <b>{adres}</b> · "
        f"Ada/Parsel {p.ada}/{p.parsel}{alan}</div>",
        unsafe_allow_html=True,
    )
else:
    st.info("Başla: soldaki panelden bir parsel seç ya da koordinat gir. Ardından aşağıdaki sekmelerden danışmanı kullan.")

# ------------------------------------------------------------------ sekmeler
tab_bakis, tab_urun, tab_sulama, tab_iklim, tab_zararli, tab_teshis, tab_soru = st.tabs(
    ["Genel Bakış", "Ürün Önerisi", "Sulama Planı", "İklim Riski", "Zararlı Takvimi", "Hastalık Teşhisi", "Danışmana Sor"]
)

has_data = "soil" in st.session_state

# --- Genel Bakis ---
with tab_bakis:
    if not has_data:
        st.write("Tarla seçilince toprak ve iklim özeti burada görünür.")
    else:
        soil = SoilData(**st.session_state["soil"])
        climate = ClimateData(**st.session_state["climate"])
        st.subheader("İklim özeti (son ~1 yıl)")
        c1, c2, c3 = st.columns(3)
        c1.metric("Ort. sıcaklık", f"{climate.temperature} C" if climate.temperature is not None else "-")
        c2.metric("Ort. nem", f"%{climate.humidity}" if climate.humidity is not None else "-")
        c3.metric("Yıllık yağış", f"{climate.rainfall} mm" if climate.rainfall is not None else "-")

        st.subheader("Toprak (SoilGrids, 0-5 cm)")
        if soil.ph is None:
            st.info(
                "SoilGrids bu hücre için toprak verisi döndürmedi (kıyı/kentsel/kapsam dışı "
                "olabilir). Öneriler yalnızca iklim verisine göre hesaplanır."
            )
        else:
            s1, s2 = st.columns(2)
            s1.metric("pH", soil.ph)
            s1.metric("Azot (g/kg)", soil.nitrogen)
            s1.metric("Organik karbon (g/kg)", soil.organic_carbon)
            s2.metric("Kil %", soil.clay)
            s2.metric("Kum %", soil.sand)
            s2.metric("Silt %", soil.silt)

        if st.button("Bu tarlayı hafızaya kaydet"):
            prof = FarmProfile(parcel=Parcel(**parcel_d), soil=soil, climate=climate)
            pid = save_profile(prof)
            st.success(f"Kaydedildi (id: {pid[:8]}...). Sonraki oturumda hatırlanacak.")

# --- Urun Onerisi ---
with tab_urun:
    if not has_data:
        st.write("Önce tarla seç; öneriler toprak ve iklime göre hesaplanır.")
    else:
        soil = SoilData(**st.session_state["soil"])
        climate = ClimateData(**st.session_state["climate"])
        if soil.ph is None and climate.temperature is None:
            st.info("Öneri için en az toprak ya da iklim verisi gerekli.")
            recos = []
        else:
            if soil.ph is None:
                st.caption("Not: Toprak verisi yok; skorlar yalnızca iklim üzerinden.")
            recos = recommend(soil, climate, top_k=4)
        for r in recos:
            with st.container(border=True):
                st.markdown(f"**{r['ad']}**  ·  skor {r['skor']}  ·  {r['uygunluk']}")
                st.caption(f"Sezon: {r['sezon']}")
                st.write(r["not"])
                if r["faktorler"]:
                    with st.expander("Neden bu skor (faktör uyumu 0-1)"):
                        st.table(r["faktorler"])

        if recos and gbdt_available():
            with st.expander("Deneysel: GBDT ikinci görüş"):
                st.caption(
                    "Kaggle veri setinde eğitilmiş destek model. Karar birincil olarak "
                    "yukarıdaki kural motorundan gelir."
                )
                npk = None
                if st.checkbox("Toprak analizi N/P/K gir"):
                    g1, g2, g3 = st.columns(3)
                    npk = {
                        "N": g1.number_input("N", value=37.0, format="%.1f"),
                        "P": g2.number_input("P", value=51.0, format="%.1f"),
                        "K": g3.number_input("K", value=32.0, format="%.1f"),
                    }
                op = gbdt_second_opinion(soil, climate, npk=npk)
                if op is None:
                    st.info("İkinci görüş için en az pH ve sıcaklık verisi gerekli.")
                else:
                    (st.warning if op["gosterge"] else st.caption)(op["not"])
                    for t in op["tahminler"]:
                        etiket = "bizim ürün" if t["bizim_urun"] else "iklim benzeri"
                        st.write(f"- {t['ad']}  (olasılık {t['olasilik']}, {etiket})")

# --- Sulama Plani ---
with tab_sulama:
    st.caption("Parselin konumundan günlük sulama ihtiyacı (FAO-56).")
    sc1, sc2 = st.columns([2, 3])
    urun_s = sc1.selectbox("Ürün", ["Hedef ürünlerin tümü"] + list(CROPS.values()), key="urun_sulama")
    asama_s = sc2.radio(
        "Gelişme aşaması", ["Başlangıç (fide/dikim)", "Gelişme (orta)", "Hasat/olgunluk"],
        horizontal=True, index=1, key="asama_sulama",
    )
    if st.button("Sulama planını hesapla", type="primary", disabled=not _has_location()):
        crop_kw = "" if urun_s.startswith("Hedef") else urun_s.lower()
        stage_kw = {"Başlangıç (fide/dikim)": "dikim", "Gelişme (orta)": "", "Hasat/olgunluk": "hasat"}[asama_s]
        st.session_state["res_sulama"] = _invoke(f"{crop_kw} sulama planı {stage_kw}".strip())
    if not _has_location():
        st.info("Önce soldan bir parsel/konum seç.")
    if st.session_state.get("res_sulama"):
        render_irrigation(st.session_state["res_sulama"])

# --- Iklim Riski ---
with tab_iklim:
    st.caption("16 günlük hava tahmininden ürüne özel don/sıcak/yağış/kuraklık riski.")
    urun_i = st.selectbox("Ürün", ["Hedef ürünlerin tümü"] + list(CROPS.values()), key="urun_iklim")
    if st.button("İklim riskini değerlendir", type="primary", disabled=not _has_location()):
        crop_kw = "" if urun_i.startswith("Hedef") else urun_i.lower()
        st.session_state["res_iklim"] = _invoke(f"{crop_kw} iklim risk don sıcak".strip())
    if not _has_location():
        st.info("Önce soldan bir parsel/konum seç.")
    if st.session_state.get("res_iklim"):
        render_climate(st.session_state["res_iklim"])

# --- Zararli Takvimi ---
with tab_zararli:
    st.caption("Sıcaklık birikimine (derece-gün) göre zararlı böcek nesil/evre tahmini.")
    urun_z = st.selectbox("Ürün", ["Hedef ürünlerin tümü"] + list(CROPS.values()), key="urun_zararli")
    if st.button("Zararlı takvimini çıkar", type="primary", disabled=not _has_location()):
        crop_kw = "" if urun_z.startswith("Hedef") else urun_z.lower()
        st.session_state["res_zararli"] = _invoke(f"{crop_kw} zararlı böcek".strip())
    if not _has_location():
        st.info("Önce soldan bir parsel/konum seç.")
    if st.session_state.get("res_zararli"):
        render_pest(st.session_state["res_zararli"])

# --- Hastalik Teshisi ---
with tab_teshis:
    if disease.is_available():
        st.success("Teşhis modeli hazır. Yaprak fotoğrafı yükleyin.")
    else:
        st.warning(
            f"Görüntüden teşhis modeli henüz hazır değil ({disease.status()}). "
            "Model eğitilince (models/disease/train.py) foto ile otomatik teşhis çalışır. "
            "Şu an belirti/hastalık adı yazarak tedavi önerisi alabilirsiniz."
        )
    foto = st.file_uploader("Yaprak/gövde fotoğrafı", type=["jpg", "jpeg", "png"])
    if foto is not None:
        suffix = Path(foto.name).suffix or ".jpg"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(foto.getbuffer())
        tmp.close()
        c1, c2 = st.columns([1, 2])
        c1.image(tmp.name, caption="Yüklenen fotoğraf", use_container_width=True)
        with c2:
            render_diagnosis(_invoke("", image_path=tmp.name))

    st.divider()
    belirti = st.text_input("Alternatif: hastalık adı / belirti yaz (örn: domateste yaprakta kahverengi leke)")
    if belirti:
        render_diagnosis(_invoke(belirti))

# --- Danismana Sor ---
with tab_soru:
    st.caption("Serbest soru sor; sistem doğru uzmana yönlendirir.")
    q = st.text_input("Örn: ne ekmeliyim / ne kadar sulamalıyım / don riski var mı")
    if q:
        res = _invoke(q)
        st.write(f"**Yönlendirilen uzman:** {res.get('agent')}")
        st.write(res.get("message", ""))
        gc = (res.get("data") or {}).get("gradcam")
        if gc and Path(gc).exists():
            st.image(gc, caption="Grad-CAM ısı haritası")
