#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
chacha_dance.py - Cha Cha Slide Dance for Pepper

DESCRIPTION:
    A fun 60-second Cha Cha Slide dance where Pepper calls out the moves
    and performs them! Slide to the left, slide to the right, criss cross!

FEATURES:
    - Pepper calls out dance instructions
    - Moves left, right, hops, stomps
    - Criss cross arm movements
    - Clapping
    - LED effects synced to moves

CHOREOGRAPHY:
    - Slide to the left
    - Slide to the right
    - Criss cross
    - Cha cha real smooth
    - Stomp
    - Clap
    - Hop

USAGE:
    # On Pepper (via SSH):
    python chacha_dance.py --ip 127.0.0.1

    # From PC:
    python chacha_dance.py --ip 192.168.0.135

DEPENDENCIES:
    - NAOqi 2.5
    - Cha Cha Slide audio file

AUDIO FILE:
    Upload chacha.wav to /home/nao/ or place in pepper_movement/audio/
"""

import argparse
import qi
import time
import math
import threading


class ChaChaSlide(object):
    """60-second Cha Cha Slide dance with call-outs"""

    def __init__(self, session):
        """
        Initialize Cha Cha Slide dance

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

        print("[ChaChaSlide] Initialized")

    def setup(self):
        """Prepare Pepper for dance"""
        print("[ChaChaSlide] Setting up...")

        # Wake up and stand
        self.motion.wakeUp()
        self.posture.goToPosture("Stand", 0.8)

        # Set movement speed parameters
        self.motion.setMoveArmsEnabled(True, True)

        # Disable external collision protection for dancing
        try:
            self.motion.setExternalCollisionProtectionEnabled("All", False)
            print("[ChaChaSlide] Collision protection disabled for dancing")
        except Exception as e:
            print("[ChaChaSlide] Warning: Could not disable collision protection: %s" % e)

        print("[ChaChaSlide] Ready to dance!")

    def chacha_led_animation(self, duration=55):
        """
        Animate LEDs with party colors during dance

        Args:
            duration (int): Duration in seconds
        """
        def led_loop():
            start_time = time.time()
            colors = [
                (1.0, 0.5, 0.0),  # Orange
                (1.0, 1.0, 0.0),  # Yellow
                (0.0, 1.0, 0.0),  # Green
                (0.0, 1.0, 1.0),  # Cyan
                (1.0, 0.0, 1.0),  # Magenta
            ]
            color_index = 0

            while time.time() - start_time < duration:
                color = colors[color_index % len(colors)]
                self.leds.fadeRGB("FaceLeds", color[0], color[1], color[2], 0.2)
                self.leds.fadeRGB("ChestLeds", color[0], color[1], color[2], 0.2)
                self.leds.fadeRGB("EarLeds", color[0], color[1], color[2], 0.2)
                time.sleep(0.5)
                color_index += 1

        led_thread = threading.Thread(target=led_loop)
        led_thread.daemon = True
        led_thread.start()

    def play_chacha_music(self):
        """Play Cha Cha Slide music at 40% volume"""
        print("[ChaChaSlide] Playing Cha Cha Slide music...")

        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        audio_dir = os.path.join(script_dir, "audio")

        audio_files = [
            os.path.join(audio_dir, "chacha.wav"),
            os.path.join(audio_dir, "chacha.ogg"),
            os.path.join(audio_dir, "chacha.mp3"),
            "/home/nao/chacha.wav",
            "/home/nao/chacha.ogg",
            "/home/nao/chacha.mp3",
        ]

        for audio_file in audio_files:
            try:
                print("[ChaChaSlide] Trying to load: %s" % audio_file)
                file_id = self.audio.loadFile(audio_file)
                self.audio.setVolume(file_id, 0.4)
                print("[ChaChaSlide] Music volume set to 40%%")
                self.audio.play(file_id, _async=True)
                print("[ChaChaSlide] Playing audio file: %s" % audio_file)
                return
            except Exception as e:
                print("[ChaChaSlide] Could not load %s: %s" % (audio_file, e))
                continue

        print("[ChaChaSlide] No audio file found, dancing without music")

    def slide_left(self):
        """Slide to the left"""
        self.tts.say("\\rspd=120\\Slide to the left!")
        # Move left
        self.motion.moveTo(0, 0.15, 0)
        time.sleep(0.3)

    def slide_right(self):
        """Slide to the right"""
        self.tts.say("\\rspd=120\\Slide to the right!")
        # Move right
        self.motion.moveTo(0, -0.15, 0)
        time.sleep(0.3)

    def criss_cross(self):
        """Criss cross arms"""
        self.tts.say("\\rspd=120\\Criss cross!")
        # Cross arms in front
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.5, 0.5], 0.5)
        self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [-0.3, 0.3], 0.5)
        self.motion.setAngles(["LElbowRoll", "RElbowRoll"], [-0.5, 0.5], 0.5)
        time.sleep(0.4)
        # Uncross
        self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.3, -0.3], 0.5)
        time.sleep(0.4)

    def cha_cha(self):
        """Cha cha real smooth"""
        self.tts.say("\\rspd=110\\Cha cha real smooth!")
        # Hip sway motion with arms
        for i in range(4):
            self.motion.setAngles("HipRoll", 0.1, 0.5)
            self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.2, -0.4], 0.5)
            time.sleep(0.3)
            self.motion.setAngles("HipRoll", -0.1, 0.5)
            self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.4, -0.2], 0.5)
            time.sleep(0.3)
        self.motion.setAngles("HipRoll", 0.0, 0.3)

    def stomp(self):
        """Stomp your feet"""
        self.tts.say("\\rspd=120\\Stomp!")
        # Simulate stomp with arm motion (Pepper can't actually stomp)
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.8, 0.8], 0.8)
        time.sleep(0.2)
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [1.2, 1.2], 0.8)
        time.sleep(0.3)

    def clap(self):
        """Clap your hands"""
        self.tts.say("\\rspd=120\\Clap your hands!")
        # Bring hands together
        for i in range(3):
            # Arms out
            self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.5, 0.5], 0.8)
            self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.3, -0.3], 0.8)
            self.motion.setAngles(["LElbowRoll", "RElbowRoll"], [0.0, 0.0], 0.8)
            time.sleep(0.2)
            # Arms together (clap)
            self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [-0.1, 0.1], 0.8)
            time.sleep(0.2)

    def hop(self):
        """Hop (simulated with bounce motion)"""
        self.tts.say("\\rspd=120\\Hop!")
        # Simulate hop with crouch and stand
        self.motion.setAngles("HipPitch", -0.1, 0.8)
        self.motion.setAngles("KneePitch", 0.1, 0.8)
        time.sleep(0.15)
        self.motion.setAngles("HipPitch", 0.0, 0.8)
        self.motion.setAngles("KneePitch", 0.0, 0.8)
        time.sleep(0.15)

    def turn_it_out(self):
        """Turn it out - spin around"""
        self.tts.say("\\rspd=120\\Turn it out!")
        # Turn 180 degrees
        self.motion.moveTo(0, 0, 1.57)
        time.sleep(0.5)

    def reverse(self):
        """Reverse reverse"""
        self.tts.say("\\rspd=120\\Reverse! Reverse!")
        # Move backward
        self.motion.moveTo(-0.1, 0, 0)
        time.sleep(0.3)
        self.motion.moveTo(-0.1, 0, 0)
        time.sleep(0.3)

    def freeze(self):
        """Everybody freeze"""
        self.tts.say("\\rspd=100\\Everybody freeze!")
        # Hold still with arms up
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.0, 0.0], 0.3)
        self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.5, -0.5], 0.3)
        time.sleep(2.0)

    def hands_on_knees(self):
        """Hands on your knees"""
        self.tts.say("\\rspd=120\\Hands on your knees!")
        # Bend forward with arms down
        self.motion.setAngles("HeadPitch", 0.3, 0.3)
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [1.0, 1.0], 0.3)
        self.motion.setAngles(["LElbowRoll", "RElbowRoll"], [-0.5, 0.5], 0.3)
        time.sleep(1.0)
        # Stand back up
        self.motion.setAngles("HeadPitch", 0.0, 0.3)
        self.posture.goToPosture("Stand", 0.5)

    def choreography(self):
        """
        Main 60-second Cha Cha Slide choreography
        """
        print("[ChaChaSlide] Starting choreography...")

        # ================================================================
        # INTRO
        # ================================================================
        print("[ChaChaSlide] Intro")
        time.sleep(1.0)

        # ================================================================
        # ROUND 1 - Slides and Criss Cross
        # ================================================================
        print("[ChaChaSlide] Round 1")

        self.slide_left()
        self.slide_right()
        self.criss_cross()
        self.cha_cha()

        # ================================================================
        # ROUND 2 - Clap, Stomp, Hop
        # ================================================================
        print("[ChaChaSlide] Round 2")

        self.clap()
        self.stomp()
        self.hop()
        self.hop()

        # ================================================================
        # ROUND 3 - Turn and Reverse
        # ================================================================
        print("[ChaChaSlide] Round 3")

        self.turn_it_out()
        self.slide_left()
        self.slide_right()
        self.reverse()

        # ================================================================
        # FINALE - Hands on knees and Freeze
        # ================================================================
        print("[ChaChaSlide] Finale")

        self.hands_on_knees()
        self.criss_cross()
        self.freeze()

        print("[ChaChaSlide] Choreography complete!")

    def perform(self):
        """
        Perform the complete Cha Cha Slide dance
        """
        print("\n" + "=" * 60)
        print("PEPPER'S CHA CHA SLIDE")
        print("=" * 60)

        # Setup
        self.setup()

        # Announce
        self.tts.say("Let's do the Cha Cha Slide!")
        time.sleep(0.5)

        # Start LED animation
        self.chacha_led_animation(duration=55)

        # Start music
        self.play_chacha_music()

        # Wait a moment for music to start
        time.sleep(0.5)

        # Perform choreography
        start_time = time.time()
        self.choreography()
        elapsed = time.time() - start_time

        print("\n[ChaChaSlide] Dance duration: %.1f seconds" % elapsed)

        # Reset LEDs to white
        self.leds.fadeRGB("FaceLeds", 1.0, 1.0, 1.0, 1.0)
        self.leds.fadeRGB("ChestLeds", 1.0, 1.0, 1.0, 1.0)
        self.leds.fadeRGB("EarLeds", 1.0, 1.0, 1.0, 1.0)

        # Return to rest
        self.posture.goToPosture("Stand", 1.0)

        print("\n" + "=" * 60)
        print("CHA CHA SLIDE COMPLETE!")
        print("=" * 60 + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Pepper's Cha Cha Slide Dance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # On Pepper (via SSH)
  python chacha_dance.py --ip 127.0.0.1

  # From PC
  python chacha_dance.py --ip 192.168.0.135

Optional: Upload Cha Cha Slide music to Pepper
  scp pepper_movement/audio/chacha.wav nao@192.168.0.135:/home/nao/chacha.wav
        """
    )
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                       help="Pepper's IP address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=9559,
                       help="NAOqi port (default: 9559)")
    args = parser.parse_args()

    print("\nPepper Cha Cha Slide Dance")
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
        dance = ChaChaSlide(session)
        dance.perform()
        return 0
    except KeyboardInterrupt:
        print("\n\n[ChaChaSlide] Dance interrupted by user")
        return 0
    except Exception as exc:
        print("\nERROR during dance: %s" % exc)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
