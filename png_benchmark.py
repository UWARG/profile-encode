"""
Benchmarks PNG compression time and size (the ratio of the compressed image to the original image)
on a given set of images (300 landing pad images captured from a flight test).

Creates a folder with a compressed image for each quality setting to visually check the quality,
as well as a .json with the test data and a .csv which provides a more human-friendly summary
of the data.
"""
import gc
import io
import json
import os
import pathlib
import time

from PIL import Image


# Setting parameters
FRAME_COUNT = 300  # Total number of frames
FRAME_TO_SAVE = 69  # This frame is good, it has both landing pads in it
INPUT_PATH = pathlib.Path("test_images", "Encode Test Dataset 2024")
OUTPUT_PATH = pathlib.Path(f"log_{int(time.time())}")
COMPRESS_TYPES = [0, 1, 2, 3, 4]  # There are 5 different compression algorithms, each are numbered
INITIAL_COMPRESS_LEVEL = 1  # Compress level 0 is skipped because it is uncompressed
MAX_COMPRESS_LEVEL = 6  # Although this maxes out at 9, it takes way too long (like 10s per image)

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

# For output csv file
HEADERS = [
    "Compression Type",
    "Compression Level",
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


def update_min_max(
        min_value: "int | float",
        max_value: "int | float",
        current_value: "int | float",
) -> "tuple[int, int] | tuple[float, float]":
    # The intended output is something like this, but it is not guaranteed
    # because the inputs could be a combination of int and float.
    # eg. could also be tuple[float, int]
    """
    Udpates the min and max values for a measurement.

    Args:
        min: previous minimum value
        max: previous maximum value
        current_value: currently measured value

    Returns: (min, max)
        min: new updated minimum recorded value
        max: new updated maximum recorded value
    """
    if current_value < min_value:
        min_value = current_value
    elif current_value > max_value:
        max_value = current_value

    return min_value, max_value


if __name__ == "__main__":
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    results = {
        f"compress_type_{compress_type}": {
            f"compress_level_{compress_level}": {
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
            } for compress_level in range(INITIAL_COMPRESS_LEVEL, MAX_COMPRESS_LEVEL + 1)
        } for compress_type in COMPRESS_TYPES
    }

    test_begin = time.time()
    print("Start time:", test_begin)


    for compress_type in COMPRESS_TYPES:
        print(f"-----------------COMPRESS TYPE {compress_type}--------------------")
        for compress_level in range(INITIAL_COMPRESS_LEVEL, MAX_COMPRESS_LEVEL + 1):
            min_time_ns = float("inf")
            max_time_ns = 0
            total_time_ns = 0
            min_size_B = float("inf")
            max_size_B = 0
            total_size_B = 0
            min_compression_ratio = float("inf")
            max_compression_ratio = 0
            total_compression_ratio = 0
            current_result = \
                results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"]
            for frame_index in range(FRAME_COUNT):
                img = Image.open(pathlib.Path(INPUT_PATH, f"{frame_index}.png"))
                buffer = io.BytesIO()

                # Running encode
                gc.disable()
                start = time.time_ns()
                img.save(
                    buffer,
                    format="PNG",
                    compress_level=compress_level,
                    compress_type=compress_type,
                )
                end = time.time_ns()
                gc.enable()

                # Save singular test results
                time_ns = end - start
                size_B = buffer.getbuffer().nbytes
                compression_ratio = 100 * size_B / os.path.getsize(
                    pathlib.Path(INPUT_PATH, f"{frame_index}.png"),
                )

                min_time_ns, max_time_ns = update_min_max(min_time_ns, max_time_ns, time_ns)
                min_size_B, max_size_B = update_min_max(min_size_B, max_size_B, size_B)
                min_compression_ratio, max_compression_ratio = update_min_max(
                    min_compression_ratio,
                    max_compression_ratio,
                    compression_ratio,
                )

                total_time_ns += time_ns
                total_size_B += size_B
                total_compression_ratio += compression_ratio
                test_result = {
                    "time_ns": time_ns,
                    "size_B": size_B,
                    "size_ratio_compressed_to_original_%": compression_ratio
                }
                current_result["frame_data"].append(test_result)

                # Save one image (this one has 2 landing pads in it) for reference
                if frame_index == FRAME_TO_SAVE:
                    img.save(
                        pathlib.Path(OUTPUT_PATH, f"ct{compress_type}_cl{compress_level}.png"),
                        format="PNG",
                        compress_level=compress_level,
                        compress_type=compress_type,
                    )

            # Save average test results
            current_result[MIN_TIME_MS] = min_time_ns / 1e6
            current_result[MAX_TIME_MS] = max_time_ns / 1e6
            current_result[AVG_TIME_MS] = total_time_ns / FRAME_COUNT / 1e6
            current_result[MIN_SIZE_B] = min_size_B
            current_result[MAX_SIZE_B] = max_size_B
            current_result[AVG_SIZE_B] = total_size_B / FRAME_COUNT
            current_result[MIN_SIZE_RATIO_COMPRESSED_TO_ORIGINAL] = min_compression_ratio
            current_result[MAX_SIZE_RATIO_COMPRESSED_TO_ORIGINAL] = max_compression_ratio
            current_result[AVG_SIZE_RATIO_COMPRESSED_TO_ORIGINAL] = \
                total_compression_ratio / FRAME_COUNT
            print(f"Compress level {compress_level} complete")

    print("")
    print("-------------------TEST COMPLETED------------------")
    print("")

    # Saving full results
    with open(pathlib.Path(OUTPUT_PATH, "results.json"), 'w', encoding="utf-8") as file:
        file.write(json.dumps(results, indent=2))

    # Saving shortcut results without frame data (for more human readability)
    with open(pathlib.Path(OUTPUT_PATH, "summary.csv"), 'w', encoding="utf-8") as file:
        file.write(HEADER_LINE)
        for compress_type in COMPRESS_TYPES:
            for compress_level in range(INITIAL_COMPRESS_LEVEL, MAX_COMPRESS_LEVEL + 1):
                current_result = \
                    results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"]
                line_stats = [
                    str(compress_type),
                    str(compress_level),
                    str(current_result[MIN_TIME_MS]),
                    str(current_result[MAX_TIME_MS]),
                    str(current_result[AVG_TIME_MS]),
                    str(current_result[MIN_SIZE_B]),
                    str(current_result[MAX_SIZE_B]),
                    str(current_result[AVG_SIZE_B]),
                    str(current_result[MIN_SIZE_RATIO_COMPRESSED_TO_ORIGINAL]),
                    str(current_result[MAX_SIZE_RATIO_COMPRESSED_TO_ORIGINAL]),
                    str(current_result[AVG_SIZE_RATIO_COMPRESSED_TO_ORIGINAL]),
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
