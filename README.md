# bbb
Download and merge BBB video&amp;audio recordings in the browser with ffmpeg.wasm

Currently only some browsers are supported. Check [here](https://github.com/ffmpegwasm/ffmpeg.wasm) for more info


## Caveats 
The web version only works with desktop-shared recordings.


For slides-only presentations, BBB does not save the rendered video and it only provides metadata for the images, their timestamps, cursor positions and drawings. 

In order to create a video out of those, a complete re-render of images and drawings is required. 
You can do it locally using the `overengineered.py` script.
Eg:
```sh
python3 overengineered.py ORIGIN MEETING_ID FPS OUTPUT_FILE.mkv

# example

python3 overengineered.py "https://your-bbb-cluster.com" "xxxxxx-yyyyy" 5 output.mkv
```

The `FPS` arg can be usded to speed-up (or down) the rendering.

Requirements for the script:
- FFmpeg (system)
- OpenCV (python)
- numpy (python)
- urllib (python)
- tqdm (python)

## License
MIT