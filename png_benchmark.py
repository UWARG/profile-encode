import gc
import io
import json
import os
import pathlib
import time

from PIL import Image

FRAME_COUNT = 300  # Total frames
FRAME_TO_SAVE = 69  # This frame is good, it has both landing pads in it
INPUT_PATH = pathlib.Path("test_images", "Encode Test Dataset 2024")
OUTPUT_PATH = pathlib.Path(f"log_{int(time.time())}")
MAX_COMPRESS_TYPE = 5
MAX_COMPRESS_LEVEL = 7  # Although this maxes out at 10, (compress_level=9), it takes way too long (like 10s per image)


if __name__ == "__main__":
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    results = {
        f"compress_type_{i}": {
            f"compress_level_{j}": {
                "max_time_ms": 0,
                "min_time_ms": 0,
                "avg_time_ms": 0,
                "max_size_B": 0,
                "min_size_B": 0,
                "avg_size_B": 0,
                "max_compression_%": 0,
                "min_compression_%": 0,
                "avg_compression_%": 0,
                "frame_data": []
            } for j in range(1, MAX_COMPRESS_LEVEL)
        } for i in range(MAX_COMPRESS_TYPE)
    }

    test_begin = time.time()
    print("Start time:", test_begin)


    for compress_type in range(MAX_COMPRESS_TYPE):
        print(f"-----------------COMPRESS TYPE {compress_type}--------------------")
        for compress_level in range(1, MAX_COMPRESS_LEVEL):
            max_time = 0
            min_time = 1e15
            total_time = 0
            max_size = 0
            min_size = 1e15
            total_size = 0
            max_compression = 0
            min_compression = 101
            total_compression = 0
            for i in range(FRAME_COUNT):
                img = Image.open(pathlib.Path(INPUT_PATH, f"{i}.png"))
                buffer = io.BytesIO()

                # Running encode
                gc.disable()
                start = time.time_ns()
                img.save(buffer, format="PNG", compress_level=compress_level, compress_type=compress_type)
                end = time.time_ns()
                gc.enable()

                # Save singular test results
                test_result = {
                    "time_ns": end-start,
                    "size_B": buffer.getbuffer().nbytes,
                    "compression_%": (1 - buffer.getbuffer().nbytes/os.path.getsize(pathlib.Path(INPUT_PATH, f"{i}.png")))*100
                }
                if test_result["time_ns"] > max_time:
                    max_time = test_result["time_ns"]
                elif test_result["time_ns"] < min_time:
                    min_time = test_result["time_ns"]
                if test_result["size_B"] > max_size:
                    max_size = test_result["size_B"]
                elif test_result["size_B"] < min_size:
                    min_size = test_result["size_B"]
                if test_result["compression_%"] > max_compression:
                    max_compression = test_result["compression_%"]
                elif test_result["compression_%"] < min_compression:
                    min_compression = test_result["compression_%"]
                total_time += test_result["time_ns"]
                total_size += test_result["size_B"]
                total_compression += test_result["compression_%"]
                results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"]["frame_data"].append(test_result)

                # Save one image (this one has 2 landing pads in it) for reference
                if(i == FRAME_TO_SAVE):
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
    
    print("\n-------------------TEST COMPLETED------------------\n")
    # Saving full results
    with open(pathlib.Path(OUTPUT_PATH, "results.json"), 'w', encoding="utf-8") as file:
        file.write(json.dumps(results, indent=2))
    
    # Saving shortcut results without frame data (for more human readability)
    with open(pathlib.Path(OUTPUT_PATH, "summary.csv"), 'w', encoding="utf-8") as file:
        file.write("Compression Type,Compression Level,Max Time (ms),Min Time (ms),Avg Time (ms),Max Size (B),Min Size (B),Avg Size (B),Max Compression (%),Min Compression (%),Avg Compression (%)\n")
        for compress_type in range(MAX_COMPRESS_TYPE):
            for compress_level in range(1, MAX_COMPRESS_LEVEL):
                temp = results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"]
                line = f"{compress_type},{compress_level},{temp['max_time_ms']},{temp['min_time_ms']},{temp['avg_time_ms']},{temp['max_size_B']},{temp['min_size_B']},{temp['avg_size_B']},{temp['max_compression_%']},{temp['min_compression_%']},{temp['avg_compression_%']}\n"
                file.write(line)
    
    test_end = time.time()
    print("End time:", test_end)
    print(f"Time taken: ~{round((test_end-test_begin)/60)} mins")
