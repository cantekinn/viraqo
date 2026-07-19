"""Zararli agent'i (Sprint 2): derece-gun (GDD) ile zararli fenoloji tahmini.

Akis:
  parsel (lat/lon) -> Open-Meteo gunluk min/max sicaklik (biofix'ten bugune)
  -> knowledge.degree_day: her zararli icin GDD birikimi -> nesil/evre
  -> izleme/mucadele penceresi mesaji.

Biofix (sezon baslangici) varsayilan 1 Mart (Antalya); erken tarihlerde
son ~1 ay verisiyle kismi tahmin.
"""
from __future__ import annotations

from datetime import date

from agents.state import AgentState
from core.config import settings
from data.open_meteo import get_season_temps
from knowledge import degree_day as dd

_CROPS = ("domates", "biber", "patates", "narenciye", "zeytin", "muz")


def _detect_crops(query: str) -> tuple[str, ...]:
    found = tuple(c for c in _CROPS if c in query)
    return found or tuple(settings.target_crops)


def pest_node(state: AgentState) -> AgentState:
    profile = state.get("farm_profile") or {}
    parcel = profile.get("parcel") or {}
    lat, lon = parcel.get("lat"), parcel.get("lon")
    query = state.get("query", "").lower()

    if lat is None or lon is None:
        return {"result": {
            "agent": "pest",
            "message": "Zararlı tahmini için önce parsel/konum girip tarlayı tanıtın.",
            "data": {},
        }}

    biofix = date(date.today().year, 3, 1)     # Antalya sezon baslangici
    try:
        temps = get_season_temps(lat, lon, biofix)
    except Exception as exc:
        return {"result": {
            "agent": "pest",
            "message": f"Hava servisine ulaşılamadı, zararlı tahmini yapılamadı ({exc}).",
            "data": {},
        }}

    if temps["gun"] == 0:
        return {"result": {
            "agent": "pest",
            "message": "Bu konum için sıcaklık serisi alınamadı.",
            "data": {},
        }}

    crops = _detect_crops(query)
    seen: set[str] = set()
    results = []
    for crop in crops:
        for pk in dd.pests_for_crop(crop):
            if pk in seen:
                continue
            seen.add(pk)
            pest = dd.PEST_TABLE[pk]
            gdd = dd.accumulate_gdd(temps["tmin"], temps["tmax"], pest["tbase"], pest["tupper"])
            results.append(dd.pest_status(gdd, pk))

    if not results:
        return {"result": {
            "agent": "pest",
            "message": "Seçilen ürün için tanımlı zararlı kaydı yok.",
            "data": {},
        }}

    lines = []
    for r in results:
        sonraki = ""
        if r["sonraki_evre"]:
            ad, kalan = r["sonraki_evre"]
            sonraki = f", sonraki evre: {ad} (yaklaşık {kalan} GDD sonra)"
        lines.append(
            f"- {r['zararli']}: {r['nesil']}. nesil, {r['evre']} evresinde "
            f"(toplam {r['toplam_gdd']} GDD){sonraki}\n    {r['not']}"
        )
    msg = (
        f"Zararlı derece-gün tahmini (başlangıç 1 Mart, {temps['gun']} gün):\n"
        + "\n".join(lines)
    )
    return {"result": {"agent": "pest", "message": msg, "data": {
        "gun": temps["gun"],
        "durumlar": results,
    }}}
