# Pepper Robot Dance Collection

A collection of fun, ready-to-use dance routines for **SoftBank Pepper Robot** (NAOqi 2.5). Make your Pepper robot dance Gangnam Style, do the Cha-Cha, perform a Robot dance, and more!

## Features

- **6 Complete Dance Routines** - Ready to run with a single command
- **LED Synchronization** - Colorful light effects synced to movements
- **Audio Support** - Optional music playback during dances
- **Standalone Scripts** - Each dance works independently
- **Well-Documented** - Clear code with detailed choreography notes

## Available Dances

| Dance | Duration | Description |
|-------|----------|-------------|
| **Gangnam Style** | ~45s | PSY's iconic horse-riding dance with lasso arms |
| **Robot Dance** | ~30s | Comedic mechanical robot movements with glitches |
| **Cha-Cha** | ~40s | Latin dance with hip movements and arm styling |
| **Christmas Dance** | ~45s | Festive holiday dance with cheerful movements |
| **Birthday Dance** | ~40s | Celebration dance perfect for parties |
| **Kung Fu Dance** | ~35s | Martial arts inspired movements |

## Quick Start

### Prerequisites

- **Pepper Robot** with NAOqi 2.5+
- **Python 2.7** (NAOqi SDK requirement)
- Network connection to Pepper

### Run a Dance

```bash
# On Pepper (via SSH)
python gangnam_dance.py --ip 127.0.0.1

# From PC (replace with your Pepper's IP)
python gangnam_dance.py --ip 192.168.0.135
```

### Available Dance Scripts

```bash
python gangnam_dance.py --ip <PEPPER_IP>    # Gangnam Style
python robot_dance.py --ip <PEPPER_IP>       # Robot Dance
python chacha_dance.py --ip <PEPPER_IP>      # Cha-Cha
python christmas_dance.py --ip <PEPPER_IP>   # Christmas
python birthday_dance.py --ip <PEPPER_IP>    # Birthday
python kungfu_dance.py --ip <PEPPER_IP>      # Kung Fu
```

## Deploying to Pepper

You can run dances either **from your PC** (remote control) or **directly on Pepper** (standalone). Running on Pepper is recommended for better performance and reliability.

### Option 1: Upload and Run on Pepper (Recommended)

```bash
# 1. Upload the entire dance package to Pepper
scp -r dances/ nao@<PEPPER_IP>:/home/nao/pepper_dance/

# 2. SSH into Pepper
ssh nao@<PEPPER_IP>
# Default password: nao

# 3. Run a dance on Pepper
cd /home/nao/pepper_dance
python gangnam_dance.py --ip 127.0.0.1
```

### Option 2: Upload Individual Dance Files

```bash
# Upload just one dance
scp dances/gangnam_dance.py nao@<PEPPER_IP>:/home/nao/

# SSH and run
ssh nao@<PEPPER_IP>
python gangnam_dance.py --ip 127.0.0.1
```

### Option 3: Run from PC (Remote Control)

If you have NAOqi SDK installed on your PC:

```bash
# Set up NAOqi SDK path (Linux/Mac)
export PYTHONPATH=/path/to/naoqi-sdk/lib/python2.7/site-packages:$PYTHONPATH

# Set up NAOqi SDK path (Windows)
set PYTHONPATH=C:\path\to\naoqi-sdk\lib\python2.7\site-packages;%PYTHONPATH%

# Run dance remotely (replace with your Pepper's IP)
cd dances
python gangnam_dance.py --ip 192.168.0.135
```

### Complete Deployment (Dance + Music)

For the full experience with music:

```bash
# 1. Upload dance scripts to Pepper
scp -r dances/ nao@<PEPPER_IP>:/home/nao/pepper_dance/

# 2. Upload music files to Pepper
scp audio/*.wav nao@<PEPPER_IP>:/home/nao/

# 3. SSH and run
ssh nao@<PEPPER_IP>
cd /home/nao/pepper_dance
python gangnam_dance.py --ip 127.0.0.1
```

### Verify Upload

```bash
# Check files on Pepper
ssh nao@<PEPPER_IP>
ls -la /home/nao/pepper_dance/
ls -la /home/nao/*.wav
```

## Project Structure

