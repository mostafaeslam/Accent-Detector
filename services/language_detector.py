import whisper
import logging

logger = logging.getLogger(__name__)


class LanguageDetector:
    def __init__(self):
        self.model = whisper.load_model("base")

    def detect(self, audio_path: str) -> tuple[str, float]:
        """
        Detect the language of the audio file.

        Args:
            audio_path: Path to the audio file

        Returns:
            tuple: (language_code, confidence_score)
        """
        try:
            # Use whisper to detect language
            result = self.model.detect_language(audio_path)
            language = result[0]
            confidence = float(result[1])

            logger.info(
                f"Detected language: {language} with confidence: {confidence:.2f}"
            )
            return language, confidence

        except Exception as e:
            logger.error(f"Error in language detection: {str(e)}")
            return "unknown", 0.0
