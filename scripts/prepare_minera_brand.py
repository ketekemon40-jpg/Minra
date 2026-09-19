"""Prepare the owner's supplied pixel mascot without redrawing or altering the character.

Rectilinear silhouette follows the supplied screenshot's pixel edges. This removes
the screenshot background, decorative rings and crosses while retaining dark boots
and equipment that a brightness/color-key removal would accidentally erase.
"""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'frontend/public/assets/branding'
source = Image.open(OUT / 'minera-original.jpg').convert('RGBA')
assert source.size == (346, 328), 'Inspect a replacement source before changing the silhouette.'
mask = Image.new('L', source.size, 0)
draw = ImageDraw.Draw(mask)
silhouette = [
    (135, 46, 212, 52), (119, 53, 228, 84), (96, 85, 259, 107),
    (119, 108, 236, 161), (96, 139, 251, 208), (88, 155, 126, 200),
    (229, 147, 259, 193), (119, 161, 229, 217),
    (119, 210, 157, 239), (190, 210, 228, 239),
    (104, 240, 165, 263), (182, 240, 243, 263),
]
for rectangle in silhouette:
    draw.rectangle(rectangle, fill=255)
source.putalpha(mask)
# Trim with a small consistent optical safe zone; preserve the complete silhouette.
mark = source.crop((86, 43, 262, 267))
mark.resize((352, 448), Image.Resampling.NEAREST).save(OUT / 'minera-logo.png', optimize=True)

# At favicon sizes a helmet/face crop is more legible than a shrunken full body.
face = source.crop((94, 44, 262, 166))
icon = Image.new('RGBA', (192, 192), (0, 0, 0, 0))
icon.alpha_composite(face, ((192-face.width)//2, (192-face.height)//2))
for size in (16, 32, 64):
    icon.resize((size, size), Image.Resampling.LANCZOS).save(OUT / f'minera-icon-{size}.png', optimize=True)
icon.save(ROOT / 'frontend/public/favicon.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48)])

# Full mascot for touch/home-screen icons, centered without stretching or clipping.
for size in (180, 192, 512):
    canvas = Image.new('RGBA', (size, size), (23, 25, 28, 255))
    height = round(size*.76)
    width = round(height*mark.width/mark.height)
    scaled = mark.resize((width, height), Image.Resampling.NEAREST)
    canvas.alpha_composite(scaled, ((size-width)//2, (size-height)//2))
    canvas.save(OUT / f'minera-icon-{size}.png', optimize=True)

assert mark.getchannel('A').getextrema() == (0, 255)
print('Prepared transparent Minera mascot, legible favicon crops and centered touch icons.')