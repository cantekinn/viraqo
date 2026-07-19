"""Sentetik yaprak goruntusu ureteci (test/duman-testi amacli).

Gercek PlantVillage veri seti (~GB) indirmeden egitim ve teshis akisini uctan
uca denemek icin basit sentetik yapraklar cizer:
  - saglikli: duz yesil yaprak + damar cizgileri
  - gec_yaniklik: yesil yaprak + koyu kahve/siyah lekeler + sari hale

Iki cikti:
  1) ornek_fotograflar/  -> UI'ya yuklenip denenecek tek tek fotograflar
  2) data/plantvillage/{train,val}/<sinif>/  -> train.py duman testi icin mini set

Calistirma: py -m models.disease.make_synth_data
Not: Bu gercek egitim verisi DEGILDIR; yalnizca pipeline'i test eder.
"""
from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw

_DIR = Path(__file__).resolve().parent
_ROOT = _DIR.parent.parent
ORNEK_DIR = _ROOT / "app" / "ornek_fotograflar"
DATA_DIR = _ROOT / "data" / "plantvillage"

SIZE = 384


def _leaf_base(rng: random.Random) -> Image.Image:
    """Yesil yaprak govdesi + orta damar + yan damarlar."""
    img = Image.new("RGB", (SIZE, SIZE), (238, 236, 228))  # acik zemin
    d = ImageDraw.Draw(img)
    green = (34 + rng.randint(-10, 20), 120 + rng.randint(-15, 25), 40 + rng.randint(-10, 20))
    # yaprak elipsi (hafif dondurme hissi icin kenar bosluklari degisir)
    m = rng.randint(24, 44)
    d.ellipse([m, m // 2, SIZE - m, SIZE - m // 2], fill=green)
    # orta damar
    d.line([(SIZE // 2, m // 2 + 8), (SIZE // 2, SIZE - m // 2 - 8)], fill=(210, 225, 195), width=4)
    # yan damarlar
    for y in range(m + 20, SIZE - m, 34):
        off = rng.randint(-6, 6)
        d.line([(SIZE // 2, y), (m + 30, y - 22 + off)], fill=(200, 218, 185), width=2)
        d.line([(SIZE // 2, y), (SIZE - m - 30, y - 22 + off)], fill=(200, 218, 185), width=2)
    return img


def _healthy(rng: random.Random) -> Image.Image:
    return _leaf_base(rng)


def _late_blight(rng: random.Random) -> Image.Image:
    """Gec yaniklik: duzensiz koyu lekeler + sari hale."""
    img = _leaf_base(rng)
    d = ImageDraw.Draw(img)
    for _ in range(rng.randint(5, 10)):
        cx = rng.randint(70, SIZE - 70)
        cy = rng.randint(60, SIZE - 60)
        r = rng.randint(14, 34)
        # sari hale
        d.ellipse([cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6], fill=(196, 190, 70))
        # koyu leke merkezi (duzensiz)
        dark = (60 + rng.randint(-15, 15), 40 + rng.randint(-10, 10), 25 + rng.randint(-10, 10))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=dark)
        for _ in range(rng.randint(3, 6)):  # duzensiz cikinti
            ox, oy = rng.randint(-r, r), rng.randint(-r, r)
            rr = rng.randint(5, 12)
            d.ellipse([cx + ox - rr, cy + oy - rr, cx + ox + rr, cy + oy + rr], fill=dark)
    return img


def _save_set(kind: str, gen, n: int, split_dir: Path, rng: random.Random) -> None:
    out = split_dir / kind
    out.mkdir(parents=True, exist_ok=True)
    for i in range(n):
        gen(rng).save(out / f"{kind}_{i:02d}.jpg", quality=88)


def main() -> None:
    rng = random.Random(42)

    # 1) UI icin ornek fotograflar
    ORNEK_DIR.mkdir(parents=True, exist_ok=True)
    _healthy(rng).save(ORNEK_DIR / "saglikli_yaprak.jpg", quality=90)
    _late_blight(rng).save(ORNEK_DIR / "hastalikli_yaprak_gec_yaniklik.jpg", quality=90)

    # 2) train.py duman testi icin mini ImageFolder seti (2 sinif)
    classes = {"domates_saglikli": _healthy, "domates_gec_yaniklik": _late_blight}
    for kind, gen in classes.items():
        _save_set(kind, gen, 8, DATA_DIR / "train", rng)
        _save_set(kind, gen, 3, DATA_DIR / "val", rng)

    print(f"Ornek fotograflar: {ORNEK_DIR}")
    print(f"Mini egitim seti : {DATA_DIR} (2 sinif, train 8 + val 3)")


if __name__ == "__main__":
    main()
