#!/usr/bin/env python3
"""Cinematic short-form villa reels from the OWNER'S REAL photos; no AI property scenes.

Generates RU/EN H.264+AAC MP4 in 9:16, with original procedural music.
Shared resort amenities remain clearly distinct from private villa amenities.
"""
from __future__ import annotations

import json
import math
import pathlib
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent.parent
PHOTOS = ROOT / "assets/photos-new"
OUT = ROOT / "dist/villa-reels-premium"
W, H, FPS = 1080, 1920, 24
FOREST = (21, 49, 41)
IVORY = (247, 244, 233)
GOLD = (216, 189, 135)
WHITE = (255, 255, 255)
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
CROSS = 0.28

# True source paths and conservative claims; 15 distinct photos plus final brand CTA.
SHOTS = [
    ("Private Swimming Pool/03.webp", "ВАШ БАЛИ НАЧИНАЕТСЯ ЗДЕСЬ", "Villa Indah · Улувату", "YOUR BALI STORY STARTS HERE", "Villa Indah · Uluwatu"),
    ("Private Swimming Pool/01.webp", "СОБСТВЕННЫЙ БАССЕЙН", "Пространство только для ваших гостей", "YOUR OWN PRIVATE POOL", "Reserved for your group"),
    ("Living room/01.webp", "ПРОСТРАНСТВО ДЛЯ ВСТРЕЧ", "Вместе, но без суеты", "SPACE TO BE TOGETHER", "Relaxed living with room to unwind"),
    ("Outdoor lounge Area/01.webp", "МЕДЛЕННЫЕ УТРА", "Террасы и тропическая зелень", "SLOW BALI MORNINGS", "Open terraces and tropical greenery"),
    ("Master Bedroom/01.webp", "ЧЕТЫРЕ СПАЛЬНИ", "Комфорт и приватность", "FOUR BEDROOMS", "Comfort and privacy"),
    ("Pool View Bedroom/01.webp", "ПРОСЫПАЙТЕСЬ НА БАЛИ", "Собственный ритм каждого дня", "WAKE UP IN BALI", "Every day, on your own terms"),
    ("Twin Bedroom/01.webp", "ДО ВОСЬМИ ГОСТЕЙ", "Отдых всей компанией", "UP TO EIGHT GUESTS", "Stay together in one villa"),
    ("Villa Grounds/01.webp", "ЗЕЛЕНЬ И УЕДИНЕНИЕ", "Ваша личная территория", "GREENERY AND PRIVACY", "An escape for your group"),
    ("Private Swimming Pool/05.webp", "ВОДА. ТИШИНА. БАЛИ.", "Каждый день здесь особенный", "POOL DAYS. BALI NIGHTS.", "Make time for the moments that matter"),
    ("Living room/03.webp", "ВСЁ ПРОСТРАНСТВО ВАШЕ", "Гостиная, кухня и зоны отдыха", "THE WHOLE VILLA IS YOURS", "Living space, kitchen and places to relax"),
    ("Terrace bedroom/02.webp", "КОМФОРТ В ДЕТАЛЯХ", "Спальни для спокойного отдыха", "COMFORT IN THE DETAILS", "Bedrooms made for taking it slow"),
    ("Resort Facilities/01.webp", "ВОЗМОЖНОСТИ КУРОРТА", "Общие зоны Karma Kandara", "RESORT EXPERIENCES", "Shared facilities at Karma Kandara"),
    ("Beach/01.webp", "ДОСТУП К ПЛЯЖУ", "Общий пляж курорта включён", "BEACH ACCESS INCLUDED", "Shared resort beach access"),
    ("Private Swimming Pool/02.webp", "ПРОСТО БУДЬТЕ ВМЕСТЕ", "Улувату · Бали", "TIME WELL SPENT TOGETHER", "Uluwatu · Bali"),
    ("Outdoor lounge Area/02.webp", "ВРЕМЯ ДЛЯ НОВЫХ ИСТОРИЙ", "Четыре спальни · до 8 гостей", "YOUR NEXT BALI MEMORY", "Four bedrooms · up to 8 guests"),
    ("Private Swimming Pool/03.webp", "УТОЧНИТЕ ДОСТУПНЫЕ ДАТЫ", "Напишите нам в Direct · Villa Indah", "ASK ABOUT AVAILABLE DATES", "DM Villa Indah to plan your stay"),
]


def font(path: str, sz: int):
    return ImageFont.truetype(path, sz)


def fit_font(draw, value: str, start: int, width: int, face=FONT_BOLD):
    for size in range(start, 22, -2):
        f = font(face, size)
        bbox = draw.textbbox((0, 0), value, font=f)
        if bbox[2] - bbox[0] <= width:
            return f
    return font(face, 22)


