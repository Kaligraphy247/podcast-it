# Podcast It! 🎙️

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/yourusername/podcast-it)
[![Open WebUI](https://img.shields.io/badge/Open%20WebUI-0.6.36+-green.svg)](https://github.com/open-webui/open-webui)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Transform text conversations into engaging multi-speaker podcasts with AI-generated voices. This Open WebUI Actions plugin uses Google's Gemini TTS API to convert formatted transcripts into natural-sounding audio with two distinct speakers.

## Features

✨ **Key Highlights**
- 🎭 Multi-speaker podcast generation with 30+ voice options
- 🌍 Multi-language support (25+ languages including English, Spanish, French, Japanese, etc.)
- 🎨 Embedded audio player with dark mode support
- 💾 Optional transcript saving
- 🔒 User-specific access control
- ☁️ Works with any storage backend (local/S3/GCS/Azure)
- ⚡ Streaming audio generation for efficient processing
- 🎯 Type-safe(ish) implementation with full type hints(ish)

## Installation

### Prerequisites
- Developed with Open WebUI version 0.6.36. Might work on versions < 0.6.36, expected to work on >= 0.6.36.
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

### Setup

1. **Install the plugin** in Open WebUI:
   - Navigate to Admin Panel → Functions
   - Click "+ New Function" to add a new function
   - Copy the contents of `main.py` into the editor. Set function name to `podcast it` or value of your choice & function description to tagline of this Readme or anything you want.
   - Save the function

2. **Configure your API key**:
   - Open the plugin settings (click the gear icon)
   - Replace `API_KEY` placeholder with your Gemini API key
   - Customize other settings as desired (voices, language, etc.)
   - Enable the plugin, might need to be done twice, one in the ... menu -> Global and the other in functions page toggle.

3. **Install dependencies**:
   The plugin requires the `google-genai` package, which is specified in the plugin metadata and will be installed automatically by Open WebUI.
   
   > You might not need this, `google-genai` might already be installed in you development or deployment environment (including in docker images)

## Usage

### Basic Workflow

1. **Prepare your transcript** in the following format:
   ```
   {Optional style instructions}
   Speaker 1: dialogue
   Speaker 2: dialogue
   Speaker 1: more dialogue
   ...
   ```

2. **Example transcript**:
   ```
   Warm, conversational tone with enthusiasm

   Speaker 1: Welcome to our podcast about AI! Today we're discussing the latest developments.
   Speaker 2: Thanks for having me! I'm excited to share what's happening in the field.
   Speaker 1: Let's dive right in. What's the most exciting thing you've seen recently?
   Speaker 2: The multimodal capabilities are really taking off. Models can now understand images, audio, and text seamlessly.
   ```

   > Hint: Create a custom Model in OWUI that already has the system prompt instructions to generate the podcast's transcript, this avoids the need to rewrite the system prompt for every new chat.

3. **Generate the podcast**:
   - Type or paste your transcript into the chat
   - Click the **"Podcast It!"** action button
   - Wait for generation to complete
   - Play the audio directly in the embedded player or download it

   > While not necessary, try to have one podcast per chat, it reduces the tokens used to generate transcripts by not including older (or probably unrelated) transcripts/conversations in your messages array. However, if you are iterating on the transcript, this fine; only the last message (that is a valid transcript) is used to generate the podcast.

### Transcript Format Rules

- **Style Instructions** (optional): Add at the beginning before any speaker lines
- **Speaker Lines** (required): Must follow the pattern `Speaker 1:` or `Speaker 2:`
- **Minimum Requirements**: At least 2 speaker exchanges with both speakers present
- **Empty Lines**: Allowed and ignored
- **Validation**: The plugin will validate your transcript and provide helpful error messages

## Configuration

### Valve Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `API_KEY` | Your Gemini API key | *Required* |
| `tts_model` | TTS model to use | `gemini-2.5-flash-preview-tts` |
| `custom_style_instructions` | Default tone/style for podcasts | `"Read aloud in a warm, welcoming tone"` |
| `speaker_1` | Voice for Speaker 1 | `Zephyr (Female)` |
| `speaker_2` | Voice for Speaker 2 | `Puck (Male)` |
| `podcast_output_language` | Output language | `English (United States)` |
| `save_transcript` | Save transcript as text file | `Yes` |

### Available Voices (30 options)

**Female Voices:**
- Achernar, Aoede, Autonoe, Callirrhoe, Despina, Erinome, Gacrux, Kore, Laomedeia, Leda, Pulcherrima, Sulafat, Vindemiatrix, Zephyr

**Male Voices:**
- Achird, Algenib, Algieba, Alnilam, Charon, Enceladus, Fenrir, Iapetus, Orus, Puck, Rasalgethi, Sadachbia, Sadaltager, Schedar, Umbriel, Zubenelgenubi

### Supported Languages (GA only)

English (US/UK/India), Spanish (Spain), French, German, Italian, Japanese, Korean, Portuguese (Brazil), Russian, Arabic (Egypt), Bangla (Bangladesh), Dutch, Hindi, Indonesian, Marathi, Polish, Romanian, Tamil, Telugu, Thai, Turkish, Ukrainian, Vietnamese

## Technical Details

### Architecture

The plugin is built with type safety and best practices in mind:

- **Type Hints**: Full type annotations throughout the codebase
- **Validation**: Comprehensive input validation with detailed error messages
- **Transaction Safety**: Files are saved only after successful generation (no orphaned files)
- **Storage Abstraction**: Uses Open WebUI's storage factory pattern for multi-backend support
- **Access Control**: User-specific file permissions (creator + admins only)
- **Error Handling**: Graceful error handling with user-friendly notifications

### File Storage

Generated files are stored via Open WebUI's storage system:

- **Naming Convention**:
  - Audio: `Podcast_{name}.wav`
  - Transcript: `Podcast_Transcript_{name}.txt`
- **Access**: Files are restricted to the creator (and admins)
- **Metadata**: Files tagged with user ID, file ID, and type for auditing
- **Storage Backends**: Supports local filesystem, S3, Google Cloud Storage, and Azure Blob Storage

### API Endpoints

Files are accessible through Open WebUI's file API:
- **Metadata**: `/api/v1/files/{file_id}`
- **Download**: `/api/v1/files/{file_id}/content`

### Event Emissions

The plugin uses Open WebUI's event emitter system:
- `status`: Progress updates during generation
- `notification`: User-facing messages (errors, warnings, success)
- `citation`: Generated files with embedded players or download links

### Citation Rendering

Audio files are displayed in the citations (Sources) UI modal using an embedded HTML player with:
- Native `<audio>` controls
- Dark mode support (automatic theme detection)
- Download link in header
- Responsive design for small modals
- Sandboxed iframe rendering for security

## Development

### Code Structure

```
podcast-it/
├── main.py          # Main plugin implementation
└── README.md          # This file
```

### Key Functions

- `_validate_transcript_format()`: Validates and parses transcript format
- `_generate_podcast()`: Generates audio using Gemini TTS API
- `_convert_to_wav()`: Converts raw audio data to WAV format
- `_parse_audio_mime_type()`: Extracts audio parameters from MIME types
- `_save_file()`: Saves files to storage with access control
- `action()`: Main entry point orchestrating the workflow

### Type Safety

All functions include comprehensive docstrings and type hints:
```python
async def _generate_podcast(
    self, transcript: str, user_id: str, podcast_name: str = "audio"
) -> list[str]:
    """Generate podcast audio from transcript."""
    ...
```

## Limitations

- **Speaker Limit**: Fixed at 2 speakers
- **Audio Format**: Outputs WAV only (larger file sizes)
- **Model**: Currently uses `gemini-2.5-flash-preview-tts`, the other option is `gemini-2.5-pro-preview-tts`
- **Language Support**: Only Generally Available (GA) languages listed and therefore supported, you can extend this list with `Preview` languages in your copy of the plugin

## Troubleshooting

### Common Issues

**"Invalid transcript format" error**
- Ensure you're using `Speaker 1:` and `Speaker 2:` (with space after colon)
- Check that you have at least 2 lines with both speakers
- Verify dialogues are not empty

**"Detected default placeholder API KEY" error**
- You need to set your actual Gemini API key in the plugin settings
- Get a key from [Google AI Studio](https://aistudio.google.com/app/apikey)

**No audio player visible**
- Check that the file was generated successfully
- Look for error notifications in the UI
- Verify your browser supports HTML5 audio

**Generation fails**
- Check your API key is valid
- Verify you have Gemini API quota available
- Check the transcript meets minimum requirements

## Contributing

~~Contributions are welcome! Please feel free to submit issues or pull requests.~~

## License

~~MIT License - see LICENSE file for details~~

## Author

Created by [@kaligraphy247](https://github.com/kaligraphy247)

## Acknowledgments

- Built for [Open WebUI](https://github.com/open-webui/open-webui)
- Powered by [Google Gemini TTS API](https://ai.google.dev/) with [Docs](https://docs.cloud.google.com/text-to-speech/docs/gemini-tts)

## Changelog

### v0.1.0 (2025-01-16)
- Initial release
- Multi-speaker podcast generation
- 30+ voice options
- 25+ language support
- Embedded audio player with dark mode
- Transaction-safe file operations
- Comprehensive type hints and validation
