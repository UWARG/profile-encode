from datetime import datetime
import gc
import io
import json
import os
from PIL import Image
import time

FRAMES = 300  # Total frames
FRAME_TO_SAVE = 69  # This frame is good, it has both landing pads in it
INPUT_PATH = "./test_images/Encode Test Dataset 2024"
OUTPUT_PATH = "./log_" + datetime.strftime(datetime.now(), "%d-%m-%Y_%H-%M-%S")
MAX_COMPRESS_TYPE = 5
MAX_COMPRESS_LEVEL = 7  # Although this maxes out at 10, (compress_level=9), it takes way too long (like 10s per image)


if not os.path.exists(OUTPUT_PATH):
    os.mkdir(OUTPUT_PATH)

results = {
    f"compress_type_{i}": {
        f"compress_level_{j}": {
            "average_time_ms": 0,
            "average_size_MB": 0,
            "average_compress_%": 0,
            "frame_data": []
        } for j in range(10)
    } for i in range(5)
}

print("Loading images...")
images = [Image.open(f"{INPUT_PATH}/{i}.png") for i in range(FRAMES)]
print("Finished loading images. Begin testing...")


for compress_type in range(MAX_COMPRESS_TYPE):
    print(f"-----------------COMPRESS TYPE {compress_type}--------------------")
    for compress_level in range(MAX_COMPRESS_LEVEL):
        total_time = 0
        total_size = 0
        total_compression = 0
        for i in range(len(images)):
            compress_options = {
                "compress_type": compress_type,
                "compress_level": compress_level
            }
            buffer = io.BytesIO()
            gc.disable()
            start = time.time_ns()
            images[i].save(buffer, format="PNG", **compress_options)
            end = time.time_ns()
            gc.enable()
            test_result = {
                "time_ns": end-start,
                "size_B": buffer.getbuffer().nbytes,
                "compress_%": (1 - buffer.getbuffer().nbytes/os.path.getsize(f"{INPUT_PATH}/{i}.png"))*100
            }
            total_time += test_result["time_ns"]
            total_size += test_result["size_B"]
            total_compression += test_result["compress_%"]
            results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"]["frame_data"].append(test_result)
            # Save one iamge (this one has 2 landing pads in it) for reference
            if(i == FRAME_TO_SAVE):
                images[i].save(f"{OUTPUT_PATH}/ct{compress_type}_cl{compress_level}.png", "PNG", **compress_options)
        results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"]["average_time_ms"] = round(total_time/FRAMES/1e6, 3)
        results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"]["average_size_MB"] = round(total_size/FRAMES/(1<<20), 3)
        results[f"compress_type_{compress_type}"][f"compress_level_{compress_level}"]["average_compress_%"] = round(total_compression/FRAMES, 3)
        print(f"Compress level {compress_level} complete")

print("\n-------------------TEST COMPLETED------------------\n")
with open(f"{OUTPUT_PATH}/results.json", 'w') as file:
    file.write(json.dumps(results, indent=2))

print("end time:", datetime.strftime(datetime.now(), "%H-%M-%S"))