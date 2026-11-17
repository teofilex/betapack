"""Pravi WebP varijante lokalnih slika iz frontend/public/ (JPEG/PNG ostaju kao rezerva).

Pokretanje:  python frontend/scripts/make-webp.py

- hero slike: puna verzija + 'mobile' isecak sa sredine (object-cover ih ionako
  prikazuje centrirane, pa je izgled isti, a telefon skida mnogo manje)
- slike sa pocetne: vise sirina za srcset
Zahteva Pillow (sa WebP podrskom).
"""
from __future__ import annotations

from pathlib import Path

import io
import math

from PIL import Image, ImageChops

PUBLIC = Path(__file__).resolve().parents[1] / 'public'
MIN_PSNR = 35.0  # dB u odnosu na izvornu sliku (za fotografije vizuelno gotovo neprimetna razlika)


def psnr(a: Image.Image, b: Image.Image) -> float:
    diff = ImageChops.difference(a.convert('RGB'), b.convert('RGB'))
    hist = diff.histogram()
    sq = sum(count * (i % 256) ** 2 for i, count in enumerate(hist))
    mse = sq / (a.width * a.height * 3)
    return 99.0 if mse == 0 else 10 * math.log10(255 ** 2 / mse)


def encode(img: Image.Image, quality: int) -> bytes:
    buf = io.BytesIO()
    img.save(buf, 'WEBP', quality=quality, method=6)
    return buf.getvalue()


def save(img: Image.Image, name: str) -> None:
    """Najnizi WebP kvalitet (50-90) koji ostaje blizu izvora (PSNR >= MIN_PSNR)."""
    chosen = None
    for quality in range(40, 95, 5):
        data = encode(img, quality)
        chosen = (quality, data)
        if psnr(img, Image.open(io.BytesIO(data))) >= MIN_PSNR:
            break
    quality, data = chosen
    (PUBLIC / name).write_bytes(data)
    print(f'{name}: {img.width}x{img.height}, q={quality}, {len(data) / 1024:.1f} KB')


def resized(img: Image.Image, width: int) -> Image.Image:
    height = round(img.height * width / img.width)
    return img.resize((width, height), Image.Resampling.LANCZOS)


def center_crop(img: Image.Image, width: int, height: int) -> Image.Image:
    left = (img.width - width) // 2
    top = (img.height - height) // 2
    return img.crop((left, top, left + width, top + height))


def main() -> None:
    # Hero prodavnica (ShopView): visina 450 px (steel) i 580 px (ambalaza), object-cover.
    # Na telefonima (<768 px) se vidi samo sredina: za steel 767 * 550 / 450 = 937 px
    # izvorne slike, za ambalazu 767 * 900 / 580 = 1190 px.
    steel = Image.open(PUBLIC / 'Betapack-hero-image-optimized.jpg').convert('RGB')
    save(steel, 'Betapack-hero-image-optimized.webp')
    save(center_crop(steel, 940, steel.height), 'Betapack-hero-image-optimized-mobile.webp')

    amb = Image.open(PUBLIC / 'AmbalazaHeroImage.jpeg').convert('RGB')
    save(amb, 'AmbalazaHeroImage.webp')
    save(center_crop(amb, 1200, amb.height), 'AmbalazaHeroImage-mobile.webp')

    # Pozadina pocetne (samo desktop)
    home = Image.open(PUBLIC / 'betapackHomeNew.jpg').convert('RGB')
    for width in (1280, 1920):
        save(resized(home, width) if width < home.width else home, f'betapackHomeNew-{width}.webp')

    # Slike panela na pocetnoj (samo telefon)
    for name, widths in (('steelMobileVersion', (640, 960, 1200)), ('ambalazaMobileVersion', (640, 960, 1280))):
        img = Image.open(PUBLIC / f'{name}.jpg').convert('RGB')
        for width in widths:
            save(resized(img, width) if width < img.width else img, f'{name}-{width}.webp')

    # Logo (providna pozadina)
    logo = Image.open(PUBLIC / 'betapack-logo.png').convert('RGBA')
    out = PUBLIC / 'betapack-logo.webp'
    logo.save(out, 'WEBP', quality=95, alpha_quality=100, method=6)
    print(f'betapack-logo.webp: {logo.width}x{logo.height}, {out.stat().st_size / 1024:.1f} KB')


if __name__ == '__main__':
    main()
