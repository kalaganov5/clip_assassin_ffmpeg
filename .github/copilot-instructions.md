# Clip Assassin FFmpeg - AI Developer Instructions

## Project Overview
Clip Assassin FFmpeg is a Python automation tool that batch processes video cuts based on text file inputs. It pairs video files with corresponding text files containing timecodes and generates individual clips using FFmpeg.

## Architecture & Data Flow
- **Entry Point**: `clip_assassin_ffmpeg.py` (single script execution).
- **Directory Structure**:
  - `input/`: Source videos and text files (auto-created).
  - `output/`: Destination for processed clips (auto-created).
- **Matching Logic**: Files are paired by basename (e.g., `video.mp4` uses `video.txt`).
- **Dependencies**: Requires `ffmpeg` and `ffprobe` binaries in the system PATH.

## Core Components

### Time Parsing (`parse_time`)
Handles conversion of various time formats into seconds.
- **Formats**:
  - Timecode: `HH:MM:SS:FF` (frames) or `HH:MM:SS;FF` (drop-frame).
  - Clock: `HH:MM:SS` or `MM:SS`.
  - Natural: `1h30m`, `1m30s`.
- **Frame Rate**: Uses `ffprobe` to determine FPS for accurate frame-based calculations.
- **Drop-Frame**: Detects `;` separator for drop-frame timecodes.

### Range Parsing (`parse_ranges`)
Parses the text file for cut segments.
- **Line Format**: `START-END --[Optional Title]`
- **Example**: `00:01:30-00:02:00 --[My Clip]`
- **Title Extraction**: Captures text inside `[]` after `--`.
- **Cleanup**: Handles en-dashes, em-dashes, and whitespace.

### Video Processing (`process_video`)
- **Engine**: Uses `subprocess` to call `ffmpeg`.
- **Encoding**: Re-encodes video to ensure frame accuracy and compatibility.
  - Video: `libx264` (CRF 22, fast preset).
  - Audio: `aac` (192k).
- **Naming Convention**: `OriginalName_Title_Start-End.ext`
  - Special characters in titles are sanitized.
  - Time strings in filenames use dashes (e.g., `00-01-30`).

## Developer Workflow
1.  **Setup**: Ensure Python 3.x and FFmpeg are installed.
2.  **Input**: Place video files in `input/` and create matching `.txt` files.
3.  **Execution**: Run `python clip_assassin_ffmpeg.py`.
4.  **Output**: Check `output/` for generated clips.

## Key Conventions
- **Path Handling**: Use `os.path.join` for cross-platform compatibility.
- **Error Handling**: The script skips invalid lines or files with warnings rather than crashing.
- **FFmpeg Output**: Standard error is suppressed (`stderr=subprocess.DEVNULL`) to keep the console clean, unless debugging.

## Common Tasks
- **Adding Formats**: Update `parse_time` to support new time string formats.
- **Changing Quality**: Modify the `ffmpeg` command arguments in `process_video` (e.g., change CRF or preset).
- **Debugging**: If cuts are inaccurate, verify the FPS detection in `get_video_info`.
