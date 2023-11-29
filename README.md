# profile-encode

Profile usage of time and space of various image encoders.

## Some first test notes
1. Generated mp4 or h264 file are very similar in size.
    1. My own test dataset of very different images have less of a compression than the drone test dataset, which have much more similar looking pictures.
    2. The re-prased images (png -> h264 -> png) has less size than the original png, but is still more than the h264/mp4 file
    3. The actual size of mp4 or 264 (or the packet size) is much more dependent on video length: if at 1fps there is basically no compression (see next section for test results)
2. When decoding a generated h264 file, it consistently does not have the last 2 frames, no matter input frame size or number of frames.
3. The first 41 frames consistently have no size, no matter if it was 2560x1440 (my own test pictures) or 1920x1200 (drone pictures).
4. It takes a significant amount of time to draw the image after it is encoded, although the encoding process takes very little time.
5. A generated packet cannot be decoded for some reason: Invalid argument \[Errno22\]
6. An example.h264 file downloaded from the internet could not be decoded by PyAV: Lots of errors, apparently they have different formats.
7. Simulated FPS basically has no effect on encoding speed or output size
    1. Note that the size result stored in the test result json is different than the actual file size, since that one skips the first 41 frames. Instead, there is a file_size attribute for that
8. More comments in the code are available for more details.

