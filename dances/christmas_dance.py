#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
christmas_dance.py - 15-second Christmas Dance for Pepper

DESCRIPTION:
    A festive 15-second Christmas dance routine with synchronized audio.
    Pepper performs cheerful movements while playing Christmas music.

FEATURES:
    - Synchronized choreography (15 seconds)
    - Christmas music playback
    - Festive gestures and movements
    - LED eyes animation (optional)

USAGE:
    # On Pepper (via SSH):
    python christmas_dance.py --ip 127.0.0.1

    # From PC:
    python christmas_dance.py --ip <PEPPER_IP>

DEPENDENCIES:
    - NAOqi 2.5
    - Christmas audio file (optional - uses TTS if not available)
"""

import argparse
import qi
import time
import math
import threading


class ChristmasDance(object):
    """15-second Christmas dance choreography"""

    def __init__(self, session):
        """
        Initialize Christmas dance

        Args:
            session (qi.Session): Active NAOqi session
        """
        self.session = session

        # NAOqi services
        self.motion = session.service("ALMotion")
        self.posture = session.service("ALRobotPosture")
        self.animation = session.service("ALAnimationPlayer")
        self.tts = session.service("ALTextToSpeech")
        self.audio = session.service("ALAudioPlayer")
        self.leds = session.service("ALLeds")

        print("[ChristmasDance] Initialized")

    def setup(self):
        """Prepare Pepper for dance"""
        print("[ChristmasDance] Setting up...")

        # Wake up and stand
        self.motion.wakeUp()
        self.posture.goToPosture("Stand", 0.8)

        # Set movement speed parameters
        self.motion.setMoveArmsEnabled(True, True)

        # Disable external collision protection to allow spinning
        try:
            self.motion.setExternalCollisionProtectionEnabled("All", False)
            print("[ChristmasDance] Collision protection disabled for spinning")
        except Exception as e:
            print("[ChristmasDance] Warning: Could not disable collision protection: %s" % e)

        print("[ChristmasDance] Ready to dance!")

    def christmas_led_animation(self, duration=20):
        """
        Animate LEDs with Christmas colors during dance

        Args:
            duration (int): Duration in seconds
        """
        def led_loop():
            start_time = time.time()
            while time.time() - start_time < duration:
                # Red eyes
                self.leds.fadeRGB("FaceLeds", 1.0, 0.0, 0.0, 0.5)
                time.sleep(0.5)

                # Green eyes
                self.leds.fadeRGB("FaceLeds", 0.0, 1.0, 0.0, 0.5)
                time.sleep(0.5)

        # Run LED animation in background
        led_thread = threading.Thread(target=led_loop)
        led_thread.daemon = True
        led_thread.start()

    def play_christmas_music(self):
        """
        Play Christmas music (uses TTS as backup)
        Music volume is set to 80% to be slightly quieter than voice

        Tries multiple audio formats in order:
        1. Local audio directory (for testing)
        2. /home/nao/ directory (uploaded to Pepper)
        3. WAV (most reliable)
        4. OGG (good compression)
        5. MP3 (may not work on all systems)
        6. TTS fallback
        """
        print("[ChristmasDance] Playing Christmas music...")

        # Try different audio formats in different locations
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        audio_dir = os.path.join(script_dir, "audio")

        audio_files = [
            # Local audio directory (for testing from PC)
            os.path.join(audio_dir, "christmas.wav"),
            os.path.join(audio_dir, "christmas.ogg"),
            os.path.join(audio_dir, "christmas.mp3"),
            # Pepper's home directory (uploaded files)
            "/home/nao/christmas.wav",
            "/home/nao/christmas.ogg",
            "/home/nao/christmas.mp3",
        ]

        for audio_file in audio_files:
            try:
                print("[ChristmasDance] Trying to load: %s" % audio_file)
                file_id = self.audio.loadFile(audio_file)

                # Set music volume to 80% (0.8) - slightly quieter than voice
                self.audio.setVolume(file_id, 0.8)
                print("[ChristmasDance] Music volume set to 80%%")

                self.audio.play(file_id, _async=True)
                print("[ChristmasDance] ✓ Playing audio file: %s" % audio_file)
                return  # Success - exit function
            except Exception as e:
                print("[ChristmasDance] ✗ Could not load %s: %s" % (audio_file, e))
                continue  # Try next format

        # Fallback: Use TTS to sing
        print("[ChristmasDance] No audio file found, using TTS singing")
        self.tts.setParameter("speed", 80)
        self.tts.setParameter("pitchShift", 1.2)

        # Start singing in background
        def sing():
            lyrics = [
                "Jingle bells, jingle bells",
                "Jingle all the way",
                "Oh what fun it is to ride",
                "In a one horse open sleigh, hey!"
            ]
            for line in lyrics:
                self.tts.say(line)

        sing_thread = threading.Thread(target=sing)
        sing_thread.daemon = True
        sing_thread.start()

    def choreography(self):
        """
        Main ~20-second Christmas dance choreography

        Timeline:
        0-3s:    Introduction - Wave and head movements
        3-6s:    Arm celebrations - Both arms up and down
        6-10s:   Spin around with gestures (takes ~4s in practice)
        10-12s:  Wave patterns - Left and right
        12-15s:  Grand finale - Big gestures and bow
        15-20s:  Return to rest (arms down)
        """
        print("[ChristmasDance] Starting choreography...")

        # ================================================================
        # 0-3 seconds: INTRODUCTION - Wave Hello
        # ================================================================
        print("[ChristmasDance] Section 1: Introduction (0-3s)")

        # Wave right arm - friendly greeting
        self.motion.setAngles("RShoulderPitch", 0.5, 0.3)  # Raise arm
        self.motion.setAngles("RShoulderRoll", -0.3, 0.3)
        self.motion.setAngles("RElbowRoll", 1.5, 0.3)
        time.sleep(0.5)

        # Wave motion - 3 waves
        for i in range(3):
            self.motion.setAngles("RElbowYaw", 1.5, 0.8)
            self.motion.setAngles("HeadYaw", 0.3, 0.5)
            time.sleep(0.4)
            self.motion.setAngles("RElbowYaw", 0.5, 0.8)
            self.motion.setAngles("HeadYaw", -0.3, 0.5)
            time.sleep(0.4)

        # Reset head
        self.motion.setAngles("HeadYaw", 0.0, 0.3)

        # ================================================================
        # 3-6 seconds: ARM CELEBRATIONS - Joy and excitement
        # ================================================================
        print("[ChristmasDance] Section 2: Arm Celebrations (3-6s)")

        # Both arms up - celebration pose
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.0, 0.0], 0.4)
        self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.3, -0.3], 0.4)
        self.motion.setAngles(["LElbowRoll", "RElbowRoll"], [-1.5, 1.5], 0.4)
        time.sleep(0.8)

        # Pump arms up and down - 2 times
        for i in range(2):
            # Arms down
            self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [1.0, 1.0], 0.5)
            time.sleep(0.4)
            # Arms up
            self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.0, 0.0], 0.5)
            time.sleep(0.4)

        # ================================================================
        # 6-9 seconds: SPIN AROUND - Full rotation with gestures
        # ================================================================
        print("[ChristmasDance] Section 3: Spin Around (6-9s)")

        # Arms out to sides
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.5, 0.5], 0.3)
        self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.4, -0.4], 0.3)
        time.sleep(0.3)

        # Spin 360 degrees (one full rotation)
        print("[ChristmasDance] Spinning 360 degrees...")
        self.motion.moveTo(0.0, 0.0, math.pi * 2, _async=False)

        time.sleep(0.2)

        # ================================================================
        # 9-12 seconds: WAVE PATTERNS - Alternating arm waves
        # ================================================================
        print("[ChristmasDance] Section 4: Wave Patterns (9-12s)")

        # Alternating arm waves - left, right, left, right
        for i in range(4):
            if i % 2 == 0:
                # Left arm up
                self.motion.setAngles("LShoulderPitch", 0.2, 0.4)
                self.motion.setAngles("LShoulderRoll", 0.3, 0.4)
                # Right arm down
                self.motion.setAngles("RShoulderPitch", 1.5, 0.4)
            else:
                # Right arm up
                self.motion.setAngles("RShoulderPitch", 0.2, 0.4)
                self.motion.setAngles("RShoulderRoll", -0.3, 0.4)
                # Left arm down
                self.motion.setAngles("LShoulderPitch", 1.5, 0.4)

            # Head follows the raised arm
            head_angle = 0.3 if i % 2 == 0 else -0.3
            self.motion.setAngles("HeadYaw", head_angle, 0.4)
            time.sleep(0.4)

        # Reset head
        self.motion.setAngles("HeadYaw", 0.0, 0.3)

        # ================================================================
        # 12-15 seconds: GRAND FINALE - Big finish with bow
        # ================================================================
        print("[ChristmasDance] Section 5: Grand Finale (12-15s)")

        # Both arms spread wide - "ta-da" pose
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.0, 0.0], 0.3)
        self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.5, -0.5], 0.3)
        self.motion.setAngles(["LElbowRoll", "RElbowRoll"], [-1.5, 1.5], 0.3)
        time.sleep(1.0)

        # Bow - head down
        self.motion.setAngles("HeadPitch", 0.5, 0.4)
        time.sleep(0.8)

        # Head back up
        self.motion.setAngles("HeadPitch", 0.0, 0.4)
        time.sleep(0.5)

        # Return arms to rest position
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [1.5, 1.5], 0.4)
        self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.0, 0.0], 0.4)
        self.motion.setAngles(["LElbowRoll", "RElbowRoll"], [0.0, 0.0], 0.4)

        print("[ChristmasDance] Choreography complete!")

    def perform(self):
        """
        Perform the complete Christmas dance

        This coordinates music, LEDs, and choreography
        """
        print("\n" + "=" * 60)
        print("🎄 PEPPER'S CHRISTMAS DANCE 🎄")
        print("=" * 60)

        # Setup
        self.setup()

        # Announce
        self.tts.say("Merry Christmas! Let me dance for you!")
        time.sleep(0.5)

        # Start LED animation
        self.christmas_led_animation(duration=20)

        # Start music
        self.play_christmas_music()

        # Wait a moment for music to start
        time.sleep(0.5)

        # Perform choreography (~20 seconds)
        start_time = time.time()
        self.choreography()
        elapsed = time.time() - start_time

        print("\n[ChristmasDance] Dance duration: %.1f seconds" % elapsed)

        # Finish
        time.sleep(0.5)
        self.tts.say("Merry Christmas and Happy New Year!")

        # Reset LEDs to white
        self.leds.fadeRGB("FaceLeds", 1.0, 1.0, 1.0, 1.0)

        # Return to rest
        self.posture.goToPosture("Stand", 1.0)

        print("\n" + "=" * 60)
        print("🎄 CHRISTMAS DANCE COMPLETE! 🎄")
        print("=" * 60 + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Pepper's 15-second Christmas Dance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # On Pepper (via SSH)
  python christmas_dance.py --ip 127.0.0.1

  # From PC
  python christmas_dance.py --ip <PEPPER_IP>

Optional: Upload Christmas music to Pepper
  scp pepper_movement/audio/christmas.wav nao@<PEPPER_IP>:/home/nao/christmas.wav
        """
    )
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                       help="Pepper's IP address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=9559,
                       help="NAOqi port (default: 9559)")
    args = parser.parse_args()

    print("\n🎄 Pepper Christmas Dance 🎄")
    print("Connecting to Pepper at %s:%d..." % (args.ip, args.port))

    try:
        session = qi.Session()
        session.connect("tcp://%s:%d" % (args.ip, args.port))
        print("✓ Connected to Pepper!\n")
    except Exception as exc:
        print("✗ ERROR: Cannot connect to Pepper!")
        print("  Error: %s" % exc)
        print("\nTroubleshooting:")
        print("  - Check Pepper is powered on")
        print("  - Verify IP address: %s" % args.ip)
        print("  - Check network connectivity: ping %s" % args.ip)
        return 1

    # Create and perform dance
    try:
        dance = ChristmasDance(session)
        dance.perform()
        return 0
    except KeyboardInterrupt:
        print("\n\n[ChristmasDance] Dance interrupted by user")
        return 0
    except Exception as exc:
        print("\n✗ ERROR during dance: %s" % exc)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
