import argparse
import subprocess
import re
import os
import sys
import json
import math
import shutil

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "REELS", "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "REELS", "output")

def get_video_info(file_path):
    """
    Retrieves the frame rate and duration of the video using ffprobe.
    """
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=r_frame_rate,duration',
        '-of', 'json',
        file_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        stream = data['streams'][0]
        
        # Calculate fps
        if '/' in stream['r_frame_rate']:
            num, den = map(int, stream['r_frame_rate'].split('/'))
            fps = num / den
        else:
            fps = float(stream['r_frame_rate'])
            
        return fps
    except Exception as e:
        print(f"Error getting video info for {file_path}: {e}")
        return None

def parse_time(time_string, fps):
    """
    Parses a time string (e.g., "00:01:30:15", "1m30s") into seconds.
    Matches the logic of the original Clip Assassin hostscript.jsx.
    """
    if not time_string:
        return None

    time_string = time_string.strip().lower()
    
    hours = 0
    minutes = 0
    seconds = 0
    frames = 0
    is_drop_frame = False
    is_timecode_format = False

    # Check for drop-frame timecode (semicolon)
    if ';' in time_string:
        is_drop_frame = True
        is_timecode_format = True
        parts = time_string.split(';')
        if len(parts) == 2:
            frames = int(parts[1])
            time_string = parts[0]

    # Parse formats
    if 'h' in time_string:
        parts = time_string.split('h')
        hours = int(parts[0])
        if len(parts) > 1 and parts[1]:
            rest = parts[1]
            if 'm' in rest:
                m_parts = rest.split('m')
                minutes = int(m_parts[0])
                if len(m_parts) > 1 and m_parts[1]:
                    seconds = int(m_parts[1].replace('s', ''))
            else:
                seconds = int(rest.replace('s', ''))
    elif 'm' in time_string:
        parts = time_string.split('m')
        minutes = int(parts[0])
        if len(parts) > 1 and parts[1]:
            seconds = int(parts[1].replace('s', ''))
    elif ':' in time_string:
        parts = time_string.split(':')
        if len(parts) == 2: # MM:SS
            minutes = int(parts[0])
            seconds = int(parts[1])
        elif len(parts) == 3: # HH:MM:SS
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
        elif len(parts) == 4: # HH:MM:SS:FF
            is_timecode_format = True
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
            frames = int(parts[3])
        elif len(parts) == 1:
            seconds = int(parts[0])
    else:
        # Just seconds
        try:
            seconds = float(time_string)
        except ValueError:
            return None

    # Timecode conversion logic from hostscript.jsx
    if is_timecode_format and fps > 0:
        timebase = round(fps)
        total_frames = (hours * 3600 * timebase) + \
                       (minutes * 60 * timebase) + \
                       (seconds * timebase) + \
                       frames
        return total_frames / fps

    # Standard conversion
    total_seconds = (hours * 3600) + (minutes * 60) + seconds
    if frames > 0 and fps > 0:
        total_seconds += (frames / fps)
        
    return total_seconds

def parse_ranges(file_path, fps):
    """
    Reads the input file and parses time ranges.
    Format: start-end
    Returns a list of tuples: (start_seconds, end_seconds, original_line_string, title)
    """
    ranges = []
    if not os.path.exists(file_path):
        return ranges

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            title = ""
            # Extract title from --[Title]
            match = re.search(r'--\s*\[(.*?)\]', line)
            if match:
                title = match.group(1)

            # Find all time-like patterns in the line
            # Matches HH:MM:SS:FF, HH:MM:SS, MM:SS, etc.
            # This regex looks for sequences of digits separated by colons or semicolons
            time_pattern = r'((?:\d{1,2}:)?\d{1,2}:\d{2}(?:[:;]\d{2})?)'
            times = re.findall(time_pattern, line)
            
            if len(times) >= 2:
                start_str = times[0]
                end_str = times[1]
                
                start_sec = parse_time(start_str, fps)
                end_sec = parse_time(end_str, fps)
                
                if start_sec is not None and end_sec is not None:
                    # Store original strings for filename generation
                    ranges.append((start_sec, end_sec, start_str, end_str, title))
                else:
                    print(f"Failed to parse time in line: {line}")
            else:
                # Fallback to dash splitting if regex fails (legacy support)
                # Normalize dashes
                clean_line = re.sub(r'[\u2013\u2014]', '-', line)
                if '--' in clean_line:
                    clean_line = clean_line.split('--')[0]
                clean_line = clean_line.replace(' ', '')
                parts = clean_line.split('-')
                
                if len(parts) >= 2:
                    start_str = parts[0]
                    end_str = parts[-1]
                    # Clean up start string from potential prefixes like "01_"
                    start_str = re.sub(r'^\d+_', '', start_str)
                    
                    start_sec = parse_time(start_str, fps)
                    end_sec = parse_time(end_str, fps)
                    
                    if start_sec is not None and end_sec is not None:
                        ranges.append((start_sec, end_sec, start_str, end_str, title))
                    else:
                        print(f"Failed to parse time in line: {line}")
                else:
                    print(f"Skipping invalid line: {line}")
                
    return ranges

