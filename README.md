# profile-encode

Profile usage of time and space of various image encoders.

## PNG

The entire test takes a very long time run (~45min), and uses approximately 20MB of memory.
`compress_level` of 7-9 are not used because they take too long and do not finish within 1s/image.
`compress_level=0` is not used because that indicates no compression (raw ARGB format).
The results of the test are uploaded to the [Autonomy OneDrive](https://uofwaterloo-my.sharepoint.com/:f:/r/personal/uwarg_uwaterloo_ca/Documents/Subteam%20Folders/Autonomy/Encode%20Test%20Results%202024/PNG?csf=1&web=1&e=Fx69iE).

### Quick recap of test results

PNG seems to be a lossless encoding, the images seem to be identical pixel by pixel
when displayed (i.e. after zooming in extensively on the landing pad).
The compression seems to be at around 75-65% of its original size depending on the setting,
and the tests were cut down to not include `compress_level` larger than 6
(as those are generally going to take more than 1 second per image).
However, `compress_type=2` and `compress_type=3` are special in that they take
constant time for all `compress_level` settings (at around 145ms/image).

## AVIF

The entire test takes a very long time to run (~1h).
The `quality` setting is an integer from `0-100`, but only increments of 10 are tested.
Although `quality=-1` is a valid setting, it is the same as `quality=100`.
The `chroma` setting is for the chroma subsampling during the compressing process.
There are 3 settings: `420`, `422`, and `444`.
`quality=100` represents lossless quality, although it is only lossless in the case when `chroma=444`.
The results of the test are uploaded to the [Autonomy OneDrive](https://uofwaterloo-my.sharepoint.com/:f:/r/personal/uwarg_uwaterloo_ca/Documents/Subteam%20Folders/Autonomy/Encode%20Test%20Results%202024/AVIF?csf=1&web=1&e=mYWPr7).

### Quick recap of test results

There is not a very noticable difference between the different `chroma` settings.
When the `quality` is from 0 to 20, the picutre quality is bad.
When the `quality` is from 30 to 40, the picture quality is ok. It is noticable but not too bad.
When the `quality` is from 50 to 60, the picture quality is good. There is a difference, but it is small.
When the `quality` is from 70 to 90, the picture quality is great.
The difference between the original and the compressed version is almost identical.
