# -*- coding: utf-8 -*-
import re
import os
import sys
# import tkinter as tk
# from tkinter import messagebox
import common

# Setup encoding and locale
common.setup_encoding()

def main():
    common.print_encoder_strategy_banner()

    # Tkinter initialization removed
    # try:
    #     root = tk.Tk()
    #     root.withdraw()
    #     root.update()
    # except Exception as e:
    #     print(f"Warning: Tkinter initialization failed: {e}")

    input_dir = common.select_input_folder()
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
        print("Внимание: Видео файлы не найдены.")
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
        fps = common.get_video_info(input_path)
        if fps is None:
            continue
            
        print(f"FPS: {fps}")
        ranges = parse_ranges(txt_file, fps)
        
        if not ranges:
            print(f"В файле {name}.txt не найдено диапазонов для нарезки.")
            continue
            
        # Create subfolder for this video
        video_output_dir = os.path.join(output_dir, name)
        if not os.path.exists(video_output_dir):
            os.makedirs(video_output_dir)

        process_video(input_path, ranges, video_output_dir)
        processed_count += 1
        
    print("\nDone! / Готово!")
    if processed_count > 0:
        print(f"Processed videos: {processed_count}\nResults in 'output' folder")
        # messagebox.showinfo("Done / Готово", f"Processed videos: {processed_count}\nResults in 'output' folder\n\nОбработано видео: {processed_count}\nРезультаты в папке 'output'")
    else:
        print("Nothing processed. Check .txt files.")
        # messagebox.showinfo("Done / Готово", "Nothing processed. Check .txt files.\n\nНичего не обработано. Проверьте .txt файлы.")

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
                
                start_sec = common.parse_time(start_str, fps)
                end_sec = common.parse_time(end_str, fps)
                
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
                    
                    start_sec = common.parse_time(start_str, fps)
                    end_sec = common.parse_time(end_str, fps)
                    
                    if start_sec is not None and end_sec is not None:
                        ranges.append((start_sec, end_sec, start_str, end_str, title))
                    else:
                        print(f"Failed to parse time in line: {line}")
                else:
                    print(f"Skipping invalid line: {line}")
                
    return ranges

def process_video(input_path, ranges, output_dir):
    """
    Cuts the video segments and saves them as separate files in output_dir.
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
        safe_start = common.format_time_for_filename(start_str)
        safe_end = common.format_time_for_filename(end_str)
        
        if title:
            # Sanitize title
            safe_title = re.sub(r'[\\/*?:"<>|]', '', title).strip()
            output_filename = f"{name}_{safe_title}_{safe_start}_{safe_end}.mp4"
        else:
            output_filename = f"{name}_{safe_start}_{safe_end}.mp4"

        output_path = os.path.join(output_dir, output_filename)
        
        print(f"  Cutting segment {i+1}: {start_str} to {end_str} -> {output_filename}")
        common.run_ffmpeg_cut(input_path, start, duration, output_path)

if __name__ == "__main__":

    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        # if Tkinter is initialized, try to show error message
        # try:
        #    messagebox.showerror("Error / Ошибка", f"An error occurred:\n{str(e)}\n\nПроизошла ошибка:\n{str(e)}")
        # except:
        #    pass
        raise
