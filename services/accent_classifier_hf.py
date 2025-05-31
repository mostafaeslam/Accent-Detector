import torch
import librosa
import numpy as np
import logging
from speechbrain.pretrained import EncoderClassifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AccentClassifier:
    def __init__(self):
        # Use SpeechBrain's pretrained ECAPA-TDNN model
        self.model = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="models/accent_classifier",
        )
        self.labels = {
            0: "US",
            1: "UK",
            2: "Australia",
            3: "Canada",
            4: "India",
            5: "African",
            6: "Others",
        }
        # Initialize the classification layer
        self.classifier = torch.nn.Linear(
            192, len(self.labels)
        )  # ECAPA-TDNN outputs 192-dim embeddings
        self.confidence_threshold = 0.4  # Minimum confidence threshold

    def preprocess_audio(self, audio, sr):
        """Preprocess audio for better accent detection"""
        try:
            # Convert to mono if stereo
            if len(audio.shape) > 1:
                audio = librosa.to_mono(audio)

            # Resample to 16kHz if needed
            if sr != 16000:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)

            # Normalize audio
            audio = librosa.util.normalize(audio)

            # Apply pre-emphasis filter
            audio = librosa.effects.preemphasis(audio)

            # Trim silence
            audio, _ = librosa.effects.trim(audio, top_db=20)

            # Ensure minimum length (1 second)
            if len(audio) < 16000:
                audio = np.pad(audio, (0, 16000 - len(audio)))

            # Cap maximum length (10 seconds)
            if len(audio) > 160000:  # 10 seconds at 16kHz
                audio = audio[:160000]

            return audio

        except Exception as e:
            logger.error(f"Error in audio preprocessing: {str(e)}")
            raise

    def predict(self, audio, sr):
        try:
            # Preprocess audio
            audio = self.preprocess_audio(audio, sr)
            logger.info(f"Preprocessed audio shape: {audio.shape}")

            # Convert to tensor
            waveform = torch.FloatTensor(audio).unsqueeze(0)

            # Get embeddings
            with torch.no_grad():
                # Move to the same device as the model
                waveform = waveform.to(self.model.device)
                embeddings = self.model.encode_batch(waveform)
                logger.info(f"Embeddings shape: {embeddings.shape}")

                # Move classifier to same device and get predictions
                self.classifier = self.classifier.to(self.model.device)
                logits = self.classifier(embeddings.squeeze(1))
                probs = torch.nn.functional.softmax(logits, dim=-1)[0].cpu().numpy()

            # Get prediction details
            top_idx = probs.argmax()
            top_label = self.labels[top_idx]
            confidence = round(float(probs[top_idx]) * 100, 2)

            # Calculate all accent scores
            all_scores = {
                self.labels[i]: round(float(p) * 100, 2) for i, p in enumerate(probs)
            }

            # Log prediction details
            logger.info(f"Predicted accent: {top_label} with confidence: {confidence}%")
            logger.info(f"All accent scores: {all_scores}")

            # Apply confidence threshold
            if confidence < (self.confidence_threshold * 100):
                logger.warning(
                    f"Low confidence prediction ({confidence}% < {self.confidence_threshold*100}%)"
                )
                return "Uncertain", confidence, all_scores

            return top_label, confidence, all_scores

        except Exception as e:
            logger.error(f"Error in accent prediction: {str(e)}")
            raise
