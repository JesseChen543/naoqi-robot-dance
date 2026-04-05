#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
robot_dance.py - Funny Robot Dance for Pepper

DESCRIPTION:
    A comedic 30-second robot dance where Pepper pretends to be a stiff,
    jerky, mechanical robot. Ironic humor since Pepper IS a robot!

FEATURES:
    - Exaggerated mechanical movements
    - Jerky, angular arm positions
    - "Error" movements and glitches
    - LED effects (red blinking for errors)
    - Funny robotic choreography
    - Optional "beep boop" sound effects

CHOREOGRAPHY SECTIONS:
    0-5s:   Boot Up Sequence - Stiff awakening
    5-10s:  Mechanical Arms - Angular movements
    10-15s: Error Mode - Glitchy movements
    15-20s: Rusty Robot - Slow, creaky moves
    20-25s: System Reboot - Fast twitches
    25-30s: Shutdown - Powering down

LED EFFECTS:
    - White/blue during normal operation
    - Red blinking during "errors"
    - Flashing during glitches

USAGE:
    # On Pepper (via SSH):
    python robot_dance.py --ip 127.0.0.1

    # From PC:
    python robot_dance.py --ip <PEPPER_IP>

DEPENDENCIES:
    - NAOqi 2.5
    - Robot dance audio file (optional)

AUDIO FILE:
    Upload robot.wav to /home/nao/ or place in pepper_movement/audio/
