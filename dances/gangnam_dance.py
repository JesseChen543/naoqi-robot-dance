#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
gangnam_dance.py - Gangnam Style Dance for Pepper

DESCRIPTION:
    A fun 45-second Gangnam Style dance featuring the iconic horse-riding
    move and arm lasso movements. Pepper performs PSY's signature moves!

FEATURES:
    - Iconic horse-riding dance move
    - Lasso arm swings
    - Side-stepping movements
    - LED effects synced to beat
    - "Oppan Gangnam Style!" announcement

CHOREOGRAPHY SECTIONS:
    0-5s:   Intro - Build up with arm movements
    5-20s:  Horse Riding - The signature move
    20-30s: Lasso Arms - Swing arms overhead
    30-40s: Horse Riding Finale - Faster version
    40-45s: Ending pose

USAGE:
    # On Pepper (via SSH):
    python gangnam_dance.py --ip 127.0.0.1

    # From PC:
    python gangnam_dance.py --ip <PEPPER_IP>

DEPENDENCIES:
    - NAOqi 2.5
    - Gangnam Style audio file (optional)

AUDIO FILE:
    Upload gangnam.wav to /home/nao/ or place in pepper_movement/audio/
"""

import argparse
import qi
import time
import math
import threading


class GangnamDance(object):
    """45-second Gangnam Style dance choreography"""

    def __init__(self, session):
        """
        Initialize Gangnam Style dance

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

        print("[GangnamDance] Initialized")

    def setup(self):
        """Prepare Pepper for dance"""
        print("[GangnamDance] Setting up...")

        # Wake up and stand
        self.motion.wakeUp()
        self.posture.goToPosture("Stand", 0.8)

        # Set movement speed parameters
        self.motion.setMoveArmsEnabled(True, True)

        # Disable external collision protection to allow dance moves
        try:
            self.motion.setExternalCollisionProtectionEnabled("All", False)
            print("[GangnamDance] Collision protection disabled for dancing")
        except Exception as e:
            print("[GangnamDance] Warning: Could not disable collision protection: %s" % e)

        print("[GangnamDance] Ready to dance!")

    def gangnam_led_animation(self, duration=40):
        """
        Animate LEDs with party colors during dance

        Args:
            duration (int): Duration in seconds
        """
        def led_loop():
            start_time = time.time()
            # Bright party colors
            colors = [
                (1.0, 0.0, 0.0),  # Red
                (1.0, 1.0, 0.0),  # Yellow
                (0.0, 1.0, 0.0),  # Green
                (0.0, 1.0, 1.0),  # Cyan
                (0.0, 0.0, 1.0),  # Blue
                (1.0, 0.0, 1.0),  # Magenta
            ]
            color_index = 0

            while time.time() - start_time < duration:
                color = colors[color_index % len(colors)]
                # Flash all LEDs to the beat
                self.leds.fadeRGB("FaceLeds", color[0], color[1], color[2], 0.1)
                self.leds.fadeRGB("ChestLeds", color[0], color[1], color[2], 0.1)
                self.leds.fadeRGB("EarLeds", color[0], color[1], color[2], 0.1)
                time.sleep(0.25)  # Beat timing
                color_index += 1

        # Run LED animation in background
        led_thread = threading.Thread(target=led_loop)
        led_thread.daemon = True
        led_thread.start()

    def play_gangnam_music(self):
        """
        Play Gangnam Style music
        Music volume is set to 40% so speech is clear
        """
        print("[GangnamDance] Playing Gangnam Style music...")

        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        audio_dir = os.path.join(script_dir, "audio")

        audio_files = [
            os.path.join(audio_dir, "gangnam.wav"),
            os.path.join(audio_dir, "gangnam.ogg"),
            os.path.join(audio_dir, "gangnam.mp3"),
            "/home/nao/gangnam.wav",
            "/home/nao/gangnam.ogg",
            "/home/nao/gangnam.mp3",
        ]

        for audio_file in audio_files:
            try:
                print("[GangnamDance] Trying to load: %s" % audio_file)
                file_id = self.audio.loadFile(audio_file)

                # Set music volume to 40% so speech is clear
                self.audio.setVolume(file_id, 0.4)
                print("[GangnamDance] Music volume set to 40%%")

                self.audio.play(file_id, _async=True)
                print("[GangnamDance] Playing audio file: %s" % audio_file)
                return
            except Exception as e:
                print("[GangnamDance] Could not load %s: %s" % (audio_file, e))
                continue

        print("[GangnamDance] No audio file found, dancing without music")

    def horse_riding_move(self, beats=8, speed=0.3):
        """
        Perform the iconic horse-riding dance move

        Args:
            beats (int): Number of beats to perform
            speed (float): Speed of movement
        """
        for i in range(beats):
            # Bounce down (like riding a horse)
            self.motion.setAngles("HipPitch", -0.2, 0.8)
            self.motion.setAngles("KneePitch", 0.2, 0.8)

            # Arms in riding position - pump up
            self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.5, 0.5], 0.8)
            self.motion.setAngles(["LElbowRoll", "RElbowRoll"], [-1.0, 1.0], 0.8)
            self.motion.setAngles(["LElbowYaw", "RElbowYaw"], [-1.2, 1.2], 0.8)
            time.sleep(speed / 2)

            # Bounce up
            self.motion.setAngles("HipPitch", 0.0, 0.8)
            self.motion.setAngles("KneePitch", 0.0, 0.8)

            # Arms pump down
            self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.8, 0.8], 0.8)
            self.motion.setAngles(["LElbowRoll", "RElbowRoll"], [-0.5, 0.5], 0.8)
            time.sleep(speed / 2)

    def lasso_arms(self, rotations=4):
        """
        Perform the lasso arm swing overhead

        Args:
            rotations (int): Number of arm rotations
        """
        # Right arm lasso motion
        for i in range(rotations):
            # Arm up and back
            self.motion.setAngles("RShoulderPitch", -0.5, 0.5)
            self.motion.setAngles("RShoulderRoll", -0.3, 0.5)
            self.motion.setAngles("RElbowRoll", 0.5, 0.5)
            time.sleep(0.25)

            # Arm forward
            self.motion.setAngles("RShoulderPitch", 0.3, 0.5)
            self.motion.setAngles("RElbowRoll", 1.0, 0.5)
            time.sleep(0.25)

        # Left arm lasso
        for i in range(rotations):
            # Arm up and back
            self.motion.setAngles("LShoulderPitch", -0.5, 0.5)
            self.motion.setAngles("LShoulderRoll", 0.3, 0.5)
            self.motion.setAngles("LElbowRoll", -0.5, 0.5)
            time.sleep(0.25)

            # Arm forward
            self.motion.setAngles("LShoulderPitch", 0.3, 0.5)
            self.motion.setAngles("LElbowRoll", -1.0, 0.5)
            time.sleep(0.25)

    def side_step(self, direction="right", steps=4):
        """
        Side-stepping dance move

        Args:
            direction (str): "left" or "right"
            steps (int): Number of steps
        """
        step_angle = 0.3 if direction == "right" else -0.3

        for i in range(steps):
            # Step to side
            self.motion.moveTo(0, step_angle, 0)
            time.sleep(0.3)

    def choreography(self):
        """
        Main 45-second Gangnam Style choreography
        """
        print("[GangnamDance] Starting choreography...")

        # ================================================================
        # 0-5 seconds: INTRO - Build up
        # ================================================================
        print("[GangnamDance] Section 1: Intro (0-5s)")

        # Start with arms crossed
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.8, 0.8], 0.3)
        self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.0, 0.0], 0.3)
        self.motion.setAngles(["LElbowRoll", "RElbowRoll"], [-0.5, 0.5], 0.3)
        time.sleep(1.0)

        # Arms out to sides
        self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.5, -0.5], 0.3)
        time.sleep(1.0)

        # Head bob
        for i in range(3):
            self.motion.setAngles("HeadPitch", 0.2, 0.5)
            time.sleep(0.3)
            self.motion.setAngles("HeadPitch", -0.1, 0.5)
            time.sleep(0.3)

        # ================================================================
        # HORSE RIDING - The signature move (8 seconds)
        # ================================================================
        print("[GangnamDance] Section 2: Horse Riding (8s)")

        # Get into horse riding position
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.5, 0.5], 0.5)
        self.motion.setAngles(["LElbowRoll", "RElbowRoll"], [-1.0, 1.0], 0.5)
        time.sleep(0.5)

        # Do the horse riding move (8 seconds = 16 beats at 0.5s each)
        self.horse_riding_move(beats=16, speed=0.5)

        # ================================================================
        # LASSO ARMS
        # ================================================================
        print("[GangnamDance] Section 3: Lasso Arms")

        # Reset to standing
        self.posture.goToPosture("Stand", 0.5)
        time.sleep(0.5)

        # Lasso moves
        self.lasso_arms(rotations=6)
        self.lasso_arms(rotations=6)

        # ================================================================
        # HORSE RIDING FINALE - Faster (4 seconds)
        # ================================================================
        print("[GangnamDance] Section 4: Horse Riding Finale (4s)")

        # Faster horse riding (4 seconds = 10 beats at 0.4s each)
        self.horse_riding_move(beats=10, speed=0.4)

        print("[GangnamDance] Choreography complete!")

    def perform(self):
        """
        Perform the complete Gangnam Style dance
        """
        print("\n" + "=" * 60)
        print("PEPPER'S GANGNAM STYLE DANCE")
        print("=" * 60)

        # Setup
        self.setup()

        # Announce
        self.tts.say("Oppan Gangnam Style!")
        time.sleep(0.5)

        # Start LED animation
        self.gangnam_led_animation(duration=40)

        # Start music
        self.play_gangnam_music()

        # Wait a moment for music to start
        time.sleep(0.5)

        # Perform choreography
        start_time = time.time()
        self.choreography()
        elapsed = time.time() - start_time

        print("\n[GangnamDance] Dance duration: %.1f seconds" % elapsed)

        # Final words
        self.tts.say("Hey! Sexy lady!")
        time.sleep(1.0)

        # Reset LEDs to white
        self.leds.fadeRGB("FaceLeds", 1.0, 1.0, 1.0, 1.0)
        self.leds.fadeRGB("ChestLeds", 1.0, 1.0, 1.0, 1.0)
        self.leds.fadeRGB("EarLeds", 1.0, 1.0, 1.0, 1.0)

        # Return to rest
        self.posture.goToPosture("Stand", 1.0)

        print("\n" + "=" * 60)
        print("GANGNAM STYLE DANCE COMPLETE!")
        print("=" * 60 + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Pepper's Gangnam Style Dance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # On Pepper (via SSH)
  python gangnam_dance.py --ip 127.0.0.1

  # From PC
  python gangnam_dance.py --ip <PEPPER_IP>

Optional: Upload Gangnam Style music to Pepper
  scp pepper_movement/audio/gangnam.wav nao@<PEPPER_IP>:/home/nao/gangnam.wav
        """
    )
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                       help="Pepper's IP address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=9559,
                       help="NAOqi port (default: 9559)")
    args = parser.parse_args()

    print("\nPepper Gangnam Style Dance")
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
        dance = GangnamDance(session)
        dance.perform()
        return 0
    except KeyboardInterrupt:
        print("\n\n[GangnamDance] Dance interrupted by user")
        return 0
    except Exception as exc:
        print("\nERROR during dance: %s" % exc)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
