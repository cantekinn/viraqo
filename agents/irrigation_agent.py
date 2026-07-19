"""Sulama agent'i (Sprint 2): FAO-56 ile gunluk sulama plani.

Akis:
  parsel (lat/lon/alan) -> Open-Meteo ET0 (FAO-56) + beklenen yagis
  -> knowledge.fao56.irrigation_plan -> her urun icin net sulama (mm/gun, litre/gun)

Urun sorguda gecerse (ornegin "domates") sadece o urun; yoksa bolge hedef
urunleri (config.settings.target_crops) icin plan uretilir.
"""
from __future__ import annotations

from agents.state import AgentState
from core.config import settings
from data.open_meteo import get_irrigation_inputs
from knowledge import fao56

# sorguda urun/asama tespiti
_CROPS = ("domates", "biber", "patates", "narenciye", "zeytin", "muz")
_STAGE_KEYWORDS = {
    "ini": ("fide", "ekim", "dikim", "baslangic", "cimlen"),
    "end": ("hasat", "olgun", "son donem"),
}


def _detect_stage(query: str) -> str:
    for stage, kws in _STAGE_KEYWORDS.items():
        if any(kw in query for kw in kws):
            return stage
    return "mid"


def _detect_crops(query: str) -> tuple[str, ...]:
    found = tuple(c for c in _CROPS if c in query)
    return found or tuple(settings.target_crops)


def irrigation_node(state: AgentState) -> AgentState:
    profile = state.get("farm_profile") or {}
    parcel = profile.get("parcel") or {}
    lat, lon = parcel.get("lat"), parcel.get("lon")
    area = parcel.get("alan_m2")
    query = state.get("query", "").lower()

    if lat is None or lon is None:
        return {"result": {
            "agent": "irrigation",
            "message": "Sulama planı için önce parsel/konum girip tarlayı tanıtın.",
            "data": {},
        }}

    try:
        inputs = get_irrigation_inputs(lat, lon)
    except Exception as exc:  # ag/servis hatasi - agent cokmesin
        return {"result": {
            "agent": "irrigation",
            "message": f"Hava servisine ulaşılamadı, sulama planı üretilemedi ({exc}).",
            "data": {},
        }}

    et0 = inputs.get("et0_mm_gun")
    if et0 is None:
        return {"result": {
            "agent": "irrigation",
            "message": "Bu konum için ET0 verisi alınamadı.",
            "data": {},
        }}

    # tahmin doneminin ORTALAMA gunluk yagisi (aya olceklemeden; yagisli bir
    # haftayi tum aya yaymak net sulamayi yaniltir).
    gun = max(inputs.get("gun", 7), 1)
    rain_daily = inputs.get("yagis_mm_donem", 0.0) / gun

    stage = _detect_stage(query)
    crops = _detect_crops(query)
    plans = [fao56.irrigation_plan(et0, c, stage, rain_daily, area) for c in crops]

    lines = []
    for p in plans:
        litre = f", yaklaşık {p['litre_gun']:.0f} L/gün (parsel)" if "litre_gun" in p else ""
        lines.append(
            f"- {p['urun'].capitalize()}: net {p['net_mm_gun']} mm/gün "
            f"(ETc {p['etc_mm_gun']}, Kc {p['kc']}){litre}"
        )
    asama = {"ini": "başlangıç", "mid": "gelişme", "end": "hasat"}[stage]
    msg = (
        f"FAO-56 sulama planı (ET0={et0} mm/gün, {asama} aşaması, "
        f"beklenen yağış {inputs['yagis_mm_donem']} mm/{gun} gün):\n"
        + "\n".join(lines)
    )
    return {"result": {"agent": "irrigation", "message": msg, "data": {
        "et0_mm_gun": et0,
        "yagis_mm_donem": inputs["yagis_mm_donem"],
        "stage": stage,
        "planlar": plans,
    }}}
