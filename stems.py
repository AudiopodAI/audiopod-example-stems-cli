"""Split a song into stems with AudioPod and save each stem to a folder.

    pip install -r requirements.txt
    export AUDIOPOD_API_KEY=ap_...
    python stems.py song.mp3                  # vocals, drums, bass, other
    python stems.py song.mp3 --mode two       # vocals + instrumental (karaoke)
    python stems.py song.mp3 --mode six       # adds guitar and piano
    python stems.py --url https://example.com/song.mp3 --out stems/
"""

import argparse
import pathlib
import sys
from urllib.parse import urlparse

import requests

from audiopod import Client
from audiopod.exceptions import AudioPodError

# Standard separation modes (every plan). See https://docs.audiopod.ai for the rest.
MODES = {
    "two": "vocals + instrumental",
    "four": "vocals, drums, bass, other",
    "six": "vocals, drums, bass, guitar, piano, other",
}


def download(link: str, target: pathlib.Path) -> None:
    with requests.get(link, stream=True, timeout=300) as resp:
        resp.raise_for_status()
        with open(target, "wb") as fh:
            for chunk in resp.iter_content(chunk_size=1 << 16):
                fh.write(chunk)


def main() -> int:
    parser = argparse.ArgumentParser(description="Split a song into stems with AudioPod.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("file", nargs="?", type=pathlib.Path, help="local audio file")
    source.add_argument("--url", help="URL of an audio or video file instead of a local file")
    parser.add_argument("--mode", choices=list(MODES), default="four",
                        help="two, four (default) or six stems")
    parser.add_argument("--out", type=pathlib.Path,
                        help="output folder (default: <name>_stems next to the file, or ./stems)")
    args = parser.parse_args()

    if args.file is not None and not args.file.is_file():
        parser.error(f"{args.file} is not a file")
    out = args.out or (args.file.with_name(f"{args.file.stem}_stems") if args.file else pathlib.Path("stems"))
    out.mkdir(parents=True, exist_ok=True)

    client = Client(timeout=300)  # reads AUDIOPOD_API_KEY; long timeout for big uploads
    name = args.file.name if args.file else args.url
    print(f"Separating {name} into {MODES[args.mode]}...")
    try:
        # separate() uploads (or fetches the URL) and waits until the job is COMPLETED.
        job = client.stem_extraction.separate(
            file=str(args.file) if args.file else None,
            url=args.url,
            mode=args.mode,
            timeout=1800,
        )
    except AudioPodError as exc:
        print(f"AudioPod error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # a failed job raises Exception, a slow one TimeoutError
        print(f"Separation failed: {exc}", file=sys.stderr)
        return 1

    links = job.get("download_urls") or {}
    if not links:
        print(f"Job {job.get('id')} finished without download links.", file=sys.stderr)
        return 1
    for stem, link in links.items():
        suffix = pathlib.PurePosixPath(urlparse(link).path).suffix or ".wav"
        target = out / f"{stem}{suffix}"
        download(link, target)
        print(f"  {stem:<13} -> {target}")
    print(f"Done (job {job['id']}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
