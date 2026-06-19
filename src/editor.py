import subprocess

def image_to_video(image_path, output_path, duration=8):
    cmd = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", image_path,
        "-vf",
        "zoompan=z='min(zoom+0.0015,1.5)':d=240:s=1920x1080",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        output_path
    ]

    subprocess.run(cmd, check=True)