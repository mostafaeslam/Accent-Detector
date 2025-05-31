import whisper
import logging
import os
import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class WhisperTranscriber:
    """
    A wrapper for OpenAI Whisper model (base).
    """

    def __init__(self, model_size: str = "base"):
        try:
            logger.info(f"Loading Whisper model: {model_size}")
            self.model = whisper.load_model(model_size)
        except Exception as e:
            logger.error(f"Error loading Whisper model: {str(e)}")
            raise

    def transcribe(self, audio_path: str) -> dict:
        """
        Transcribes speech from an audio file and detects language.

        Args:
            audio_path (str): Path to the WAV file

        Returns:
            dict: Transcription result with keys:
                  'text', 'language', 'segments', 'language_confidence'
        """
        try:
            logger.info(f"Transcribing audio: {audio_path}")
            if not os.path.isfile(audio_path):
                logger.error(f"Audio file does not exist: {audio_path}")
                raise FileNotFoundError(f"Audio file does not exist: {audio_path}")

            # Load audio using whisper's built-in function
            audio = whisper.load_audio(audio_path)
            audio = whisper.pad_or_trim(audio)

            logger.info(f"Loaded audio shape: {audio.shape}")

            # Make log-Mel spectrogram and move to the same device as the model
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)

            # Detect the language
            _, probs = self.model.detect_language(mel)
            detected_lang = max(probs, key=probs.get)
            language_confidence = probs[detected_lang]

            logger.info(
                f"Detected language: {detected_lang} with confidence: {language_confidence:.2f}"
            )

            # Transcribe the audio
            result = self.model.transcribe(audio_path)

            # Ensure we have text
            if not result.get("text"):
                logger.warning("No text was transcribed from the audio")
                result["text"] = ""

            return {
                "text": result["text"],
                "language": detected_lang,
                "segments": result.get("segments", []),
                "language_confidence": round(language_confidence * 100, 2),
            }

        except Exception as e:
            logger.error(f"Error in transcription: {str(e)}")
            return {
                "text": "",
                "language": "unknown",
                "segments": [],
                "language_confidence": 0.0,
            }
