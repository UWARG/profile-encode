import av
import os

PATH = "./output_av.h264"
fh = open(PATH, "rb")
size = os.path.getsize(PATH)
print(size)

codec = av.CodecContext.create("h264", "r")

# Why does this consistently miss the last 2 frames?
while True:
    # Read 8 MB per time
    chunk = fh.read(1 << 23)

    packets = codec.parse(chunk)
    print(f"parsed {len(packets)} packets from {len(chunk)} bytes")

    for packet in packets:
        # The first 2 packets are not decoded, although the last 2 frames are not present
        print("   ", packet)
        frames = codec.decode(packet)
        for frame in frames:
            print("       ", frame)
            print("       ", frame.key_frame)
            frame.to_image().save(f"./parsed_images/{frame.index}.png")

    # Wait until end to stop so it will use the empty buffer to flush parser before exiting
    if not chunk:
        break

fh.close()