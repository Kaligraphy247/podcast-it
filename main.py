"""
title: Podcast It!
author: @kaligraphy247
version: 0.1.0
required_open_webui_version: 0.6.36
icon_url: data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLXBvZGNhc3QtaWNvbiBsdWNpZGUtcG9kY2FzdCI+PHBhdGggZD0iTTEzIDE3YTEgMSAwIDEgMC0yIDBsLjUgNC41YTAuNSAwLjUgMCAwIDAgMSAweiIgZmlsbD0iY3VycmVudENvbG9yIi8+PHBhdGggZD0iTTE2Ljg1IDE4LjU4YTkgOSAwIDEgMC05LjcgMCIvPjxwYXRoIGQ9Ik04IDE0YTUgNSAwIDEgMSA4IDAiLz48Y2lyY2xlIGN4PSIxMiIgY3k9IjExIiByPSIxIiBmaWxsPSJjdXJyZW50Q29sb3IiLz48L3N2Zz4=
description:
    Transform text conversations into engaging multi-speaker podcasts with AI-generated
    voices. Uses Google's Gemini TTS API to convert formatted transcripts into natural-sounding
    audio with two distinct speakers. Features an embedded audio player with dark mode support,
    optional transcript saving, and 30+ voice options. Simply format your content with
    "Speaker 1:" and "Speaker 2:" dialogue, click the action button, and get a professional
    podcast instantly. Files are securely stored via OWUI with user-specific access control.
"""
# requirements: google-genai

import io
import mimetypes
import re
import struct
import uuid

# from typing import Any, Optional
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from open_webui.models.files import FileForm, Files
from open_webui.storage.provider import Storage

LANGUAGES = {
    "Arabic (Egypt)": "ar-EG",
    "Bangla (Bangladesh)": "bn-BD",
    "Dutch (Netherlands)": "nl-NL",
    "English (India)": "en-IN",
    "English (United States)": "en-US",
    "English (United Kingdom)": "en-GB",
    "French (France)": "fr-FR",
    "German (Germany)": "de-DE",
    "Hindi (India)": "hi-IN",
    "Indonesian (Indonesia)": "id-ID",
    "Italian (Italy)": "it-IT",
    "Japanese (Japan)": "ja-JP",
    "Korean (South Korea)": "ko-KR",
    "Marathi (India)": "mr-IN",
    "Polish (Poland)": "pl-PL",
    "Portuguese (Brazil)": "pt-BR",
    "Romanian (Romania)": "ro-RO",
    "Russian (Russia)": "ru-RU",
    "Spanish (Spain)": "es-ES",
    "Tamil (India)": "ta-IN",
    "Telugu (India)": "te-IN",
    "Thai (Thailand)": "th-TH",
    "Turkish (Turkey)": "tr-TR",
    "Ukrainian (Ukraine)": "uk-UA",
    "Vietnamese (Vietnam)": "vi-VN",
}

SPEAKERS = {
    "Achernar (Female)": "Achernar",
    "Achird (Male)": "Achird",
    "Algenib (Male)": "Algenib",
    "Algieba (Male)": "Algieba",
    "Alnilam (Male)": "Alnilam",
    "Aoede (Female)": "Aoede",
    "Autonoe (Female)": "Autonoe",
    "Callirrhoe (Female)": "Callirrhoe",
    "Charon (Male)": "Charon",
    "Despina (Female)": "Despina",
    "Enceladus (Male)": "Enceladus",
    "Erinome (Female)": "Erinome",
    "Fenrir (Male)": "Fenrir",
    "Gacrux (Female)": "Gacrux",
    "Iapetus (Male)": "Iapetus",
    "Kore (Female)": "Kore",
    "Laomedeia (Female)": "Laomedeia",
    "Leda (Female)": "Leda",
    "Orus (Male)": "Orus",
    "Pulcherrima (Female)": "Pulcherrima",
    "Puck (Male)": "Puck",
    "Rasalgethi (Male)": "Rasalgethi",
    "Sadachbia (Male)": "Sadachbia",
    "Sadaltager (Male)": "Sadaltager",
    "Schedar (Male)": "Schedar",
    "Sulafat (Female)": "Sulafat",
    "Umbriel (Male)": "Umbriel",
    "Vindemiatrix (Female)": "Vindemiatrix",
    "Zephyr (Female)": "Zephyr",
    "Zubenelgenubi (Male)": "Zubenelgenubi",
}

