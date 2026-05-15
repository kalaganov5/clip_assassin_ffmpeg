# -*- coding: utf-8 -*-
import subprocess
import re
import os
import sys
import json
import locale

_CACHED_VIDEO_ENCODER = None
_CACHED_ENCODER_CONTEXT = None

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


def _is_hw_encoder(encoder_name):
    return encoder_name in {'h264_nvenc', 'h264_qsv', 'h264_amf', 'h264_vaapi', 'h264_videotoolbox'}


def _get_encoder_policy():
    policy = (os.getenv('CA_ENCODER_POLICY') or 'auto').strip().lower()
    if policy not in {'auto', 'strict_gpu', 'cpu_only'}:
        print(f"  [Encoder] Unknown CA_ENCODER_POLICY='{policy}', using 'auto'.")
        return 'auto'
    return policy


def _get_encoder_log_level():
    level = (os.getenv('CA_ENCODER_LOG') or 'basic').strip().lower()
    if level not in {'basic', 'debug'}:
        return 'basic'
    return level


def _log_encoder(message, level='basic'):
    current = _get_encoder_log_level()
    if current == 'debug' or level == 'basic':
        print(f"  [Encoder] {message}")


def _default_encoder_priority():
    if sys.platform == 'win32':
        return ['h264_nvenc', 'h264_qsv', 'h264_amf', 'libx264']
    if sys.platform == 'darwin':
        return ['h264_videotoolbox', 'libx264']
    return ['h264_vaapi', 'h264_nvenc', 'h264_qsv', 'h264_amf', 'libx264']


def _platform_encoder_hint():
    if sys.platform == 'win32':
        return "Windows: GPU priority NVENC -> QSV -> AMF, then CPU (libx264)"
    if sys.platform == 'darwin':
        return "macOS (Apple Silicon/Intel): GPU priority VideoToolbox, then CPU (libx264)"
    return "Linux: GPU priority VAAPI -> NVENC -> QSV -> AMF, then CPU (libx264)"


def _get_encoder_priority():
    raw = os.getenv('CA_ENCODER_PRIORITY')
    if not raw:
        return _default_encoder_priority()

    requested = [item.strip().lower() for item in raw.split(',') if item.strip()]
    if not requested:
        return _default_encoder_priority()

    # Keep order, dedupe, and ensure software fallback exists in auto/cpu flows.
    priority = []
    seen = set()
    for enc in requested:
        if enc not in seen:
            priority.append(enc)
            seen.add(enc)

    if 'libx264' not in seen:
        priority.append('libx264')

    return priority


