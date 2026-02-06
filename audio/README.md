# Audio Files for Pepper Dances

Place your audio files here for each dance routine.

## Expected Files

| Dance | Filename | Notes |
|-------|----------|-------|
| Gangnam Style | `gangnam.wav` | The iconic K-pop track |
| Robot Dance | `robot.wav` | Electronic/robotic music |
| Cha-Cha | `chacha.wav` | Latin rhythm |
| Christmas | `christmas.wav` | Holiday music |
| Birthday | `birthday.wav` | Birthday celebration music |
| Kung Fu | `kungfu.wav` | Action/martial arts music |

## Supported Formats

- `.wav` (recommended - best compatibility)
- `.ogg`
- `.mp3`

## Audio Specifications

For best results with Pepper:
- **Sample Rate**: 22050 Hz or 44100 Hz
- **Channels**: Mono or Stereo
- **Bit Depth**: 16-bit
- **Duration**: Match dance duration (30-45 seconds)

## Uploading to Pepper

```bash
# Copy audio file to Pepper
scp gangnam.wav nao@<PEPPER_IP>:/home/nao/

# Or copy all audio files
scp *.wav nao@<PEPPER_IP>:/home/nao/
```

## Converting Audio

Use FFmpeg to convert audio to compatible format:

```bash
# Convert MP3 to WAV
ffmpeg -i input.mp3 -ar 22050 -ac 1 output.wav

# Trim to specific duration (e.g., 45 seconds)
ffmpeg -i input.mp3 -t 45 -ar 22050 -ac 1 output.wav
```

## Note

Audio files are not included in this repository due to copyright.
You'll need to provide your own music files.
