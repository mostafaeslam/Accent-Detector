import os
import requests
import logging

# Set up logger
logger = logging.getLogger(__name__)


def download_model_if_needed(model_path, model_url, description=None):
    """
    Downloads a model file if it doesn't exist locally.

    Args:
        model_path: Path where the model should be stored
        model_url: URL to download the model from
        description: Optional description of the model for logging
    """
    model_name = description or os.path.basename(model_path)

    try:
        if not os.path.exists(model_path):
            logger.info(f"Downloading {model_name} model...")
            os.makedirs(os.path.dirname(model_path), exist_ok=True)

            with requests.get(model_url, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get("content-length", 0))

                with open(model_path, "wb") as f:
                    if total_size == 0:  # No content length header
                        f.write(r.content)
                    else:
                        dl = 0
                        for chunk in r.iter_content(chunk_size=8192):
                            dl += len(chunk)
                            f.write(chunk)
                            done = int(50 * dl / total_size)
                            if done % 5 == 0:  # Log every 10%
                                logger.info(
                                    f"Downloading {model_name}: {dl}/{total_size} bytes"
                                )

            logger.info(f"{model_name} model downloaded successfully to {model_path}")
            return True
        else:
            logger.info(f"{model_name} model already exists at {model_path}")
            return False
    except Exception as e:
        logger.error(f"Error downloading {model_name} model: {str(e)}")
        return False


def setup_models():
    """
    Downloads all required models if they don't exist locally.
    Add each model that needs to be downloaded here.
    """
    # Base paths
    model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
    pretrained_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "pretrained_models"
    )

    # Create directories if they don't exist
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(pretrained_dir, exist_ok=True)

    # List of models to download - add your models here
    models = [
        # English Accent Classifier model
        {
            "path": os.path.join(
                model_dir, "accent_id_commonaccent_xlsr_en_english", "wav2vec2.ckpt"
            ),
            "url": "https://huggingface.co/Jzuluaga/accent-id-commonaccent_xlsr-en-english/resolve/main/wav2vec2.ckpt",  # Actual URL from Hugging Face
            "description": "English Accent Classifier wav2vec2",
        },
        # Language ID model
        {
            "path": os.path.join(
                pretrained_dir, "lang-id-commonlanguage_ecapa", "embedding_model.ckpt"
            ),
            "url": "https://huggingface.co/speechbrain/lang-id-commonlanguage_ecapa/resolve/main/embedding_model.ckpt",  # Actual URL from Hugging Face
            "description": "Language ID ECAPA Embedding Model",
        },
        # Add more models as needed
    ]

    # Download each model if needed
    for model in models:
        download_model_if_needed(model["path"], model["url"], model["description"])


if __name__ == "__main__":
    # For testing
    setup_models()
