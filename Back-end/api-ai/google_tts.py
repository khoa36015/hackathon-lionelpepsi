"""
Google Cloud Text-to-Speech integration

This module replaces the previous FPT.AI implementation and wraps the
official `google-cloud-texttospeech` SDK with a simple interface used by
our Flask API.
"""
from __future__ import annotations

import base64
import json
import os
from functools import lru_cache
from typing import Dict, Optional

from google.cloud import texttospeech
from google.oauth2 import service_account

# Character limit enforced by Google Cloud Text-to-Speech.
MAX_INPUT_CHARACTERS = 5000

DEFAULT_VOICE = os.getenv("GOOGLE_TTS_DEFAULT_VOICE", "vi-VN-Neural2-A")
DEFAULT_AUDIO_FORMAT = os.getenv("GOOGLE_TTS_AUDIO_FORMAT", "mp3").lower()

SUPPORTED_VOICES: Dict[str, Dict[str, str]] = {
    "vi-VN-Neural2-A": {
        "language_code": "vi-VN",
        "gender": "FEMALE",
        "display_name": "Nữ miền Bắc (Neural2-A)",
    },
    "vi-VN-Neural2-B": {
        "language_code": "vi-VN",
        "gender": "MALE",
        "display_name": "Nam miền Bắc (Neural2-B)",
    },
    "vi-VN-Neural2-C": {
        "language_code": "vi-VN",
        "gender": "FEMALE",
        "display_name": "Nữ miền Nam (Neural2-C)",
    },
    "vi-VN-Neural2-D": {
        "language_code": "vi-VN",
        "gender": "MALE",
        "display_name": "Nam miền Nam (Neural2-D)",
    },
    "vi-VN-Wavenet-A": {
        "language_code": "vi-VN",
        "gender": "FEMALE",
        "display_name": "Nữ miền Bắc (Wavenet-A)",
    },
    "vi-VN-Wavenet-B": {
        "language_code": "vi-VN",
        "gender": "MALE",
        "display_name": "Nam miền Bắc (Wavenet-B)",
    },
}

AUDIO_FORMATS = {
    "mp3": texttospeech.AudioEncoding.MP3,
    "wav": texttospeech.AudioEncoding.LINEAR16,
    "ogg": texttospeech.AudioEncoding.OGG_OPUS,
}

AUDIO_MIME_TYPES = {
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "ogg": "audio/ogg",
}


def _load_service_account_credentials():
    """
    Try multiple ways to load service-account credentials:
      1. GOOGLE_TTS_CREDENTIALS_JSON → inline JSON
      2. GOOGLE_TTS_CREDENTIALS_BASE64 → base64-encoded JSON
      3. GOOGLE_TTS_CREDENTIALS_PATH → explicit path
      4. Default Google credential chain (GOOGLE_APPLICATION_CREDENTIALS, etc)
    """
    json_payload = os.getenv("GOOGLE_TTS_CREDENTIALS_JSON")
    if json_payload:
        info = json.loads(json_payload)
        return service_account.Credentials.from_service_account_info(info)

    b64_payload = os.getenv("GOOGLE_TTS_CREDENTIALS_BASE64")
    if b64_payload:
        decoded = base64.b64decode(b64_payload)
        info = json.loads(decoded)
        return service_account.Credentials.from_service_account_info(info)

    credentials_path = os.getenv("GOOGLE_TTS_CREDENTIALS_PATH")
    if credentials_path and os.path.exists(credentials_path):
        return service_account.Credentials.from_service_account_file(credentials_path)

    # Fall back to default credential chain
    return None


@lru_cache(maxsize=1)
def _get_client() -> texttospeech.TextToSpeechClient:
    credentials = _load_service_account_credentials()
    if credentials:
        return texttospeech.TextToSpeechClient(credentials=credentials)
    return texttospeech.TextToSpeechClient()


def _resolve_voice(voice_code: Optional[str]) -> Dict[str, str]:
    if voice_code and voice_code in SUPPORTED_VOICES:
        return {**SUPPORTED_VOICES[voice_code], "code": voice_code}

    # Fallback to default voice
    return {**SUPPORTED_VOICES.get(DEFAULT_VOICE, SUPPORTED_VOICES["vi-VN-Neural2-A"]), "code": DEFAULT_VOICE}


def synthesize_speech(
    text: str,
    voice: Optional[str] = None,
    speaking_rate: float = 1.0,
    pitch: float = 0.0,
    audio_format: str = DEFAULT_AUDIO_FORMAT,
) -> Dict[str, str]:
    """
    Convert text to speech using Google Cloud Text-to-Speech.

    Returns a dict that mirrors the previous API but includes base64 audio data.
    """
    if not text or len(text.strip()) < 3:
        return {"success": False, "error": "Text must contain at least 3 characters."}

    if len(text) > MAX_INPUT_CHARACTERS:
        return {"success": False, "error": f"Text exceeds {MAX_INPUT_CHARACTERS} character limit."}

    audio_format = (audio_format or DEFAULT_AUDIO_FORMAT).lower()
    if audio_format not in AUDIO_FORMATS:
        return {"success": False, "error": f"Unsupported audio format '{audio_format}'."}

    try:
        client = _get_client()
        voice_info = _resolve_voice(voice)

        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice_params = texttospeech.VoiceSelectionParams(
            language_code=voice_info["language_code"],
            name=voice_info["code"],
            ssml_gender=texttospeech.SsmlVoiceGender[voice_info["gender"]],
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=AUDIO_FORMATS[audio_format],
            speaking_rate=speaking_rate,
            pitch=pitch,
        )

        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice_params,
            audio_config=audio_config,
        )

        audio_b64 = base64.b64encode(response.audio_content).decode("utf-8")
        return {
            "success": True,
            "voice": voice_info["code"],
            "audio_content": audio_b64,
            "audio_mime_type": AUDIO_MIME_TYPES[audio_format],
            "characters": len(text),
            "speaking_rate": speaking_rate,
            "pitch": pitch,
        }
    except Exception as exc:
        return {
            "success": False,
            "error": f"Google TTS error: {exc}",
        }


def get_available_voices():
    """
    Return curated Vietnamese voices for the UI.
    """
    return [
        {
            "code": code,
            "name": meta["display_name"],
            "language_code": meta["language_code"],
            "gender": meta["gender"],
        }
        for code, meta in SUPPORTED_VOICES.items()
    ]


