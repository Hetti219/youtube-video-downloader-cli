# YouTube Video Downloader CLI

A fast, feature-rich command-line tool for downloading YouTube videos and audio, powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp).

## Features

- 🎬 Download videos in any available quality (up to 4K+)
- 🎵 Audio-only mode — extract audio as MP3
- 📋 Playlist support — download entire playlists in one command
- 📊 Live progress bar with speed and ETA
- 🎯 Quality selection — choose your preferred resolution
- ✅ URL validation with clear error messages

## Prerequisites

- **Python 3.8+**
- **ffmpeg** — required for merging high-res video+audio streams and audio extraction.
  - Ubuntu/Debian: `sudo apt install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Installation

```bash
git clone https://github.com/Hetti219/youtube-video-downloader-cli.git
cd youtube-video-downloader-cli
pip install -r requirements.txt
```

## Usage

```bash
# Download a video (best quality, saved to current directory)
python ytvd_main.py https://youtu.be/dQw4w9WgXcQ

# Specify an output directory
python ytvd_main.py https://youtu.be/dQw4w9WgXcQ -o ~/Videos

# Download at a specific quality (e.g. 720p)
python ytvd_main.py https://youtu.be/dQw4w9WgXcQ --quality 720

# Download audio only as MP3
python ytvd_main.py https://youtu.be/dQw4w9WgXcQ --audio-only

# Download an entire playlist
python ytvd_main.py "https://youtube.com/playlist?list=PLxxxxxx" --playlist

# Combine options
python ytvd_main.py https://youtu.be/dQw4w9WgXcQ -o ~/Music --audio-only
```

### All Options

| Option | Description |
|---|---|
| `url` | YouTube video or playlist URL (required) |
| `-o, --output DIR` | Save directory (default: current directory) |
| `-q, --quality HEIGHT` | Preferred video height: `1080`, `720`, `480`, etc. (default: `best`) |
| `--audio-only` | Download audio only and convert to MP3 |
| `--playlist` | Download entire playlist |
| `-v, --version` | Show version number |
| `-h, --help` | Show help message |

## License

This project is licensed under the GNU General Public License v3.0 — see the [LICENSE](LICENSE) file for details.
