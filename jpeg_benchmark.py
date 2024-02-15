import gc
import io
import json
import os
import pathlib
import time
import datetime
from PIL import Image

# Setting parameters
FRAME_COUNT = 300
REAL_FPS = 30
FRAME_TO_SAVE = 69
INPUT_PATH = pathlib.Path("test_images", "Encode Test Dataset 2024")
OUTPUT_PATH = pathlib.Path(f"log_{int(time.time())}")
ENCODING = "jpeg"
NUM_REPEATS = 1

# Keys for dictionary entries
TOTAL_TIME_MS = "total_time_ms"
AVG_TIME_MS = "avg_time_ms"
TOTAL_SPACE_B = "total_space_B"
AVG_SPACE_B = "avg_space_B"
FRAME_SPACE = "frame_space"
FRAME_DATA = "frame_data"

STIMULATED_FPS = [1, 5, 10, 30] # Test image compression, FPS
QUALITY_SETTINGS = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

# For output csv file
HEADERS = [
    "Quality",
    "Stimulated FPS",
    "Total Time (ms)",  
    "Avg Time (ms)",
    "Max Space (B)",
    "Avg Space (B)",
    "Frame Space",
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
    print("\n--------------Loading Images----------------\n")
    images = [Image.open(INPUT_PATH / f"{i}.png") for i in range(FRAME_COUNT)]
    print("\n--------------Images Loaded----------------\n")

    # Set up results dictionary
    results = {
        f"lossy_{quality}": {
            f"stimulated_fps_{sfps}": {
                TOTAL_TIME_MS: 0,
                AVG_TIME_MS: 0,
                TOTAL_SPACE_B: 0,
                AVG_SPACE_B: 0,
                FRAME_SPACE: int(FRAME_COUNT/REAL_FPS * sfps),
                FRAME_DATA: [],
            } for sfps in STIMULATED_FPS
        } for quality in QUALITY_SETTINGS
    }

    test_begin = time.time()
    print("Start time:", test_begin)

    for quality in QUALITY_SETTINGS:
        quality_directory = "lossless" if quality == 100 else f"loss_{quality}"
        if not os.path.exists(f"./results/{quality_directory}"):
            os.mkdir(f"./results/{quality_directory}")

        for sfps in STIMULATED_FPS:
            TOTAL_SPACE_B = 0
            if not os.path.exists(f"./results/{quality_directory}/{sfps}fps"):
                os.mkdir(f"./results/{quality_directory}/{sfps}fps")

            for i in range(NUM_REPEATS):
                test_result = {
                    TOTAL_TIME_MS: 0,
                    AVG_TIME_MS: 0,
                    TOTAL_SPACE_B: 0,
                    AVG_SPACE_B: 0,
                    FRAME_COUNT: int(FRAME_COUNT/REAL_FPS * sfps),
                    FRAME_DATA: []
                }
                frame_ratio = int(REAL_FPS/sfps)

                for jpeg in range(FRAME_COUNT):
                    FILE_NAME = f"{jpeg}.{ENCODING}"
                    image = Image.fromarray(images[jpeg*frame_ratio][:, :, ::-1])

                    # Encode the frame with specified settings and time
                    gc.disable()
                    start = time.time_ns()
                    image.save(f"./results/{quality_directory}/{sfps}fps/{FILE_NAME}",
                                ENCODING,
                                optimize = True,
                                quality = quality)
                    end = time.time_ns()
                    gc.enable()
                    test_result[TOTAL_TIME_MS] += (end - start)

                    # Find size in bytes
                    frame_size = os.path.getsize(f"./results/{quality_directory}/{sfps}fps/{FILE_NAME}")
                    test_result[FRAME_DATA].append({TOTAL_TIME_MS: end-start, TOTAL_SPACE_B: frame_size})
                    TOTAL_SPACE_B += frame_size
                    test_result[TOTAL_SPACE_B] += TOTAL_SPACE_B
                
                # Save results and append to results array
                test_result[AVG_TIME_MS] = test_result[TOTAL_TIME_MS]/test_result[FRAME_COUNT]
                test_result[AVG_SPACE_B] = test_result[TOTAL_SPACE_B]/test_result[FRAME_COUNT]
                results[f"lossy_{quality}"][f"stimulated_fps_{sfps}"] = test_result
    
    print("")
    print("-------------------TEST COMPLETED------------------")
    print("")

     # Saving full results
    with open(pathlib.Path(OUTPUT_PATH, "results.json"), 'w', encoding="utf-8") as file:
        file.write(json.dumps(results, indent=2))

    # Saving shortcut results without frame data (for more human readability)
    with open(pathlib.Path(OUTPUT_PATH, "summary.csv"), 'w', encoding="utf-8") as file:
        file.write(HEADER_LINE)
        for quality in QUALITY_SETTINGS:
            for sfps in STIMULATED_FPS:
                current_result = results[f"lossy_{quality}"][f"stimulated_fps_{sfps}"]
                line_stats = [
                    str(quality),
                    str(sfps),
                    str(current_result[TOTAL_TIME_MS]),
                    str(current_result[AVG_TIME_MS]),
                    str(current_result[TOTAL_SPACE_B]),
                    str(current_result[AVG_SPACE_B]),
                    str(current_result[FRAME_COUNT])
                ]
                line = ",".join(line_stats) + "\n"
                file.write(line)

    test_end = time.time()
    print("End time:", test_end)
    print(
        "Time taken:",
        int((test_end - test_begin) / 60),
        "mins",
        int(test_end - test_begin) % 60,
        "secs",
    )

if __name__ == "__main__":
    run()
