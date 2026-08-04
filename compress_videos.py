import os
import subprocess
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
print(f"Using ffmpeg binary at: {ffmpeg_exe}")

videos = ['bg_video.mp4', 'video_1.mp4', 'video_2.mp4']
videos_dir = os.path.join(os.path.dirname(__file__), 'static', 'videos')

for v in videos:
    input_path = os.path.join(videos_dir, v)
    if not os.path.exists(input_path):
        print(f"Skipping {v}, file not found")
        continue

    temp_path = os.path.join(videos_dir, f"compressed_{v}")
    orig_size = os.path.getsize(input_path) / (1024 * 1024)
    print(f"\nCompressing {v} (Original size: {orig_size:.2f} MB)...")

    # ffmpeg faststart + H.264 + 720p web scaling + audio strip (-an)
    cmd = [
        ffmpeg_exe, '-y',
        '-i', input_path,
        '-vf', 'scale=-2:720',
        '-c:v', 'libx264',
        '-crf', '28',
        '-preset', 'faster',
        '-an',
        '-movflags', '+faststart',
        temp_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and os.path.exists(temp_path):
        new_size = os.path.getsize(temp_path) / (1024 * 1024)
        print(f"Successfully compressed {v}: {orig_size:.2f} MB -> {new_size:.2f} MB (Saved {((orig_size - new_size)/orig_size)*100:.1f}%)")
        os.replace(temp_path, input_path)
    else:
        print(f"Error compressing {v}: {result.stderr}")

print("\nAll background videos successfully compressed and optimized for fast streaming!")
