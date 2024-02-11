import gc
import io
import json
import os
import pathlib
import time

from PIL import Image

# Setting parameters
FRAME_COUNT = 300
FRAME_TO_SAVE = 69
INPUT_PATH = pathlib.Path("test_images", "Encode Test Dataset 2024")
OUTPUT_PATH = pathlib.Path(f"log_{int(time.time())}")
ENCODING = "jpeg"
NUM_REPEATS = 1

# Keys for dictionary entries
MAX_TIME_MS = "max_time_ms"
MIN_TIME_MS = "min_time_ms"
AVG_TIME_MS = "avg_time_ms"
MAX_SIZE_B = "max_size_B"
MIN_SIZE_B = "min_size_B"
AVG_SIZE_B = "avg_size_B"
MAX_SIZE_RATIO_COMPRESSED_TO_ORIGINAL = "max_size_ratio_compressed_to_original_%"
MIN_SIZE_RATIO_COMPRESSED_TO_ORIGINAL = "min_size_ratio_compressed_to_original_%"
AVG_SIZE_RATIO_COMPRESSED_TO_ORIGINAL = "avg_size_ratio_compressed_to_original_%"
FRAME_DATA = "frame_data"
ENCODING = "jpeg"
STIMULATED_FPS = [1, 5, 10, 30] # Test image compression, FPS
QUALITY_SETTINGS = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

# For output csv file
HEADERS = [
    "Quality",
    "Stimulated FPS",
    "Min Time (ms)",
    "Max Time (ms)",   
    "Avg Time (ms)",
    "Min Size (B)",
    "Max Size (B)",
    "Avg Size (B)",
    "Min Size Ratio (compressed to original in %)",
    "Max Size Ratio (compressed to original in %)",
    "Avg Size Ratio (compressed to original in %)",
]
HEADER_LINE = ",".join(HEADERS) + "\n"

def update_min_max(min_value: "int | float",
                   max_value: "int | float",
                   current_value: "int | float",) -> "tuple[int, int] | tuple[float, float]":
    """
    Updates the min and max values for a measurement.

    Args:
        min_value: previous minimum value
        max_value: previous maximum value
        current_value: currently measured value

    Returns: (min_value, max_value)
        min_value: new updated minimum recorded value
        max_value: new updated maximum recorded value
        
        The intended output is something like [int, int] or [float, float],
        but it is not guaranteed because the inputs could be a combination of int and float.
        eg. could also be tuple[float, int]
    """
    if current_value < min_value:
        min_value = current_value
    if current_value > max_value:
        max_value = current_value

    return min_value, max_value

def run():
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    
    results = {
        f"lossy_{quality}": {
            f"stimulated_fps_{sfps}": {
                MIN_TIME_MS: 0,
                MAX_TIME_MS: 0,
                AVG_TIME_MS: 0,
                MIN_SIZE_B: 0,
                MAX_SIZE_B: 0,
                AVG_SIZE_B: 0,
                # % of original size
                MIN_SIZE_RATIO_COMPRESSED_TO_ORIGINAL: 0,
                MAX_SIZE_RATIO_COMPRESSED_TO_ORIGINAL: 0,
                AVG_SIZE_RATIO_COMPRESSED_TO_ORIGINAL: 0,
                FRAME_DATA: [],
            } for sfps in STIMULATED_FPS
        } for quality in QUALITY_SETTINGS
    }

    test_begin = time.time()
    print("Start time:", test_begin)

if __name__ == "__main__":
    run()