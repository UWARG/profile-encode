import av
import cv2
import datetime
import gc
import json
import os
import time
import numpy as np

images = [cv2.imread(f"./in_images/{i}.png") for i in range(0, 43)]
PATH = "output_av.mp4"

# Change this file to .h264 or .mp4, there's a big difference
with av.open(PATH, 'w') as container:
    # h264 has a video file container of mp4
    # h264 supports the following pixel formats: yuv420, yuv422, yuv444, MONO8 (grayscale)
    stream = container.add_stream("h264", '1', format=av.VideoFormat('yuv420p', width=2560, height=1440))
    stream.bit_rate = 1 << 23  # 8 MB
    codec = av.CodecContext.create("h264", "r")

    i = 0
    for img in images:
        # the input png images are in the pixel format bgr24
        frame = av.VideoFrame.from_ndarray(img, format='bgr24')
        print(frame.key_frame)  # Initially, all are key_frames

        # This encodes the input into h264 stream
        packets = stream.encode(frame)
        print(f"frame packet {i}:", packets)  # This seems to be outputting empty packets all the time, until it gets past frame 41
        # Then on frame 42, when there is a packet, it crashes because of apparently it cannot decode it, even though it's copied from the official docs?
        
        i+=1
        # # This reads the encoded frame and saves it as an image?
        #
        # for packet in packets:
        #     # None of the following work, all with same error of Invalid argumnet errno22
        #     out_frames = packet.decode()
        #     out_frames = codec.decode(packet)
        #     out_frames = stream.decode(packet)
        #     # This puts the h264 encoded data into the mp4 file
        #     container.mux(packet)

        #     print("   ", packet)
        #     # out_frames = stream.decode(packet)
        #     for f in out_frames:
        #         print("       ", f)
        #         f.to_image().save(f"./out_images/frame-{f.index}.png")
        
        container.mux(packets)

    # Flush
    flush_packet = stream.encode(None)
    container.mux(flush_packet)

print("\n")
print(round(os.path.getsize(PATH)/2**20, 2), "MB")