def make_card(path: str, heading: str, sub: str, index: int, language: str, target: pathlib.Path):
    source = PHOTOS / path
    if not source.exists():
        raise FileNotFoundError(f"Missing real original property photo: {source}")
    with Image.open(source) as photo:
        original = photo.convert("RGB")
    background = ImageOps.fit(original, (W, H), method=Image.Resampling.LANCZOS)
    background = background.filter(ImageFilter.GaussianBlur(32))
    background = Image.blend(background, Image.new("RGB", (W, H), FOREST), 0.48)

    image = Image.new("RGB", (W, H), FOREST)
    image.paste(background)
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, 0, W, 260), fill=(15, 37, 32, 162))
    draw.rectangle((0, 1470, W, H), fill=(14, 38, 32, 239))

    # Editorial photograph window: crop only, never invent or alter the property.
    photo_image = ImageOps.fit(original, (1000, 1125), Image.Resampling.LANCZOS,
                              centering=(0.5 if index % 2 else 0.48, 0.48))
    draw.rounded_rectangle((30, 290, 1050, 1437), radius=18, fill=(1, 7, 5, 85))
    image.paste(photo_image, (40, 300))
    draw = ImageDraw.Draw(image)

    draw.text((80, 53), "VILLA  INDAH", font=font(FONT_SERIF, 58), fill=IVORY)
    draw.text((83, 151), "U L U W A T U    ·    B A L I",
              font=font(FONT_REG, 24), fill=GOLD)
    draw.line((80, 1470, 1000, 1470), fill=GOLD, width=3)

    hf = fit_font(draw, heading, 60, 950)
    draw.text((80, 1565), heading, font=hf, fill=IVORY)
    sf = fit_font(draw, sub, 30, 910, FONT_REG)
    draw.text((81, 1693), sub, font=sf, fill=IVORY)
    draw.line((81, 1800, 190, 1800), fill=GOLD, width=4)
    draw.text((81, 1850), "V I L L A   I N D A H   /   " + language.upper(),
              font=font(FONT_REG, 18), fill=IVORY)
    draw.text((965, 1850), f"{index + 1:02d}", font=font(FONT_REG, 20), fill=GOLD)

    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target, "JPEG", quality=92, optimize=True, subsampling=0)


def run(args: list[str], quiet=True):
    subprocess.run(args, check=True,
                   stdout=subprocess.DEVNULL if quiet else None,
                   stderr=subprocess.PIPE if quiet else None)


def make_clip(card: pathlib.Path, video: pathlib.Path, duration: float, reverse: bool):
    # Subtle push-in/pull-out, intentionally within a photo scene (not AI footage).
    zoom = ("max(1.0,1.064-on*0.0012)" if reverse
            else "min(zoom+0.0012,1.064)")
    vf = (
        f"zoompan=z='{zoom}':x='iw/2-(iw/zoom/2)':"
        f"y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},"
        "format=yuv420p"
    )
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-loop", "1", "-framerate", str(FPS), "-t", str(duration),
         "-i", str(card), "-vf", vf,
         "-an", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20",
         "-pix_fmt", "yuv420p", str(video)])


def synthesise_music(length_seconds: float, output: pathlib.Path):
    """An ORIGINAL atmospheric beat, no samples or copyrighted tune."""
    rate = 24000
    n = int((length_seconds + 0.25) * rate)
    t = np.arange(n, dtype=np.float64) / rate
    audio = np.zeros(n, dtype=np.float64)
    bpm = 112
    beat = 60.0 / bpm
    chords = [
        [220.0, 261.63, 329.63],
        [174.61, 220.00, 261.63],
        [196.00, 246.94, 293.66],
        [164.81, 220.00, 261.63],
    ]
    # Quiet sustained pads under video, very light harmonic texture.
    for bar in range(int(length_seconds / (4 * beat)) + 2):
        start = bar * beat * 4
        if start >= length_seconds:
            break
        a = int(start * rate)
        b = min(n, a + int(4.1 * beat * rate))
        tt = np.arange(b - a) / rate
        env = np.minimum(tt / 0.5, 1.0) * np.minimum((tt[-1] - tt) / 0.7, 1.0)
        env = np.clip(env, 0, 1)
        chord = chords[bar % len(chords)]
        pad = sum(np.sin(2 * np.pi * freq * tt + np.sin(2 * np.pi * 0.15 * tt) * 0.02)
                  for freq in chord)
        audio[a:b] += (pad / len(chord)) * env * 0.055

    rng = np.random.default_rng(208)
    for bi in range(int(length_seconds / beat) + 1):
        a = int(bi * beat * rate)
        if a >= n:
            break
        # Soft electronic kick.
        L = min(int(0.23 * rate), n - a)
        s = np.arange(L) / rate
        wave_k = np.sin(2 * np.pi * (66.0 * s - 28.0 * s * s)) * np.exp(-18 * s)
        audio[a:a + L] += 0.24 * wave_k
        # Subtle brushed snare on 2 and 4.
        if bi % 4 in (1, 3):
            length = min(int(0.12 * rate), n - a)
            ss = np.arange(length) / rate
            audio[a:a + length] += 0.045 * rng.standard_normal(length) * np.exp(-32 * ss)

    for bi in range(int(length_seconds / (beat / 2)) + 1):
        a = int(bi * (beat / 2) * rate)
        if a >= n:
            break
        length = min(int(0.045 * rate), n - a)
        s = np.arange(length) / rate
        audio[a:a + length] += 0.018 * rng.standard_normal(length) * np.exp(-90 * s)

    # A minimal original plucked motif, not a cover or borrowed melody.
    notes = [440.00, 392.00, 329.63, 261.63, 329.63, 392.00, 293.66, 349.23]
    for i in range(int(length_seconds / beat) + 1):
        a = int(i * beat * rate)
        if a >= n:
            break
        length = min(int(0.29 * rate), n - a)
        s = np.arange(length) / rate
        freq = notes[i % len(notes)]
        pluck = (np.sin(2 * np.pi * freq * s) +
                 0.3 * np.sin(2 * np.pi * freq * 2 * s)) * np.exp(-12 * s)
        audio[a:a + length] += 0.065 * pluck

    fade_in = np.clip(t / 0.6, 0, 1)
    fade_out = np.clip((length_seconds - t) / 1.0, 0, 1)
    audio = np.tanh(audio * 1.3) * np.minimum(fade_in, fade_out)
    output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes((np.clip(audio, -0.98, 0.98) * 32767).astype("<i2").tobytes())


