# profile-encode

Profile usage of time and space of various image encoders.

## PNG
The entire test takes a very long time run (~45min), and uses approximately 20MB of memory.
`compress_level` of 7-9 are not used because they take too long and do not finish within 1s/image.
`compress_level=0` is not used because that indicates no compression (raw ARGB format).
The results of the test are uploaded to the [Autonomy OneDrive](https://uofwaterloo-my.sharepoint.com/:f:/r/personal/uwarg_uwaterloo_ca/Documents/Subteam%20Folders/Autonomy/Encode%20Test%20Results%202024/PNG?csf=1&web=1&e=Fx69iE).

### Quick recap of test results
PNG seems to be a lossless encoding, the images seem to be identical pixel by pixel when displayed (i.e. after zooming in extensively on the landing pad). The compression seems to be at around 25-35% depending on the setting, and the tests were cut down to not include `compress_level` larger than 6 (as those are generally going to take more than 1 second per image). However, `compress_type=2` and `compress_type=3` are special in that they take constant time for all `compress_level` settings (at around 145ms/image).