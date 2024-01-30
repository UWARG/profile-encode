"""
Benchmarks AVIF compression time and size (the ratio of the compressed image to the original image)
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
import pillow_heif


# Setting parameters
FRAME_COUNT = 300  # Total number of frames
FRAME_TO_SAVE = 69  # This frame is good, it has both landing pads in it
INPUT_PATH = pathlib.Path("test_images", "Encode Test Dataset 2024")
OUTPUT_PATH = pathlib.Path(f"log_{int(time.time())}")
# All the quality settings to test (-1 should represent 'lossless',
# although it is only lossless in case of 444 subsampling)
QUALITY_SETTINGS = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
CHROMA_SETTINGS = [420, 422, 444]

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
    "Quality",
    "Chroma",
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
    pillow_heif.register_avif_opener(thumbnails=False)

    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    results = {
        f"quality_{quality}": {
            f"chroma_{chroma}": {
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
            } for chroma in CHROMA_SETTINGS
        } for quality in QUALITY_SETTINGS
    }

    test_begin = time.time()
    print("Start time:", test_begin)


    for quality in QUALITY_SETTINGS:
        print(f"-----------------QUALITY = {quality}--------------------")
        for chroma in CHROMA_SETTINGS:

            min_time_ns = float("inf")
            max_time_ns = 0
            total_time_ns = 0
            min_size_B = float("inf")
            max_size_B = 0
            total_size_B = 0
            min_compression_ratio = float("inf")
            max_compression_ratio = 0
            total_compression_ratio = 0
            current_result = results[f"quality_{quality}"][f"chroma_{chroma}"]
            for frame_index in range(FRAME_COUNT):
                img = pillow_heif.from_pillow(
                    Image.open(pathlib.Path(INPUT_PATH, f"{frame_index}.png"))
                )
                buffer = io.BytesIO()

                # Running encode
                gc.disable()
                start = time.time_ns()
                img.save(
                    buffer,
                    format="AVIF",
                    quality=quality,
                    chroma=chroma,
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
                        pathlib.Path(OUTPUT_PATH, f"q{quality}_c{chroma}.avif"),
                        format="AVIF",
                        quality=quality,
                        chroma=chroma,
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
            print(f"chroma {chroma} completed")

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
            for chroma in CHROMA_SETTINGS:
                current_result = results[f"quality_{quality}"][f"chroma_{chroma}"]
                line_stats = [
                    str(quality),
                    str(chroma),
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


if __name__ == "__main__":
    run()
