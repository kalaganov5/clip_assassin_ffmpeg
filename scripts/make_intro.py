# -*- coding: utf-8 -*-
import argparse
import subprocess
import re
import os
import sys
import json
import math
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import locale

# Ensure UTF-8 encoding for output
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass # Python < 3.7

# Set locale for macOS to avoid encoding issues
if sys.platform == 'darwin':
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except locale.Error:
        pass

# Configuration
# We will determine directories dynamically via GUI

def select_input_folder():
    """Opens a dialog to select the input folder."""
    root = tk.Tk()
    root.withdraw() # Hide the main window
    folder_path = filedialog.askdirectory(title="Select Input Folder / Выберите папку с видео")
    return folder_path

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
    Returns a list of tuples: (start_seconds, end_seconds, raw_line_content)
    """
    ranges = []
    if not os.path.exists(file_path):
        return ranges

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
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
                    # Store raw line for filename generation
                    ranges.append((start_sec, end_sec, line))
                else:
                    print(f"Failed to parse time in line: {line}")
            else:
                # Fallback to dash splitting if regex fails (legacy support)
                # Normalize dashes
                clean_line = re.sub(r'[\u2013\u2014]', '-', line)
                # Note: We don't strip comments here anymore to preserve text for filename
                
                parts = clean_line.split('-')
                
                if len(parts) >= 2:
                    # Try to find time-like strings in the split parts
                    # This is a bit heuristic
                    start_candidate = parts[0].strip()
                    end_candidate = parts[1].strip()
                    
                    # Clean up start string from potential prefixes like "01_" just for parsing
                    start_clean = re.sub(r'^\d+_', '', start_candidate)
                    # Clean up end string from potential text
                    end_clean = end_candidate.split(' ')[0]

                    start_sec = parse_time(start_clean, fps)
                    end_sec = parse_time(end_clean, fps)
                    
                    if start_sec is not None and end_sec is not None:
                        ranges.append((start_sec, end_sec, line))
                    else:
                        print(f"Failed to parse time in line: {line}")
                else:
                    print(f"Skipping invalid line: {line}")
                
    return ranges

def clean_filename(text):
    """
    Cleans the text to be used as a filename according to user requirements.
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

def process_video(input_path, ranges, output_dir):
    """
    Cuts the video segments and saves them as separate files in output_dir.
    """
    filename = os.path.basename(input_path)
    name, ext = os.path.splitext(filename)
    
    print(f"Processing {len(ranges)} segments for {filename}...")
    
    for i, (start, end, raw_line) in enumerate(ranges):
        duration = end - start
        if duration <= 0:
            print(f"Skipping invalid range: {start} -> {end}")
            continue
            
        # Generate filename from the raw line content
        output_filename = clean_filename(raw_line) + ext
        output_path = os.path.join(output_dir, output_filename)
        
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
        
        print(f"  Cutting segment {i+1}: {output_filename}")
        try:
            subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL) # Hide ffmpeg output
        except subprocess.CalledProcessError as e:
            print(f"  Error cutting segment: {e}")

def main():
    print("Запуск Clip Assassin Intro...")
    
    input_dir = select_input_folder()
    if not input_dir:
        print("Папка не выбрана. Выход.")
        return

    output_dir = os.path.join(input_dir, "output")
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Создана папка для результатов: {output_dir}")
        except OSError as e:
            print(f"Ошибка создания папки output: {e}")
            input("Нажмите Enter для выхода...")
            return

    # Scan for video files
    video_extensions = ('.mp4', '.mov', '.mkv', '.avi', '.m4v')
    files = [f for f in os.listdir(input_dir) if f.lower().endswith(video_extensions)]
    
    if not files:
        print(f"В папке '{input_dir}' не найдено видео файлов.")
        messagebox.showwarning("Внимание", "Видео файлы не найдены в выбранной папке.")
        return

    print(f"Найдено {len(files)} видео в '{input_dir}'.")
    
    processed_count = 0

    for video_file in files:
        input_path = os.path.join(input_dir, video_file)
        name, _ = os.path.splitext(video_file)
        
        # Look for corresponding text file: video.txt
        txt_file = os.path.join(input_dir, f"{name}.txt")
        
        if not os.path.exists(txt_file):
            print(f"Пропуск {video_file}: Не найден текстовый файл ({name}.txt)")
            continue
            
        print(f"\n--- Обработка {video_file} ---")
        fps = get_video_info(input_path)
        if fps is None:
            continue
            
        print(f"FPS: {fps}")
        ranges = parse_ranges(txt_file, fps)
        
        if not ranges:
            print(f"В файле {name}.txt не найдено диапазонов для нарезки.")
            continue
            
        process_video(input_path, ranges, output_dir)
        processed_count += 1
        
    print("\nDone! / Готово!")
    if processed_count > 0:
        messagebox.showinfo("Done / Готово", f"Processed videos: {processed_count}\nResults in 'output' folder\n\nОбработано видео: {processed_count}\nРезультаты в папке 'output'")
    else:
        messagebox.showinfo("Done / Готово", "Nothing processed. Check .txt files.\n\nНичего не обработано. Проверьте .txt файлы.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        messagebox.showerror("Error / Ошибка", f"An error occurred:\n{str(e)}\n\nПроизошла ошибка:\n{str(e)}")
        raise
