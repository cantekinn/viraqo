"""Orkestrator: niyeti belirler ve dogru uzman agent'a yonlendirir.

Sprint 2: tum uzman agent'lar gercek (crop_reco, irrigation, climate_risk,
pest, diagnosis, advisor). Sadece carbon Sprint 3'e kadar stub.
Router anahtar-kelime tabanli; ayrica fotograf varsa dogrudan teshise gider.
"""
from __future__ import annotations

from langgraph.graph import END, StateGraph

from agents.advisor_agent import advisor_node
from agents.climate_risk_agent import climate_risk_node
from agents.diagnosis_agent import diagnosis_node
from agents.irrigation_agent import irrigation_node
from agents.pest_agent import pest_node
from agents.state import AgentState
from core.schemas import ClimateData, SoilData
from models.crop_reco import recommend

# Niyet -> anahtar kelimeler (basit kural tabanli router).
# Anahtarlar ASCII yazilir; _norm() sorgudaki Turkce karakterleri ASCII'ye katladigi
# icin "zararlı böcek" gibi Turkce girisler de eslesir.
INTENT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "diagnosis": ("hastalik", "yaprak", "leke", "teshis", "curume"),
    "crop_reco": ("ne ek", "urun", "oneri", "tavsiye", "ekim"),
    "irrigation": ("sula", "su ", "sulama"),
    "climate_risk": ("don", "kurak", "risk", "hava", "sicaklik"),
    "pest": ("bocek", "zararli", "haser"),
    "carbon": ("karbon", "ayak izi"),
}

# Turkce -> ASCII katlama (router eslesmesi karakterden bagimsiz olsun)
_TR_FOLD = str.maketrans("çğıiöşüÇĞİIÖŞÜ", "cgiiosucgiiosu")


def _norm(text: str) -> str:
    return text.translate(_TR_FOLD).lower()


def route_intent(state: AgentState) -> AgentState:
    """Kullanici sorgusundan (veya fotograf varliginda) niyeti cikarir."""
    if state.get("image_path"):
        return {"intent": "diagnosis"}     # foto varsa dogrudan teshis
    query = _norm(state.get("query", ""))
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(kw in query for kw in keywords):
            return {"intent": intent}
    return {"intent": "advisor"}  # varsayilan: genel danisman


def _stub(agent_name: str, message: str):
    """Henuz yazilmamis agent'lar icin yer tutucu dugum uretir."""
    def node(state: AgentState) -> AgentState:
        return {"result": {"agent": agent_name, "message": message, "data": {}}}
    return node


def crop_reco_node(state: AgentState) -> AgentState:
    """Aktif tarla profilinden toprak+iklime gore urun onerir (Sprint 1 - Sila)."""
    profile = state.get("farm_profile") or {}
    soil = SoilData(**(profile.get("soil") or {}))
    climate = ClimateData(**(profile.get("climate") or {}))

    if soil.ph is None and climate.temperature is None:
        return {
            "result": {
                "agent": "crop_reco",
                "message": "Once tarla konumunu girip toprak/iklim verisini getirin.",
                "data": {},
            }
        }

    recos = recommend(soil, climate, top_k=3)
    lines = [
        f"{i}. {r['ad']} - skor {r['skor']} ({r['uygunluk']})"
        for i, r in enumerate(recos, 1)
    ]
    message = "Toprak ve iklime en uygun urunler:\n" + "\n".join(lines)
    return {"result": {"agent": "crop_reco", "message": message, "data": {"oneriler": recos}}}


# Sprint 2: uzman agent'lar gercek (ilgili modullerden import edildi).
# carbon Sprint 3'te gelecek -> simdilik stub.
carbon_node = _stub("carbon", "[stub] Karbon ayak izi Sprint 3'te gelecek.")

AGENT_NODES = {
    "crop_reco": crop_reco_node,
    "diagnosis": diagnosis_node,
    "irrigation": irrigation_node,
    "climate_risk": climate_risk_node,
    "pest": pest_node,
    "carbon": carbon_node,
    "advisor": advisor_node,
}


def build_graph():
    """Orkestrasyon grafigini kurar ve derler."""
    graph = StateGraph(AgentState)

    graph.add_node("router", route_intent)
    for name, node in AGENT_NODES.items():
        graph.add_node(name, node)

    graph.set_entry_point("router")
    # router -> niyete gore ilgili agent
    graph.add_conditional_edges(
        "router",
        lambda state: state["intent"],
        {name: name for name in AGENT_NODES},
    )
    # her agent -> son
    for name in AGENT_NODES:
        graph.add_edge(name, END)

    return graph.compile()
