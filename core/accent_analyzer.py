from services.whisper_service import WhisperTranscriber
from services.accent_classifier_hf import AccentClassifier
from services.language_detector import LanguageDetector
import librosa
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AccentAnalysisResult:
    def __init__(
        self,
        accent: str,
        confidence: float,
        language: str,
        language_score: float,
        transcript: str,
        all_scores: dict,
    ):
        self.accent = accent
        self.confidence = confidence
        self.language = language
        self.language_score = language_score
        self.transcript = transcript
        self.all_scores = all_scores

    def to_dict(self):
        # Create a detailed summary including all accent scores
        scores_text = ", ".join([f"{k}: {v:.1f}%" for k, v in self.all_scores.items()])
        summary = (
            f"The speaker is using a {self.accent} English accent with {self.confidence}% confidence.\n"
            f"All accent scores: {scores_text}"
        )

        return {
            "accent": self.accent,
            "confidence": self.confidence,
            "language": self.language,
            "language_score": self.language_score,
            "transcript": self.transcript,
            "all_scores": self.all_scores,
            "summary": summary,
        }


class AccentAnalyzer:
    def __init__(self):
        self.accent_classifier = AccentClassifier()
        self.language_detector = LanguageDetector()
        self.transcriber = WhisperTranscriber()

    def analyze(self, audio_path: str) -> dict:
        try:
            # Transcribe and detect language
            transcription_result = self.transcriber.transcribe(audio_path)
            language = transcription_result["language"]
            language_conf = transcription_result["language_confidence"]
            transcript = transcription_result["text"]

            # Only proceed if the speaker is speaking English
            if language != "en" or language_conf < 80:
                return {
                    "accent": "Non-English or unclear",
                    "confidence": 0.0,
                    "language": language,
                    "language_score": language_conf,
                    "transcript": transcript,
                    "summary": "The language detected is not English or is unclear.",
                    "all_scores": {},
                }

            # Load audio and get accent classification
            audio, sr = librosa.load(audio_path, sr=16000)
            accent, confidence, all_scores = self.accent_classifier.predict(audio, sr)

            # Create result object
            result = AccentAnalysisResult(
                accent=accent,
                confidence=confidence,
                language=language,
                language_score=language_conf,
                transcript=transcript,
                all_scores=all_scores,
            )

            return result.to_dict()

        except Exception as e:
            logger.error(f"Error in accent analysis: {str(e)}")
            return {
                "accent": "Error",
                "confidence": 0.0,
                "language": "unknown",
                "language_score": 0.0,
                "transcript": str(e),
                "summary": f"An error occurred during analysis: {str(e)}",
                "all_scores": {},
            }


def detect_accent(audio_path):
    analyzer = AccentAnalyzer()
    result = analyzer.analyze(audio_path)
    return result["accent"], result["confidence"], result["summary"]
