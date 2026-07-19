"""PlantDoc gercek TARLA fotograflarini indirir (lab-saha ucurumunu kapatmak icin).

Kaynak: pratikkayal/PlantDoc-Dataset (GitHub, kamuya acik, kimlik gerektirmez).
PlantVillage laboratuvar fotolari (tek yaprak, duz zemin) gercek tarla kosullarini
temsil etmez; model saha fotosunda dusuk guven verir. PlantDoc dogal ortamda cekilmis
(coklu yaprak, degisken isik/arka plan) fotograflar sunar.

Bu indirici mevcut data/plantvillage klasorunu SILMEZ; uzerine EKLER:
  PlantDoc train/<sinif> -> data/plantvillage/train/<turkce_anahtar>   (lab + saha karisik egitim)
  PlantDoc test/<sinif>  -> data/plantvillage/val/<turkce_anahtar>     (val artik saha da olcer)

Boylece egitim hem bol lab verisini hem gercek saha cesitliligini gorur; en iyi
checkpoint secimi saha genellemesini de gozetir.

Not: PlantDoc'ta saglikli PATATES yaprak sinifi YOK; patates_saglikli yalnizca
PlantVillage (lab) ile kalir. Domates kullemesi zaten iki veri setinde de yok.

Calistirma:  py -m models.disease.download_plantdoc  (once download_plantvillage calismis olmali)
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

_DIR = Path(__file__).resolve().parent
DATA_ROOT = _DIR.parent.parent / "data" / "plantvillage"
API = "https://api.github.com/repos/pratikkayal/PlantDoc-Dataset/contents/"

# PlantDoc sinif klasoru -> bizim etiketimiz (classifier/treatments ile ayni).
# Yalnizca hedef urunlerimizin (domates/biber/patates) esdegeri siniflar cekilir.
CLASS_MAP = {
    "Tomato leaf": "domates_saglikli",
    "Tomato Early blight leaf": "domates_erken_yaniklik",
    "Tomato leaf late blight": "domates_gec_yaniklik",
    "Tomato leaf bacterial spot": "domates_bakteriyel_leke",
    "Bell_pepper leaf": "biber_saglikli",
    "Bell_pepper leaf spot": "biber_bakteriyel_leke",
    "Potato leaf early blight": "patates_erken_yaniklik",
    "Potato leaf late blight": "patates_gec_yaniklik",
}

# PlantDoc split -> bizim split (train'i egitime, test'i val'e ekle)
SPLIT_MAP = {"train": "train", "test": "val"}


def _list_dir(path: str) -> list[dict]:
    url = API + urllib.parse.quote(path) + "?per_page=1000"
    req = urllib.request.Request(url, headers={"User-Agent": "agri-app"})
    with urllib.request.urlopen(req, timeout=30) as fh:
        return json.load(fh)


def _download(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "agri-app"})
        with urllib.request.urlopen(req, timeout=30) as fh:
            dest.write_bytes(fh.read())
        return True
    except Exception:
        return False


def main() -> None:
    if not (DATA_ROOT / "train").exists():
        raise RuntimeError(
            f"Once PlantVillage indirilmeli: {DATA_ROOT}/train yok. "
            "py -m models.disease.download_plantvillage calistirin."
        )

    total = 0
    for pd_split, our_split in SPLIT_MAP.items():
        for pd_class, key in CLASS_MAP.items():
            try:
                items = _list_dir(f"{pd_split}/{pd_class}")
            except Exception as exc:
                print(f"  {pd_class} ({pd_split}) listelenemedi: {exc}")
                continue
            files = [d for d in items if d["type"] == "file"
                     and d["name"].lower().endswith((".jpg", ".jpeg", ".png"))]
            out = DATA_ROOT / our_split / key
            out.mkdir(parents=True, exist_ok=True)
            jobs = {}
            with ThreadPoolExecutor(max_workers=16) as ex:
                for f in files:
                    # cakismayi onlemek icin saha kaynagini ad onune ekle
                    dest = out / ("plantdoc_" + f["name"])
                    jobs[ex.submit(_download, f["download_url"], dest)] = dest
                ok = sum(1 for fut in as_completed(jobs) if fut.result())
            total += ok
            print(f"{key:26s} {our_split:5s} (saha): {ok}/{len(files)}")
    print(f"Toplam {total} SAHA goruntusu eklendi -> {DATA_ROOT}")


if __name__ == "__main__":
    main()