DEFAULT_GEMINI_API_KEY_PLACEHOLDER = "REPLACE WITH YOUR GEMINI API KEY!!!"


def document_content_template(file_content_url: str, filename: str) -> str:
    """
    Generates an HTML template string for embedding a podcast audio player with a download link.

    The template includes CSS styles for light and dark modes and provides a styled audio
    control along with a download link for the audio file.

    Args:
        file_content_url (str): The URL to the audio file content.
        filename (str): The filename to use for the download link.

    Returns:
        str: An HTML string containing the styled audio player and download link.
    """
    return f"""
<style>
    :root {{
        --bg-color: #ffffff;
        --text-color: #1f2937;
        --heading-color: #111827;
        --link-color: #3b82f6;
        --link-hover-color: #2563eb;
        --border-color: #e5e7eb;
    }}

    @media (prefers-color-scheme: dark) {{
        :root {{
            --bg-color: #1f2937;
            --text-color: #e5e7eb;
            --heading-color: #f9fafb;
            --link-color: #60a5fa;
            --link-hover-color: #93c5fd;
            --border-color: #374151;
        }}
    }}

    .podcast-container {{
        padding: 10px 20px 20px 20px;
        background-color: var(--bg-color);
        color: var(--text-color);
        border-radius: 8px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol';
    }}

    .podcast-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        gap: 10px;
    }}

    .podcast-heading {{
        margin: 0;
        color: var(--heading-color);
        font-size: 1.125rem;
        font-weight: 600;
    }}

    .podcast-audio {{
        width: 100%;
        border-radius: 4px;
    }}

    .podcast-link {{
        color: var(--link-color);
        text-decoration: none;
        font-size: 0.875rem;
        white-space: nowrap;
        transition: color 0.2s ease;
    }}

    .podcast-link:hover {{
        color: var(--link-hover-color);
        text-decoration: underline;
    }}
</style>

<div class="podcast-container">
    <div class="podcast-header">
        <h3 class="podcast-heading">🎙️ Podcast Audio Player</h3>
        <a href="{file_content_url}" download="{filename}" class="podcast-link">
            📥 Download
        </a>
    </div>
    <audio controls class="podcast-audio">
        <source src="{file_content_url}" type="audio/wav">
        Your browser does not support the audio element.
    </audio>
</div>
"""


