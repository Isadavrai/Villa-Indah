#!/usr/bin/env python3
"""Deterministic, source-photo-only Villa Indah Telegram collage pack.

Source photographs are reused from assets/photos-new without generative edits.
Only layout, frame, typography and background are added. The rendered files
are checked into assets/telegram/{ru,en}/ by GitHub Actions.
"""
from PIL import Image, ImageDraw, ImageFont, ImageOps
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets/photos-new"
DEST = ROOT / "assets/telegram"
W = H = 1080
IVORY = (246, 242, 232)
GREEN = (27, 60, 47)
MUTED = (105, 106, 88)
WHITE = (253, 250, 243)
# Verified paths in the official original photography library.
STORIES = {
    "overview": ["Private Swimming Pool/03.webp", "Resort Facilities/02.webp", "Living room/01.webp", "Beach/02.webp"],
    "private_pool": ["Private Swimming Pool/03.webp", "Private Swimming Pool/01.webp", "Private Swimming Pool/04.webp", "Outdoor lounge Area/01.webp"],
    "beach": ["Beach/02.webp", "Beach/01.webp", "Beach/04.webp", "Beach/03.webp"],
    "grounds": ["Villa Grounds/02.webp", "Villa Grounds/01.webp", "Outdoor lounge Area/02.webp", "Private Swimming Pool/03.webp"],
    "master": ["Master Bedroom/02.webp", "Master Bedroom/01.webp", "Master Bedroom/03.webp", "Master Bedroom/04.webp"],
    "terrace": ["Terrace bedroom/01.webp", "Terrace bedroom/02.webp", "Terrace bedroom/03.webp", "Terrace bedroom/04.webp"],
    "twin": ["Twin Bedroom/01.webp", "Twin Bedroom/02.webp", "Twin Bedroom/03.webp", "Villa Grounds/01.webp"],
    "pool_view": ["Pool View Bedroom/01.webp", "Pool View Bedroom/03.webp", "Pool View Bedroom/04.webp", "Pool View Bedroom/05.webp"],
    "living": ["Living room/01.webp", "Living room/02.webp", "Living room/04.webp", "Living room/05.webp"],
    "lounge": ["Outdoor lounge Area/01.webp", "Outdoor lounge Area/02.webp", "Private Swimming Pool/06.webp", "Villa Grounds/01.webp"],
    "resort_experiences": ["Resort Facilities/02.webp", "Resort Facilities/03.webp", "Resort Facilities/04.webp", "Beach/02.webp"],
}
TITLES = {
    "ru": {
        "overview": "Вилла и курорт",
        "private_pool": "Собственный бассейн", "beach": "Пляж и океан",
        "grounds": "Территория виллы", "master": "Главная спальня",
        "terrace": "Спальня с террасой", "twin": "Спальня с двумя кроватями",
        "pool_view": "Спальня у бассейна", "living": "Гостиная и столовая",
        "lounge": "Зона отдыха", "resort_experiences": "Инфраструктура курорта",
    },
    "en": {
        "overview": "Villa & Resort",
        "private_pool": "Private Swimming Pool", "beach": "Beach & Ocean",
        "grounds": "Villa Grounds", "master": "Master Bedroom",
        "terrace": "Terrace Bedroom", "twin": "Twin Bedroom",
        "pool_view": "Pool View Bedroom", "living": "Living & Dining",
        "lounge": "Garden Lounge", "resort_experiences": "Resort Experiences",
    }
}
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
SERIF = FONT_DIR / "DejaVuSerif.ttf"
SANS = FONT_DIR / "DejaVuSans.ttf"


def font(path, size):
    if not path.exists():
        raise FileNotFoundError(f"Required system font missing: {path}")
    return ImageFont.truetype(str(path), size)


def centered(draw, text, y, style, fill, left=0, right=W):
    bbox = draw.textbbox((0, 0), text, font=style)
    width = bbox[2] - bbox[0]
    x = (left + right - width) // 2
    draw.text((x, y), text, font=style, fill=fill, stroke_width=0)


def draw_photo(canvas, source, bounds, radius=13):
    file = SRC / source
    if not file.is_file():
        raise FileNotFoundError(file)
    x0, y0, x1, y1 = bounds
    width, height = x1 - x0, y1 - y0
    with Image.open(file) as image:
        image = ImageOps.exif_transpose(image)
        image = ImageOps.fit(image.convert("RGB"), (width, height), Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, width - 1, height - 1), radius=radius, fill=255)
    canvas.paste(image, (x0, y0), mask)


def render(lang, key, photo_paths):
    img = Image.new("RGB", (W, H), IVORY)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((22, 22, W-23, H-23), radius=22, outline=GREEN, width=2)
    d.line((82, 103, 337, 103), fill=MUTED, width=2)
    d.line((743, 103, 998, 103), fill=MUTED, width=2)
    centered(d, "VILLA INDAH", 66, font(SERIF, 43), GREEN)
    centered(d, "PRIVATE VILLA  •  BALI", 136, font(SANS, 17), MUTED)
    # One large property photograph + three complementary gallery views.
    layout = [
        (62, 193, 1018, 604),
        (62, 618, 373, 873),
        (385, 618, 696, 873),
        (708, 618, 1018, 873),
    ]
    for path, box in zip(photo_paths, layout):
        draw_photo(img, path, box)
    title = TITLES[lang][key]
    selected = font(SERIF, 38 if len(title) < 24 else 32)
    while d.textbbox((0, 0), title, font=selected)[2] > 940:
        selected = font(SERIF, selected.size-2)
    centered(d, title, 898, selected, GREEN)
    d.line((170, 968, 420, 968), fill=MUTED, width=1)
    d.line((660, 968, 910, 968), fill=MUTED, width=1)
    centered(d, "ULUWATU  ·  BALI", 952, font(SANS, 20), MUTED)
    target = DEST / lang / (key + ".jpg")
    target.parent.mkdir(parents=True, exist_ok=True)
    img.save(target, "JPEG", quality=88, optimize=True, subsampling=0)
    if target.stat().st_size > 8_000_000:
        raise ValueError(f"Image too large: {target}")
    return {"path": str(target.relative_to(DEST)), "photos": photo_paths}


def main():
    records = []
    for lang in ("ru", "en"):
        for key, photos in STORIES.items():
            records.append(render(lang, key, photos))
    (DEST / "manifest.json").write_text(
        json.dumps({"source": "assets/photos-new", "generator": "scripts/build_telegram_collages.py", "files": records}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    print(f"Produced {len(records)} original-photo branded media cards")


if __name__ == "__main__":
    main()
