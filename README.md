# Speech to Text (Python)

Transcribe long audio files — lectures, interviews, voice notes — to text from the command line, in English, Persian or any language supported by Google's speech recognition.

```bash
python speech_to_text.py interview.mp3 --language fa-IR -o interview.txt
```

## How it works

Free speech-recognition endpoints only handle short clips reliably, so the script:

1. loads the file with **pydub** (any format ffmpeg can read),
2. splits it into chunks wherever there is a pause in speech,
3. sends each chunk to the Google Web Speech API via **SpeechRecognition**,
4. joins the recognized sentences into one transcript.

Chunks are written to a temporary folder that is cleaned up automatically.

## Setup

```bash
pip install -r requirements.txt
```

pydub needs [ffmpeg](https://ffmpeg.org/download.html) on your PATH for non-WAV formats (`brew install ffmpeg`, `sudo apt install ffmpeg`, or `choco install ffmpeg`).

## Usage

| Option | Description |
| --- | --- |
| `audio` | input file (wav, mp3, m4a, ogg ...) |
| `-l, --language` | language code, default `en-US` (e.g. `fa-IR`, `de-DE`) |
| `-o, --output` | save the transcript to a file instead of printing it |
| `-v, --verbose` | show each chunk as it is recognized |

## Notes

- The free Google Web Speech API needs an internet connection and has rate limits; for large volumes or offline use, swap `recognize_google` for `recognize_whisper` (local, via OpenAI Whisper).
- Accuracy depends on audio quality; tune `min_silence_ms` and `silence_offset_db` in `split_audio()` for noisy recordings.

## Credits

The silence-based chunking approach is based on the "How to Convert Speech to Text in Python" tutorial by The Python Code.

## License

[MIT](LICENSE)
