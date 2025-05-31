import os
import uuid
import logging
import tempfile
from moviepy.editor import VideoFileClip
import subprocess
import shutil

# Logger setup
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def download_video(video_url: str, download_dir: str) -> str:
    """
    Downloads a video from a given URL using yt-dlp.

    Args:
        video_url (str): The URL of the video.
        download_dir (str): The directory to save the downloaded file.

    Returns:
        str: Path to the downloaded video file.
    """
    video_id = str(uuid.uuid4())
    output_path = os.path.join(download_dir, f"{video_id}.mp4")

    logger.info(f"Downloading video from URL: {video_url}")

    command = [
        "C:\\Users\\mosta\\yt-dlp\\yt-dlp.exe",
        "-f",
        "mp4",
        video_url,
        "-o",
        output_path,
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        logger.error("Failed to download video")
        raise RuntimeError(result.stderr.decode())

    logger.info(f"Video saved to: {output_path}")
    return output_path


def extract_audio_from_video(video_path: str, output_dir: str) -> str:
    """
    Extracts audio from video and converts to mono 16kHz WAV.

    Args:
        video_path (str): Path to the video file.
        output_dir (str): Directory to save the audio.

    Returns:
        str: Path to the extracted audio file.
    """
    audio_path = os.path.join(output_dir, f"{uuid.uuid4()}.wav")

    logger.info(f"Extracting audio from: {video_path}")

    try:
        clip = VideoFileClip(video_path)
        clip.audio.write_audiofile(audio_path, fps=16000, nbytes=2, codec="pcm_s16le")
        clip.close()
    except Exception as e:
        logger.error("Error extracting audio: %s", str(e))
        raise

    logger.info(f"Audio saved to: {audio_path}")
    return audio_path


def process_video_url(video_url: str) -> str:
    """
    Complete process: download video and return WAV path.

    Args:
        video_url (str): The public video URL.

    Returns:
        str: Path to processed WAV audio.
    """
    samples_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "samples")
    os.makedirs(samples_dir, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp_dir:
        video_path = download_video(video_url, temp_dir)
        audio_path = extract_audio_from_video(video_path, temp_dir)
        # Copy audio to samples dir
        final_audio_path = os.path.join(samples_dir, f"{uuid.uuid4()}.wav")
        shutil.copy2(audio_path, final_audio_path)
        # Always return an absolute, normalized path
        final_audio_path = os.path.abspath(os.path.normpath(final_audio_path))
        logger.info(f"Final audio path: {final_audio_path}")
        return final_audio_path
