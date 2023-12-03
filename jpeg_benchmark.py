import av
import cv2
from PIL import Image
import datetime
import gc
import json
import os
import time

REAL_FPS = 30  # FPS of input 'video'
FRAMES = 300  # Total frames
WIDTH = 1920  # Width of input images (in pixels)
HEIGHT = 1200  # Height of input images (in pixels)
INPUT_PATH = "./test_images/Encode Test Dataset 2024/"

ENCODING = "jpeg"
NUM_REPEATS = 1  # Number of times to test the same settings

# All tested simulated fps
simulated_fps = [30, 15, 10, 5, 1]

# How much to compress the image
# quality of image after compression (100 is no change)
compression_quality = [100, 75, 50, 25, 10]

# Initialize results dictionary/object
results = {
    "lossless" if cq == 100 else f"lossy_{cq}" : {
        str(sfps) : [] for sfps in simulated_fps
    } for cq in compression_quality
}

# Make output location
if not os.path.exists("./results"):
    os.mkdir("./results")

# Get all the images
print("Loading images...")
images = [cv2.imread(f"{INPUT_PATH}/{i}.png") for i in range(300)]
print("Finished loading images, begin testing...\n")
    
for cq in compression_quality:
    cq_name = "lossless" if cq == 100 else f"lossy_{cq}"

    if not os.path.exists(f"./results/{cq_name}/"):
        os.mkdir(f"./results/{cq_name}")

    for sfps in simulated_fps:
        total_size = 0

        if not os.path.exists(f"./results/{cq_name}/{sfps}fps/"):
            os.mkdir(f"./results/{cq_name}/{sfps}fps")

        # Repeat the test
        for i in range(NUM_REPEATS):
            test_result = {
                "total_time": 0,
                "avg_time": 0,
                "total_space": 0,
                "avg_space": 0,
                "frame_count": int(FRAMES/REAL_FPS*sfps),
                "frame_data": []
            }
            frame_ratio = int(REAL_FPS/sfps)

            for j in range(int(FRAMES/frame_ratio)):
                # Set test parameters
                FILE_NAME = f"{j}.{ENCODING}"

                # Get the video frame (picutre)
                image = Image.fromarray(images[j*frame_ratio][:, :, ::-1])

                # Encode the frame with specified settings and time
                gc.disable()
                start = time.time_ns()
                image.save(f"./results/{cq_name}/{sfps}fps/{FILE_NAME}",
                            ENCODING,
                            optimize = True,
                            quality = cq)
                end = time.time_ns()
                gc.enable()
                test_result["total_time"] += (end - start)

                # Find size in bytes
                frame_size = os.path.getsize(f"./results/{cq_name}/{sfps}fps/{FILE_NAME}")
                test_result["frame_data"].append({"time": end-start, "space": frame_size})
                test_result["total_space"] += frame_size
                total_size += frame_size
            
            # Save results
            test_result["avg_time"] = test_result["total_time"]/test_result["frame_count"]
            test_result["avg_space"] = test_result["total_space"]/test_result["frame_count"]
            # Add repeated results to the real results
            results[f"{cq_name}"][str(sfps)].append(test_result)
        
        # Add print runtime test progress
        print(f"./results/{cq_name}/{sfps}fps",
            "completed:  ~",
            round(total_size/(2**20), 2),
            "MB total"
        )

# Save test data into json
TEST_DATA_FILENAME = f"{ENCODING}_{datetime.datetime.isoformat(datetime.datetime.now(), timespec='seconds').replace(':','-')}.json"
with open(f"./results/{TEST_DATA_FILENAME}", 'w') as output:
    output.write(json.dumps(results, indent=2))

print("\n--------------test end----------------\n")