```
pepper_dance/
├── dances/
│   ├── gangnam_dance.py      # Gangnam Style dance
│   ├── robot_dance.py        # Mechanical robot dance
│   ├── chacha_dance.py       # Cha-Cha Latin dance
│   ├── christmas_dance.py    # Holiday dance
│   ├── birthday_dance.py     # Birthday celebration
│   └── kungfu_dance.py       # Martial arts dance
├── core/
│   ├── base_motion.py        # Base motion utilities
│   └── __init__.py
├── utils/
│   ├── list_animations.py    # List Pepper's animations
│   ├── animations.py         # Animation discovery utilities
│   └── __init__.py
├── audio/                    # Optional music files
│   └── README.md
├── examples/
│   └── custom_dance.py       # Template for custom dances
├── requirements.txt
└── README.md
```

## Adding Music

Each dance can play background music. Upload audio files to Pepper:

```bash
# Upload music to Pepper
scp audio/gangnam.wav nao@<PEPPER_IP>:/home/nao/

# Supported formats: .wav, .ogg, .mp3
```

Or place audio files in the `audio/` directory when running from PC.

## Listing Available Animations

Pepper has many built-in animations. Use the utility to discover them:

```bash
python utils/list_animations.py --ip <PEPPER_IP>
python utils/list_animations.py --ip <PEPPER_IP> --show-tags
python utils/list_animations.py --ip <PEPPER_IP> --by-category
```

## Creating Custom Dances

Use the template to create your own dances:

```python
from core.base_motion import connect_to_pepper

session = connect_to_pepper(ip="192.168.0.135")
motion = session.service("ALMotion")
posture = session.service("ALRobotPosture")

# Wake up and stand
motion.wakeUp()
posture.goToPosture("Stand", 0.8)

# Your choreography here
motion.setAngles("LShoulderPitch", 0.5, 0.3)
# ... more movements
```

See `examples/custom_dance.py` for a complete template.

## API Reference

### Core Motion Methods

```python
from core.base_motion import BaseMotion, connect_to_pepper

# Connect to Pepper
session = connect_to_pepper(ip="192.168.0.135", port=9559)

# Create motion controller
controller = BaseMotion(session)

# Basic controls
controller.wake_up()           # Enable motors
controller.rest()              # Disable motors
controller.go_to_posture("Stand", 1.0)  # Change posture
controller.emergency_stop()    # Stop all movement
```

### Dance Class Pattern

All dances follow this pattern:

```python
class MyDance(object):
    def __init__(self, session):
        self.motion = session.service("ALMotion")
        self.posture = session.service("ALRobotPosture")
        self.tts = session.service("ALTextToSpeech")
        self.leds = session.service("ALLeds")
        self.audio = session.service("ALAudioPlayer")

    def setup(self):
        """Prepare robot for dancing"""
        self.motion.wakeUp()
        self.posture.goToPosture("Stand", 0.8)

    def choreography(self):
        """Main dance movements"""
        # Your choreography
        pass

    def perform(self):
        """Execute the complete dance"""
        self.setup()
        self.choreography()
```

## Troubleshooting

### "Cannot connect to Pepper"

- Verify Pepper is powered on and on the same network
- Check IP address: `ping <PEPPER_IP>`
- Ensure NAOqi is running on port 9559

### "ModuleNotFoundError: No module named 'qi'"

- Use Python 2.7 (NAOqi SDK requirement)
- Add NAOqi SDK to PYTHONPATH:
  ```bash
  export PYTHONPATH=/path/to/naoqi-sdk/lib/python2.7/site-packages
  ```

### "Movement fails or is blocked"

- Robot may have collision protection enabled
- Check battery level (low battery affects movement)
- Ensure robot is in standing posture before dancing

## Safety Notes

- Ensure clear space around Pepper (2m radius recommended)
- Dances temporarily disable collision protection for fluid movement
- Always supervise Pepper during dance routines
- Press chest button to emergency stop if needed

## Related Projects

This is a standalone dance module extracted from the [Wonderbyte Pepper Project](https://github.com/JesseChen543/pepper), a comprehensive toolkit for Pepper robot development including:

- Voice/TTS control
- Camera streaming
- Web-based control interface
- And more!

## Keywords

`pepper robot` `softbank pepper` `naoqi` `robot dance` `pepper dance` `gangnam style robot` `robot choreography` `humanoid robot` `social robot` `pepper animation` `robot entertainment` `python robotics` `naoqi python`

## Disclaimer

**Audio files included in this repository are provided for educational and personal use only.** The maintainers of this repository are not responsible for any copyright infringement. If you are the copyright holder of any audio file and wish to have it removed, please open an issue.

Users are responsible for ensuring their use of the audio files complies with applicable copyright laws in their jurisdiction.

## License

MIT License - Feel free to use, modify, and share!

The code in this repository is licensed under MIT. Audio files may be subject to separate copyright terms.

