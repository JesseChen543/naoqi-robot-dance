#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
birthday_dance.py - 35-second Happy Birthday Dance for Pepper

DESCRIPTION:
    A cheerful 35-second birthday celebration dance with synchronized audio.
    Pepper performs festive movements while playing Happy Birthday music,
    ending with clockwise and anticlockwise spins.

FEATURES:
    - Synchronized choreography (35 seconds)
    - Happy Birthday music playback
    - LED eyes animation (optional)
    - Celebratory gestures
    - Spinning finale (clockwise + anticlockwise)

USAGE:
    # On Pepper (via SSH):
    python birthday_dance.py --ip 127.0.0.1

    # From PC:
    python birthday_dance.py --ip <PEPPER_IP>

DEPENDENCIES:
    - NAOqi 2.5
    - Birthday audio file (optional - uses TTS if not available)
"""

import argparse
import qi
import time
import math
import threading


class BirthdayDance(object):
    """35-second Happy Birthday dance choreography with spinning finale"""

    def __init__(self, session):
        """
        Initialize Birthday dance

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

        print("[BirthdayDance] Initialized")

    def setup(self):
        """Prepare Pepper for dance"""
        print("[BirthdayDance] Setting up...")

        # Wake up and stand
        self.motion.wakeUp()
        self.posture.goToPosture("Stand", 0.8)

        # Set movement speed parameters
        self.motion.setMoveArmsEnabled(True, True)

        # Disable external collision protection to allow spinning
        try:
            self.motion.setExternalCollisionProtectionEnabled("All", False)
            print("[BirthdayDance] Collision protection disabled for spinning")
        except Exception as e:
            print("[BirthdayDance] Warning: Could not disable collision protection: %s" % e)

        print("[BirthdayDance] Ready to dance!")

    def birthday_led_animation(self, duration=35):
        """
        Animate LEDs with birthday colors during dance

        Args:
            duration (int): Duration in seconds
        """
        def led_loop():
            start_time = time.time()
            colors = [
                (1.0, 0.0, 1.0),  # Magenta
                (1.0, 1.0, 0.0),  # Yellow
                (0.0, 1.0, 1.0),  # Cyan
                (1.0, 0.5, 0.0),  # Orange
            ]
            color_index = 0

            while time.time() - start_time < duration:
                color = colors[color_index % len(colors)]
                self.leds.fadeRGB("FaceLeds", color[0], color[1], color[2], 0.5)
                time.sleep(0.5)
                color_index += 1

        # Run LED animation in background
        led_thread = threading.Thread(target=led_loop)
        led_thread.daemon = True
        led_thread.start()

    def play_birthday_music(self):
        """
        Play Happy Birthday music (uses TTS as backup)
        Music volume is set to 80% to be slightly quieter than voice
        """
        print("[BirthdayDance] Playing birthday music...")

        # Try different audio formats in different locations
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        audio_dir = os.path.join(script_dir, "audio")

        audio_files = [
            # Local audio directory (for testing from PC)
            os.path.join(audio_dir, "birthday.wav"),
            os.path.join(audio_dir, "birthday.ogg"),
            os.path.join(audio_dir, "birthday.mp3"),
            # Pepper's home directory (uploaded files)
            "/home/nao/birthday.wav",
            "/home/nao/birthday.ogg",
            "/home/nao/birthday.mp3",
        ]

        for audio_file in audio_files:
            try:
                print("[BirthdayDance] Trying to load: %s" % audio_file)
                file_id = self.audio.loadFile(audio_file)

                # Set music volume to 80% (0.8) - slightly quieter than voice
                self.audio.setVolume(file_id, 0.8)
                print("[BirthdayDance] Music volume set to 80%%")

                self.audio.play(file_id, _async=True)
                print("[BirthdayDance] Playing audio file: %s" % audio_file)
                return  # Success - exit function
            except Exception as e:
                print("[BirthdayDance] Could not load %s: %s" % (audio_file, e))
                continue  # Try next format

        # Fallback: Use TTS to sing
        print("[BirthdayDance] No audio file found, using TTS singing")
        self.tts.setParameter("speed", 70)
        self.tts.setParameter("pitchShift", 1.3)

        # Start singing in background
        def sing():
            lyrics = [
                "Happy birthday to you",
                "Happy birthday to you",
                "Happy birthday dear friend",
                "Happy birthday to you"
            ]
            for line in lyrics:
                self.tts.say(line)

        sing_thread = threading.Thread(target=sing)
        sing_thread.daemon = True
        sing_thread.start()

    def choreography(self):
        """
        Main ~35-second Birthday dance choreography

        Timeline:
        0-5s:    Introduction - Excited wave and clapping
        5-10s:   Celebration - Jump and cheer motions
        10-15s:  Party time - Side-to-side dance moves
        15-20s:  Cake time - Blow candles gesture
        20-25s:  Gift opening - Surprise and joy
        25-30s:  Grand finale - Victory pose and bow
        30-35s:  Spinning finale - Clockwise then anticlockwise spins
        """
        print("[BirthdayDance] Starting choreography...")

        # ================================================================
        # 0-5 seconds: INTRODUCTION - Excited wave and clapping
        # ================================================================
        print("[BirthdayDance] Section 1: Introduction (0-5s)")

        # Both arms wave excitedly
        for i in range(3):
            self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.5, 0.5], 0.5)
            self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.3, -0.3], 0.5)
            self.motion.setAngles(["LElbowRoll", "RElbowRoll"], [-1.5, 1.5], 0.5)
            time.sleep(0.4)
            self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [1.0, 1.0], 0.5)
            time.sleep(0.4)

        # Clapping motion
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.8, 0.8], 0.3)
        self.motion.setAngles(["LElbowRoll", "RElbowRoll"], [-0.5, 0.5], 0.3)
        time.sleep(0.5)

        # ================================================================
        # 5-10 seconds: CELEBRATION - Jump and cheer motions
        # ================================================================
        print("[BirthdayDance] Section 2: Celebration (5-10s)")

        # Arms raise up high (cheering)
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.0, 0.0], 0.4)
        self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.4, -0.4], 0.4)
        self.motion.setAngles(["LElbowRoll", "RElbowRoll"], [-1.5, 1.5], 0.4)
        time.sleep(1.0)

        # Pump arms 3 times
        for i in range(3):
            self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.3, 0.3], 0.5)
            time.sleep(0.4)
            self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.0, 0.0], 0.5)
            time.sleep(0.4)

        # ================================================================
        # 10-15 seconds: PARTY TIME - Side-to-side dance
        # ================================================================
        print("[BirthdayDance] Section 3: Party Time (10-15s)")

        # Side-to-side hip movement with arm waves
        for i in range(4):
            if i % 2 == 0:
                # Lean left, right arm up
                self.motion.setAngles("RShoulderPitch", 0.2, 0.4)
                self.motion.setAngles("RElbowRoll", 1.5, 0.4)
                self.motion.setAngles("LShoulderPitch", 1.2, 0.4)
                self.motion.setAngles("HeadYaw", 0.4, 0.4)
            else:
                # Lean right, left arm up
                self.motion.setAngles("LShoulderPitch", 0.2, 0.4)
                self.motion.setAngles("LElbowRoll", -1.5, 0.4)
                self.motion.setAngles("RShoulderPitch", 1.2, 0.4)
                self.motion.setAngles("HeadYaw", -0.4, 0.4)
            time.sleep(0.6)

        # Reset head
        self.motion.setAngles("HeadYaw", 0.0, 0.3)

        # ================================================================
        # 15-20 seconds: CAKE TIME - Blow candles gesture
        # ================================================================
        print("[BirthdayDance] Section 4: Cake Time (15-20s)")

        # Bring hands together (holding imaginary cake)
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [1.0, 1.0], 0.4)
        self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.2, -0.2], 0.4)
        self.motion.setAngles(["LElbowRoll", "RElbowRoll"], [-1.0, 1.0], 0.4)
        time.sleep(1.5)

        # Deep breath in (head back slightly)
        self.motion.setAngles("HeadPitch", -0.2, 0.3)
        time.sleep(1.0)

        # Blow candles (head forward)
        self.motion.setAngles("HeadPitch", 0.3, 0.3)
        time.sleep(1.5)

        # Reset head
        self.motion.setAngles("HeadPitch", 0.0, 0.3)

        # ================================================================
        # 20-25 seconds: GIFT OPENING - Surprise and joy
        # ================================================================
        print("[BirthdayDance] Section 5: Gift Opening (20-25s)")

        # Opening gift motion (arms spread wide)
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.5, 0.5], 0.4)
        self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.5, -0.5], 0.4)
        time.sleep(0.8)

        # Surprise! (hands to face)
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.3, 0.3], 0.5)
        self.motion.setAngles(["LElbowRoll", "RElbowRoll"], [-1.0, 1.0], 0.5)
        time.sleep(1.0)

        # Joy! (arms up)
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.0, 0.0], 0.4)
        self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.4, -0.4], 0.4)
        self.motion.setAngles(["LElbowRoll", "RElbowRoll"], [-1.5, 1.5], 0.4)
        time.sleep(1.5)

        # ================================================================
        # 25-30 seconds: GRAND FINALE - Victory pose and bow
        # ================================================================
        print("[BirthdayDance] Section 6: Grand Finale (25-30s)")

        # Victory pose (both arms up in V)
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [-0.2, -0.2], 0.3)
        self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.5, -0.5], 0.3)
        self.motion.setAngles(["LElbowRoll", "RElbowRoll"], [-1.5, 1.5], 0.3)
        time.sleep(1.5)

        # Bow
        self.motion.setAngles("HeadPitch", 0.5, 0.4)
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [1.2, 1.2], 0.4)
        time.sleep(1.0)

        # Head back up
        self.motion.setAngles("HeadPitch", 0.0, 0.4)

        # Return arms to rest
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [1.5, 1.5], 0.4)
        self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.0, 0.0], 0.4)
        self.motion.setAngles(["LElbowRoll", "RElbowRoll"], [0.0, 0.0], 0.4)
        time.sleep(0.5)

        # ================================================================
        # 30-35 seconds: SPINNING FINALE - Clockwise then anticlockwise
        # ================================================================
        print("[BirthdayDance] Section 7: Spinning Finale (30-35s)")

        # Clockwise spin (360 degrees = 2 * pi radians)
        print("[BirthdayDance] Spinning clockwise...")
        self.motion.moveTo(0.0, 0.0, 2 * math.pi, _async=False)
        time.sleep(0.3)

        # Anticlockwise spin (negative angle)
        print("[BirthdayDance] Spinning anticlockwise...")
        self.motion.moveTo(0.0, 0.0, -2 * math.pi, _async=False)
        time.sleep(0.3)

        print("[BirthdayDance] Choreography complete!")

    def perform(self):
        """
        Perform the complete Birthday dance

        This coordinates music, LEDs, and choreography
        """
        print("\n" + "=" * 60)
        print("🎂 PEPPER'S BIRTHDAY DANCE 🎂")
        print("=" * 60)

        # Setup
        self.setup()

        # Announce
        self.tts.say("Happy Birthday! Let me celebrate with you!")
        time.sleep(0.5)

        # Start LED animation
        self.birthday_led_animation(duration=40)

        # Start music
        self.play_birthday_music()

        # Wait a moment for music to start
        time.sleep(0.5)

        # Perform choreography (~30 seconds)
        start_time = time.time()
        self.choreography()
        elapsed = time.time() - start_time

        print("\n[BirthdayDance] Dance duration: %.1f seconds" % elapsed)

        # Finish
        time.sleep(0.5)
        self.tts.say("I hope you have the best birthday ever!")

        # Reset LEDs to white
        self.leds.fadeRGB("FaceLeds", 1.0, 1.0, 1.0, 1.0)

        # Return to rest
        self.posture.goToPosture("Stand", 1.0)

        print("\n" + "=" * 60)
        print("🎂 BIRTHDAY DANCE COMPLETE! 🎂")
        print("=" * 60 + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Pepper's 35-second Birthday Dance with spinning finale",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # On Pepper (via SSH)
  python birthday_dance.py --ip 127.0.0.1

  # From PC
  python birthday_dance.py --ip <PEPPER_IP>

Optional: Upload birthday music to Pepper
  scp pepper_movement/audio/birthday.wav nao@<PEPPER_IP>:/home/nao/birthday.wav
        """
    )
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                       help="Pepper's IP address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=9559,
                       help="NAOqi port (default: 9559)")
    args = parser.parse_args()

    print("\n🎂 Pepper Birthday Dance 🎂")
    print("Connecting to Pepper at %s:%d..." % (args.ip, args.port))

    try:
        session = qi.Session()
        session.connect("tcp://%s:%d" % (args.ip, args.port))
        print("Connected to Pepper!\n")
    except Exception as exc:
        print("ERROR: Cannot connect to Pepper!")
        print("  Error: %s" % exc)
        print("\nTroubleshooting:")
        print("  - Check Pepper is powered on")
        print("  - Verify IP address: %s" % args.ip)
        print("  - Check network connectivity: ping %s" % args.ip)
        return 1

    # Create and perform dance
    try:
        dance = BirthdayDance(session)
        dance.perform()
        return 0
    except KeyboardInterrupt:
        print("\n\n[BirthdayDance] Dance interrupted by user")
        return 0
    except Exception as exc:
        print("\nERROR during dance: %s" % exc)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
