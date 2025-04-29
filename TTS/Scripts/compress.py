import os
import glob
import subprocess

# Set desired bitrate and sample rate
bitrate = "64k"
sample_rate = "22050"

# Find all .mp3 files that don't already have "(compressed)" in the name
input_files = [f for f in glob.glob("*.mp3") if "(compressed)" not in f]

if not input_files:
    print(" No MP3 files found to compress.")
else:
    print(f" Found {len(input_files)} MP3 files...\n")
    for file in input_files:
        name, ext = os.path.splitext(file)
        output_file = f"{name} (compressed){ext}"

        # Build and run ffmpeg command
        cmd = [
            "ffmpeg", "-y", "-i", file,
            "-b:a", bitrate,
            "-ar", sample_rate,
            output_file
        ]

        print(f" Compressing: {file} → {output_file}")
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if result.returncode == 0:
            print(f" Done: {output_file}")
        else:
            print(f" Failed to compress: {file}")

    print("\n🏁 All files processed.")