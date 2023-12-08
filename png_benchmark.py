import gc
import io
import json
import os
import pathlib
import time

from PIL import Image

FRAME_COUNT = 300  # Total number of frames
FRAME_TO_SAVE = 69  # This frame is good, it has both landing pads in it
INPUT_PATH = pathlib.Path("test_images", "Encode Test Dataset 2024")
OUTPUT_PATH = pathlib.Path(f"log_{int(time.time())}")
COMPRESS_TYPES = [0, 1, 2, 3, 4]  # There are 5 different compression algorithms, each are numbered
INITIAL_COMPRESS_LEVEL = 1  # Compress level 0 is skipped because it is uncompressed
MAX_COMPRESS_LEVEL = 6  # Although this maxes out at 9, it takes way too long (like 10s per image)


if __name__ == "__main__":
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    results = {
        f"compress_type_{compress_type}": {
            f"compress_level_{compress_level}": {
                "max_time_ms": 0,
                "min_time_ms": 0,
                "avg_time_ms": 0,
                "max_size_B": 0,
                "min_size_B": 0,
                "avg_size_B": 0,
                "max_compression_%": 0,  # % of original size
                "min_compression_%": 0,
                "avg_compression_%": 0,
                "frame_data": []
            } for compress_level in range(INITIAL_COMPRESS_LEVEL, MAX_COMPRESS_LEVEL+1)
        } for compress_type in COMPRESS_TYPES
    }

    test_begin = time.time()
    print("Start time:", test_begin)


    for compress_type in COMPRESS_TYPES:
        print(f"-----------------COMPRESS TYPE {compress_type}--------------------")
        for compress_level in range(INITIAL_COMPRESS_LEVEL, MAX_COMPRESS_LEVEL+1):
            max_time = 0
            min_time = float("inf")
            total_time = 0
            max_size = 0
            min_size = float("inf")
            total_size = 0
            max_compression = 0
            min_compression = float("inf")
            total_compression = 0
            for frame in range(FRAME_COUNT):
                img = Image.open(pathlib.Path(INPUT_PATH, f"{frame}.png"))
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
                compression = size_B / os.path.getsize(pathlib.Path(INPUT_PATH, f"{frame}.png")) * 100

                if time_ns > max_time:
                    max_time = time_ns
                elif time_ns < min_time:
                    min_time = time_ns
                
                if size_B > max_size:
                    max_size = size_B
                elif size_B < min_size:
                    min_size = size_B
                
                if compression > max_compression:
                    max_compression = compression
                elif compression < min_compression:
                    min_compression = compression
                
                total_time += time_ns
                total_size += size_B
                total_compression += compression
                test_result = {
                    "time_ns": time_ns,
                    "size_B": size_B,
                    "compression_%": compression
                }
                results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"]["frame_data"].append(test_result)

                # Save one image (this one has 2 landing pads in it) for reference
                if frame == FRAME_TO_SAVE:
                    img.save(f"{OUTPUT_PATH}/ct{compress_type}_cl{compress_level}.png", "PNG", compress_level=compress_level, compress_type=compress_type)
            
            # Save average test results
            results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"]["max_time_ms"] = max_time/1e6
            results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"]["min_time_ms"] = min_time/1e6
            results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"]["avg_time_ms"] = total_time/FRAME_COUNT/1e6
            results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"]["max_size_B"] = max_size
            results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"]["min_size_B"] = min_size
            results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"]["avg_size_B"] = total_size/FRAME_COUNT
            results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"]["max_compression_%"] = max_compression
            results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"]["min_compression_%"] = min_compression
            results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"]["avg_compression_%"] = total_compression/FRAME_COUNT
            print(f"Compress level {compress_level} complete")
    
    print("")
    print("-------------------TEST COMPLETED------------------")
    print("")
    # Saving full results
    with open(pathlib.Path(OUTPUT_PATH, "results.json"), 'w', encoding="utf-8") as file:
        file.write(json.dumps(results, indent=2))
    
    # Saving shortcut results without frame data (for more human readability)
    with open(pathlib.Path(OUTPUT_PATH, "summary.csv"), 'w', encoding="utf-8") as file:
        file.write("Compression Type,Compression Level,Max Time (ms),Min Time (ms),Avg Time (ms),Max Size (B),Min Size (B),Avg Size (B),Max Compression (%),Min Compression (%),Avg Compression (%)\n")
        for compress_type in COMPRESS_TYPES:
            for compress_level in range(INITIAL_COMPRESS_LEVEL, MAX_COMPRESS_LEVEL+1):
                current_result = results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"]
                line = f"{compress_type},{compress_level},{current_result['max_time_ms']},{current_result['min_time_ms']},{current_result['avg_time_ms']},{current_result['max_size_B']},{current_result['min_size_B']},{current_result['avg_size_B']},{current_result['max_compression_%']},{current_result['min_compression_%']},{current_result['avg_compression_%']}\n"
                file.write(line)
    
    test_end = time.time()
    print("End time:", test_end)
    print(f"Time taken: {round((test_end-test_begin)/60)} mins {int(test_end-test_begin)%60} secs")
