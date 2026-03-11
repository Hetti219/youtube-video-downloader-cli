#!/usr/bin/env python3
"""
YouTube Video Downloader CLI
A command-line tool for downloading YouTube videos and audio using yt-dlp.
"""

import argparse
import re
import shutil
import sys

import yt_dlp


# ── Constants ────────────────────────────────────────────────────────────────

VERSION = "2.1.0"

YOUTUBE_URL_PATTERN = re.compile(
    r"(https?://)?(www\.)?"
    r"(youtube\.com/(watch\?v=|shorts/|playlist\?list=)|youtu\.be/)"
    r"[\w\-]+"
)

# ANSI color helpers
_GREEN = "\033[92m"
_YELLOW = "\033[93m"
_RED = "\033[91m"
_CYAN = "\033[96m"
_BOLD = "\033[1m"
_RESET = "\033[0m"


# ── Helpers ──────────────────────────────────────────────────────────────────


def _info(msg: str) -> None:
    print(f"{_GREEN}✔ {msg}{_RESET}")


def _warn(msg: str) -> None:
    print(f"{_YELLOW}⚠ {msg}{_RESET}")


def _error(msg: str) -> None:
    print(f"{_RED}✖ {msg}{_RESET}", file=sys.stderr)


def validate_url(url: str) -> bool:
    """Return True if *url* looks like a valid YouTube URL."""
    return bool(YOUTUBE_URL_PATTERN.match(url))


def _find_aria2c() -> str | None:
    """Return path to aria2c if installed, else None."""
    return shutil.which("aria2c")


def build_ydl_opts(args: argparse.Namespace) -> dict:
    """Build the yt-dlp options dict from parsed CLI arguments."""
    outtmpl = f"{args.output}/%(title)s.%(ext)s"

    ydl_opts: dict = {
        "outtmpl": outtmpl,
        "noplaylist": not args.playlist,
        "quiet": False,
        "no_warnings": False,
        "progress_hooks": [_progress_hook],

        # ── Speed optimizations ──────────────────────────────────────
        # Enable Node.js as the JavaScript runtime so yt-dlp can
        # extract the full (un-throttled) format list from YouTube.
        "js_runtimes": {"node": {}},

        # Download up to 8 DASH/HLS fragments at once.
        "concurrent_fragment_downloads": 8,

        # Use 10 MiB HTTP chunks for faster throughput.
        "http_chunk_size": 10_485_760,

        # Retry resilience
        "retries": 10,
        "fragment_retries": 10,

        # Bypass YouTube's bandwidth throttle on DASH streams.
        "throttled_rate": "100K",
    }

    # Use aria2c as external downloader for multi-connection speed boost
    aria2c = _find_aria2c()
    if aria2c:
        ydl_opts["external_downloader"] = "aria2c"
        ydl_opts["external_downloader_args"] = {
            "aria2c": [
                "--min-split-size=1M",
                "--max-connection-per-server=16",
                "--split=16",
            ]
        }

    if args.audio_only:
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]
    elif args.quality and args.quality != "best":
        height = args.quality
        ydl_opts["format"] = (
            f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"
        )
    else:
        ydl_opts["format"] = "bestvideo+bestaudio/best"

    # Merge to mp4 when downloading separate video+audio streams
    if not args.audio_only:
        ydl_opts.setdefault("postprocessors", []).append(
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }
        )
        ydl_opts["merge_output_format"] = "mp4"

    return ydl_opts


def _progress_hook(d: dict) -> None:
    """Called by yt-dlp during download to show progress."""
    if d["status"] == "downloading":
        pct = d.get("_percent_str", "N/A").strip()
        speed = d.get("_speed_str", "N/A").strip()
        eta = d.get("_eta_str", "N/A").strip()
        print(
            f"\r{_CYAN}⬇  {pct}  |  {speed}  |  ETA: {eta}{_RESET}",
            end="",
            flush=True,
        )
    elif d["status"] == "finished":
        print()  # newline after progress
        _info("Download complete — post-processing…")


# ── Core ─────────────────────────────────────────────────────────────────────


def download(url: str, ydl_opts: dict) -> None:
    """Download *url* with the given yt-dlp options."""
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


# ── CLI ──────────────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ytvd",
        description="Download YouTube videos and audio from the command line.",
        epilog="Examples:\n"
        "  ytvd https://youtu.be/dQw4w9WgXcQ\n"
        "  ytvd https://youtu.be/dQw4w9WgXcQ -o ~/Videos\n"
        "  ytvd https://youtu.be/dQw4w9WgXcQ --audio-only\n"
        "  ytvd https://youtu.be/dQw4w9WgXcQ --quality 720\n"
        '  ytvd "https://youtube.com/playlist?list=PLxyz" --playlist\n',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("url", help="YouTube video or playlist URL")
    parser.add_argument(
        "-o",
        "--output",
        default=".",
        help="Directory to save downloads (default: current directory)",
    )
    parser.add_argument(
        "-q",
        "--quality",
        default="best",
        metavar="HEIGHT",
        help="Preferred video height, e.g. 1080, 720, 480 (default: best)",
    )
    parser.add_argument(
        "--audio-only",
        action="store_true",
        help="Download audio only and convert to MP3",
    )
    parser.add_argument(
        "--playlist",
        action="store_true",
        help="Download entire playlist instead of a single video",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # ── Validate URL ──────────────────────────────────────────────────
    if not validate_url(args.url):
        _error("Invalid YouTube URL.")
        _warn("Supported formats: youtube.com/watch?v=..., youtu.be/..., youtube.com/playlist?list=...")
        sys.exit(1)

    # ── Build options and download ────────────────────────────────────
    ydl_opts = build_ydl_opts(args)

    mode = "audio" if args.audio_only else "video"
    quality = args.quality if not args.audio_only else "192 kbps MP3"
    print(f"\n{_BOLD}▶  Starting {mode} download  |  Quality: {quality}{_RESET}")
    print(f"   {_CYAN}{args.url}{_RESET}\n")

    try:
        download(args.url, ydl_opts)
        print()
        _info(f"Saved to: {args.output}")
    except yt_dlp.utils.DownloadError as e:
        _error(f"Download failed: {e}")
        sys.exit(1)
    except yt_dlp.utils.ExtractorError as e:
        _error(f"Could not extract video info: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print()
        _warn("Download cancelled by user.")
        sys.exit(130)
    except Exception as e:
        _error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
