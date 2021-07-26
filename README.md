# BBB
Download and merge BBB video&amp;audio recordings in the browser with ffmpeg.wasm: https://bbb-merger.netlify.app

The web version uses experimental APIs currently unsupported by many browsers. Check [here](https://github.com/ffmpegwasm/ffmpeg.wasm) for more info.

A telegram bot is also available here: [@bbb_renderer_bot](https://t.me/bbb_renderer_bot)

Example usage:
`/render https://bbb-cluster.example.it/playback/presentation/2.0/playback.html?meetingId=xxx`

## Caveats 
The web version only works with desktop-shared recordings.

For slides-only presentations, BBB does not save the rendered video and it only provides metadata for the images, their timestamps, cursor positions and drawings. 

In order to create a video out of those, a complete re-render of images and drawings is required. 
You can either use our telegram bot or render the recordings locally using the `/render/app/overengineered.py` script.
Eg:
```sh
python3 overengineered.py ORIGIN MEETING_ID FPS OUTPUT_FILE.mkv

# example

python3 overengineered.py "https://your-bbb-cluster.com" "xxxxxx-yyyyy" 5 output.mkv
```

The `FPS` arg can be used to speed-up (or down) the rendering.

Requirements for the script:
- FFmpeg and OpenCV

Check `render/Dockerfile` for more information on requirements

## Support
If you like this project, please consider supporting it:
- BTC: 1Fydx8Nh3czBgn4gqQ7mrkFd3aLWYXSdfN
- ETH: 0x6c9f6fe637856802ae25bc486219ff8f36925838
- DOGE: DLse4LLcZsifBxLWpRWrgu8rsn9zBrVfDA

## License
GPL-3.0 License
