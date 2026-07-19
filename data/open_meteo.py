"""Open-Meteo istemcisi: koordinattan iklim ozeti (ucretsiz, anahtarsiz).

Urun onerisi modeli sicaklik/nem/yagis ister. Bunlari son 1 yillik
gecmis veriden (archive API) ozetleyerek temsili deger uretiriz:
- temperature: yillik ortalama sicaklik (C)
- humidity: yillik ortalama bagil nem (%)
- rainfall: yillik toplam yagis (mm)
"""
from __future__ import annotations

from datetime import date, timedelta

import requests

from core.schemas import ClimateData

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def get_climate(lat: float, lon: float, timeout: int = 20) -> ClimateData:
    """Verilen koordinat icin son ~1 yilin iklim ozetini dondurur."""
    end = date.today() - timedelta(days=7)   # arsiv verisi ~1 hafta gecikmeli
    start = end - timedelta(days=365)

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "daily": "temperature_2m_mean,precipitation_sum",
        "hourly": "relative_humidity_2m",
        "timezone": "auto",
    }
    resp = requests.get(ARCHIVE_URL, params=params, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    daily = data.get("daily", {})
    temps = [t for t in daily.get("temperature_2m_mean", []) if t is not None]
    rains = [r for r in daily.get("precipitation_sum", []) if r is not None]
    hums = [h for h in data.get("hourly", {}).get("relative_humidity_2m", []) if h is not None]

    return ClimateData(
        temperature=round(sum(temps) / len(temps), 1) if temps else None,
        humidity=round(sum(hums) / len(hums), 1) if hums else None,
        rainfall=round(sum(rains), 1) if rains else None,
    )


def get_season_temps(
    lat: float, lon: float, start: date, timeout: int = 20
) -> dict:
    """Biofix'ten bugune gunluk min/max sicaklik serisi (GDD icin, archive API).

    Donen: {"tmin": [...], "tmax": [...], "gun": n}
    """
    end = date.today() - timedelta(days=7)   # arsiv gecikmesi
    if start > end:
        start = end - timedelta(days=30)
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "daily": "temperature_2m_min,temperature_2m_max",
        "timezone": "auto",
    }
    resp = requests.get(ARCHIVE_URL, params=params, timeout=timeout)
    resp.raise_for_status()
    daily = resp.json().get("daily", {})
    tmins = [t for t in daily.get("temperature_2m_min", []) if t is not None]
    tmaxs = [t for t in daily.get("temperature_2m_max", []) if t is not None]
    n = min(len(tmins), len(tmaxs))
    return {"tmin": tmins[:n], "tmax": tmaxs[:n], "gun": n}


def get_forecast_series(lat: float, lon: float, days: int = 16, timeout: int = 20) -> dict:
    """Iklim riski icin gunluk min/max sicaklik + yagis tahmini (forecast API).

    Donen: {"tmin": [...], "tmax": [...], "prec": [...], "gun": n}
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_min,temperature_2m_max,precipitation_sum",
        "forecast_days": days,
        "timezone": "auto",
    }
    resp = requests.get(FORECAST_URL, params=params, timeout=timeout)
    resp.raise_for_status()
    daily = resp.json().get("daily", {})
    tmins = [t for t in daily.get("temperature_2m_min", []) if t is not None]
    tmaxs = [t for t in daily.get("temperature_2m_max", []) if t is not None]
    precs = [p for p in daily.get("precipitation_sum", []) if p is not None]
    n = min(len(tmins), len(tmaxs))
    return {"tmin": tmins[:n], "tmax": tmaxs[:n], "prec": precs[:n], "gun": n}


def get_irrigation_inputs(lat: float, lon: float, days: int = 7, timeout: int = 20) -> dict:
    """Sulama plani icin yakin donem ET0 ve yagis (Open-Meteo forecast).

    Open-Meteo, FAO-56 Penman-Monteith referans terlemesini
    (et0_fao_evapotranspiration) dogrudan gunluk verir. Bunun ortalamasi ile
    beklenen yagis toplamini dondururuz.

    Donen:
      et0_mm_gun       : onumuzdeki `days` gunun ortalama ET0'i (mm/gun)
      yagis_mm_donem   : ayni donemin beklenen toplam yagisi (mm)
      gun              : kullanilan gun sayisi
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "et0_fao_evapotranspiration,precipitation_sum",
        "forecast_days": days,
        "timezone": "auto",
    }
    resp = requests.get(FORECAST_URL, params=params, timeout=timeout)
    resp.raise_for_status()
    daily = resp.json().get("daily", {})

    et0s = [e for e in daily.get("et0_fao_evapotranspiration", []) if e is not None]
    rains = [r for r in daily.get("precipitation_sum", []) if r is not None]

    return {
        "et0_mm_gun": round(sum(et0s) / len(et0s), 2) if et0s else None,
        "yagis_mm_donem": round(sum(rains), 1) if rains else 0.0,
        "gun": len(et0s),
    }
