"""PlantVillage alt kumesini indirir (gercek egitim verisi, Sprint 2).

Kaynak: spMohanty/PlantVillage-Dataset (GitHub, kamuya acik, kimlik gerektirmez).
Sadece hedef urunlerimizin (domates/biber/patates) siniflari cekilir ve
treatments.yaml/classifier etiketleriyle eslesen Turkce anahtarlara donusturulur.

Not: PlantVillage'de domates kullemesi (powdery mildew) yok; o sinif yalnizca
metinden tedavi eslemesiyle (treatments.yaml) desteklenir, goruntu modeli disinda.

ImageFolder duzeni uretir:
    data/plantvillage/train/<turkce_sinif>/*.jpg
    data/plantvillage/val/<turkce_sinif>/*.jpg

Calistirma:  py -m models.disease.download_plantvillage
"""
from __future__ import annotations

import json
import shutil
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

_DIR = Path(__file__).resolve().parent
DATA_ROOT = _DIR.parent.parent / "data" / "plantvillage"
API = "https://api.github.com/repos/spMohanty/PlantVillage-Dataset/contents/raw/color/"

# PlantVillage sinif klasoru -> bizim etiketimiz (classifier/treatments ile ayni)
CLASS_MAP = {
    "Tomato___healthy": "domates_saglikli",
    "Tomato___Early_blight": "domates_erken_yaniklik",
    "Tomato___Late_blight": "domates_gec_yaniklik",
    "Tomato___Bacterial_spot": "domates_bakteriyel_leke",
    "Pepper,_bell___healthy": "biber_saglikli",
    "Pepper,_bell___Bacterial_spot": "biber_bakteriyel_leke",
    "Potato___healthy": "patates_saglikli",
    "Potato___Early_blight": "patates_erken_yaniklik",
    "Potato___Late_blight": "patates_gec_yaniklik",
}

TRAIN_PER_CLASS = 300
VAL_PER_CLASS = 60


def _list_dir(pv_class: str) -> list[dict]:
    """Bir PlantVillage sinif klasorundeki dosyalari listeler (GitHub API)."""
    url = API + urllib.parse.quote(pv_class) + "?per_page=1000"
    req = urllib.request.Request(url, headers={"User-Agent": "agri-app"})
    with urllib.request.urlopen(req, timeout=30) as fh:
        return [d for d in json.load(fh) if d["type"] == "file"]


def _download(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "agri-app"})
        with urllib.request.urlopen(req, timeout=30) as fh:
            dest.write_bytes(fh.read())
        return True
    except Exception:
        return False


def main() -> None:
    if DATA_ROOT.exists():
        shutil.rmtree(DATA_ROOT)  # eski sentetik test verisini temizle

    total = 0
    for pv_class, tr_key in CLASS_MAP.items():
        files = _list_dir(pv_class)
        files = [f for f in files if f["name"].lower().endswith((".jpg", ".jpeg", ".png"))]
        files.sort(key=lambda f: f["name"])
        take = files[: TRAIN_PER_CLASS + VAL_PER_CLASS]
        # az goruntulu siniflarda (ornek: patates saglikli=152) val her zaman pay alsin
        val_n = min(VAL_PER_CLASS, max(1, len(take) // 6))
        splits = {"train": take[: len(take) - val_n], "val": take[len(take) - val_n:]}

        for split, items in splits.items():
            out = DATA_ROOT / split / tr_key
            out.mkdir(parents=True, exist_ok=True)
            jobs = {}
            with ThreadPoolExecutor(max_workers=16) as ex:
                for f in items:
                    dest = out / f["name"]
                    jobs[ex.submit(_download, f["download_url"], dest)] = dest
                ok = sum(1 for fut in as_completed(jobs) if fut.result())
            total += ok
            print(f"{tr_key:26s} {split:5s}: {ok}/{len(items)}")
    print(f"Toplam {total} goruntu indirildi -> {DATA_ROOT}")


if __name__ == "__main__":
    main()
