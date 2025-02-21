import os
import shutil
import subprocess
import json
import time
from pathlib import Path

# Configuration
SOURCE_FOLDER = r"E:\test"              # Folder with original .ts files
ORIGINALS_FOLDER = r"E:\test\Originals" # Folder to store original files
WORKING_FOLDER = r"E:\test\Working"     # Temporary folder for processing
COMSKIP_PATH = "comskip"                # Assumes comskip is in PATH
FFMPEG_PATH = "ffmpeg"                  # Assumes ffmpeg is in PATH
PROCESSED_TRACKER = r"E:\test\processed_files.json"  # File to track processed videos
COMSKIP_INI = r"E:\test\comskip.ini"    # Optional: custom Comskip config

# Ensure directories exist
for folder in [SOURCE_FOLDER, ORIGINALS_FOLDER, WORKING_FOLDER]:
    os.makedirs(folder, exist_ok=True)
    print(f"Ensured directory exists: {folder}")

def load_processed_files():
    """Load the list of already processed files from the tracker JSON."""
    if os.path.exists(PROCESSED_TRACKER):
        try:
            with open(PROCESSED_TRACKER, 'r') as f:
                processed = set(json.load(f))
                print(f"Loaded processed files: {processed}")
                return processed
        except Exception as e:
            print(f"Error loading {PROCESSED_TRACKER}: {e}")
    print("No processed_files.json found, starting fresh.")
    return set()

def save_processed_files(processed_files):
    """Save the list of processed files to the tracker JSON."""
    try:
        with open(PROCESSED_TRACKER, 'w') as f:
            json.dump(list(processed_files), f)
        print(f"Saved processed files to {PROCESSED_TRACKER}: {processed_files}")
    except Exception as e:
        print(f"Error saving {PROCESSED_TRACKER}: {e}")

def run_comskip(video_path):
    """Run Comskip on the video file and return the .edl file path if successful."""
    command = [COMSKIP_PATH, video_path]
    if os.path.exists(COMSKIP_INI):
        command.extend(["--ini", COMSKIP_INI])
    print(f"Running Comskip command: {' '.join(command)} from directory {WORKING_FOLDER}")
    try:
        result = subprocess.run(command, cwd=WORKING_FOLDER, capture_output=True, text=True)
        print(f"Comskip stdout: {result.stdout}")
        print(f"Comskip stderr: {result.stderr}")
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        edl_file = os.path.join(WORKING_FOLDER, base_name + ".edl")
        print(f"Checking for .edl file at: {edl_file}")
        time.sleep(2)
        if os.path.exists(edl_file):
            print(f"Comskip succeeded, .edl file created at {edl_file}")
            return edl_file
        else:
            print(f"Comskip failed to create .edl for {video_path}")
            print(f"Checking {WORKING_FOLDER} contents: {os.listdir(WORKING_FOLDER)}")
            return None
    except FileNotFoundError:
        print("Comskip not found in PATH. Please check PATH or provide full path in COMSKIP_PATH.")
        return None

