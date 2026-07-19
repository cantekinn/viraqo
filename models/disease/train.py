"""Hastalik CNN egitimi (Sprint 2 - transfer ogrenme).

EfficientNetV2-S'i (timm, ImageNet on-egitimli) PlantVillage/PlantDoc alt kumesi
uzerinde ince ayar eder. Veri seti ImageFolder duzeninde beklenir:

    data/plantvillage/
        train/<sinif>/*.jpg
        val/<sinif>/*.jpg

Sinif klasor adlari labels.txt olarak kaydedilir; classifier.py bunlari kullanir.
Cikti: efficientnetv2_plant.pt (model agirliklari).

Calistirma:  py -m models.disease.train
Gereksinim: torch, torchvision, timm + indirilen veri seti (bu repo'ya dahil degil).
Not: memory karari geregi saha/lab farki icin PlantDoc/Cassava ile zenginlestirme onerilir.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

_DIR = Path(__file__).resolve().parent
DATA_ROOT = _DIR.parent.parent / "data" / "plantvillage"
CKPT = _DIR / "efficientnetv2_plant.pt"
LABELS_FILE = _DIR / "labels.txt"

MODEL_NAME = "tf_efficientnetv2_s"
IMG_SIZE = 224  # CPU egitimi icin 384 yerine 224 (PlantVillage kolay, hizli doygunlasir)


def _deps_ok() -> bool:
    return all(importlib.util.find_spec(m) for m in ("torch", "torchvision", "timm"))


# Saha (PlantDoc) fotolari egitimde azinlikta (~%20); lab-saha ucurumunu kapatmak
# icin bunlari daha sik ornekle. Dosya adi "plantdoc_" ile baslayanlar sahadir.
FIELD_WEIGHT = 3.0


def train(epochs: int = 10, batch_size: int = 32, lr: float = 3e-4) -> str:
    if not _deps_ok():
        raise RuntimeError("Egitim icin torch, torchvision, timm kurulmali.")
    if not (DATA_ROOT / "train").exists():
        raise RuntimeError(f"Veri seti bulunamadi: {DATA_ROOT}/train (ImageFolder duzeni).")

    import timm
    import torch
    from torch import nn
    from torch.utils.data import DataLoader, WeightedRandomSampler
    from torchvision import datasets, transforms

    device = "cuda" if torch.cuda.is_available() else "cpu"

    train_tf = transforms.Compose([
        transforms.RandomResizedCrop(IMG_SIZE, scale=(0.7, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(0.2, 0.2, 0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    val_tf = transforms.Compose([
        transforms.Resize(IMG_SIZE),
        transforms.CenterCrop(IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    train_ds = datasets.ImageFolder(DATA_ROOT / "train", train_tf)
    val_ds = datasets.ImageFolder(DATA_ROOT / "val", val_tf)
    LABELS_FILE.write_text("\n".join(train_ds.classes), encoding="utf-8")

    # saha fotolarini agirliklandirip azinlik dezavantajini gider
    weights = [FIELD_WEIGHT if "plantdoc_" in Path(p).name else 1.0 for p, _ in train_ds.samples]
    n_field = sum(1 for w in weights if w > 1.0)
    print(f"Egitim: {len(train_ds)} foto ({n_field} saha, x{FIELD_WEIGHT} agirlik), "
          f"{len(val_ds)} val, {len(train_ds.classes)} sinif.")
    sampler = WeightedRandomSampler(weights, num_samples=len(train_ds), replacement=True)

    train_dl = DataLoader(train_ds, batch_size=batch_size, sampler=sampler, num_workers=2)
    val_dl = DataLoader(val_ds, batch_size=batch_size, num_workers=2)

    model = timm.create_model(MODEL_NAME, pretrained=True, num_classes=len(train_ds.classes)).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
    crit = nn.CrossEntropyLoss(label_smoothing=0.1)

    # val ornekleri sirali: hangileri saha (plantdoc_) - ayri olcmek icin maske
    is_field = ["plantdoc_" in Path(p).name for p, _ in val_ds.samples]

    # Checkpoint secimi SAHA dogruluguna gore (asil hedef gercek tarla fotosu).
    # Esitlikte lab dogrulugu ayirt eder.
    best_field = -1.0
    best_lab = 0.0
    for ep in range(epochs):
        model.train()
        for xb, yb in train_dl:
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad()
            loss = crit(model(xb), yb)
            loss.backward()
            opt.step()
        sched.step()

        model.eval()
        preds: list[bool] = []
        with torch.no_grad():
            for xb, yb in val_dl:
                xb = xb.to(device)
                p = model(xb).argmax(1).cpu()
                preds.extend((p == yb).tolist())

        lab_c = lab_t = fld_c = fld_t = 0
        for ok, fld in zip(preds, is_field):
            if fld:
                fld_t += 1; fld_c += ok
            else:
                lab_t += 1; lab_c += ok
        lab_acc = lab_c / max(lab_t, 1)
        fld_acc = fld_c / max(fld_t, 1)
        print(f"epoch {ep+1}/{epochs}  saha_acc={fld_acc:.4f} ({fld_c}/{fld_t})  "
              f"lab_acc={lab_acc:.4f} ({lab_c}/{lab_t})", flush=True)
        if (fld_acc, lab_acc) >= (best_field, best_lab):
            best_field, best_lab = fld_acc, lab_acc
            torch.save({"model": model.state_dict(), "classes": train_ds.classes}, CKPT)

    print(f"Bitti. En iyi saha_acc={best_field:.4f}, lab_acc={best_lab:.4f}. Agirlik: {CKPT}")
    return str(CKPT)


if __name__ == "__main__":
    train()
