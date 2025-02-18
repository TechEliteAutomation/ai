# Gemini Speech Interaction

This repository contains two Python scripts that integrate the Gemini API for generating AI-driven responses and convert these responses into speech. The scripts use different text-to-speech libraries to convert the Gemini-generated responses into audio output.

## Features

- **Gemini AI Integration**: Both scripts interact with the Gemini API to generate logical, concise responses based on user input.
- **Speech Synthesis**: Converts Gemini's AI-generated responses into speech using two different methods:
  1. **espeak-ng + aplay** (Program 1)
  2. **gTTS (Google Text-to-Speech) + Pygame Mixer** (Program 2)

## Requirements

Before running the scripts, ensure you have the following installed:

- Python 3.x
- `requests` library for API interactions
- `subprocess`, `gtts`, `pygame` for speech synthesis
- **For Program 1**: `espeak-ng` and `aplay` must be installed and available on your system.
- **For Program 2**: `pygame` and `gtts` libraries must be installed.

To install required libraries, use the following:

```bash
pip install requests gtts pygame
```

**Note**: You must set your **Gemini API Key** as an environment variable:

```bash
export GEMINI_API_KEY="your_api_key_here"
```

## Scripts

### Program 1: `gemini_speech_espeak.py`

This script uses **espeak-ng** for speech synthesis. The response from Gemini is spoken aloud via the `aplay` command.

#### How to Run:
```bash
python gemini_speech_espeak.py
```

### Program 2: `gemini_speech_gtts.py`

This script uses **Google Text-to-Speech (gTTS)** and **Pygame** to synthesize and play audio. It saves the generated speech to an `output.mp3` file and then plays it back.

#### How to Run:
```bash
python gemini_speech_gtts.py
```

## Functionality

- **User Input**: The script prompts the user to enter a query.
- **Gemini Response**: The input is sent to the Gemini API for a response.
- **Speech Output**: The response is converted into speech and played back to the user.

## Exit the Program

To exit the program at any time, type `exit`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