def parse_edl(edl_file):
    """Parse the .edl file to get commercial segments (start, end times)."""
    segments = []
    try:
        with open(edl_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    start, end = float(parts[0]), float(parts[1])
                    segments.append((start, end))
        print(f"Parsed {len(segments)} commercial segments from {edl_file}")
    except Exception as e:
        print(f"Error parsing {edl_file}: {e}")
    return segments

def get_non_commercial_segments(segments, video_duration):
    """Convert commercial segments to non-commercial segments."""
    if not segments:
        print(f"No commercial segments found, using full duration: {video_duration}")
        return [(0, video_duration)]
    non_commercials = []
    last_end = 0
    for start, end in sorted(segments):
        if last_end < start:
            non_commercials.append((last_end, start))
        last_end = max(last_end, end)
    if last_end < video_duration:
        non_commercials.append((last_end, video_duration))
    print(f"Generated {len(non_commercials)} non-commercial segments")
    return non_commercials

def get_video_duration(video_path):
    """Get the duration of the video using FFmpeg."""
    command = [FFMPEG_PATH, "-i", video_path, "-hide_banner"]
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        for line in result.stderr.splitlines():
            if "Duration" in line:
                time_str = line.split("Duration: ")[1].split(",")[0]
                h, m, s = map(float, time_str.split(":"))
                duration = h * 3600 + m * 60 + s
                print(f"Video duration: {duration} seconds")
                return duration
        print("Could not determine video duration")
        return 0
    except FileNotFoundError:
        print("FFmpeg not found in PATH. Please check PATH or provide full path in FFMPEG_PATH.")
        return 0

def remove_commercials_ffmpeg(input_video, output_video, segments):
    """Use FFmpeg to create a video without commercials."""
    filter_complex = "".join(
        f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{i}];"
        f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{i}];"
        for i, (start, end) in enumerate(segments)
    )
    filter_complex += "".join(f"[v{i}][a{i}]" for i in range(len(segments))) + f"concat=n={len(segments)}:v=1:a=1[outv][outa]"
    
    command = [
        FFMPEG_PATH, "-i", input_video, "-filter_complex", filter_complex,
        "-map", "[outv]", "-map", "[outa]", "-c:v", "libx264", "-c:a", "aac",
        "-y", output_video
    ]
    print(f"Running FFmpeg command: {' '.join(command)}")
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"FFmpeg stdout: {result.stdout}")
        print(f"FFmpeg stderr: {result.stderr}")
        print(f"FFmpeg succeeded for {output_video}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg failed: {e.stderr}")
        return False
    except FileNotFoundError:
        print("FFmpeg not found in PATH. Please check PATH or provide full path in FFMPEG_PATH.")
        return False

def clean_working_folder():
    """Delete all files in the working folder."""
    for filename in os.listdir(WORKING_FOLDER):
        file_path = os.path.join(WORKING_FOLDER, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

def process_videos():
    """Main function to process all .ts files."""
    try:
        processed_files = load_processed_files()
        
        print(f"Scanning {SOURCE_FOLDER} for .ts files...")
        ts_files = [f for f in os.listdir(SOURCE_FOLDER) if f.lower().endswith('.ts')]
        print(f"Found {len(ts_files)} .ts files: {ts_files}")
        
        if not ts_files:
            print("No .ts files found in E:\test")
            return
        
        for ts_file in ts_files:
            source_path = os.path.join(SOURCE_FOLDER, ts_file)
            print(f"Processing file: {source_path}")
            if source_path in processed_files:
                print(f"Skipping already processed file: {ts_file}")
                continue
            
            # Move original to ORIGINALS_FOLDER with _original suffix
            original_filename = f"{os.path.splitext(ts_file)[0]}_original.ts"
            original_path = os.path.join(ORIGINALS_FOLDER, original_filename)
            try:
                shutil.move(source_path, original_path)
                print(f"Moved original to {original_path}")
            except Exception as e:
                print(f"Failed to move {source_path} to {original_path}: {e}")
                continue
            
            # Copy to working folder with ORIGINAL filename (no _original)
            working_path = os.path.join(WORKING_FOLDER, ts_file)
            try:
                shutil.copy2(original_path, working_path)
                print(f"Copied {original_path} to {working_path}")
            except Exception as e:
                print(f"Failed to copy {original_path} to {working_path}: {e}")
                shutil.move(original_path, source_path)
                continue
            
            # Run Comskip
            edl_file = run_comskip(working_path)
            if not edl_file:
                print(f"Comskip failed for {ts_file}, leaving working files for inspection")
                continue
            
            # Parse commercial segments and get non-commercial parts
            commercial_segments = parse_edl(edl_file)
            duration = get_video_duration(working_path)
            non_commercial_segments = get_non_commercial_segments(commercial_segments, duration)
            
            # Output path is the original source path (same name)
            output_path = source_path
            
            # Remove commercials with FFmpeg
            if remove_commercials_ffmpeg(working_path, output_path, non_commercial_segments):
                os.remove(working_path)
                os.remove(edl_file)
                processed_files.add(source_path)  # Track SOURCE_PATH, not original_path
                save_processed_files(processed_files)
            else:
                print(f"Failed to process {ts_file}, restoring original.")
                shutil.move(original_path, source_path)
                continue
        
        clean_working_folder()
    
    except Exception as e:
        print(f"Unexpected error in process_videos: {e}")

if __name__ == "__main__":
    process_videos()