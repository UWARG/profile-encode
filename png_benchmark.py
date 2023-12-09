import gc
import io
import json
import os
import pathlib
import time

from PIL import Image

# Setting parameters
FRAME_COUNT = 10  # Total number of frames
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
MAX_COMPRESSION = "max_size_ratio_%"
MIN_COMPRESSION = "min_size_ratio_%"
AVG_COMPRESSION = "avg_size_ratio_%"
FRAME_DATA = "frame_data"


if __name__ == "__main__":
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    results = {
        f"compress_type_{compress_type}": {
            f"compress_level_{compress_level}": {
                MAX_TIME_MS: 0,
                MIN_TIME_MS: 0,
                AVG_TIME_MS: 0,
                MAX_SIZE_B: 0,
                MIN_SIZE_B: 0,
                AVG_SIZE_B: 0,
                MAX_COMPRESSION: 0,  # % of original size
                MIN_COMPRESSION: 0,
                AVG_COMPRESSION: 0,
                FRAME_DATA: []
            } for compress_level in range(INITIAL_COMPRESS_LEVEL, MAX_COMPRESS_LEVEL+1)
        } for compress_type in COMPRESS_TYPES
    }

    test_begin = time.time()
    print("Start time:", test_begin)


    for compress_type in COMPRESS_TYPES:
        print(f"-----------------COMPRESS TYPE {compress_type}--------------------")
        for compress_level in range(INITIAL_COMPRESS_LEVEL, MAX_COMPRESS_LEVEL+1):
            max_time_ns = 0
            min_time_ns = float("inf")
            total_time_ns = 0
            max_size_B = 0
            min_size_B = float("inf")
            total_size_B = 0
            max_compression = 0
            min_compression = float("inf")
            total_compression = 0
            for frame_index in range(FRAME_COUNT):
                img = Image.open(pathlib.Path(INPUT_PATH, f"{frame_index}.png"))
                buffer = io.BytesIO()

                # Running encode
                gc.disable()
                start = time.time_ns()
                img.save(buffer, format="PNG", compress_level=compress_level, compress_type=compress_type)
                end = time.time_ns()
                gc.enable()

                # Save singular test results
                time_ns = end-start
                size_B = buffer.getbuffer().nbytes
                compression = size_B / os.path.getsize(pathlib.Path(INPUT_PATH, f"{frame_index}.png")) * 100

                if time_ns > max_time_ns:
                    max_time_ns = time_ns
                elif time_ns < min_time_ns:
                    min_time_ns = time_ns
                
                if size_B > max_size_B:
                    max_size_B = size_B
                elif size_B < min_size_B:
                    min_size_B = size_B
                
                if compression > max_compression:
                    max_compression = compression
                elif compression < min_compression:
                    min_compression = compression
                
                total_time_ns += time_ns
                total_size_B += size_B
                total_compression += compression
                test_result = {
                    "time_ns": time_ns,
                    "size_B": size_B,
                    "size_ratio_%": compression
                }
                results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"]["frame_data"].append(test_result)

                # Save one image (this one has 2 landing pads in it) for reference
                if frame_index == FRAME_TO_SAVE:
                    img.save(pathlib.Path(OUTPUT_PATH, f"ct{compress_type}_cl{compress_level}.png"), "PNG", compress_level=compress_level, compress_type=compress_type)
            
            # Save average test results
            results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"][MAX_TIME_MS] = max_time_ns / 1e6
            results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"][MIN_TIME_MS] = min_time_ns / 1e6
            results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"][AVG_TIME_MS] = total_time_ns / FRAME_COUNT / 1e6
            results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"][MAX_SIZE_B] = max_size_B
            results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"][MIN_SIZE_B] = min_size_B
            results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"][AVG_SIZE_B] = total_size_B / FRAME_COUNT
            results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"][MAX_COMPRESSION] = max_compression
            results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"][MIN_COMPRESSION] = min_compression
            results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"][AVG_COMPRESSION] = total_compression / FRAME_COUNT
            print(f"Compress level {compress_level} complete")
    
    print("")
    print("-------------------TEST COMPLETED------------------")
    print("")
    
    # Saving full results
    with open(pathlib.Path(OUTPUT_PATH, "results.json"), 'w', encoding="utf-8") as file:
        file.write(json.dumps(results, indent=2))
    
    # Saving shortcut results without frame data (for more human readability)
    with open(pathlib.Path(OUTPUT_PATH, "summary.csv"), 'w', encoding="utf-8") as file:
        file.write("Compression Type,Compression Level,Max Time (ms),Min Time (ms),Avg Time (ms),Max Size (B),Min Size (B),Avg Size (B),Max Size Ratio (%),Min Size Ratio (%),Avg Size Ratio (%)\n")
        for compress_type in COMPRESS_TYPES:
            for compress_level in range(INITIAL_COMPRESS_LEVEL, MAX_COMPRESS_LEVEL+1):
                current_result = results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"]
                line = f"{compress_type},{compress_level},{current_result[MAX_TIME_MS]},{current_result[MIN_TIME_MS]},{current_result[AVG_TIME_MS]},{current_result[MAX_SIZE_B]},{current_result[MIN_SIZE_B]},{current_result[AVG_SIZE_B]},{current_result[MAX_COMPRESSION]},{current_result[MIN_COMPRESSION]},{current_result[AVG_COMPRESSION]}\n"
                file.write(line)
    
    test_end = time.time()
    print("End time:", test_end)
    print(f"Time taken: {int((test_end-test_begin)/60)} mins {int(test_end-test_begin)%60} secs")
