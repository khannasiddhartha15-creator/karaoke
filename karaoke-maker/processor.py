"""Core audio logic: turn a song into a karaoke (vocal-free) track.

Two methods:
  1. AI  (Demucs)  - separates vocals from music with a neural network. Best quality.
  2. Basic (FFmpeg) - cancels the centre channel. Fast, no AI, lower quality.
"""
import shutil
import subprocess
import sys
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "outputs"


def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def demucs_available() -> bool:
    try:
        import demucs  # noqa: F401
        return True
    except ImportError:
        return False


def _to_mp3(src: Path, dst: Path) -> Path:
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(src), "-codec:a", "libmp3lame", "-q:a", "2", str(dst)],
        check=True, capture_output=True,
    )
    return dst


def make_karaoke_ai(input_path: Path, job_id: str) -> Path:
    """Use Demucs two-stem mode: output is 'no_vocals.wav' (the instrumental)."""
    work = OUTPUT_DIR / job_id
    work.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [sys.executable, "-m", "demucs", "--two-stems=vocals", "-o", str(work), str(input_path)],
        check=True, capture_output=True,
    )
    stem = next(work.rglob("no_vocals.wav"))
    return _to_mp3(stem, work / "karaoke.mp3")


def make_karaoke_basic(input_path: Path, job_id: str) -> Path:
    """Phase-cancel the centre channel (where vocals usually sit)."""
    work = OUTPUT_DIR / job_id
    work.mkdir(parents=True, exist_ok=True)
    out = work / "karaoke.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(input_path),
         "-af", "pan=stereo|c0=c0-c1|c1=c1-c0",
         "-codec:a", "libmp3lame", "-q:a", "2", str(out)],
        check=True, capture_output=True,
    )
    return out


def make_karaoke(input_path: Path, job_id: str, method: str = "auto") -> tuple[Path, str]:
    """Returns (output_file, method_used)."""
    if not ffmpeg_available():
        raise RuntimeError("FFmpeg is not installed. Install it and add it to PATH.")
    if method in ("auto", "ai") and demucs_available():
        return make_karaoke_ai(input_path, job_id), "ai"
    if method == "ai":
        raise RuntimeError("Demucs is not installed. Run: pip install demucs")
    return make_karaoke_basic(input_path, job_id), "basic"