"""

import argparse
import qi
import time
import math
import threading


class RobotDance(object):
    """30-second comedic robot dance choreography"""

    def __init__(self, session):
        """
        Initialize Robot dance

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

        print("[RobotDance] Initialized")

    def setup(self):
        """Prepare Pepper for dance"""
        print("[RobotDance] Setting up...")

        # Wake up and stand
        self.motion.wakeUp()
        self.posture.goToPosture("Stand", 0.8)

        # Set movement speed parameters
        self.motion.setMoveArmsEnabled(True, True)

        # Disable external collision protection to allow movements
        try:
            self.motion.setExternalCollisionProtectionEnabled("All", False)
            print("[RobotDance] Collision protection disabled for dancing")
        except Exception as e:
            print("[RobotDance] Warning: Could not disable collision protection: %s" % e)

        print("[RobotDance] Ready to dance!")

    def robot_led_animation(self, duration=30):
        """
        Animate LEDs with robot-themed colors during dance

        Args:
            duration (int): Duration in seconds
        """
        def led_loop():
            start_time = time.time()
            elapsed = 0

            while elapsed < duration:
                elapsed = time.time() - start_time

                # Timing aligned with actual choreography:
                # 0-3.5s: Boot Up (rapid flashing), 3.5-7s: Mechanical Arms, 7-9s: Error Mode
                # 9-14s: Rusty Robot, 14-17s: System Reboot, 17-22s: Shutdown

                # 0-3.5s: Rapid multi-color flashing (booting up) - ALL LEDs
                if elapsed < 3.5:
                    # Cycle through different colors rapidly
                    colors = [
                        (1.0, 0.0, 0.0),  # Red
                        (0.0, 1.0, 0.0),  # Green
                        (0.0, 0.0, 1.0),  # Blue
                        (1.0, 1.0, 0.0),  # Yellow
                        (0.0, 1.0, 1.0),  # Cyan
                        (1.0, 0.0, 1.0),  # Magenta
                        (1.0, 1.0, 1.0),  # White
                    ]
                    # Change color every 0.05s for very rapid flashing
                    color_index = int(elapsed * 20) % len(colors)
                    r, g, b = colors[color_index]
                    self.leds.fadeRGB("FaceLeds", r, g, b, 0.0)
                    self.leds.fadeRGB("ChestLeds", r, g, b, 0.0)
                    self.leds.fadeRGB("EarLeds", r, g, b, 0.0)
                    time.sleep(0.05)
                # 3.5-7s: White (normal operation - mechanical arms)
                elif elapsed < 7:
                    self.leds.fadeRGB("FaceLeds", 1.0, 1.0, 1.0, 0.5)
                    time.sleep(0.5)
                # 7-9s: Red blinking (error mode) - ALL LEDs
                elif elapsed < 9:
                    self.leds.fadeRGB("FaceLeds", 1.0, 0.0, 0.0, 0.2)
                    self.leds.fadeRGB("ChestLeds", 1.0, 0.0, 0.0, 0.2)
                    self.leds.fadeRGB("EarLeds", 1.0, 0.0, 0.0, 0.2)
                    time.sleep(0.2)
                    self.leds.fadeRGB("FaceLeds", 0.0, 0.0, 0.0, 0.2)
                    self.leds.fadeRGB("ChestLeds", 0.0, 0.0, 0.0, 0.2)
                    self.leds.fadeRGB("EarLeds", 0.0, 0.0, 0.0, 0.2)
                    time.sleep(0.2)
                # 9-14s: Yellow (warning - rusty robot)
                elif elapsed < 14:
                    self.leds.fadeRGB("FaceLeds", 1.0, 1.0, 0.0, 0.4)
                    time.sleep(0.4)
                # 14-17s: Blue (system reboot)
                elif elapsed < 17:
                    self.leds.fadeRGB("FaceLeds", 0.0, 0.5, 1.0, 0.3)
                    time.sleep(0.3)
                # 17-30s: Fade to blue (shutdown)
                else:
                    self.leds.fadeRGB("FaceLeds", 0.0, 0.5, 1.0, 0.5)
                    time.sleep(0.5)

        # Run LED animation in background
        led_thread = threading.Thread(target=led_loop)
        led_thread.daemon = True
        led_thread.start()

    def play_robot_music(self):
        """
        Play robot dance music (uses TTS as backup)
        Music volume is set to 80% to be slightly quieter than voice
        """
        print("[RobotDance] Playing robot music...")

        # Try different audio formats in different locations
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        audio_dir = os.path.join(script_dir, "audio")

        audio_files = [
            # Local audio directory (for testing from PC)
            os.path.join(audio_dir, "robot.wav"),
            os.path.join(audio_dir, "robot.ogg"),
            os.path.join(audio_dir, "robot.mp3"),
            # Pepper's home directory (uploaded files)
            "/home/nao/robot.wav",
            "/home/nao/robot.ogg",
            "/home/nao/robot.mp3",
        ]

        for audio_file in audio_files:
            try:
                print("[RobotDance] Trying to load: %s" % audio_file)
                file_id = self.audio.loadFile(audio_file)

                # Set music volume to 40% (0.4) - much quieter so speech is clear
                self.audio.setVolume(file_id, 0.4)
                print("[RobotDance] Music volume set to 40%%")

                self.audio.play(file_id, _async=True)
                print("[RobotDance] Playing audio file: %s" % audio_file)
                return  # Success - exit function
            except Exception as e:
                print("[RobotDance] Could not load %s: %s" % (audio_file, e))
                continue  # Try next format

        # Fallback: Use TTS for robotic sounds
        print("[RobotDance] No audio file found, using TTS")
        self.tts.setParameter("pitchShift", 0.8)  # Lower pitch for robotic voice

        # Start beeping in background
        def beep():
            beeps = ["beep", "boop", "beep beep", "boop boop", "error error"]
            for sound in beeps:
                self.tts.say("\\rspd=200\\%s" % sound)
                time.sleep(2)

        beep_thread = threading.Thread(target=beep)
        beep_thread.daemon = True
        beep_thread.start()

    def choreography(self):
        """
        Main ~30-second Robot dance choreography

        Timeline:
        0-5s:   Boot Up Sequence - Stiff awakening
        5-10s:  Mechanical Arms - Angular movements
        10-15s: Error Mode - Glitchy movements
        15-20s: Rusty Robot - Slow, creaky moves
        20-25s: System Reboot - Fast twitches
        25-30s: Shutdown - Powering down
        """
        print("[RobotDance] Starting choreography...")

        # ================================================================
        # 0-5 seconds: BOOT UP SEQUENCE - Stiff awakening
        # ================================================================
        print("[RobotDance] Section 1: Boot Up (0-5s)")

        # Start from crouch position (like powering on)
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [1.5, 1.5], 0.3)
        self.motion.setAngles(["LElbowRoll", "RElbowRoll"], [-0.5, 0.5], 0.3)
        self.motion.setAngles("HeadPitch", 0.3, 0.3)
        time.sleep(1.0)

        # Head up (power on)
        self.motion.setAngles("HeadPitch", 0.0, 0.2)
        time.sleep(0.5)

        # Arms out stiffly (90-degree angles)
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.0, 0.0], 0.2)
        self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.3, -0.3], 0.2)
        self.motion.setAngles(["LElbowRoll", "RElbowRoll"], [-1.5, 1.5], 0.2)
        time.sleep(1.0)

        # Jerky head turns (left-center-right-center)
        for angle in [0.5, 0.0, -0.5, 0.0]:
            self.motion.setAngles("HeadYaw", angle, 0.15)
            time.sleep(0.4)

        # ================================================================
        # 5-10 seconds: MECHANICAL ARMS - Angular movements
        # ================================================================
        print("[RobotDance] Section 2: Mechanical Arms (5-10s)")

        # Right angle poses - very stiff and angular
        # Right arm up, left arm down
        self.motion.setAngles(["RShoulderPitch", "RElbowRoll"], [0.0, 1.5], 0.2)
        self.motion.setAngles(["LShoulderPitch", "LElbowRoll"], [1.5, -0.5], 0.2)
        time.sleep(0.8)

        # Swap - left arm up, right arm down
        self.motion.setAngles(["LShoulderPitch", "LElbowRoll"], [0.0, -1.5], 0.2)
        self.motion.setAngles(["RShoulderPitch", "RElbowRoll"], [1.5, 0.5], 0.2)
        time.sleep(0.8)

        # Both arms forward at 90 degrees (like a zombie robot)
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.5, 0.5], 0.2)
        self.motion.setAngles(["LElbowRoll", "RElbowRoll"], [0.0, 0.0], 0.2)
        time.sleep(0.8)

        # T-pose (both arms out sideways)
        self.motion.setAngles(["LShoulderPitch", "RShoulderPitch"], [0.5, 0.5], 0.2)
        self.motion.setAngles(["LShoulderRoll", "RShoulderRoll"], [0.8, -0.8], 0.2)
        self.motion.setAngles(["LElbowRoll", "RElbowRoll"], [-0.5, 0.5], 0.2)
        time.sleep(1.0)

        # ================================================================
        # 10-15 seconds: ERROR MODE - Glitchy movements
        # ================================================================
        print("[RobotDance] Section 3: Error Mode (10-15s)")

        # Rapid twitchy movements (simulating glitches)
        for i in range(6):
            # Random jerky arm positions
            import random
            left_pitch = random.choice([0.0, 0.5, 1.0, 1.5])
            right_pitch = random.choice([0.0, 0.5, 1.0, 1.5])
            head_yaw = random.choice([-0.3, 0.0, 0.3])

            self.motion.setAngles("LShoulderPitch", left_pitch, 0.8)
            self.motion.setAngles("RShoulderPitch", right_pitch, 0.8)
            self.motion.setAngles("HeadYaw", head_yaw, 0.8)

            # Say "error" with robotic voice
            self.tts.say("\\rspd=150\\error")
            time.sleep(0.1)

        # Reset head
        self.motion.setAngles("HeadYaw", 0.0, 0.2)

        # ================================================================
        # REBOOT SEQUENCE - Crouch and stand back up
        # ================================================================
        print("[RobotDance] Section 4: Reboot (crouch and stand)")

        # Crouch down (powering off)
        self.tts.say("\\rspd=100\\Rebooting")
        self.posture.goToPosture("Crouch", 0.8)
        time.sleep(1.0)

        # Stand back up (rebooting complete)
        self.tts.say("\\rspd=100\\System restored")
        self.posture.goToPosture("Stand", 0.8)
        time.sleep(1.0)

        # ================================================================
        # TERMINATOR - Iconic thumbs up pose
        # ================================================================
        print("[RobotDance] Section 5: Terminator")

        # Slow head scan left to right (scanning for targets)
        self.motion.setAngles("HeadYaw", 0.5, 0.1)
        time.sleep(1.0)
        self.motion.setAngles("HeadYaw", -0.5, 0.1)
        time.sleep(1.0)
        self.motion.setAngles("HeadYaw", 0.0, 0.1)
        time.sleep(0.5)

        # Raise right arm for thumbs up (the iconic Terminator pose)
        # Arm forward and up
        self.motion.setAngles("RShoulderPitch", 0.0, 0.3)  # Arm up
        self.motion.setAngles("RShoulderRoll", -0.2, 0.3)  # Slightly inward
        self.motion.setAngles("RElbowRoll", 0.5, 0.3)      # Bent elbow
        self.motion.setAngles("RElbowYaw", 1.5, 0.3)       # Rotate forearm
        self.motion.setAngles("RWristYaw", 0.0, 0.3)       # Wrist straight
        time.sleep(1.0)

        # Close hand to fist with thumb up (simulated)
        try:
            self.motion.setAngles("RHand", 0.3, 0.5)  # Partially closed
        except:
            pass
        time.sleep(0.5)

        # Hold the pose
        time.sleep(2.0)

        # Say the iconic line
        self.tts.setParameter("pitchShift", 0.7)  # Deep voice
        self.tts.say("\\rspd=80\\I'll be back.")
        time.sleep(1.0)

        # Lower arm slowly
        self.motion.setAngles("RShoulderPitch", 1.5, 0.2)
        self.motion.setAngles("RElbowRoll", 0.5, 0.2)
        time.sleep(1.0)

        # Wait 5 seconds
        time.sleep(5.0)

        # ================================================================
        # DRIVE AWAY - Terminator drives off
        # ================================================================
        print("[RobotDance] Section 6: Drive Away")

        # Run the drive car animation
        self.animation.run("animations/Stand/Waiting/DriveCar_1")

        print("[RobotDance] Choreography complete!")

    def perform(self):
        """
        Perform the complete Robot dance

        This coordinates music, LEDs, and choreography
        """
        print("\n" + "=" * 60)
        print("🤖 PEPPER'S ROBOT DANCE 🤖")
        print("=" * 60)

        # Setup
        self.setup()

        # Announce
        self.tts.setParameter("pitchShift", 0.8)  # Robotic voice
        self.tts.say("\\rspd=80\\Initiating. Robot. Dance. Mode.")
        time.sleep(0.5)

        # Start LED animation
        self.robot_led_animation(duration=30)

        # Start music
        self.play_robot_music()

        # Wait a moment for music to start
        time.sleep(0.5)

        # Perform choreography (~30 seconds)
        start_time = time.time()
        self.choreography()
        elapsed = time.time() - start_time

        print("\n[RobotDance] Dance duration: %.1f seconds" % elapsed)

        # Reset LEDs to white
        self.leds.fadeRGB("FaceLeds", 1.0, 1.0, 1.0, 1.0)
        self.leds.fadeRGB("ChestLeds", 1.0, 1.0, 1.0, 1.0)
        self.leds.fadeRGB("EarLeds", 1.0, 1.0, 1.0, 1.0)

        # Return to rest
        self.posture.goToPosture("Stand", 1.0)

        print("\n" + "=" * 60)
        print("🤖 ROBOT DANCE COMPLETE! 🤖")
        print("=" * 60 + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Pepper's 30-second Robot Dance with funny mechanical movements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # On Pepper (via SSH)
  python robot_dance.py --ip 127.0.0.1

  # From PC
  python robot_dance.py --ip <PEPPER_IP>

Optional: Upload robot music to Pepper
  scp pepper_movement/audio/robot.wav nao@<PEPPER_IP>:/home/nao/robot.wav
        """
    )
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                       help="Pepper's IP address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=9559,
                       help="NAOqi port (default: 9559)")
    args = parser.parse_args()

    print("\n🤖 Pepper Robot Dance 🤖")
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
        dance = RobotDance(session)
        dance.perform()
        return 0
    except KeyboardInterrupt:
        print("\n\n[RobotDance] Dance interrupted by user")
        return 0
    except Exception as exc:
        print("\nERROR during dance: %s" % exc)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
