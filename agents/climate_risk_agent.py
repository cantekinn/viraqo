"""Iklim risk agent'i (Sprint 2): tahmini urune ozel risklere cevirir.

Akis:
  parsel (lat/lon) -> Open-Meteo 16 gunluk tahmin (min/max sicaklik, yagis)
  -> knowledge.climate_risk: urune ozel esiklerle don/sicak/yagis/kuraklik riski.

Urun sorguda gecerse o urun; yoksa bolge hedef urunleri degerlendirilir.
"""
from __future__ import annotations

from agents.state import AgentState
from core.config import settings
from data.open_meteo import get_forecast_series
from knowledge import climate_risk
from models.crop_reco.recommender import load_knowledge_base

_CROPS = ("domates", "biber", "patates", "narenciye", "zeytin", "muz")


def _detect_crops(query: str) -> tuple[str, ...]:
    found = tuple(c for c in _CROPS if c in query)
    return found or tuple(settings.target_crops)


def climate_risk_node(state: AgentState) -> AgentState:
    profile = state.get("farm_profile") or {}
    parcel = profile.get("parcel") or {}
    lat, lon = parcel.get("lat"), parcel.get("lon")
    query = state.get("query", "").lower()

    if lat is None or lon is None:
        return {"result": {
            "agent": "climate_risk",
            "message": "İklim riski için önce parsel/konum girip tarlayı tanıtın.",
            "data": {},
        }}

    try:
        fc = get_forecast_series(lat, lon)
    except Exception as exc:
        return {"result": {
            "agent": "climate_risk",
            "message": f"Hava tahminine ulaşılamadı ({exc}).",
            "data": {},
        }}

    if fc["gun"] == 0:
        return {"result": {
            "agent": "climate_risk",
            "message": "Bu konum için tahmin verisi alınamadı.",
            "data": {},
        }}

    kb = load_knowledge_base()
    crops = _detect_crops(query)

    per_crop = {}
    for crop in crops:
        risks = climate_risk.assess_climate_risk(
            fc["tmin"], fc["tmax"], fc["prec"], crop_key=crop, crop_params=kb.get(crop)
        )
        per_crop[crop] = risks

    # mesaj: en yuksek seviyeli riskleri one al
    order = {"yuksek": 0, "orta": 1, "dusuk": 2}
    lines = []
    for crop, risks in per_crop.items():
        risks_sorted = sorted(risks, key=lambda r: order[r["seviye"]])
        rl = "; ".join(f"[{r['seviye']}] {r['aciklama']}" for r in risks_sorted)
        lines.append(f"- {crop.capitalize()}: {rl}")

    msg = "16 günlük iklim risk değerlendirmesi:\n" + "\n".join(lines)
    return {"result": {"agent": "climate_risk", "message": msg, "data": {
        "gun": fc["gun"],
        "riskler": per_crop,
    }}}
