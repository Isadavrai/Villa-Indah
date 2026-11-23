"""Two vertical Villa Indah films, composed exclusively from its photo gallery."""

import argparse
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.io.wavfile import write as wave_write
from scipy.signal import butter, sosfilt

WIDTH, HEIGHT, FPS = 1080, 1920, 30
RATE = 48000
SERIF = "/usr/share/fonts/truetype/noto/NotoSerifDisplay-Regular.ttf"
SANS = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
POOLS = "Private Swimming Pool"


@dataclass(frozen=True)
class Shot:
    end: float
    group: str
    number: int
    x: float
    y: float = .5
    zoom: float = 1
    move: float = .027
    drift: float = 0
    exposure: float = 1


# Endpoints follow the changes in scale and phrasing of each reference.
QUIET = [
    Shot(4.28, POOLS, 4, .58, .56, 1.22, .040, -.029, .87),
    Shot(6.60, "Living room", 3, .50, .51, 1.01, .025, .006, .83),
    Shot(9.40, "Pool View Bedroom", 1, .74, .51, 1.10, -.028, .037, .91),
    Shot(12.32, "Master Bedroom", 4, .59, .50, 1.03, .030, .019, .87),
    Shot(14.44, "Outdoor lounge Area", 2, .38, .51, 1.12, .033, .014, .85),
    Shot(16.00, "Master Bedroom", 8, .66, .78, 2.32, -.025, -.029, .91),
    Shot(18.24, "Living room", 5, .73, .44, 1.43, .036, .021, .83),
    Shot(19.76, "Twin Bedroom", 3, .67, .59, 1.20, .023, .009, .85),
    Shot(22.60, POOLS, 7, .76, .56, 1.17, .031, -.018, .82),
    Shot(26.32, POOLS, 2, .53, .75, 1.44, -.040, -.012, .80),
    Shot(31.34, POOLS, 2, .48, .51, 1.02, -.023, .012, .85),
]

RHYTHM = [
    Shot(.88, POOLS, 2, .48),
    Shot(1.64, "Living room", 5, .77, .44, 1.55),
    Shot(2.36, "Villa Grounds", 2, .49),
    Shot(3.36, POOLS, 6, .77, .47, 1.16),
    Shot(4.40, POOLS, 3, .68),
    Shot(5.44, "Living room", 3, .50),
    Shot(5.88, "Living room", 2, .31, .51, 1.18),
    Shot(7.64, "Master Bedroom", 2, .47, .56, 1.17),
    Shot(8.56, "Master Bedroom", 1, .62),
    Shot(9.40, "Master Bedroom", 7, .50, .62, 1.11),
    Shot(10.04, "Terrace bedroom", 2, .57, .45, 1.13),
    Shot(10.80, "Terrace bedroom", 8, .67),
    Shot(11.60, "Terrace bedroom", 3, .67),
    Shot(12.12, "Terrace bedroom", 5, .22, .47, 1.22),
    Shot(12.48, "Living room", 4, .73, .57, 1.25),
    Shot(12.88, "Master Bedroom", 5, .46, .54),
    Shot(13.44, "Pool View Bedroom", 6, .26, .56),
    Shot(14.08, "Pool View Bedroom", 3, .53, .60),
    Shot(15.28, "Pool View Bedroom", 4, .56),
    Shot(16.08, "Pool View Bedroom", 7, .62, .46),
    Shot(17.72, "Twin Bedroom", 1, .48),
    Shot(18.80, "Twin Bedroom", 3, .57, .53),
    Shot(19.60, "Villa Grounds", 1, .50, .52),
    Shot(20.52, "Outdoor lounge Area", 1, .51, .54),
    Shot(21.44, "Outdoor lounge Area", 2, .37, .53, 1.20),
    Shot(22.12, POOLS, 7, .76, .52, 1.10),
    Shot(23.08, POOLS, 6, .71, .58, 1.15),
    Shot(23.44, "Living room", 5, .70, .48, 1.24),
    Shot(24.08, "Living room", 6, .52, .44),
    Shot(24.72, "Master Bedroom", 4, .55, .53, 1.07),
    Shot(25.08, "Master Bedroom", 8, .69, .74, 1.59),
    Shot(25.72, "Terrace bedroom", 7, .52, .43),
    Shot(26.44, "Pool View Bedroom", 1, .69, .54),
    Shot(27.24, "Pool View Bedroom", 5, .59, .54),
    Shot(28.16, "Living room", 1, .39),
    Shot(28.60, "Living room", 4, .47, .57, 1.13),
    Shot(29.40, POOLS, 5, .46),
    Shot(30.24, POOLS, 1, .67, .58),
    Shot(31.08, POOLS, 7, .72, .67, 1.57),
    Shot(31.56, POOLS, 6, .76, .60, 1.35),
    Shot(32.20, POOLS, 4, .39, .48),
    Shot(32.88, "Villa Grounds", 2, .49, .54, 1.18),
    Shot(33.40, "Twin Bedroom", 3, .73, .56, 1.30),
    Shot(34.08, POOLS, 4, .75, .60, 1.28),
    Shot(34.60, POOLS, 3, .49, .63, 1.32),
    Shot(35.20, POOLS, 2, .48, .74, 1.32),
    Shot(35.84, "Beach", 2, .75, .52, 1.08),
    Shot(36.56, "Beach", 1, .55, .50, 1, -.03),
    Shot(37.32, "Villa Grounds", 1, .40, .50, 1.04),
    Shot(38.68, POOLS, 5, .56, .53, 1.10, -.025),
    Shot(42.80, POOLS, 2, .49, .50, 1, -.036),
]


