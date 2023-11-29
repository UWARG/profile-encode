import av
import cv2
import datetime
import gc
import json
import os
import time

REAL_FPS = 30  # FPS of input 'video'
FRAMES = 300  # Total frames
WIDTH = 1920  # Width of input images (in pixels)
HEIGHT = 1200  # Height of input images (in pixels)
INPUT_PIXEL_FORMAT = "bgr24"  # input PNG is saved in bgr and not rgb, 24 bits per pixel
INPUT_PATH = "./test_images/Encode Test Dataset 2024/"

ENCODING = "h264"
NUM_REPEATS = 1  # Number of times to test the same settings

# All tested simulated fps
simulated_fps = [30, 15, 10, 5, 1]

# Possible h264 chroma subsamples
# If using other ratios, the pixels/regions would have different sizes
subsamples = [
    # "yuv411p",  # Apparently these 2 are not supported
    "yuv420p",
    "yuv422p",
    # "yuv440p",
    "yuv444p"
]

# This is actually what really determnies picture quality vs size
# "variable" means setting the video to a constant 10s
output_fps = ["variable", 30, 60, 120]

# Create results dictionary/object
results = dict.fromkeys(
    [str(ofps) for ofps in output_fps],
    dict.fromkeys(
        subsamples,
        dict.fromkeys(
            [str(sfps) for sfps in simulated_fps],
            None  # Cannot initialize a list because somehow they all share the same address if done here
        )
    )
)

# Make output location
if not os.path.exists("./results"):
    os.mkdir("./results")

# Get all the images
print("Loading images...")
images = [cv2.imread(f"{INPUT_PATH}/{i}.png") for i in range(300)]
print("Finished loading images, begin testing...\n")

for ofps in output_fps:
    if not os.path.exists(f"./results/{str(ofps)}_fps"):
        os.mkdir(f"./results/{str(ofps)}_fps")
    print(f"\n-------------------{str(ofps)} fps------------------")
    
    for subsample in subsamples:
        for sfps in simulated_fps:
            repeated_results = []
            # Repeat the test
            for i in range(NUM_REPEATS):
                test_result = {
                    "total_time": 0,
                    "avg_time": 0,
                    "total_space": 0,
                    "avg_space": 0,
                    "file_size": 0,
                    "frame_count": int(FRAMES/REAL_FPS*sfps),
                    "frame_data": []
                }
                # Set test parameters
                FILE_NAME = f"{ENCODING}_{subsample}_{sfps}fps.mp4"
                container = av.open(f"./results/{str(ofps)}_fps/{FILE_NAME}", 'w')
                video_format = av.VideoFormat(subsample, width=WIDTH, height=HEIGHT)
                if ofps == "variable":
                    stream = container.add_stream(ENCODING, sfps, format=video_format)
                else:
                    stream = container.add_stream(ENCODING, ofps, format=video_format)
                stream.bit_rate = 1 << 23  # 8MB
                frame_ratio = int(REAL_FPS/sfps)

                for j in range(int(FRAMES/frame_ratio)):
                    # Get the video frame (picutre)
                    frame = av.VideoFrame.from_ndarray(images[j*frame_ratio], format=INPUT_PIXEL_FORMAT)

                    # Encode the frame with specified settings and time
                    gc.disable()
                    start = time.time_ns()
                    packets = stream.encode(frame)
                    end = time.time_ns()
                    gc.enable()
                    test_result["total_time"] += (end - start)

                    # Find size in bytes
                    frame_size = 0
                    for packet in packets:
                        frame_size += packet.size
                    test_result["frame_data"].append({"time": end-start, "space": frame_size})
                    test_result["total_space"] += frame_size

                    # Save output images (only do this once, don't need 5 identical videos)
                    # It seems that even if you don't run this, is still saves it into the video,
                    # since we are adding to the container's output stream
                    if(i == 0):
                        container.mux(packets)
                
                # Flush stream
                if(i == 0):
                    packets = stream.encode(None)
                    container.mux(packets)

                # Save results
                test_result["avg_time"] = test_result["total_time"]/test_result["frame_count"]
                test_result["avg_space"] = test_result["total_space"]/test_result["frame_count"]
                test_result["file_size"] = os.path.getsize(f"./results/{str(ofps)}_fps/{FILE_NAME}")
                repeated_results.append(test_result)

                container.close()
            
            # Add repeated results to the real results
            results[str(ofps)][subsample][str(sfps)] = repeated_results
            print(f"./results/{str(ofps)}/{FILE_NAME}",
                "completed:  ~",
                round(os.path.getsize(f"./results/{str(ofps)}_fps/{FILE_NAME}")/(2**20), 2),
                "MB"
            )

# Save test data into json
TEST_DATA_FILENAME = f"{ENCODING}_{datetime.datetime.isoformat(datetime.datetime.now(), timespec='seconds').replace(':','-')}.json"
with open(f"./results/{TEST_DATA_FILENAME}", 'w') as output:
    output.write(json.dumps(results, indent=2))

# Test ended, get a picture (60.png) for comparison (optional, as the video exists)
# for subsample in subsamples:
#     for fps in simulated_fps:
#         FILE_NAME = f"./results/{ENCODING}_{subsample}_{fps}fps.mp4"
#         output = av.open(FILE_NAME, "r")
#         frames = output.decode(video=0)
#         # apparently frames is a generator, and not a list, so have to loop through it
#         i = 0
#         for frame in frames:
#             if(i == 60/REAL_FPS*fps):
#                 frame.to_image().save(f"./results/h264_{subsample}_{fps}fps.png")
#             i+=1
#         output.close()

print("\n--------------test end----------------\n")
