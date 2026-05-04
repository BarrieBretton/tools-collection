import contextlib
import csv
import wave
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterator, Optional

try:
    from mutagen import File as MutagenFile
except ImportError:
    MutagenFile = None


@dataclass
class AudioInfo:
    filename: str
    path: str
    extension: str
    duration_seconds: Optional[float]
    duration_fraction: Optional[Fraction]
    error: Optional[str] = None


def seconds_to_hms_ms(total_seconds: float) -> tuple[int, int, int, int]:
    """
    Convert seconds to (hours, minutes, seconds, milliseconds).
    Rounds to nearest millisecond.
    """
    total_ms = round(total_seconds * 1000)

    hours = total_ms // 3_600_000
    total_ms %= 3_600_000

    minutes = total_ms // 60_000
    total_ms %= 60_000

    seconds = total_ms // 1000
    milliseconds = total_ms % 1000

    return hours, minutes, seconds, milliseconds


def format_hms_ms(total_seconds: float) -> str:
    h, m, s, ms = seconds_to_hms_ms(total_seconds)
    return f"{h}:{m:02d}:{s:02d}.{ms:03d}"


def get_wav_duration_fraction(path: Path) -> Fraction:
    """
    Return exact WAV duration as a Fraction using frame count / frame rate.
    """
    with contextlib.closing(wave.open(str(path), "rb")) as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        if rate <= 0:
            raise ValueError("Invalid WAV frame rate")
        return Fraction(frames, rate)


def get_mutagen_duration_seconds(path: Path) -> float:
    """
    Return duration in seconds for non-WAV audio files using mutagen.
    """
    if MutagenFile is None:
        raise RuntimeError(
            "mutagen is not installed. Install it with: pip install mutagen"
        )

    audio = MutagenFile(path)
    if audio is None or not hasattr(audio, "info") or audio.info is None:
        raise ValueError("Unsupported or unreadable audio format")

    length = getattr(audio.info, "length", None)
    if length is None:
        raise ValueError("Could not determine audio duration")

    return float(length)


def iter_files(folder: Path, recursive: bool) -> Iterator[Path]:
    if recursive:
        yield from (p for p in folder.rglob("*") if p.is_file())
    else:
        yield from (p for p in folder.iterdir() if p.is_file())


def read_audio_folder(
    dir_name: str | Path,
    recursive: bool = True,
    audio_extensions: Optional[set[str]] = None,
    wav_log_only: bool = True,
    hide_logs: bool = False,
    show_exceptions: bool = True,
) -> tuple[list[AudioInfo], Fraction]:
    """
    Scan a folder for audio files and return:
      - a list of AudioInfo
      - total duration as Fraction seconds

    WAV files are measured exactly using Fraction(frames, rate).
    Other supported audio formats use mutagen and are stored as Fraction from float.
    """
    folder = Path(dir_name).expanduser().resolve()
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a valid directory: {folder}")

    if audio_extensions is None:
        audio_extensions = {
            ".wav",
            ".mp3",
            ".flac",
            ".ogg",
            ".oga",
            ".m4a",
            ".aac",
            ".wma",
            ".opus",
        }

    results: list[AudioInfo] = []
    total_duration = Fraction(0, 1)

    files = sorted(iter_files(folder, recursive=recursive), key=lambda p: str(p).lower())

    for index, path in enumerate(files, start=1):
        ext = path.suffix.lower()

        if ext not in audio_extensions:
            if not wav_log_only and not hide_logs:
                print(f"{index}: {ext[1:] or 'no_ext'}   > {path.name}")
            continue

        try:
            if ext == ".wav":
                duration_fraction = get_wav_duration_fraction(path)
                duration_seconds = float(duration_fraction)
            else:
                duration_seconds = get_mutagen_duration_seconds(path)
                duration_fraction = Fraction(duration_seconds).limit_denominator(1_000_000)

            results.append(
                AudioInfo(
                    filename=path.name,
                    path=str(path),
                    extension=ext,
                    duration_seconds=duration_seconds,
                    duration_fraction=duration_fraction,
                )
            )
            total_duration += duration_fraction

            if not hide_logs:
                print(f"{index}: {ext[1:]}   > {path.name}")
                print(f"    {format_hms_ms(duration_seconds)}")

        except Exception as exc:
            results.append(
                AudioInfo(
                    filename=path.name,
                    path=str(path),
                    extension=ext,
                    duration_seconds=None,
                    duration_fraction=None,
                    error=str(exc),
                )
            )
            if show_exceptions and not hide_logs:
                print(f"{index}: Read exception   > {ext[1:] or 'unknown'}   > {path.name}")
                print(f"    {exc}")

    return results, total_duration


def export_csv(results: list[AudioInfo], output_csv: str | Path) -> Path:
    """
    Export per-file audio results to CSV.
    """
    output_path = Path(output_csv).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "filename",
                "path",
                "extension",
                "duration_seconds",
                "duration_hms_ms",
                "error",
            ]
        )

        for item in results:
            if item.duration_seconds is not None:
                duration_seconds = f"{item.duration_seconds:.6f}"
                duration_hms_ms = format_hms_ms(item.duration_seconds)
            else:
                duration_seconds = ""
                duration_hms_ms = ""

            writer.writerow(
                [
                    item.filename,
                    item.path,
                    item.extension,
                    duration_seconds,
                    duration_hms_ms,
                    item.error or "",
                ]
            )

    return output_path


if __name__ == "__main__":
    folder = Path(r"D:\FL Utils\Downloaded Songs")

    results, total_fraction = read_audio_folder(
        folder,
        recursive=True,
        wav_log_only=True,
        hide_logs=False,
        show_exceptions=True,
    )

    total_seconds = float(total_fraction)
    print("\nTotal duration:", format_hms_ms(total_seconds))

    csv_path = export_csv(results, folder / "audio_durations_report.csv")
    print("CSV exported to:", csv_path)

    readable_count = sum(1 for r in results if r.duration_seconds is not None)
    error_count = sum(1 for r in results if r.error)
    print(f"Readable audio files: {readable_count}")
    print(f"Files with read errors: {error_count}")