import os
from speechbrain.inference import EncoderClassifier
import torch
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class AccentClassifier:
    """
    Accent/language classifier using a pretrained SpeechBrain model.
    """

    def __init__(self):
        logger.info("Loading SpeechBrain ECAPA model...")
        self.classifier = EncoderClassifier.from_hparams(
            source="speechbrain/lang-id-commonlanguage_ecapa",
            savedir="pretrained_models/lang-id-commonlanguage_ecapa",
        )

    def classify_accent(self, audio_path: str) -> dict:
        """
        Predicts the spoken accent/language in the audio file.

        Args:
            audio_path (str): Path to WAV file

        Returns:
            dict: {
                'label': predicted accent/language,
                'score': confidence score (0–100%)
            }
        """
        # Normalize the audio path for Windows compatibility
        audio_path = os.path.abspath(os.path.normpath(audio_path))
        # Replace backslashes with forward slashes for compatibility
        audio_path = audio_path.replace("\\", "/")
        logger.info(f"Classifying accent for: {audio_path}")
        print(f"DEBUG: Path passed to SpeechBrain: {audio_path}")

        # Predict
        probs, score, index, label = self.classifier.classify_file(audio_path)
        confidence = round(float(score) * 100, 2)

        result = {"label": label, "score": confidence}

        logger.info(f"Predicted accent/language: {label} ({confidence}%)")
        return result
