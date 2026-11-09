"""Transcribe long audio files to text.

The audio is split on silences into chunks (short requests are far more
reliable with free speech APIs), each chunk is sent to the Google Web
Speech API through the SpeechRecognition library, and the results are
joined. Any format ffmpeg can read works (wav, mp3, m4a, ogg ...).

Example:
    python speech_to_text.py lecture.mp3 --language fa-IR -o lecture.txt
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile

import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence


def split_audio(
    sound: AudioSegment, min_silence_ms: int = 500, silence_offset_db: float = 14
) -> list[AudioSegment]:
    """Split ``sound`` wherever there is at least ``min_silence_ms`` of silence.

    Silence is anything quieter than the clip's average loudness minus
    ``silence_offset_db``. Falls back to the whole clip if no split point exists.
    """
    chunks = split_on_silence(
        sound,
        min_silence_len=min_silence_ms,
        silence_thresh=sound.dBFS - silence_offset_db,
        keep_silence=300,
    )
    return chunks or [sound]


def transcribe_chunk(recognizer: sr.Recognizer, path: str, language: str) -> str:
    """Return the text for one audio chunk, or an empty string if nothing was understood."""
    with sr.AudioFile(path) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio, language=language)
    except sr.UnknownValueError:
        return ""


def transcribe(path: str, language: str = "en-US", verbose: bool = False) -> str:
    """Transcribe the audio file at ``path`` and return the full text."""
    recognizer = sr.Recognizer()
    sound = AudioSegment.from_file(path)
    pieces: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        chunks = split_audio(sound)
        for i, chunk in enumerate(chunks, start=1):
            chunk_path = os.path.join(tmp, f"chunk{i}.wav")
            chunk.export(chunk_path, format="wav")
            text = transcribe_chunk(recognizer, chunk_path, language)
            if verbose:
                print(f"[{i}/{len(chunks)}] {text or '(unrecognized)'}", file=sys.stderr)
            if text:
                pieces.append(text[0].upper() + text[1:] + ".")
    return " ".join(pieces)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Transcribe an audio file to text.")
    parser.add_argument("audio", help="path to an audio file (wav, mp3, m4a, ...)")
    parser.add_argument("-l", "--language", default="en-US", help="e.g. en-US, fa-IR, de-DE")
    parser.add_argument("-o", "--output", help="write the transcript to this file")
    parser.add_argument("-v", "--verbose", action="store_true", help="print each chunk")
    args = parser.parse_args(argv)

    try:
        text = transcribe(args.audio, args.language, args.verbose)
    except FileNotFoundError:
        print(f"File not found: {args.audio}", file=sys.stderr)
        return 1
    except sr.RequestError as exc:
        print(f"Speech API request failed: {exc}", file=sys.stderr)
        return 1

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"Transcript written to {args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
