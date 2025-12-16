# Clip Assassin FFmpeg - AI Developer Instructions

## Project Overview
This is a Python-based automation tool that wraps FFmpeg to batch process video cuts based on text file inputs. It matches video files with corresponding text files containing timecodes and generates individual clips.

## Architecture & Data Flow
- **Entry Point**: `clip_assassin_ffmpeg.py` is the single execution script.
- **Input/Output**:
  - Reads from `./input/` (auto-created).
  - Writes to `./output/` (auto-created).
- **Matching Logic**: The script pairs files by basename.
  - Example: `input/interview.mp4` is processed using `input/interview.txt`.
- **Dependency**: Relies heavily on `ffmpeg` and `ffprobe` binaries being available in the system PATH.

## Core Components

### Time Parsing (`parse_time`)
The system supports a flexible time format parser that must be maintained.
- **Formats**:
  - Timecode: `HH:MM:SS:FF` (frames) or `HH:MM:SS;FF` (drop-frame).
  - Clock: `HH:MM:SS` or `MM:SS`.
  - Natural: `1h30m`, `1m30s`.
- **Frame Rate**: Frame-based calculations depend on the video's actual FPS, retrieved via `ffprobe`.

### Video Processing
- **Info Retrieval**: Uses `ffprobe` with JSON output to get metadata (FPS, duration).
- **Cutting**: Uses `ffmpeg` via `subprocess`.
  - **Key Flags**: `-ss` (start time), `-to` (end time), `-c copy` (stream copy for speed/quality).
  - **Stream Copy**: The tool prioritizes stream copying (`-c copy`) to avoid re-encoding.

## Developer Workflow
- **Running**: `python clip_assassin_ffmpeg.py`
- **Testing**:
  1. Place a video file in `input/`.
  2. Create a matching `.txt` file with time ranges (e.g., `00:00:05-00:00:10`).
  3. Run the script and verify `output/` contains the clip.
- **Debugging**:
  - Check `subprocess` calls for FFmpeg errors.
  - Verify FPS detection if frame-based cuts are inaccurate.

## Conventions
- **Filenames**: Output files are suffixed with the time range: `original_start-end.ext`.
- **Error Handling**: The script should skip invalid pairs or bad timecodes without crashing the entire batch.
- **Path Handling**: Use `os.path.join` for cross-platform compatibility (Windows/macOS/Linux).