def finalize(clips: list[pathlib.Path], lengths: list[float],
             soundtrack: pathlib.Path, output: pathlib.Path):
    video_temp = output.with_name(output.stem + "_noaudio.mp4")
    all_inputs = []
    for clip in clips:
        all_inputs += ["-i", str(clip)]
    graph = []
    for i in range(len(clips)):
        graph.append(f"[{i}:v]fps={FPS},format=yuv420p,settb=AVTB,"
                     f"setpts=PTS-STARTPTS[v{i}]")
    prev = "v0"
    accumulated = lengths[0]
    moves = ("fade", "smoothleft", "fade", "smoothup", "fadeblack")
    for i in range(1, len(clips)):
        node = f"x{i}"
        graph.append(
            f"[{prev}][v{i}]xfade=transition={moves[(i-1) % len(moves)]}:"
            f"duration={CROSS:.2f}:offset={accumulated-CROSS:.2f}[{node}]"
        )
        prev = node
        accumulated += lengths[i] - CROSS
    try:
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             *all_inputs, "-filter_complex", ";".join(graph),
             "-map", f"[{prev}]", "-an", "-c:v", "libx264",
             "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
             "-movflags", "+faststart", str(video_temp)])
        print("TRANSITIONS=cinematic", flush=True)
    except subprocess.CalledProcessError:
        # The Instagram-ready files MUST still be emitted if xfade is not available.
        concat_file = output.with_name(output.stem + "_segments.txt")
        concat_file.write_text("\n".join(
            "file '" + str(clip.resolve()).replace("'", "'\\''") + "'"
            for clip in clips
        ) + "\n", encoding="utf-8")
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-f", "concat", "-safe", "0", "-i", str(concat_file),
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
             "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(video_temp)])
        print("TRANSITIONS=hardcuts_fallback", flush=True)

    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(video_temp), "-i", str(soundtrack),
         "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
         "-c:a", "aac", "-b:a", "160k", "-shortest",
         "-movflags", "+faststart", str(output)])
    video_temp.unlink(missing_ok=True)
    info = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_name,width,height:format=duration,size", "-of", "json",
         str(output)], text=True)
    data = json.loads(info)
    streams = data["streams"]
    assert any(s.get("width") == W and s.get("height") == H and s["codec_name"] == "h264"
               for s in streams), "Wrong Instagram video format"
    assert any(s["codec_name"] == "aac" for s in streams), "Audio missing"
    assert float(data["format"]["duration"]) > 29, "Reel shorter than expected"
    print(f"OK_FILE={output.name} DURATION={data['format']['duration']} "
          f"BYTES={data['format']['size']} AUDIO=original", flush=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    durations = [2.45 if i in (0, len(SHOTS)-1) else 2.3
                 for i in range(len(SHOTS))]
    target_duration = sum(durations) - CROSS * (len(durations) - 1)
    soundtrack = OUT / "original_music.wav"
    synthesise_music(target_duration, soundtrack)
    for lang in ("ru", "en"):
        work = OUT / ("working_" + lang)
        work.mkdir(exist_ok=True)
        clips = []
        for i, (source, ru, ru_sub, en, en_sub) in enumerate(SHOTS):
            card = work / f"card_{i:02d}.jpg"
            clip = work / f"clip_{i:02d}.mp4"
            heading, subtitle = (ru, ru_sub) if lang == "ru" else (en, en_sub)
            make_card(source, heading, subtitle, i, lang, card)
            make_clip(card, clip, durations[i], reverse=bool(i % 2))
            clips.append(clip)
        finalize(clips, durations, soundtrack,
                 OUT / f"villa_indah_dynamic_{lang}_instagram.mp4")
    print("REELS_READY=2 UNIQUE_REAL_PHOTOS=15 LANGUAGES=ru,en", flush=True)


if __name__ == "__main__":
    main()
