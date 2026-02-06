#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
kungfu_dance.py - Mystical Chinese Kung Fu Dance

A 60-second dynamic Kung Fu-inspired dance with powerful movements.
Features graceful arm movements, punches, kicks, centered stances, and warrior poses
synchronized with traditional Chinese instrumental music.

CHOREOGRAPHY SECTIONS:
    0-8s:   Opening Stance - Awakening chi energy
    8-16s:  Flowing Forms - Tai Chi inspired movements
    16-24s: Crane Stance - Balance and focus
    24-32s: Dragon Movement - Power and fluidity
    32-42s: Warrior Strikes - Aggressive punches and strikes
    42-60s: Victory Stance - Powerful finish and meditation

LED EFFECTS:
    - Deep red and gold colors (traditional Chinese)
    - Transitions match movement intensity
    - Mystical purple accents
    - Faster transitions during aggressive sections

USAGE:
    python2.7 kungfu_dance.py --ip 127.0.0.1 --port 9559

DEPENDENCIES:
    - NAOqi SDK (Python 2.7)
    - qi framework
    - Audio file: kungfu.wav (optional, will use TTS if missing)
"""

import sys
import os
import time
import argparse
import math

def main(session):
    """
    Execute mystical Kung Fu dance choreography

    Args:
        session: Active qi.Session connected to robot
    """
    tts = None
    original_tts_volume = None
    led_thread = None

    try:
        # Get NAOqi services
        motion = session.service("ALMotion")
        posture = session.service("ALRobotPosture")
        audio_player = session.service("ALAudioPlayer")
        tts = session.service("ALTextToSpeech")
        leds = session.service("ALLeds")

        print("[KungFu] Initializing Kung Fu dance...")

        # Boost TTS volume so speech sits above background music
        try:
            original_tts_volume = float(tts.getVolume())
            boosted_tts_volume = 1.0
            if abs(boosted_tts_volume - original_tts_volume) > 0.01:
                tts.setVolume(boosted_tts_volume)
                print("[KungFu] TTS volume boosted from {:.2f} to {:.2f}".format(original_tts_volume, boosted_tts_volume))
            else:
                print("[KungFu] TTS volume already at {:.2f}".format(original_tts_volume))
        except Exception as volume_error:
            print("[KungFu] Could not adjust TTS volume: {}".format(volume_error))
            original_tts_volume = None

        # Wake up and stand
        motion.wakeUp()
        posture.goToPosture("StandInit", 0.8)
        time.sleep(0.5)

        # Note: We keep collision protection enabled for safety
        # Kung Fu movements are slow and controlled, so they work fine with protection on

        # Start LED animation in background
        led_thread = KungFuLEDAnimation(leds)
        led_thread.start_animation()

        # Check for audio file
        audio_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "audio",
            "kungfu.wav"
        )

        # Try to play audio file
        audio_started = False

        # Try different locations for the audio file
        audio_files = [
            audio_file,  # Script's audio directory
            "/home/nao/kungfu.wav",  # Pepper's home directory
        ]

        for audio_path in audio_files:
            if os.path.exists(audio_path):
                try:
                    print("[KungFu] Playing Kung Fu music: {}".format(audio_path))
                    # Load file and play asynchronously (non-blocking)
                    file_id = audio_player.loadFile(audio_path)

                    # Set music volume to 60% (0.6) so speech is clearly louder
                    audio_player.setVolume(file_id, 0.6)
                    print("[KungFu] Music volume set to 60%")

                    audio_player.play(file_id, _async=True)
                    audio_started = True
                    print("[KungFu] Music started (non-blocking)")
                    break
                except Exception as e:
                    print("[KungFu] Audio playback failed: {}".format(e))

        if not audio_started:
            print("[KungFu] No audio file, using TTS narration...")
            tts.say("\\rspd=70\\Ancient wisdom flows through movement.")

        # Small delay to let music start
        time.sleep(0.5)

        # Execute choreography (will run simultaneously with music)
        choreography = KungFuChoreography(motion, posture, tts)
        choreography.perform()

        # Return to standing position
        print("[KungFu] Returning to standing position...")
        posture.goToPosture("StandInit", 0.8)

        print("[KungFu] Kung Fu dance complete!")

    except Exception as e:
        print("[KungFu] Error during dance: {}".format(e))
        import traceback
        traceback.print_exc()

        # Try to recover
        try:
            posture.goToPosture("StandInit", 0.5)
        except:
            pass
    finally:
        if led_thread is not None:
            try:
                led_thread.stop_animation()
            except Exception:
                pass
        if tts is not None and original_tts_volume is not None:
            try:
                tts.setVolume(original_tts_volume)
                print("[KungFu] Restored TTS volume to {:.2f}".format(original_tts_volume))
            except Exception as restore_error:
                print("[KungFu] Failed to restore TTS volume: {}".format(restore_error))


class KungFuChoreography(object):
    """Mystical Kung Fu dance choreography"""

    def __init__(self, motion, posture, tts):
        self.motion = motion
        self.posture = posture
        self.tts = tts

    def perform(self):
        """Execute the full 60-second choreography"""
        print("[KungFu] Starting choreography...")

        # Section 1: Opening Stance (0-8s) - Awakening chi energy
        self.opening_stance()

        # Section 2: Flowing Forms (8-16s) - Tai Chi inspired
        self.flowing_forms()

        # Section 3: Crane Stance (16-24s) - Balance and focus
        self.crane_stance()

        # Section 4: Dragon Movement (24-32s) - Power and fluidity
        self.dragon_movement()

        # Section 5: Warrior Strikes (32-42s) - Aggressive punches and strikes
        self.warrior_strikes()

        # Section 6: Victory Stance (42-50s) - Powerful finish
        self.victory_stance()

        print("[KungFu] Choreography complete")

    def opening_stance(self):
        """0-8s: Opening stance - Awakening chi energy"""
        print("[KungFu] Section 1: Opening Stance (0-8s)")

        # Announce section with TTS (in background thread to not block)
        import threading
        threading.Thread(target=lambda: self.tts.say("Opening Stance!")).start()

        # Start with hands at sides, slowly raise to meditation position
        # Very slow, centered movements

        # Raise both arms slowly to chest level (prayer position)
        names = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll",
                 "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"]
        angles = [1.2, 0.15, -1.2, -0.5,
                  1.2, -0.15, 1.2, 0.5]
        times = [3.0] * 8
        self.motion.angleInterpolation(names, angles, times, True)

        # Hold meditation pose
        time.sleep(1.0)

        # Slowly lower hands to waist level (gathering chi)
        angles = [1.4, 0.3, -1.0, -0.3,
                  1.4, -0.3, 1.0, 0.3]
        times = [2.5] * 8
        self.motion.angleInterpolation(names, angles, times, True)

        time.sleep(1.5)

    def flowing_forms(self):
        """8-16s: Flowing Forms - Tai Chi inspired movements"""
        print("[KungFu] Section 2: Flowing Forms (8-16s)")

        # Announce section with TTS (in background thread to not block)
        import threading
        threading.Thread(target=lambda: self.tts.say("Flowing Forms!")).start()

        # Wave-like movements - left to right
        # Slow, continuous flow

        # Left arm rises, right arm extends
        names = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll",
                 "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll",
                 "HeadYaw"]

        # Flow to left
        angles = [0.8, 0.6, -1.5, -0.8,
                  1.2, -0.1, 0.5, 0.3,
                  0.4]
        times = [3.0] * 8 + [3.0]
        self.motion.angleInterpolation(names, angles, times, True)

        time.sleep(0.5)

        # Flow to right (mirror)
        angles = [1.2, 0.1, -0.5, -0.3,
                  0.8, -0.6, 1.5, 0.8,
                  -0.4]
        times = [3.0] * 8 + [3.0]
        self.motion.angleInterpolation(names, angles, times, True)

        time.sleep(0.5)

        # Return to center with circular movement
        angles = [1.0, 0.2, -1.0, -0.5,
                  1.0, -0.2, 1.0, 0.5,
                  0.0]
        times = [2.0] * 8 + [2.0]
        self.motion.angleInterpolation(names, angles, times, True)

    def crane_stance(self):
        """16-24s: Crane Stance - Balance and focus"""
        print("[KungFu] Section 3: Crane Stance (16-24s)")

        # Announce section with TTS (in background thread to not block)
        import threading
        threading.Thread(target=lambda: self.tts.say("Crane Stance!")).start()

        # One arm up (crane wing), one arm out
        # Slow head turn to side
        # Hold balance pose

        names = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll",
                 "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll",
                 "HeadYaw", "HeadPitch"]

        # Left arm up, right arm extended low
        angles = [0.0, 0.3, -1.2, -1.2,  # Left arm up like crane wing
                  1.5, -0.5, 1.0, 0.2,   # Right arm extended
                  -0.5, -0.2]            # Head turns left, looks down
        times = [3.5] * 8 + [3.5, 3.5]
        self.motion.angleInterpolation(names, angles, times, True)

        # Hold the pose
        time.sleep(2.0)

        # Switch sides - mirror
        angles = [1.5, 0.5, -1.0, -0.2,  # Right arm up
                  0.0, -0.3, 1.2, 1.2,   # Left arm extended
                  0.5, -0.2]             # Head turns right
        times = [2.5] * 8 + [2.5, 2.5]
        self.motion.angleInterpolation(names, angles, times, True)

        time.sleep(2.0)

    def dragon_movement(self):
        """24-32s: Dragon Movement - Power and fluidity"""
        print("[KungFu] Section 4: Dragon Movement (24-32s)")

        # Announce section with TTS (in background thread to not block)
        import threading
        threading.Thread(target=lambda: self.tts.say("Dragon Movement!")).start()

        # Powerful sweeping movements
        # Arms move in dragon-like patterns
        # More dynamic but still controlled

        names = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll",
                 "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll",
                 "HeadYaw", "HeadPitch"]

        # Dragon sweep right
        angles = [0.5, 0.8, -1.8, -1.0,
                  0.5, -0.8, 1.8, 1.0,
                  0.6, 0.1]
        times = [2.0] * 8 + [2.0, 2.0]
        self.motion.angleInterpolation(names, angles, times, True)

        time.sleep(0.5)

        # Dragon sweep left
        angles = [0.5, 0.8, -1.8, -1.0,
                  0.5, -0.8, 1.8, 1.0,
                  -0.6, 0.1]
        times = [2.0] * 8 + [2.0, 2.0]
        self.motion.angleInterpolation(names, angles, times, True)

        time.sleep(0.5)

        # Rising dragon - arms sweep up
        angles = [0.2, 0.4, -1.4, -0.8,
                  0.2, -0.4, 1.4, 0.8,
                  0.0, -0.3]
        times = [2.5] * 8 + [2.5, 2.5]
        self.motion.angleInterpolation(names, angles, times, True)

        time.sleep(0.5)

    def warrior_strikes(self):
        """32-42s: Warrior Strikes - Aggressive punches and strikes"""
        print("[KungFu] Section 5: Warrior Strikes (32-42s)")

        # Announce section with TTS - more energetic! (in background thread to not block)
        import threading
        threading.Thread(target=lambda: self.tts.say("\\rspd=120\\Warrior Strikes!")).start()

        # Enable movement (will move forward and backward)
        self.motion.setMoveArmsEnabled(True, True)

        names = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll",
                 "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll",
                 "HeadYaw", "HeadPitch"]

        # Move forward significantly while getting into fighting stance
        self.motion.moveTo(0.5, 0.0, 0.0)  # Move 50cm forward
        time.sleep(0.5)

        # Fighting stance - arms up, ready to strike
        angles = [1.0, 0.3, -1.0, -0.8,
                  1.0, -0.3, 1.0, 0.8,
                  0.0, -0.1]
        times = [0.5] * 8 + [0.5, 0.5]
        self.motion.angleInterpolation(names, angles, times, True)

        # Series of rapid punches - LEFT PUNCH
        for i in range(2):
            # Left punch - extend left arm fast
            angles = [0.8, 0.1, -1.5, -0.1,  # Left arm extends
                      1.0, -0.3, 1.0, 0.8,   # Right arm stays back
                      -0.3, -0.1]            # Head turns with punch
            times = [0.3] * 8 + [0.3, 0.3]
            self.motion.angleInterpolation(names, angles, times, True)
            time.sleep(0.1)

            # Retract left punch
            angles = [1.0, 0.3, -1.0, -0.8,
                      1.0, -0.3, 1.0, 0.8,
                      0.0, -0.1]
            times = [0.3] * 8 + [0.3, 0.3]
            self.motion.angleInterpolation(names, angles, times, True)
            time.sleep(0.1)

            # RIGHT PUNCH
            # Right punch - extend right arm fast
            angles = [1.0, 0.3, -1.0, -0.8,  # Left arm stays back
                      0.8, -0.1, 1.5, 0.1,   # Right arm extends
                      0.3, -0.1]             # Head turns with punch
            times = [0.3] * 8 + [0.3, 0.3]
            self.motion.angleInterpolation(names, angles, times, True)
            time.sleep(0.1)

            # Retract right punch
            angles = [1.0, 0.3, -1.0, -0.8,
                      1.0, -0.3, 1.0, 0.8,
                      0.0, -0.1]
            times = [0.3] * 8 + [0.3, 0.3]
            self.motion.angleInterpolation(names, angles, times, True)
            time.sleep(0.1)

        # Move backward while doing spinning block
        self.motion.moveTo(-0.5, 0.0, 0.0)  # Move 50cm backward
        time.sleep(0.5)

        # Spinning block - both arms sweep across
        angles = [0.5, 0.8, -1.8, -1.2,
                  0.5, -0.8, 1.8, 1.2,
                  0.5, 0.0]
        times = [0.4] * 8 + [0.4, 0.4]
        self.motion.angleInterpolation(names, angles, times, True)
        time.sleep(0.2)

        # Turn slightly and do uppercut motion - LEFT
        self.motion.moveTo(0.0, 0.0, 0.2)  # Turn 11 degrees left
        angles = [0.3, 0.4, -1.2, -1.5,  # Left uppercut
                  1.2, -0.2, 0.8, 0.5,
                  -0.3, 0.0]
        times = [0.4] * 8 + [0.4, 0.4]
        self.motion.angleInterpolation(names, angles, times, True)
        time.sleep(0.3)

        # Turn to center and uppercut RIGHT
        self.motion.moveTo(0.0, 0.0, -0.2)  # Turn back
        angles = [1.2, 0.2, -0.8, -0.5,
                  0.3, -0.4, 1.2, 1.5,  # Right uppercut
                  0.3, 0.0]
        times = [0.4] * 8 + [0.4, 0.4]
        self.motion.angleInterpolation(names, angles, times, True)
        time.sleep(0.3)

        # Final powerful double punch - BOTH ARMS
        angles = [0.7, 0.2, -1.5, -0.2,
                  0.7, -0.2, 1.5, 0.2,
                  0.0, -0.15]
        times = [0.4] * 8 + [0.4, 0.4]
        self.motion.angleInterpolation(names, angles, times, True)
        time.sleep(0.5)

        # Pull back to ready stance
        angles = [1.0, 0.3, -1.0, -0.8,
                  1.0, -0.3, 1.0, 0.8,
                  0.0, 0.0]
        times = [0.5] * 8 + [0.5, 0.5]
        self.motion.angleInterpolation(names, angles, times, True)
        time.sleep(0.5)

    def victory_stance(self):
        """42-60s: Victory Stance - Powerful finish and meditation"""
        print("[KungFu] Section 6: Victory Stance (42-60s)")

        # Announce section with TTS - triumphant! (in background thread to not block)
        import threading
        threading.Thread(target=lambda: self.tts.say("\\rspd=110\\Victory Stance!")).start()

        names = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll",
                 "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll",
                 "HeadYaw", "HeadPitch"]

        # Victory pose - both arms raised high
        angles = [0.0, 0.4, -1.3, -1.5,
                  0.0, -0.4, 1.3, 1.5,
                  0.0, -0.2]
        times = [2.0] * 8 + [2.0, 2.0]  # Slower rise to victory
        self.motion.angleInterpolation(names, angles, times, True)
        time.sleep(3.0)  # Hold victory pose longer

        # Slowly bring arms down to meditation position
        angles = [1.2, 0.15, -1.2, -0.5,
                  1.2, -0.15, 1.2, 0.5,
                  0.0, 0.0]
        times = [3.0] * 8 + [3.0, 3.0]  # Slower, more graceful
        self.motion.angleInterpolation(names, angles, times, True)
        time.sleep(2.0)

        # Deep respectful bow
        angles = [1.8, 0.15, -1.2, -0.5,
                  1.8, -0.15, 1.2, 0.5,
                  0.0, 0.4]
        times = [2.5] * 8 + [2.5, 2.5]  # Slower bow
        self.motion.angleInterpolation(names, angles, times, True)
        time.sleep(2.5)  # Hold bow longer for dramatic finish


class KungFuLEDAnimation(object):
    """Mystical LED effects for Kung Fu dance"""

    def __init__(self, leds):
        self.leds = leds
        self.running = False

    def start_animation(self):
        """Start LED animation (non-blocking)"""
        self.running = True

        # Use threading to animate LEDs in background
        import threading
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()

    def stop_animation(self):
        """Stop LED animation"""
        self.running = False
        try:
            # Reset LEDs to white
            self.leds.fadeRGB("FaceLeds", 1.0, 1.0, 1.0, 1.0)
        except:
            pass

    def _animate(self):
        """LED animation loop - deep reds, golds, and mystical purples
        Speeds up during aggressive sections (32-42 seconds)"""
        colors = [
            (0.8, 0.0, 0.0),   # Deep red
            (1.0, 0.6, 0.0),   # Gold
            (0.5, 0.0, 0.5),   # Mystical purple
            (0.8, 0.2, 0.0),   # Dark orange
            (0.6, 0.0, 0.3),   # Deep magenta
            (1.0, 0.0, 0.0),   # Bright red (for aggressive section)
        ]

        color_index = 0
        start_time = time.time()

        try:
            while self.running:
                elapsed = time.time() - start_time
                color = colors[color_index % len(colors)]

                # Faster transitions during aggressive section (32-42s)
                if 32 <= elapsed <= 42:
                    fade_time = 1.0  # Fast transitions for warrior strikes
                else:
                    fade_time = 4.0  # Slow transitions for graceful movements

                # Fade to next color
                self.leds.fadeRGB("FaceLeds", color[0], color[1], color[2], fade_time)

                # Also color chest LED
                self.leds.fadeRGB("ChestLeds", color[0], color[1], color[2], fade_time)

                time.sleep(fade_time)
                color_index += 1

        except Exception as e:
            print("[KungFu] LED animation error: {}".format(e))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mystical Kung Fu Dance")
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                      help="Robot IP address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=9559,
                      help="NAOqi port (default: 9559)")
    args = parser.parse_args()

    try:
        import qi

        # Connect to robot
        session = qi.Session()
        session.connect("tcp://{}:{}".format(args.ip, args.port))
        print("[KungFu] Connected to robot at {}:{}".format(args.ip, args.port))

        # Execute dance
        main(session)

    except RuntimeError as e:
        print("[KungFu] Connection error: {}".format(e))
        print("[KungFu] Make sure robot is on and NAOqi is running")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[KungFu] Dance interrupted by user")
        sys.exit(0)