def format_time_for_filename(time_str):
    """
    Replaces colons and other special chars with dashes for safe filenames.
    e.g. 00:01:30:15 -> 00-01-30-15
    """
    return re.sub(r'[:;.]', '-', time_str)

def process_video(input_path, ranges):
    """
    Cuts the video segments and saves them as separate files in OUTPUT_DIR.
    """
    filename = os.path.basename(input_path)
    name, ext = os.path.splitext(filename)
    
    print(f"Processing {len(ranges)} segments for {filename}...")
    
    for i, (start, end, start_str, end_str, title) in enumerate(ranges):
        duration = end - start
        if duration <= 0:
            print(f"Skipping invalid range: {start} -> {end}")
            continue
            
        # Format filename: video_START_END.mp4
        safe_start = format_time_for_filename(start_str)
        safe_end = format_time_for_filename(end_str)
        
        if title:
            # Sanitize title
            safe_title = re.sub(r'[\\/*?:"<>|]', '', title).strip()
            output_filename = f"{name}_{safe_title}_{safe_start}_{safe_end}{ext}"
        else:
            output_filename = f"{name}_{safe_start}_{safe_end}{ext}"

        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        # Construct ffmpeg command for this segment
        cmd = [
            'ffmpeg',
            '-y', # Overwrite
            '-ss', str(start),
            '-i', input_path,
            '-t', str(duration),
            '-c:v', 'libx264', # Use x264
            '-preset', 'fast',
            '-crf', '22', # Good quality
            '-c:a', 'aac',
            '-b:a', '192k',
            output_path
        ]
        
        print(f"  Cutting segment {i+1}: {start_str} to {end_str} -> {output_filename}")
        try:
            subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL) # Hide ffmpeg output
        except subprocess.CalledProcessError as e:
            print(f"  Error cutting segment: {e}")

def main():
    # Ensure directories exist
    if not os.path.exists(INPUT_DIR):
        os.makedirs(INPUT_DIR)
        print(f"Created '{INPUT_DIR}' folder. Please put your videos there.")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Scan for video files
    video_extensions = ('.mp4', '.mov', '.mkv', '.avi', '.m4v')
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(video_extensions)]
    
    if not files:
        print(f"No video files found in '{INPUT_DIR}'.")
        return

    print(f"Found {len(files)} video(s) in '{INPUT_DIR}'.")

    for video_file in files:
        input_path = os.path.join(INPUT_DIR, video_file)
        name, _ = os.path.splitext(video_file)
        
        # Look for corresponding text file: video.txt
        txt_file = os.path.join(INPUT_DIR, f"{name}.txt")
        
        if not os.path.exists(txt_file):
            print(f"Skipping {video_file}: No matching text file found ({name}.txt)")
            continue
            
        print(f"\n--- Processing {video_file} ---")
        fps = get_video_info(input_path)
        if fps is None:
            continue
            
        print(f"Detected FPS: {fps}")
        ranges = parse_ranges(txt_file, fps)
        
        if not ranges:
            print(f"No valid ranges found in {name}.txt")
            continue
            
        process_video(input_path, ranges)
        
    print("\nAll done!")

if __name__ == "__main__":
    main()
