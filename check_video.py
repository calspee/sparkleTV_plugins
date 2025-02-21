import os
import subprocess
import shutil
from pathlib import Path
import json

def check_and_fix_videos(folder_path, output_folder="repaired_videos", json_file=None, tracking_file="checked_videos.json"):
    """
    Check video files in a folder and attempt to repair corrupted ones using FFmpeg.
    Original corrupted files are copied to output_folder as backup, and repaired versions
    replace the originals in the source folder with the same filename.
    Healthy files are left unchanged and not backed up.
    Uses a tracking file to skip previously checked videos.
    Uses simple stream copy repair.
    """
    tracking_path = Path(folder_path) / tracking_file
    checked_videos = {}
    if tracking_path.exists():
        try:
            with open(tracking_path, "r") as f:
                checked_videos = json.load(f)
        except Exception as e:
            print(f"Error loading tracking file {tracking_file}: {str(e)}")

    expected_durations = {}
    if json_file:
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
            if isinstance(data, list):
                for entry in data:
                    url = entry.get("Url")
                    if url:
                        file_name = os.path.basename(url)
                        start = entry.get("Start")
                        stop = entry.get("Stop")
                        if start is not None and stop is not None:
                            expected_duration = (stop - start) / 1000.0
                            expected_durations[file_name] = expected_duration
            elif isinstance(data, dict):
                expected_durations = data
        except Exception as e:
            print(f"Error loading JSON file {json_file}: {str(e)}")
    
    output_path = Path(folder_path) / output_folder
    output_path.mkdir(exist_ok=True)
    
    video_extensions = ('.ts',)
    updated_tracking = False
    
    for file in os.listdir(folder_path):
        if file.lower().endswith(video_extensions):
            input_file = os.path.join(folder_path, file)
            original_backup = output_path / file
            temp_output_file = os.path.join(folder_path, f"temp_repaired_{file}")
            
            if file in checked_videos:
                print(f"Skipping {file} - already checked")
                continue
                
            print(f"Checking: {file}")
            
            expected_duration = expected_durations.get(file)
            
            if is_video_corrupted(input_file, expected_duration):
                print(f"Corruption detected in {file}. Attempting repair...")
                shutil.copy2(input_file, original_backup)
                
                success = repair_video(input_file, temp_output_file)
                
                if success:
                    os.replace(temp_output_file, input_file)
                    print(f"Successfully repaired: {file}")
                    checked_videos[file] = "repaired"
                else:
                    if os.path.exists(temp_output_file):
                        os.remove(temp_output_file)
                    print(f"Failed to repair: {file}")
                    checked_videos[file] = "failed"
                updated_tracking = True
            else:
                print(f"{file} appears to be healthy")
                checked_videos[file] = "healthy"
                updated_tracking = True

    if updated_tracking:
        try:
            with open(tracking_path, "w") as f:
                json.dump(checked_videos, f, indent=2)
        except Exception as e:
            print(f"Error saving tracking file {tracking_file}: {str(e)}")

def is_video_corrupted(file_path, expected_duration=None, tolerance=500.0):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 
             'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', 
             file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=30
        )
        
        if result.returncode != 0 or not result.stdout.strip():
            print(f"ffprobe error for {file_path}: {result.stderr}")
            return True
        
        duration = float(result.stdout.strip())
        if duration <= 0 or duration > 1e6:
            return True
        
        if expected_duration is not None:
            if abs(duration - expected_duration) > tolerance:
                print(f"Duration mismatch for {file_path}: expected {expected_duration}, got {duration}")
                return True
        
        return False
        
    except subprocess.TimeoutExpired:
        print(f"ffprobe timed out for {file_path}")
        return True
    except Exception as e:
        print(f"Error checking {file_path}: {str(e)}")
        return True

def repair_video(input_file, output_file):
    """
    Attempt to repair a corrupted video file using FFmpeg with simple stream copy.
    Returns True if repair is successful, False otherwise.
    """
    try:
        # Simplified stream copy repair (matching your working command)
        result = subprocess.run(
            ['ffmpeg', '-i', input_file, '-c', 'copy', str(output_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=300  # Keep timeout as a safety net
        )
        
        if result.returncode == 0 and os.path.exists(output_file):
            print(f"FFmpeg output for {input_file}: {result.stderr}")
            if not is_video_corrupted(str(output_file)):
                return True
            else:
                print(f"Stream copy repair didn't resolve issues for {input_file}")
        
        print(f"FFmpeg error for {input_file}: {result.stderr}")
        return False
        
    except subprocess.TimeoutExpired as e:
        print(f"Repair timed out for {input_file}: {e.stderr}")
        return False
    except Exception as e:
        print(f"Error repairing {input_file}: {str(e)}")
        return False

if __name__ == "__main__":
    video_folder = r"c:\replace this"                        #put your direct path to your recording folder here
    recordings_json = r"C:\replace this too\recordings"      #this is the json file that sparkleTV player creates which contains the details on your DRV video files
    check_and_fix_videos(video_folder, json_file=recordings_json)
