from PIL import Image, ImageEnhance

SRC = r'c:\Users\Milos\Desktop\betaPackTests\code\betapack\frontend\public\Betapack-home.jpeg'
OUT_DIR = r'c:\Users\Milos\Desktop\betaPackTests\code\betapack\frontend\public'

src = Image.open(SRC)
w, h = src.size
target_ratio = 4 / 5


def crop_to_ratio(img, ratio, horizontal_bias=0.5, vertical_bias=0.5):
    iw, ih = img.size
    current_ratio = iw / ih
    if current_ratio > ratio:
        new_w = int(ih * ratio)
        left = int((iw - new_w) * horizontal_bias)
        left = max(0, min(left, iw - new_w))
        return img.crop((left, 0, left + new_w, ih))
    new_h = int(iw / ratio)
    top = int((ih - new_h) * vertical_bias)
    top = max(0, min(top, ih - new_h))
    return img.crop((0, top, iw, top + new_h))


# Ambalaža — desni deo sa proizvodima, crop ka desno
amb = src.crop((int(w * 0.52), 0, w, h))
amb = crop_to_ratio(amb, target_ratio, horizontal_bias=0.92, vertical_bias=0.05)
amb = amb.resize((900, 1125), Image.Resampling.LANCZOS)
amb = ImageEnhance.Brightness(amb).enhance(1.1)
amb = ImageEnhance.Contrast(amb).enhance(1.06)
amb.save(f'{OUT_DIR}/Betapack-home-mobile-ambalaza.jpeg', 'JPEG', quality=88, optimize=True)

# Gvožđara — leva polovina, kapije
steel = src.crop((0, 0, int(w * 0.54), h))
steel = crop_to_ratio(steel, target_ratio, horizontal_bias=0.35, vertical_bias=0.35)
steel = steel.resize((900, 1125), Image.Resampling.LANCZOS)
steel = ImageEnhance.Brightness(steel).enhance(1.05)
steel.save(f'{OUT_DIR}/Betapack-home-mobile-steel.jpeg', 'JPEG', quality=88, optimize=True)

print('Created mobile home images in', OUT_DIR)
