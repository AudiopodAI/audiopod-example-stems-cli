# Split a song into stems from the command line with AudioPod

A small Python CLI that separates a song into vocals, drums, bass and other stems and saves each one as an audio file, using the [AudioPod](https://audiopod.ai) Python SDK (`pip install audiopod`).

## Quickstart

```bash
pip install -r requirements.txt
export AUDIOPOD_API_KEY=ap_...          # create one at https://audiopod.ai/dashboard/account/api-keys
python stems.py song.mp3
# -> song_stems/vocals.wav, drums.wav, bass.wav, other.wav
```

Expected output:

```text
Separating song.mp3 into vocals, drums, bass, other...
  vocals        -> song_stems/vocals.wav
  drums         -> song_stems/drums.wav
  bass          -> song_stems/bass.wav
  other         -> song_stems/other.wav
Done (job 123).
```

## Options

```bash
python stems.py song.mp3 --mode two                         # vocals + instrumental (karaoke / acapella)
python stems.py song.mp3 --mode six                         # vocals, drums, bass, guitar, piano, other
python stems.py --url https://example.com/song.mp3 --out stems/
```

This CLI uses AudioPod's standard 2/4/6-stem separation, available on every plan; the premium 45-instrument catalog is available on Creator+. See [docs.audiopod.ai](https://docs.audiopod.ai/quickstarts/stem-separation).

## How it works

All of the AudioPod code is in [`stems.py`](stems.py):

```python
from audiopod import Client

client = Client()  # reads AUDIOPOD_API_KEY

job = client.stem_extraction.separate(file="song.mp3", mode="four")  # waits until COMPLETED
for stem, link in job["download_urls"].items():
    print(stem, link)  # a temporary download link per stem
```

`separate()` waits for the job by default. Pass `wait_for_completion=False` to get the job back right away, then call `client.stem_extraction.wait_for_completion(job["id"])` later.

## Pricing

The free Basic plan includes 5,000 credits, no card required. For paid plans and pay-as-you-go, see [audiopod.ai/pricing](https://audiopod.ai/pricing).

## Links

- AudioPod: https://audiopod.ai
- Docs: https://docs.audiopod.ai (stem separation guide: https://docs.audiopod.ai/quickstarts/stem-separation)
- Python SDK: https://pypi.org/project/audiopod/

## License

MIT