def _load_available_encoders():
    try:
        result = subprocess.run(
            ['ffmpeg', '-hide_banner', '-encoders'],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout.lower()
    except Exception as e:
        _log_encoder(f"Failed to list ffmpeg encoders: {e}", level='debug')
        return set()

    encoders = set()
    pattern = re.compile(r'^\s*V\S*\s+([a-z0-9_]+)\b', re.IGNORECASE)
    for line in output.splitlines():
        match = pattern.match(line)
        if match:
            encoders.add(match.group(1).lower())
    return encoders


def print_encoder_strategy_banner():
    """
    Prints encoder strategy information at startup before processing begins.
    """
    policy = _get_encoder_policy()
    priority = _get_encoder_priority()
    selected = _detect_best_video_encoder()
    selected_mode = "GPU" if _is_hw_encoder(selected) else "CPU"

    print("=" * 60)
    print("Encoder Strategy / Стратегия кодирования")
    print(f"Platform: {sys.platform}")
    print(f"Policy: {policy}")
    print(f"Priority: {', '.join(priority)}")
    print(f"Approach: {selected_mode} ({selected})")
    print(_platform_encoder_hint())
    print("=" * 60)


def _detect_best_video_encoder():
    """
    Detects the best available H.264 encoder in ffmpeg.
    On Windows, hardware encoders are preferred when available.
    """
    global _CACHED_VIDEO_ENCODER, _CACHED_ENCODER_CONTEXT

    policy = _get_encoder_policy()
    priority = _get_encoder_priority()
    cache_key = (policy, tuple(priority))

    if _CACHED_VIDEO_ENCODER is not None and _CACHED_ENCODER_CONTEXT == cache_key:
        return _CACHED_VIDEO_ENCODER

    available = _load_available_encoders()
    if not available:
        _CACHED_VIDEO_ENCODER = 'libx264'
        _CACHED_ENCODER_CONTEXT = cache_key
        return _CACHED_VIDEO_ENCODER

    _log_encoder(f"Policy={policy} Priority={','.join(priority)}")

    if policy == 'cpu_only':
        _CACHED_VIDEO_ENCODER = 'libx264'
        _CACHED_ENCODER_CONTEXT = cache_key
        _log_encoder("CPU-only policy selected. Using libx264.")
        return _CACHED_VIDEO_ENCODER

    for encoder in priority:
        if encoder not in available:
            _log_encoder(f"Skip {encoder}: not present in ffmpeg encoders list.", level='debug')
            continue
        if policy == 'strict_gpu' and not _is_hw_encoder(encoder):
            _log_encoder(f"Skip {encoder}: strict_gpu allows hardware encoders only.", level='debug')
            continue
        if _is_encoder_usable(encoder):
            _CACHED_VIDEO_ENCODER = encoder
            _CACHED_ENCODER_CONTEXT = cache_key
            _log_encoder(f"Selected encoder: {encoder}")
            return _CACHED_VIDEO_ENCODER
        _log_encoder(f"Skip {encoder}: encoder initialization failed.", level='debug')

    if policy == 'strict_gpu':
        raise RuntimeError(
            "No usable hardware H.264 encoder found for strict_gpu policy. "
            "Check GPU drivers and ffmpeg build."
        )

    _log_encoder("No usable GPU encoder found. Falling back to libx264.")
    _CACHED_VIDEO_ENCODER = 'libx264'
    _CACHED_ENCODER_CONTEXT = cache_key
    return _CACHED_VIDEO_ENCODER

def _is_encoder_usable(encoder_name):
    """
    Verifies that ffmpeg can actually initialize the encoder on this machine.
    Some ffmpeg builds list hardware encoders, but runtime init may fail due to
    missing/old drivers, unavailable hardware, or partial ffmpeg builds.
    """
    # Some hardware encoders (notably NVENC) may reject very small frames.
    # Use a conservative HD test frame to avoid false negatives.
    test_cmd = [
        'ffmpeg',
        '-hide_banner',
        '-loglevel', 'error',
        '-f', 'lavfi',
        '-i', 'color=c=black:s=1920x1080:r=30',
        '-frames:v', '30',
        '-pix_fmt', 'yuv420p',
        '-c:v', encoder_name,
        '-f', 'null',
        '-'
    ]
    try:
        subprocess.run(test_cmd, capture_output=True, text=True, check=True)
        return True
    except Exception:
        return False

def run_ffmpeg_cut(input_path, start, duration, output_path):
    """
    Executes the ffmpeg command to cut the video.
    """
    policy = _get_encoder_policy()
    video_encoder = _detect_best_video_encoder()

    cmd = [
        'ffmpeg',
        '-y', # Overwrite
        '-ss', str(start),
        '-i', input_path,
        '-t', str(duration),
        '-c:v', video_encoder,
        '-c:a', 'aac',
        '-b:a', '320k', # High quality audio
        output_path
    ]

    if video_encoder == 'libx264':
        cmd[8:8] = ['-preset', 'slow', '-crf', '18']
    elif video_encoder == 'h264_nvenc':
        # Good quality/size default for NVENC while keeping speed benefit.
        cmd[8:8] = ['-preset', 'p5', '-cq', '19', '-b:v', '0']
    
    try:
        subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL) # Hide ffmpeg output
    except subprocess.CalledProcessError as e:
        # Hardware encoders can still fail at runtime for a specific file.
        # Fall back to software encode instead of failing the whole segment.
        if video_encoder != 'libx264' and policy != 'strict_gpu':
            print(f"  Encoder {video_encoder} failed, fallback to libx264.")
            fallback_cmd = [
                'ffmpeg',
                '-y',
                '-ss', str(start),
                '-i', input_path,
                '-t', str(duration),
                '-c:v', 'libx264',
                '-preset', 'slow',
                '-crf', '18',
                '-c:a', 'aac',
                '-b:a', '320k',
                output_path
            ]
            try:
                subprocess.run(fallback_cmd, check=True, stderr=subprocess.DEVNULL)
                return
            except subprocess.CalledProcessError as e2:
                print(f"  Error cutting segment with fallback: {e2}")
                return
        if policy == 'strict_gpu' and video_encoder != 'libx264':
            print(f"  Error cutting segment with strict_gpu policy: {e}")
            raise
        print(f"  Error cutting segment: {e}")
