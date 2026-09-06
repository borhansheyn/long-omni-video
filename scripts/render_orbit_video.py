import cv2
import numpy as np
import imageio_ffmpeg
import subprocess
import os

def create_orbit_handheld_video():
    img_start_path = "generated_output/ravankav_shot_start.jpg"
    img_end_path = "generated_output/ravankav_45deg_consistent.jpg"
    audio_path = "generated_output/ravankav_speech.mp3"
    output_temp_video = "generated_output/temp_video.mp4"
    output_final_video = "generated_output/ravankav_45deg_handheld_video.mp4"

    # Load images
    img_start = cv2.imread(img_start_path)
    img_end = cv2.imread(img_end_path)

    # Ensure same height and width
    h, w, _ = img_start.shape
    img_end = cv2.resize(img_end, (w, h))

    fps = 30
    duration = 11.54  # speech length
    total_frames = int(fps * duration)

    # Setup video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_temp_video, fourcc, fps, (w, h))

    np.random.seed(42)  # reproducible handheld shake

    for frame_idx in range(total_frames):
        # Progress 0.0 to 1.0 (smooth easing curve)
        t = frame_idx / float(total_frames - 1)
        # Smooth step easing: 3*t^2 - 2*t^3
        smooth_t = 3 * (t ** 2) - 2 * (t ** 3)

        # Blend start (0 deg) and end (45 deg orbit) images
        blended = cv2.addWeighted(img_start, 1.0 - smooth_t, img_end, smooth_t, 0)

        # Handheld Camera Shake simulation:
        # Low frequency drift + high frequency jitter
        drift_x = 4.0 * np.sin(2 * np.pi * frame_idx / (fps * 2.5))
        drift_y = 3.0 * np.cos(2 * np.pi * frame_idx / (fps * 3.1))
        jitter_x = np.random.normal(0, 1.2)
        jitter_y = np.random.normal(0, 1.2)

        dx = drift_x + jitter_x
        dy = drift_y + jitter_y

        # Slight handheld tilt rotation
        angle = 0.2 * np.sin(2 * np.pi * frame_idx / (fps * 2.0)) + np.random.normal(0, 0.08)

        # Apply transformation matrix
        M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.02)  # slight zoom to avoid border clipping
        M[0, 2] += dx
        M[1, 2] += dy

        frame_shake = cv2.warpAffine(blended, M, (w, h), borderMode=cv2.BORDER_REFLECT)
        out.write(frame_shake)

    out.release()
    print("Temp video rendered successfully.")

    # Mux with audio using ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe, "-y",
        "-i", output_temp_video,
        "-i", audio_path,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        output_final_video
    ]
    subprocess.run(cmd, check=True)
    print("Final video created at:", output_final_video)

if __name__ == "__main__":
    create_orbit_handheld_video()
