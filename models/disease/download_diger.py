"""'diger' (hedef-disi yaprak) sinifi indirici - outlier exposure icin.

Sorun: model yalnizca domates/biber/patates biliyor; narenciye/yabanci yaprak
gorunce zorla 9 siniftan birine itip yanlis teshis veriyor. Post-hoc guven/enerji
skoru in-dist ile OOD'yi ayirmadi (olculdu). Cozum: modele hedef-disi gercek
yapraklardan olusan bir "diger" sinifi ogret; boylece bilmedigi yapragi "diger"
diye reddeder.

Kaynak: pratikkayal/PlantDoc-Dataset (gercek tarla fotolari, hedef-disi turler).
Egitim sinifi PlantDoc train/<tur> -> data/plantvillage/train/diger
Val (olcum)   PlantDoc test/<tur>  -> data/plantvillage/val/diger

HELD-OUT: bazi turler (narenciyeye vekil, egitimde HIC gorulmeyen) ayri klasore
(data/ood_holdout) indirilir; genelleme testi icin - "diger" sinifi hic gormedigi
yaprak turunu de reddedebiliyor mu?

Calistirma:  py -m models.disease.download_diger
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

_DIR = Path(__file__).resolve().parent
DATA_ROOT = _DIR.parent.parent / "data"
PV = DATA_ROOT / "plantvillage"
HOLDOUT = DATA_ROOT / "ood_holdout"
API = "https://api.github.com/repos/pratikkayal/PlantDoc-Dataset/contents/"

# "diger" sinifina girecek hedef-disi PlantDoc turleri (egitim + val'e eklenir).
DIGER_CLASSES = [
    "Apple leaf", "Apple Scab Leaf", "Apple rust leaf",
    "Blueberry leaf", "Corn leaf blight", "Corn rust leaf",
    "grape leaf", "grape leaf black rot", "Soyabean leaf",
    "Strawberry leaf", "Squash Powdery mildew leaf",
]
# Egitimde HIC gorulmeyecek turler (narenciyeye vekil; sadece genelleme testi).
HOLDOUT_CLASSES = ["Cherry leaf", "Peach leaf", "Raspberry leaf"]

SPLIT_MAP = {"train": "train", "test": "val"}
DIGER_CAP = 300  # diger sinifini diger siniflarla dengede tut (train)


def _list_dir(path: str) -> list[dict]:
    url = API + urllib.parse.quote(path) + "?per_page=1000"
    req = urllib.request.Request(url, headers={"User-Agent": "agri-app"})
    with urllib.request.urlopen(req, timeout=30) as fh:
        return json.load(fh)


def _dl(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "agri-app"})
        with urllib.request.urlopen(req, timeout=30) as fh:
            dest.write_bytes(fh.read())
        return True
    except Exception:
        return False


def _pull(classes, split_map, out_root, prefix, cap=None):
    total = 0
    for cls in classes:
        for pd_split, our_split in split_map.items():
            try:
                items = _list_dir(f"{pd_split}/{cls}")
            except Exception as exc:
                print(f"  {cls} ({pd_split}) atlandi: {exc}")
                continue
            files = [d for d in items if d["type"] == "file"
                     and d["name"].lower().endswith((".jpg", ".jpeg", ".png"))]
            out = out_root / our_split / "diger" if out_root == PV else out_root / cls.replace(" ", "_")
            out.mkdir(parents=True, exist_ok=True)
            with ThreadPoolExecutor(max_workers=16) as ex:
                jobs = {ex.submit(_dl, f["download_url"],
                                  out / (prefix + cls.replace(" ", "_") + "_" + f["name"])): f
                        for f in files}
                ok = sum(1 for fut in as_completed(jobs) if fut.result())
            total += ok
            print(f"  {cls:28s} {pd_split:5s}: {ok}/{len(files)}")
    return total


def main():
    if not (PV / "train").exists():
        raise RuntimeError(f"Once PlantVillage indirilmeli: {PV}/train yok.")
    print("== 'diger' sinifi (egitim + val) ==")
    n = _pull(DIGER_CLASSES, SPLIT_MAP, PV, "plantdoc_")
    print(f"'diger' toplam {n} foto -> {PV}/[train,val]/diger")
    # egitim tarafini cap'e indir - SINIFLAR ARASI DENGELI ornekle (cesitlilik korunur)
    train_diger = PV / "train" / "diger"
    by_cls: dict[str, list[Path]] = {}
    for p in sorted(train_diger.glob("*")):
        cls = p.name.split("_", 1)[1].rsplit("_", 1)[0]  # plantdoc_<cls>_<file>
        by_cls.setdefault(cls, []).append(p)
    keep: list[Path] = []
    i = 0
    # round-robin: her turden sirayla al -> cap'e kadar dengeli karisim
    while len(keep) < DIGER_CAP and any(i < len(v) for v in by_cls.values()):
        for v in by_cls.values():
            if i < len(v) and len(keep) < DIGER_CAP:
                keep.append(v[i])
        i += 1
    keepset = set(keep)
    removed = 0
    for p in train_diger.glob("*"):
        if p not in keepset:
            p.unlink(); removed += 1
    print(f"  train/diger dengeli kirpma: {len(keep)} tutuldu, {removed} silindi "
          f"({len(by_cls)} turden karisik)")

    print("== HELD-OUT (genelleme testi, egitime GIRMEZ) ==")
    m = _pull(HOLDOUT_CLASSES, {"test": "x"}, HOLDOUT, "hold_")
    print(f"held-out toplam {m} foto -> {HOLDOUT} (narenciye vekili, egitimde yok)")


if __name__ == "__main__":
    main()