## Video size test results, just with different video lengths
For reference, all the pictures added together takes 980 MB (all units are scaled in 2^10 bytes)
### Variable fps
(video length is constant at 10 seconds, just like the real video)
Picture quality is good.
```
./results/variable_fps/h264_yuv420p_30fps.mp4 completed:  ~ 10.12 MB
./results/variable_fps/h264_yuv420p_15fps.mp4 completed:  ~ 10.29 MB
./results/variable_fps/h264_yuv420p_10fps.mp4 completed:  ~ 10.41 MB
./results/variable_fps/h264_yuv420p_5fps.mp4 completed:  ~ 10.7 MB
./results/variable_fps/h264_yuv420p_1fps.mp4 completed:  ~ 10.61 MB
./results/variable_fps/h264_yuv422p_30fps.mp4 completed:  ~ 10.12 MB
./results/variable_fps/h264_yuv422p_15fps.mp4 completed:  ~ 10.35 MB
./results/variable_fps/h264_yuv422p_10fps.mp4 completed:  ~ 10.42 MB
./results/variable_fps/h264_yuv422p_5fps.mp4 completed:  ~ 10.97 MB
./results/variable_fps/h264_yuv422p_1fps.mp4 completed:  ~ 11.17 MB
./results/variable_fps/h264_yuv444p_30fps.mp4 completed:  ~ 10.12 MB
./results/variable_fps/h264_yuv444p_15fps.mp4 completed:  ~ 10.33 MB
./results/variable_fps/h264_yuv444p_10fps.mp4 completed:  ~ 10.4 MB
./results/variable_fps/h264_yuv444p_5fps.mp4 completed:  ~ 10.93 MB
./results/variable_fps/h264_yuv444p_1fps.mp4 completed:  ~ 11.08 MB
```
### 30fps
Picutre quality is good (since this is basically the same as variable fps setting).
```
./results/30_fps/h264_yuv420p_30fps.mp4 completed:  ~ 10.12 MB
./results/30_fps/h264_yuv420p_15fps.mp4 completed:  ~ 5.19 MB
./results/30_fps/h264_yuv420p_10fps.mp4 completed:  ~ 3.53 MB
./results/30_fps/h264_yuv420p_5fps.mp4 completed:  ~ 1.89 MB
./results/30_fps/h264_yuv420p_1fps.mp4 completed:  ~ 0.57 MB
./results/30_fps/h264_yuv422p_30fps.mp4 completed:  ~ 10.12 MB
./results/30_fps/h264_yuv422p_15fps.mp4 completed:  ~ 5.25 MB
./results/30_fps/h264_yuv422p_10fps.mp4 completed:  ~ 3.55 MB
./results/30_fps/h264_yuv422p_5fps.mp4 completed:  ~ 1.93 MB
./results/30_fps/h264_yuv422p_1fps.mp4 completed:  ~ 0.57 MB
./results/30_fps/h264_yuv444p_30fps.mp4 completed:  ~ 10.12 MB
./results/30_fps/h264_yuv444p_15fps.mp4 completed:  ~ 5.24 MB
./results/30_fps/h264_yuv444p_10fps.mp4 completed:  ~ 3.55 MB
./results/30_fps/h264_yuv444p_5fps.mp4 completed:  ~ 1.91 MB
./results/30_fps/h264_yuv444p_1fps.mp4 completed:  ~ 0.57 MB
```
### 60fps
Picture quality is beginning to suffer (for the simulated 1fps)
The other ones look fine.
```
./results/60_fps/h264_yuv420p_30fps.mp4 completed:  ~ 5.07 MB
./results/60_fps/h264_yuv420p_15fps.mp4 completed:  ~ 2.63 MB
./results/60_fps/h264_yuv420p_10fps.mp4 completed:  ~ 1.79 MB
./results/60_fps/h264_yuv420p_5fps.mp4 completed:  ~ 0.96 MB
./results/60_fps/h264_yuv420p_1fps.mp4 completed:  ~ 0.25 MB
./results/60_fps/h264_yuv422p_30fps.mp4 completed:  ~ 5.08 MB
./results/60_fps/h264_yuv422p_15fps.mp4 completed:  ~ 2.67 MB
./results/60_fps/h264_yuv422p_10fps.mp4 completed:  ~ 1.81 MB
./results/60_fps/h264_yuv422p_5fps.mp4 completed:  ~ 0.97 MB
./results/60_fps/h264_yuv422p_1fps.mp4 completed:  ~ 0.25 MB
./results/60_fps/h264_yuv444p_30fps.mp4 completed:  ~ 5.08 MB
./results/60_fps/h264_yuv444p_15fps.mp4 completed:  ~ 2.66 MB
./results/60_fps/h264_yuv444p_10fps.mp4 completed:  ~ 1.81 MB
./results/60_fps/h264_yuv444p_5fps.mp4 completed:  ~ 0.97 MB
./results/60_fps/h264_yuv444p_1fps.mp4 completed:  ~ 0.25 MB
```
### 120fps
Picture quality is terrible. Visible squares, things are looking mismatched (for the simulated 1fps).
The simulated 30fps one still looks fine.
No longer able to see the H on the landing pad, it is just a big blur.
```
./results/120_fps/h264_yuv420p_30fps.mp4 completed:  ~ 2.51 MB
./results/120_fps/h264_yuv420p_15fps.mp4 completed:  ~ 1.31 MB
./results/120_fps/h264_yuv420p_10fps.mp4 completed:  ~ 0.9 MB
./results/120_fps/h264_yuv420p_5fps.mp4 completed:  ~ 0.47 MB
./results/120_fps/h264_yuv420p_1fps.mp4 completed:  ~ 0.11 MB
./results/120_fps/h264_yuv422p_30fps.mp4 completed:  ~ 2.53 MB
./results/120_fps/h264_yuv422p_15fps.mp4 completed:  ~ 1.33 MB
./results/120_fps/h264_yuv422p_10fps.mp4 completed:  ~ 0.91 MB
./results/120_fps/h264_yuv422p_5fps.mp4 completed:  ~ 0.47 MB
./results/120_fps/h264_yuv422p_1fps.mp4 completed:  ~ 0.11 MB
./results/120_fps/h264_yuv444p_30fps.mp4 completed:  ~ 2.53 MB
./results/120_fps/h264_yuv444p_15fps.mp4 completed:  ~ 1.33 MB
./results/120_fps/h264_yuv444p_10fps.mp4 completed:  ~ 0.91 MB
./results/120_fps/h264_yuv444p_5fps.mp4 completed:  ~ 0.47 MB
./results/120_fps/h264_yuv444p_1fps.mp4 completed:  ~ 0.11 MB
```
