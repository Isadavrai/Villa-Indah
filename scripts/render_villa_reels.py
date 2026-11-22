#!/usr/bin/env python3
"""Produce real-photo vertical reels for Villa Indah without generative scene edits.

Source photos come ONLY from this repository. No synthetic property imagery.
Outputs: bilingual silent MP4 reels for review, not auto-published.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1080, 1920
FPS = 24
DURATION = 3
CROSSFADE = 0.45
PAPER = (247, 245, 239)
FOREST = (27, 55, 46)
QUIET = (101, 109, 101)
GOLD = (144, 124, 90)
BASE = pathlib.Path(__file__).resolve().parent.parent

SCENES = [
    ("Private Swimming Pool/03.webp",
     {"ru": ("СВОЯ ВИЛЛА НА БАЛИ", "Индивидуальное пространство для вашей компании."),
      "en": ("YOUR OWN BALI VILLA", "A private place to stay together.")}),
    ("Living room/01.webp",
     {"ru": ("БОЛЬШЕ ПРОСТРАНСТВА", "Гостиная, кухня и открытые террасы."),
      "en": ("MORE ROOM TO RELAX", "A living area, kitchen and open terraces.")}),
    ("Master Bedroom/01.webp",
     {"ru": ("ЧЕТЫРЕ СПАЛЬНИ", "Комфортное размещение до 8 гостей."),
      "en": ("FOUR BEDROOMS", "Room for up to eight guests.")}),
    ("Private Swimming Pool/01.webp",
     {"ru": ("СОБСТВЕННЫЙ БАССЕЙН", "Только для гостей вашей виллы."),
      "en": ("YOUR PRIVATE POOL", "Reserved for your villa guests.")}),
    ("Beach/01.webp",
     {"ru": ("ПЛЯЖ КУРОРТА", "Доступ к общему пляжу входит в проживание."),
      "en": ("RESORT BEACH ACCESS", "Shared beach access included in your stay.")}),
    ("Villa Grounds/01.webp",
     {"ru": ("VILLA INDAH", "Уточните даты проживания в личных сообщениях."),
      "en": ("VILLA INDAH", "Message us to enquire about your dates.")}),
]
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    if not os.path.isfile(path):
        raise FileNotFoundError("Missing system font on renderer: " + path)
    return ImageFont.truetype(path, size)


def fit_font(draw: ImageDraw.ImageDraw, text: str, face: str,
             start: int, maxwidth: int, minimum: int = 25):
    size = start
    while size > minimum:
        f = font(face, size)
        if draw.textbbox((0, 0), text, font=f)[2] <= maxwidth:
            return f
        size -= 2
    return font(face, minimum)


def centered(draw: ImageDraw.ImageDraw, y: int, message: str, face: str,
             size: int, fill, maxwidth: int = 970):
    f = fit_font(draw, message, face, size, maxwidth)
    box = draw.textbbox((0, 0), message, font=f)
    width = box[2] - box[0]
    draw.text(((W - width) // 2, y), message, font=f, fill=fill,
              stroke_width=0)


def create_card(root: pathlib.Path, filename: str, heading: str, line: str,
                lang: str, output: pathlib.Path, index: int):
    original = root / "assets/photos-new" / filename
    if not original.is_file():
        raise FileNotFoundError("Villa photo missing: " + str(original))
    with Image.open(original) as source:
        photo = ImageOps.fit(source.convert("RGB"), (990, 1100),
                             method=Image.Resampling.LANCZOS,
                             centering=(0.5, 0.5))
    base = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(base)
    centered(draw, 89, "V I L L A   B A L I", FONT_SANS, 35, GOLD)
    centered(draw, 167, "INDAH", FONT_SERIF, 139, FOREST)
    centered(draw, 350, "ULUWATU  /  BALI", FONT_SANS, 27, QUIET)

    photo_y = 440
    base.paste(photo, (45, photo_y))
    draw = ImageDraw.Draw(base)
    draw.line((45, photo_y + 1140, 1035, photo_y + 1140),
              fill=(195, 189, 175), width=2)
    centered(draw, 1632, heading, FONT_SANS, 54, FOREST)
    centered(draw, 1731, line, FONT_SANS, 30, QUIET, 980)
    draw.line((460, 1836, 620, 1836), fill=GOLD, width=4)
    page_label = f"{index:02d}  /  {len(SCENES):02d}"
    centered(draw, 1868, page_label, FONT_SANS, 20, QUIET)
    output.parent.mkdir(parents=True, exist_ok=True)
    base.save(output, quality=92, optimize=True)


def encode_reel(cards: list[pathlib.Path], output: pathlib.Path):
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    for card in cards:
        command.extend(["-loop", "1", "-framerate", str(FPS),
                        "-t", str(DURATION), "-i", str(card)])
    filters = []
    for i in range(len(cards)):
        filters.append(
            f"[{i}:v]format=yuv420p,setsar=1,trim=duration={DURATION},"
            f"setpts=PTS-STARTPTS[v{i}]"
        )
    prev = "v0"
    for i in range(1, len(cards)):
        name = f"mix{i}"
        offset = (DURATION - CROSSFADE) * i
        filters.append(f"[{prev}][v{i}]xfade=transition=fade:"
                       f"duration={CROSSFADE}:offset={offset:.2f}[{name}]")
        prev = name
    filters.append(f"[{prev}]format=yuv420p[video]")
    command.extend([
        "-filter_complex", ";".join(filters),
        "-map", "[video]", "-an",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
        "-pix_fmt", "yuv420p", "-r", str(FPS), "-movflags", "+faststart",
        "-t", str(DURATION * len(cards) - CROSSFADE * (len(cards) - 1)),
        str(output),
    ])
    subprocess.run(command, check=True)
    subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                    "-show_entries", "stream=width,height,r_frame_rate",
                    "-of", "default=noprint_wrappers=1", str(output)],
                   check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=pathlib.Path, default=BASE)
    parser.add_argument("--out", type=pathlib.Path, default=BASE / "dist/villa-video")
    args = parser.parse_args()
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=True)
    for lang in ("ru", "en"):
        cards = []
        for idx, (filename, labels) in enumerate(SCENES, start=1):
            heading, subheading = labels[lang]
            card = output / "cards" / f"{lang}_{idx:02d}.jpg"
            create_card(args.repo.resolve(), filename, heading, subheading,
                        lang, card, idx)
            cards.append(card)
        encode_reel(cards, output / f"villa_indah_{lang}_vertical_silent.mp4")
    print("CREATED=2 LANGUAGES=ru,en FORMAT=1080x1920 SILENT=true")
    print("All imagery originates from the real Villa Indah photo repository.")
    print("No music rights are asserted. No upload/posting is performed.")


if __name__ == "__main__":
    main()
