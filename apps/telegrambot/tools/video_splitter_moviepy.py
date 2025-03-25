import logging
from pathlib import Path

from moviepy.video.io.VideoFileClip import VideoFileClip
from tqdm import tqdm  # Import tqdm for progress bar

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def split_video_moviepy(input_path, segment_duration=60):
    """
    Split video into segments using moviepy.

    Args:
        input_path (str): Path to input video file
        segment_duration (int): Duration of each segment in seconds

    Returns:
        list: List of paths to generated segments
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Create output directory
    output_dir = input_path.parent / f"{input_path.stem}_segments"
    output_dir.mkdir(exist_ok=True)

    # Load video
    video = VideoFileClip(str(input_path))
    duration = video.duration
    num_segments = int(duration // segment_duration) + (1 if duration % segment_duration else 0)

    output_files = []

    try:
        for i in tqdm(range(num_segments), desc="Splitting video", unit="segment"):
            start_time = i * segment_duration
            end_time = min(start_time + segment_duration, duration)

            output_file = output_dir / f"{input_path.stem}_part{i+1}{input_path.suffix}"

            # Extract segment
            segment = video.subclipped(start_time, end_time)

            # Write segment without re-encoding video but properly handle audio
            try:
                logger.info(f"Writing segment {i+1} to {output_file}")
                segment.write_videofile(
                    str(output_file),
                    audio_codec="aac",  # Use aac codec for audio
                    temp_audiofile=str(output_dir / f"temp{i}.m4a"),
                    remove_temp=True,
                )
                output_files.append(output_file)
            except Exception as e:
                logger.error(f"Error writing segment {i+1}: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Error processing video: {e}", exc_info=True)
    finally:
        video.close()

    return output_files


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Split video into segments using moviepy")
    parser.add_argument("input_video", help="Path to input video file")
    parser.add_argument(
        "-d", "--duration", type=int, default=60, help="Duration of each segment in seconds (default: 60)"
    )

    args = parser.parse_args()

    try:
        segments = split_video_moviepy(args.input_video, args.duration)
        print(f"Successfully created {len(segments)} segments:")
        for segment in segments:
            print(f"- {segment}")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
