# -*- coding: utf-8 -*-
import subprocess
import re
import os
import sys
import json
import locale

# Tkinter removed to prevent macOS crashes
# import tkinter as tk
# from tkinter import filedialog

def setup_encoding():
    """
    Sets up UTF-8 encoding for stdout/stderr and locale for macOS.
    """
    # Ensure UTF-8 encoding for output
    if sys.stdout and getattr(sys.stdout, 'encoding', None) != 'utf-8':
        try:
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
            if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
                sys.stderr.reconfigure(encoding='utf-8')
        except AttributeError:
            pass # Python < 3.7

    # Set locale for macOS to avoid encoding issues
    if sys.platform == 'darwin':
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except locale.Error:
            pass

def select_input_folder():
    """Opens a dialog to select the input folder."""
    if sys.platform == 'darwin':
        try:
            cmd = """
            tell application "System Events"
                activate
                set f to choose folder with prompt "Select Input Folder / Выберите папку с видео"
                return POSIX path of f
            end tell
            """
            result = subprocess.run(['osascript', '-e', cmd], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None # User cancelled
    else:
        # Fallback for other OS (CLI only to avoid Tkinter dependency)
        print("Enter input folder path:")
        path = input("> ").strip().strip('"').strip("'")
        return path if path else None

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

def format_time_for_filename(time_str):
    """
    Replaces colons and other special chars with dashes for safe filenames.
    e.g. 00:01:30:15 -> 00-01-30-15
    """
    return re.sub(r'[:;.]', '-', time_str)

def clean_filename(text):
    """
    Cleans the text to be used as a filename.
    """
    # User specific replacements
    text = text.replace('--', '-')
    text = re.sub(r'Фраза:\s*', '', text, flags=re.IGNORECASE)
    text = text.replace('«', '').replace('»', '').replace('"', '')
    
    # Windows invalid chars
    # Replace : with - to look similar to time
    text = text.replace(':', '-')
    # Remove others
    text = re.sub(r'[\\/*?"<>|]', '', text)
    
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def run_ffmpeg_cut(input_path, start, duration, output_path):
    """
    Executes the ffmpeg command to cut the video.
    """
    cmd = [
        'ffmpeg',
        '-y', # Overwrite
        '-ss', str(start),
        '-i', input_path,
        '-t', str(duration),
        '-c:v', 'libx264', # Use x264
        '-preset', 'slow', # Better compression efficiency
        '-crf', '18', # High quality (visually lossless)
        '-c:a', 'aac',
        '-b:a', '320k', # High quality audio
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL) # Hide ffmpeg output
    except subprocess.CalledProcessError as e:
        print(f"  Error cutting segment: {e}")