class Action:
    class Valves(BaseModel):
        # fmt: off
        API_KEY: str = Field(default=DEFAULT_GEMINI_API_KEY_PLACEHOLDER, description="Your Gemini API Key")
        # fmt:on
        tts_model: str = "gemini-2.5-flash-preview-tts"
        custom_style_instructions: str = "Read aloud in a warm, welcoming tone"
        speaker_1: str = Field(
            default="Zephyr (Female)",
            description="Select the voice for Speaker 1",
            json_schema_extra={"enum": list(SPEAKERS.keys())},
        )
        speaker_2: str = Field(
            default="Puck (Male)",
            description="Select the voice for Speaker 2",
            json_schema_extra={"enum": list(SPEAKERS.keys())},
        )
        podcast_output_language: str = Field(
            default="English (United States)",
            description="Select the output language for the podcast. (Only GA languages are listed)",
            json_schema_extra={"enum": list(LANGUAGES.keys())},
        )
        save_transcript: str = Field(
            default="Yes",
            description="Whether to save the processed Podcast transcript or not",
            json_schema_extra={"enum": ["Yes", "No"]},
        )

    def __init__(self) -> None:
        """Initialize the Action class with default Valves configuration."""
        self.valves = self.Valves()

    def _validate_transcript_format(self, text: str) -> dict:
        """
        Validate and parse transcript format with detailed feedback.

        Parses the transcript to ensure it follows the required format for podcast generation.
        Validates speaker line formatting, counts speaker occurrences, and extracts style
        instructions if present. Falls back to default style instructions when none provided.

        Expected format:
            {Style instructions} (optional)
            Speaker 1: dialogue
            Speaker 2: dialogue
            ...

        Args:
            text: The raw transcript text to validate and parse.

        Returns:
            dict: A dictionary containing validation results and parsed data:
                {
                    "valid": bool - Whether the transcript is valid
                    "error": str | None - Error message if validation failed
                    "warning": str | None - Warning message for non-critical issues
                    "style": str - Style instructions (user-provided or default)
                    "dialogues": list[dict] - Parsed speaker dialogues [{"speaker": "1"|"2", "text": str}, ...]
                    "has_style": bool - Whether style instructions were found
                    "speaker_1_count": int - Number of Speaker 1 lines
                    "speaker_2_count": int - Number of Speaker 2 lines
                }
        """
        result = {
            "valid": False,
            "error": None,
            "warning": None,
            "style": "",
            "dialogues": [],
            "has_style": False,
            "speaker_1_count": 0,
            "speaker_2_count": 0,
        }

        # Check for empty input
        if not text or not text.strip():
            result["error"] = "Transcript is empty"
            return result

        lines: list = text.strip().split("\n")
        # Pattern for speaker lines
        speaker_pattern = r"^Speaker ([12]):\s*(.+)$"

        # style_lines = ""
        style_lines = []
        dialogues = []
        first_speaker_found = False

        for line_num, line in enumerate(lines, 1):
            line: str = line.strip()

            # Skip empty lines
            if not line:
                continue

            match = re.match(speaker_pattern, line)
            if match:
                first_speaker_found = True
                speaker_num = match.group(1)
                content = match.group(2).strip()

                # Check for empty dialogues
                if not content:
                    result["error"] = (
                        f"Line {line_num}: Speaker {speaker_num} has no dialogue"
                    )
                    return result

                dialogues.append({"speaker": speaker_num, "text": content})
            else:
                # Non speaker line
                if not first_speaker_found:
                    # Before first speaker = style instructions
                    # style_lines = line
                    style_lines.append(line)
                else:
                    # After speakers = malformed
                    result["warning"] = (
                        f"Line {line_num}: Unexpected text after speakers started: '{line[:50]}...'"
                    )

        # Count speakers
        speaker_1_count = sum(1 for d in dialogues if d["speaker"] == "1")
        speaker_2_count = sum(1 for d in dialogues if d["speaker"] == "2")

        result["speaker_1_count"] = speaker_1_count
        result["speaker_2_count"] = speaker_2_count

        # Validation checks
        if len(dialogues) == 0:
            result["error"] = (
                "No speaker dialogues found. Expected format:\nSpeaker 1: text\nSpeaker 2: text"
            )
            return result

        if len(dialogues) < 2:
            result["error"] = (
                f"Need at least 2 speaker lines for a conversation, found only {len(dialogues)}"
            )
            return result

        if speaker_1_count == 0:
            result["error"] = "Missing Speaker 1 lines"
            return result

        if speaker_2_count == 0:
            result["error"] = "Missing Speaker 2 lines"
            return result

        # Style instructions check
        if style_lines:
            result["has_style"] = True
            result["style"] = "\n".join(style_lines)
        else:
            result["warning"] = (
                "No style instructions found. Consider adding tone/style guidance before speaker lines to set the tone of the conversation"
            )

            result["has_style"] = True
            # use the default/custom self.valves.custom_style_instructions
            result["style"] = self.valves.custom_style_instructions

        # and the success
        result["valid"] = True
        result["dialogues"] = dialogues
        return result

    async def _generate_podcast(
        self, transcript: str, user_id: str, podcast_name: str = "audio"
    ) -> list[str]:
        """
        Convert transcript to podcast audio using Gemini TTS API.

        Streams audio generation from the Gemini API with multi-speaker voice configuration.
        Automatically converts non-WAV formats to WAV. Saves transcript file only after
        successful audio generation to prevent orphaned files. Supports chunked audio output
        for longer podcasts.

        Args:
            transcript: The formatted transcript text with speaker dialogues.
            user_id: User ID for file ownership and access control.
            podcast_name: Base name for the generated files (default: "audio").

        Returns:
            list[str]: List of file IDs in order - transcript file (if enabled) followed by
                      audio file(s). Returns empty list if generation fails.

        Raises:
            Exception: Propagates any errors from Gemini API or file storage operations.
        """
        file_ids = []

        # Generate audio first (don't save transcript until we know audio generation succeeds)
        client = genai.Client(api_key=self.valves.API_KEY)

        # Prepare content
        contents = [
            types.Content(role="user", parts=[types.Part.from_text(text=transcript)])
        ]

        # Prepare speech config
        speech_config = types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                    types.SpeakerVoiceConfig(
                        speaker="Speaker 1",
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=SPEAKERS[self.valves.speaker_1]
                            )
                        ),
                    ),
                    types.SpeakerVoiceConfig(
                        speaker="Speaker 2",
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=SPEAKERS[self.valves.speaker_2]
                            )
                        ),
                    ),
                ]
            )
        )

        # Generate config
        generate_content_config = types.GenerateContentConfig(
            temperature=1, response_modalities=["audio"], speech_config=speech_config
        )

        # Stream and save audio chunks
        file_index = 0
        for chunk in client.models.generate_content_stream(
            model=self.valves.tts_model,
            contents=contents,  # type: ignore
            config=generate_content_config,
        ):
            if (
                chunk.candidates is None
                or chunk.candidates[0].content is None
                or chunk.candidates[0].content.parts is None
            ):
                continue

            if (
                chunk.candidates[0].content.parts[0].inline_data
                and chunk.candidates[0].content.parts[0].inline_data.data
            ):
                inline_data = chunk.candidates[0].content.parts[0].inline_data
                data_buffer = inline_data.data
                file_extension = mimetypes.guess_extension(inline_data.mime_type)  # type: ignore

                # Convert to WAV if needed
                if file_extension is None:
                    file_extension = ".wav"
                    data_buffer = self._convert_to_wav(
                        inline_data.data,  # type: ignore
                        inline_data.mime_type,  # type: ignore
                    )

                # Save audio file with index if multiple chunks
                chunk_name = (
                    f"{podcast_name}_{file_index}" if file_index > 0 else podcast_name
                )
                audio_file_id = self._save_file(
                    file_bytes=data_buffer,  # type: ignore
                    user_id=user_id,
                    name=chunk_name,
                    mime="audio/wav",
                )
                file_ids.append(audio_file_id)
                file_index += 1

            else:
                # Text response (shouldn't happen with audio modality)
                print(f"Unexpected text chunk: {chunk.text}")

        # Optionally save transcript after successful audio generation, if enabled
        if self.valves.save_transcript == "Yes" and len(file_ids) > 0:
            transcript_bytes = transcript.encode("utf-8")
            transcript_file_id = self._save_file(
                file_bytes=transcript_bytes,
                user_id=user_id,
                name=podcast_name,
                mime="text/plain",
            )
            file_ids.insert(
                0, transcript_file_id
            )  # Insert at beginning so transcript is first

        return file_ids

    def _convert_to_wav(self, audio_data: bytes, mime_type: str) -> bytes:
        """
        Convert raw audio data to WAV format by generating a proper WAV file header.

        Parses the MIME type to extract sample rate and bit depth, then constructs a
        valid WAV/RIFF header according to the WAV specification. Defaults to 24000 Hz
        sample rate and 16-bit PCM encoding if parameters cannot be extracted.

        Format specification: http://soundfile.sapp.org/doc/WaveFormat/

        Args:
            audio_data: The raw audio data as a bytes object (PCM samples).
            mime_type: MIME type of the audio data (e.g., "audio/L16;rate=24000").

        Returns:
            bytes: Complete WAV file (header + audio data) ready to be saved.
        """
        parameters = self._parse_audio_mime_type(mime_type)
        bits_per_sample = parameters["bits_per_sample"]
        sample_rate = parameters["rate"]
        num_channels = 1
        data_size = len(audio_data)
        bytes_per_sample = bits_per_sample // 8  # type: ignore
        block_align = num_channels * bytes_per_sample
        byte_rate = sample_rate * block_align  # type: ignore
        chunk_size = 36 + data_size  # 36 bytes for header fields before data chunk size

        # http://soundfile.sapp.org/doc/WaveFormat/

        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",  # ChunkID
            chunk_size,  # ChunkSize (total file size - 8 bytes)
            b"WAVE",  # Format
            b"fmt ",  # Subchunk1ID
            16,  # Subchunk1Size (16 for PCM)
            1,  # AudioFormat (1 for PCM)
            num_channels,  # NumChannels
            sample_rate,  # SampleRate
            byte_rate,  # ByteRate
            block_align,  # BlockAlign
            bits_per_sample,  # BitsPerSample
            b"data",  # Subchunk2ID
            data_size,  # Subchunk2Size (size of audio data)
        )
        return header + audio_data

    def _parse_audio_mime_type(self, mime_type: str) -> dict[str, int | None]:
        """
        Parse bits per sample and sample rate from an audio MIME type string.

        Extracts audio encoding parameters from MIME type strings. Assumes bits per sample
        is encoded like "L16" (Linear 16-bit) and rate as "rate=xxxxx". Falls back to
        safe defaults (16-bit, 24000 Hz) if parameters cannot be parsed.

        Args:
            mime_type: The audio MIME type string (e.g., "audio/L16;rate=24000").

        Returns:
            dict[str, int | None]: Dictionary with "bits_per_sample" and "rate" keys.
                                   Values are integers (default: 16 bits, 24000 Hz).

        Examples:
            >>> _parse_audio_mime_type("audio/L16;rate=24000")
            {"bits_per_sample": 16, "rate": 24000}
            >>> _parse_audio_mime_type("audio/L24;rate=48000")
            {"bits_per_sample": 24, "rate": 48000}
        """
        bits_per_sample = 16
        rate = 24000

        # Extract rate from parameters
        parts = mime_type.split(";")
        for param in parts:  # Skip the main type part
            param = param.strip()
            if param.lower().startswith("rate="):
                try:
                    rate_str = param.split("=", 1)[1]
                    rate = int(rate_str)
                except (ValueError, IndexError):
                    # Handle cases like "rate=" with no value or non-integer value
                    pass  # Keep rate as default
            elif param.startswith("audio/L"):
                try:
                    bits_per_sample = int(param.split("L", 1)[1])
                except (ValueError, IndexError):
                    pass  # Keep bits_per_sample as default if conversion fails

        return {"bits_per_sample": bits_per_sample, "rate": rate}

    def _save_file(
        self,
        file_bytes: bytes,
        user_id: str,
        name: str,
        mime: str = "audio/wav",
    ) -> str:
        """
        Save file to Open WebUI storage and create database record with access control.

        Handles both transcript (text/plain) and audio (audio/wav) files using Open WebUI's
        storage factory pattern, which automatically routes to the configured backend
        (local/S3/GCS/Azure). Creates database records with user-specific access control
        and appropriate metadata tags.

        Args:
            file_bytes: The file content as bytes.
            user_id: User ID for file ownership and access control.
            name: Base name for the file (without extension).
            mime: MIME type of the file - "text/plain" or "audio/wav" (default: "audio/wav").

        Returns:
            str: The unique file ID assigned to the saved file.

        Note:
            - Transcript files are named: "Podcast_Transcript_{name}.txt"
            - Audio files are named: "Podcast_{name}.wav"
            - Access is restricted to the creator (and admins)
            - Files are tagged with user ID, file ID, and type for auditing
        """
        # Generate unique ID (common for both text and audio)
        file_id = str(uuid.uuid4())

        if mime == "text/plain":
            # Save transcript as text file
            filename = f"Podcast_Transcript_{name}.txt"
            storage_filename = f"{file_id}_{filename}"

            # Upload to storage
            file_obj = io.BytesIO(file_bytes)
            contents, file_path = Storage.upload_file(
                file=file_obj,
                filename=storage_filename,
                tags={
                    "OpenWebUI-User-Id": user_id,
                    "OpenWebUI-File-Id": file_id,
                    "OpenWebUI-Type": "podcast_transcript",
                },
            )

            # Create database record for transcript with access control
            file_form = FileForm(
                id=file_id,
                filename=filename,
                path=file_path,
                data={"status": "completed", "content": "Podcast transcript"},
                meta={
                    "name": filename,
                    "content_type": "text/plain",
                    "size": len(file_bytes),
                    "data": {"type": "podcast_transcript"},
                },
                access_control={"read": {"user_ids": [user_id]}},
            )

            file_item = Files.insert_new_file(user_id=user_id, form_data=file_form)
            return file_item.id  # type: ignore

        else:
            # Save audio file (wav)
            filename = f"Podcast_{name}.wav"
            storage_filename = f"{file_id}_{filename}"

            # Upload to storage
            # (factory pattern automatically handles local/S3/GCS/Azure)
            file_obj = io.BytesIO(file_bytes)
            contents, file_path = Storage.upload_file(
                file=file_obj,
                filename=storage_filename,
                tags={
                    "OpenWebUI-User-Id": user_id,
                    "OpenWebUI-File-Id": file_id,
                    "OpenWebUI-Type": "podcast_audio",
                },
            )

            # Generate database record with access control
            file_form = FileForm(
                id=file_id,
                filename=filename,
                path=file_path,
                data={"status": "completed"},
                meta={
                    "name": filename,
                    "content_type": "audio/wav",
                    "size": len(file_bytes),
                    "data": {"type": "generated_podcast"},
                },
                access_control={"read": {"user_ids": [user_id]}},
            )

            file_item = Files.insert_new_file(user_id=user_id, form_data=file_form)
            return file_item.id  # type: ignore

    # fmt:off
    async def action(
        self,
        body: dict,
        __user__=None,
        __event_emitter__=None,
        __event_call__=None,
        __model__=None,
        __request__=None,
        __id__=None
    ):
        """
        Main action handler for the Podcast It! plugin.

        Orchestrates the complete podcast generation workflow:
        1. Validates required parameters and API key
        2. Extracts and validates transcript format
        3. Generates podcast audio via Gemini TTS API
        4. Saves files to storage with access control
        5. Emits citations with embedded audio player

        The action is triggered when users click the "Podcast It!" button in the UI.

        Args:
            body: Request body containing messages and metadata.
            __user__: Current user object with id and permissions (required).
            __event_emitter__: Function to emit events (status, notifications, citations) (required).
            __event_call__: Event call identifier (required for actions).
            __model__: Model identifier (unused).
            __request__: FastAPI request object for base URL construction (optional).
            __id__: Action invocation ID (unused).

        Returns:
            None: Actions always return None. Results are communicated via event emissions.

        Event Types Emitted:
            - "status": Progress updates during generation
            - "notification": User-facing messages (errors, warnings, success)
            - "citation": Generated files with embedded players or download links
        """
        # fmt:on
        if not __user__:
            return None

        if not __event_call__:
            return None

        if not __event_emitter__:
            return None

        # check if api key was provided or not
        if self.valves.API_KEY == DEFAULT_GEMINI_API_KEY_PLACEHOLDER:
            err_msg = f"Detected default placeholder API KEY: \"{DEFAULT_GEMINI_API_KEY_PLACEHOLDER}\", please update with your real Gemini API Key"
            await __event_emitter__({
                "type": "notification",
                "data": {"type": "error", "content": err_msg}
            })
            return None

        messages: list[dict] = body.get("messages", [])
        if not messages:
            await __event_emitter__({
                "type": "notification",
                "data": {
                    "type": "error",
                    "content": "No messages found in conversation"
                }
            })
            return None

        transcript = messages[-1]["content"]

        # validate & parse
        result = self._validate_transcript_format(text=transcript)

        # Handle errors
        if not result["valid"]:
            await __event_emitter__({
                "type": "notification",
                "data": {
                    "type": "error",
                    "content": f"Invalid transcript format: {result['error']}\n\n"
                                             f"Expected format:\n"
                                             f"{{Style instructions}} (optional)\n"
                                             f"Speaker 1: dialogue\n"
                                             f"Speaker 2: dialogue\n"
                                             f"..."}
            })
            return None

        # Handle warning and continue...
        if result["warning"]:
            await __event_emitter__({
                "type": "notification",
                "data": {
                    "type": "warning",
                    "content": f"{result['warning']}"
                }
            })

        # Show parsing stats
        await __event_emitter__({
            "type": "status",
            "data": {
                "description": f"Transcript validated: Speaker 1 has: {result['speaker_1_count']} {'line' if result['speaker_1_count'] == 1 else 'lines'}, "
            }
        })
        await __event_emitter__({
            "type": "status",
            "data": {
                "description": f"Speaker 2 has: {result['speaker_2_count']} {'line' if result['speaker_2_count'] == 1 else 'lines'}."
            }
        })

        # generate podcast
        await __event_emitter__({
            "type": "status",
            "data": {"description": "Generating Podcast..."}
        })
        await __event_emitter__({
            "type": "notification",
            "data": {"type": "info", "content": "Podcast generation started. Sit tight, this might take awhile..."}
        })

        try:
            file_ids = await self._generate_podcast(transcript=transcript, user_id=__user__["id"] )
            # Success notification
            await __event_emitter__({
                "type": "status",
                "data": {"description": "Podcast generation complete!"}
            })
            await __event_emitter__({
                "type": "notification",
                "data": {"type": "info", "content": "Podcast generation complete!"}
            })

            # Emit citations with links to generated files
            for file_id in file_ids:
                file = Files.get_file_by_id(file_id)
                if file and file.meta:
                    # Construct base URL
                    if __request__:
                        base_url = f"{__request__.url.scheme}://{__request__.url.netloc}"
                    else:
                        base_url = ""

                    # Content download endpoint
                    file_content_url = f"{base_url}/api/v1/files/{file_id}/content"

                    # Determine source name and document content based on file type
                    content_type = file.meta.get("content_type", "")

                    if content_type.startswith("text/"):
                        # For transcripts: show actual content + download link
                        source_name = "📄 Podcast Transcript"
                        document_content = f"Download: {file_content_url}\n\n{transcript}"
                        metadata = {"source": file.meta.get("name", file.filename)}

                    elif content_type.startswith("audio/"):
                        # For audio: embed HTML audio player
                        source_name = "🎙️ Podcast Audio"
                        document_content = document_content_template(file_content_url, file.meta.get("name", file.filename))
                        metadata = {"source": file.meta.get("name", file.filename), "html": True}

                    else:
                        # Generic file
                        source_name = "📎 Generated File"
                        document_content = file_content_url
                        metadata = {"source": file.meta.get("name", file.filename)}

                    await __event_emitter__({
                        "type": "citation",
                        "data": {
                            "source": {"name": source_name},
                            "document": [document_content],
                            "metadata": [metadata],
                        }
                    })

            # Success
            return None

        except Exception as e:
            await __event_emitter__({
                "type": "status",
                "data": {"description": f"Podcast generation failed with error: {str(e)[:47]}..."}
            })
            await __event_emitter__({
                "type": "notification",
                "data": {"type": "error", "content": f"Podcast generation failed with error: {str(e)[:47]}..."}
            })
            return None
