#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
custom_dance.py - Template for Creating Custom Pepper Dances

DESCRIPTION:
    Use this template as a starting point for creating your own
    dance routines for Pepper Robot.

USAGE:
    python custom_dance.py --ip 127.0.0.1      # On Pepper via SSH
    python custom_dance.py --ip <PEPPER_IP>  # From PC

CUSTOMIZATION:
    1. Rename the class to your dance name
    2. Modify the choreography() method with your movements
    3. Adjust LED colors in led_animation() method
    4. Update the music file name in play_music() method
"""

import argparse
import qi
import time
import math
import threading


class CustomDance(object):
    """Template for custom Pepper dance choreography"""

    def __init__(self, session):
        """
        Initialize dance controller

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

        print("[CustomDance] Initialized")

    def setup(self):
        """Prepare Pepper for dance"""
        print("[CustomDance] Setting up...")

        # Wake up and stand
        self.motion.wakeUp()
        self.posture.goToPosture("Stand", 0.8)

        # Enable arm movement
        self.motion.setMoveArmsEnabled(True, True)

        # Disable collision protection for fluid dance moves
        try:
            self.motion.setExternalCollisionProtectionEnabled("All", False)
            print("[CustomDance] Collision protection disabled for dancing")
        except Exception as e:
            print("[CustomDance] Warning: %s" % e)

        print("[CustomDance] Ready to dance!")

    def led_animation(self, duration=30):
        """
        Animate LEDs during dance

        Args:
            duration (int): Duration in seconds
        """
        def led_loop():
            start_time = time.time()
            colors = [
                (1.0, 0.0, 0.0),  # Red
                (0.0, 1.0, 0.0),  # Green
                (0.0, 0.0, 1.0),  # Blue
                (1.0, 1.0, 0.0),  # Yellow
                (1.0, 0.0, 1.0),  # Magenta
                (0.0, 1.0, 1.0),  # Cyan
            ]
            index = 0

            while time.time() - start_time < duration:
                r, g, b = colors[index % len(colors)]
                self.leds.fadeRGB("FaceLeds", r, g, b, 0.3)
                self.leds.fadeRGB("ChestLeds", r, g, b, 0.3)
                time.sleep(0.5)
                index += 1

        led_thread = threading.Thread(target=led_loop)
        led_thread.daemon = True
        led_thread.start()

    def play_music(self):
        """Play dance music (optional)"""
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        audio_dir = os.path.join(os.path.dirname(script_dir), "audio")

        audio_files = [
            os.path.join(audio_dir, "custom.wav"),
            "/home/nao/custom.wav",
        ]

        for audio_file in audio_files:
            try:
                file_id = self.audio.loadFile(audio_file)
                self.audio.setVolume(file_id, 0.4)
                self.audio.play(file_id, _async=True)
                print("[CustomDance] Playing: %s" % audio_file)
                return
            except Exception:
                continue

        print("[CustomDance] No audio file found, dancing without music")

    def choreography(self):
        """
        Main dance choreography

        CUSTOMIZE THIS METHOD with your own movements!

        Useful motion methods:
            self.motion.setAngles(joint_names, angles, speed)
            self.motion.moveTo(x, y, theta)
            self.posture.goToPosture(posture_name, speed)
            self.animation.run("animations/Stand/Gestures/Hey_1")

        Joint names:
            Head: HeadYaw, HeadPitch
            Arms: LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, LWristYaw
                  RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll, RWristYaw
            Hands: LHand, RHand (0.0=open, 1.0=closed)
            Hip: HipRoll, HipPitch
            Knees: LKneePitch, RKneePitch
        """
        print("[CustomDance] Starting choreography...")

        # ================================================================
        # SECTION 1: Opening (0-5 seconds)
        # ================================================================
        print("[CustomDance] Section 1: Opening")

        # Wave hello
        self.motion.setAngles("RShoulderPitch", -0.5, 0.3)
        self.motion.setAngles("RShoulderRoll", -0.2, 0.3)
        self.motion.setAngles("RElbowRoll", 0.5, 0.3)
        time.sleep(0.5)

        # Wave motion
        for i in range(3):
            self.motion.setAngles("RWristYaw", 0.5, 0.5)
            time.sleep(0.3)
            self.motion.setAngles("RWristYaw", -0.5, 0.5)
            time.sleep(0.3)

        # Return arm
        self.motion.setAngles("RShoulderPitch", 1.5, 0.3)
        time.sleep(1.0)

        # ================================================================
        # SECTION 2: Main Dance (5-20 seconds)
        # ================================================================
        print("[CustomDance] Section 2: Main Dance")

        # Arms out to sides
        self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.5, -0.5], 0.3)
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.5, 0.5], 0.3)
        time.sleep(1.0)

        # Bounce movement (4 times)
        for i in range(4):
            # Down
            self.motion.setAngles("HipPitch", -0.1, 0.5)
            time.sleep(0.25)
            # Up
            self.motion.setAngles("HipPitch", 0.0, 0.5)
            time.sleep(0.25)

        # Head movements
        for angle in [0.5, 0.0, -0.5, 0.0]:
            self.motion.setAngles("HeadYaw", angle, 0.3)
            time.sleep(0.5)

        # Arms crossing
        for i in range(2):
            # Cross arms
            self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [-0.3, 0.3], 0.3)
            time.sleep(0.5)
            # Open arms
            self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.5, -0.5], 0.3)
            time.sleep(0.5)

        # ================================================================
        # SECTION 3: Finale (20-30 seconds)
        # ================================================================
        print("[CustomDance] Section 3: Finale")

        # Build-in animation (optional)
        try:
            self.animation.run("animations/Stand/Gestures/Enthusiastic_4")
        except Exception:
            pass

        time.sleep(2.0)

        # Final pose - hands on hips
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [1.0, 1.0], 0.3)
        self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.3, -0.3], 0.3)
        self.motion.setAngles(["LElbowRoll", "RElbowRoll"], [-1.5, 1.5], 0.3)
        time.sleep(1.0)

        print("[CustomDance] Choreography complete!")

    def perform(self):
        """Perform the complete dance"""
        print("\n" + "=" * 60)
        print("PEPPER'S CUSTOM DANCE")
        print("=" * 60)

        # Setup
        self.setup()

        # Announce
        self.tts.say("Let's dance!")
        time.sleep(0.5)

        # Start LED animation
        self.led_animation(duration=30)

        # Start music
        self.play_music()
        time.sleep(0.5)

        # Perform choreography
        start_time = time.time()
        self.choreography()
        elapsed = time.time() - start_time

        print("\n[CustomDance] Dance duration: %.1f seconds" % elapsed)

        # Reset
        self.leds.fadeRGB("FaceLeds", 1.0, 1.0, 1.0, 1.0)
        self.leds.fadeRGB("ChestLeds", 1.0, 1.0, 1.0, 1.0)
        self.posture.goToPosture("Stand", 1.0)

        # Closing
        self.tts.say("Thank you!")

        print("\n" + "=" * 60)
        print("DANCE COMPLETE!")
        print("=" * 60 + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Pepper Custom Dance Template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python custom_dance.py --ip 127.0.0.1      # On Pepper via SSH
  python custom_dance.py --ip <PEPPER_IP>  # From PC
        """
    )
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Pepper's IP address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=9559,
                        help="NAOqi port (default: 9559)")
    args = parser.parse_args()

    print("\nPepper Custom Dance")
    print("Connecting to Pepper at %s:%d..." % (args.ip, args.port))

    try:
        session = qi.Session()
        session.connect("tcp://%s:%d" % (args.ip, args.port))
        print("Connected!\n")
    except Exception as exc:
        print("ERROR: Cannot connect to Pepper: %s" % exc)
        return 1

    try:
        dance = CustomDance(session)
        dance.perform()
        return 0
    except KeyboardInterrupt:
        print("\n\nDance interrupted")
        return 0
    except Exception as exc:
        print("\nERROR: %s" % exc)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
