import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path


def atom_offsets(path):
    offsets = {}
    with path.open("rb") as stream:
        while True:
            offset = stream.tell()
            head = stream.read(8)
            if not head:
                return offsets
            size, kind = struct.unpack(">I4s", head)
            if size == 1:
                size = struct.unpack(">Q", stream.read(8))[0]
            assert size >= 8
            offsets[kind] = offset
            stream.seek(offset + size)


def verify(path, frame_count):
    probe = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)
    ]))
    video, audio = [next(s for s in probe["streams"] if s["codec_type"] == k) for k in ("video", "audio")]
    assert (video["width"], video["height"], video["pix_fmt"]) == (1080, 1920, "yuv420p")
    assert video["codec_name"] == "h264" and audio["codec_name"] == "aac"
    assert video["avg_frame_rate"] == video["r_frame_rate"] == "30/1"
    assert int(video["nb_frames"]) == frame_count
    assert video["color_space"] == video["color_primaries"] == video["color_transfer"] == "bt709"
    assert abs(float(probe["format"]["duration"]) - frame_count/30) < .04
    atoms = atom_offsets(path)
    assert atoms[b"moov"] < atoms[b"mdat"]
    subprocess.run(["ffmpeg", "-v", "error", "-xerror", "-i", str(path), "-f", "null", "-"], check=True)
    print(f"{path.name}: verified {frame_count} frames, {path.stat().st_size:,} bytes", flush=True)
    return hashlib.sha256(path.read_bytes()).hexdigest() + "  " + path.name


if __name__ == "__main__":
    directory = Path(sys.argv[1])
    sums = [
        verify(directory / "Villa_Indah_Quiet_Hours.mp4", 996),
        verify(directory / "Villa_Indah_Golden_Rhythm.mp4", 1284),
    ]
    (directory / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n")