def ease(v):
    v = np.clip(v, 0, 1)
    return v * v * (3 - 2 * v)


def tint(source, quiet, exposure):
    rgb = np.asarray(source.convert("RGB"), dtype=np.float32) / 255
    x = np.clip(rgb, 0, 1) ** (1.20 if quiet else 1.045)
    y = x @ np.array([.2126, .7152, .0722], dtype=np.float32)
    x = y[:, :, None] + (x - y[:, :, None]) * (.79 if quiet else .92)
    warmth = (.066 if quiet else .045) * np.sqrt(y) * (1 - y * .63)
    x += warmth[:, :, None] * np.array([1, .18, -.78], dtype=np.float32)
    x += ((1 - y)**2 * .011)[:, :, None] * np.array([0, .48, .51], dtype=np.float32)
    return np.uint8(np.clip(x * exposure, 0, 1) * 255 + .5)


def photo_frame(image, shot, phase):
    h, w = image.shape[:2]
    scale = max(WIDTH / w, HEIGHT / h) * (shot.zoom + .008 + abs(shot.move) / 2 + shot.move * (phase - .5))
    cx = (shot.x + shot.drift * (phase - .5)) * w
    cy = shot.y * h
    x = float(np.clip(WIDTH / 2 - cx * scale, WIDTH - w * scale, 0))
    y = float(np.clip(HEIGHT / 2 - cy * scale, HEIGHT - h * scale, 0))
    m = np.array([[scale, 0, x], [0, scale, y]], dtype=np.float64)
    return cv2.warpAffine(image, m, (WIDTH, HEIGHT), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def spaced_row(draw, content, font, y, tracking, color):
    widths = [draw.textlength(c, font=font) for c in content]
    x = (WIDTH - sum(widths) - tracking * (len(widths) - 1)) / 2
    for c, w in zip(content, widths):
        draw.text((x, y), c, font=font, fill=color, anchor="ls")
        x += w + tracking


def wordmark(quiet):
    canvas = Image.new("RGBA", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(canvas)
    warm = (244, 234, 212, 255) if quiet else (253, 229, 180, 255)
    spaced_row(draw, "VILLA INDAH", ImageFont.truetype(SERIF, 92), 969, 7, warm)
    spaced_row(draw, "ULUWATU  ·  BALI", ImageFont.truetype(SANS, 30), 1032, 5, warm)
    box = canvas.getbbox()
    colors = np.asarray(canvas.crop(box), dtype=np.float32)
    return box, colors[:, :, :3], colors[:, :, 3:] / 255


def finish_frame(frame, time, quiet, mark):
    if quiet:
        dark = 1 - .978 * float(ease((time - 29.95) / 1.38))
        title = float(ease((time - 27.92) / 1.15))
        if time >= 31.34:
            dark = 1
    else:
        dark = 1 - .89 * float(ease((time - 41.72) / 1.08))
        title = max(float(ease(time / .22) * (1 - ease((time - .71) / .17))),
                    float(ease((time - 39.24) / .78)))
        dark *= 1 - .34 * title
    if dark < 1:
        frame = cv2.convertScaleAbs(frame, alpha=dark)
    if title > .0001:
        (l, t, r, b), rgb, alpha = mark
        a = alpha * title
        region = frame[t:b, l:r]
        region[:] = np.uint8(region * (1 - a) + rgb * a + .5)
    return frame


def score(path, seconds, quiet, cuts):
    n = round(seconds * RATE)
    rng = np.random.default_rng(450 if quiet else 128)
    mix = np.zeros((n, 2))

    def add(signal, at, volume, pan=0):
        start = round(at * RATE)
        end = min(n, start + len(signal))
        if end > start:
            mix[start:end] += signal[:end-start, None] * volume * np.sqrt([(1-pan)/2, (1+pan)/2])

    def time(length):
        return np.arange(round(length * RATE)) / RATE

    def tone(note):
        return 440 * 2 ** ((note - 69) / 12)

    def key(note, length=2.7):
        t = time(length)
        p = 2 * np.pi * tone(note) * t
        return (np.sin(p) * np.exp(-1.38*t) + .27*np.sin(p*2.005)*np.exp(-4*t)
                + .10*np.sin(p*3.007)*np.exp(-7*t)) * (1 - np.exp(-t*110))

    patterns = [[45,52,59,60,64], [41,48,55,57,64], [48,55,59,62,67], [43,50,57,59,62]]
    phrase = 6.60 if quiet else 4.04
    for i, at in enumerate(np.arange(0, seconds, phrase)):
        notes = patterns[i % len(patterns)]
        t = time(phrase + 1.6)
        env = ease(t/.72) * ease((phrase+1.6-t)/1.6)
        for j, note in enumerate(notes):
            f = tone(note)
            p = 2*np.pi*f*t
            pad = (np.sin(p+.38*np.sin(t*2.2+j)) + .24*np.sin(p*2+.2*np.sin(t*1.7))) * env
            add(pad, at, (.023 if quiet else .017) * (1.3 if j == 0 else 1), .23*(j-2))
        for j, offset in enumerate([.75, 2.5, 4.95] if quiet else [.52, 1.51, 2.52, 3.53]):
            add(key(notes[(j+2)%5]+12), at+offset, .079 if quiet else .063, .31*(-1)**j)
    if quiet:
        amb = sosfilt(butter(2, [115, 620], fs=RATE, btype="bandpass", output="sos"), rng.normal(size=n))
        w = time(seconds)
        add(amb * (.58+.34*np.sin(w*1.38)**2), 0, .026, -.36)
        for i, cut in enumerate(cuts[::2]):
            add(key([69,64,67,62][i%4], 3.4), max(.15, cut-.3), .034, .38)
    else:
        period = .505
        for i, at in enumerate(np.arange(0.88, seconds-1.9, period)):
            t = time(.32)
            pulse = np.sin(2*np.pi*(46*t+2.28*(1-np.exp(-t*27))))*np.exp(-t*16)*ease(t/.004)
            add(pulse, at, .115 if i%4 in (0,2) else .052)
            t = time(.14)
            tick = np.diff(rng.normal(size=len(t)+1))*np.exp(-t*49)*ease(t/.005)
            add(tick, at+period/2, .015, (-1)**i*.31)
            if i%4 in (1,3):
                t = time(.18)
                snap = np.diff(rng.normal(size=len(t)+1))*np.exp(-t*35)*ease(t/.007)
                add(snap, at, .028, .16)
        for j, cut in enumerate([.88, 5.44, 7.64, 12.12, 17.72, 23.08, 29.4, 35.84, 38.68]):
            add(key([76,72,79,74][j%4], 1.9), cut, .071, (-1)**j*.40)
        t = time(4)
        air = sosfilt(butter(2, [130, 1550], fs=RATE, btype="bandpass", output="sos"), rng.normal(size=len(t)))
        add(air * np.sin(np.pi*t/4)**2, 34.7, .050, .30)
    dry = mix.copy()
    for delay, gain in [(.169,.17),(.33,.13),(.502,.09),(.779,.07), (1.09,.04)]:
        offset = round(delay * RATE)
        mix[offset:] += dry[:-offset, ::-1] * gain
    t = time(seconds)
    mix *= (ease(t/(.85 if quiet else .33)) * ease((seconds-t)/(2.7 if quiet else 1.45)))[:,None]
    mix *= .67 / max(np.abs(mix).max(), .001)
    wave_write(path, RATE, np.int16(mix*32767))


def render(label, shots, duration, quiet, repo, dest, scratch, preview):
    gallery = repo / "assets/photos-new"
    name = f"Villa_Indah_{label}"
    mark = wordmark(quiet)
    count = round(duration * FPS)
    ends = [round(s.end * FPS) for s in shots]
    cols = 5 if quiet else 7
    samples = len(shots)+1 if quiet else len(shots)
    contact = Image.new("RGB", (cols*159, math.ceil(samples/cols)*294), "#101611")
    draw = ImageDraw.Draw(contact)
    if not preview:
        wav = scratch / f"{label}.wav"
        score(wav, count/FPS, quiet, [s.end for s in shots[:-1]])
        output = dest / f"{name}.mp4"
        process = subprocess.Popen([
            "ffmpeg", "-y", "-v", "error", "-filter_threads", "1", "-f", "rawvideo",
            "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-i", "pipe:0",
            "-i", str(wav), "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,"
            "setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-threads", "3",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
            "-c:a", "aac", "-b:a", "192k", "-af", "loudnorm=I=-17:TP=-1.5:LRA=10", "-ar", "48000",
            "-t", str(count/FPS), "-movflags", "+faststart", str(output)
        ], stdin=subprocess.PIPE)

    def collect(frame, index, time):
        image = Image.fromarray(frame).resize((153,272), Image.Resampling.LANCZOS)
        x, y = index%cols*159, index//cols*294
        contact.paste(image, (x,y))
        draw.text((x+5,y+275), f"{time:05.2f}", fill="#eee2c6")

    begin = 0
    for i, (shot, end) in enumerate(zip(shots, ends)):
        image = tint(Image.open(gallery / shot.group / f"{shot.number:02d}.webp"), quiet, shot.exposure)
        mid = (begin+end)//2
        for k in ([mid] if preview else range(begin,end)):
            u = (k-begin) / max(1, end-begin-1)
            phase = .7*u+.3*float(ease(u))
            frame = finish_frame(photo_frame(image, shot, phase), k/FPS, quiet, mark)
            if k == mid:
                collect(frame, i, k/FPS)
            if not preview:
                process.stdin.write(frame.tobytes())
        begin = end
    if quiet:
        frame = finish_frame(np.full((HEIGHT,WIDTH,3), (7,9,8), dtype=np.uint8), 32.4, quiet, mark)
        collect(frame, samples-1, 32.4)
        if not preview:
            data = frame.tobytes()
            for _ in range(begin, count):
                process.stdin.write(data)
    if not preview:
        process.stdin.close()
        if process.wait() != 0:
            raise RuntimeError(f"Failed to render {label}")
    contact.save(dest / f"{name}_contact.jpg", quality=90)
    print(f"{name}: {count} frames, {count/FPS:.2f}s", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()
    cv2.setNumThreads(1)
    for path in [args.out, args.work]:
        path.mkdir(parents=True, exist_ok=True)
    for job in [("Quiet_Hours", QUIET, 33.20, True), ("Golden_Rhythm", RHYTHM, 42.80, False)]:
        render(*job, args.repo, args.out, args.work, args.preview)


if __name__ == "__main__":
    main()
