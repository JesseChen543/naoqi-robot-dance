#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
base_motion.py - Base Motion Class for Pepper Robot

DESCRIPTION:
    Provides base class for all motion modules with NAOqi connection management,
    service initialization, and common motion utilities.

FEATURES:
    - NAOqi session and service management
    - Automatic service initialization
    - Error handling and logging
    - Common motion utilities (wake up, rest, posture control)

DEPENDENCIES:
    - Python 2.7 (NAOqi SDK)
    - qi
    - naoqi

USAGE:
    This is a base class, not meant to be used directly.
    See walk.py, arm.py, or navigation.py for concrete implementations.
"""

import qi
import sys


class BaseMotion(object):
    """Base class for all Pepper motion modules"""

    def __init__(self, session):
        """
        Initialize base motion controller

        Args:
            session: qi.Session object connected to Pepper
        """
        self.session = session
        self._init_services()

    def _init_services(self):
        """Initialize NAOqi services"""
        try:
            self.motion = self.session.service("ALMotion")
            self.posture = self.session.service("ALRobotPosture")
            self.memory = self.session.service("ALMemory")
            self.autonomous_life = self.session.service("ALAutonomousLife")
            print("[BaseMotion] Services initialized successfully")
        except RuntimeError as e:
            print("[BaseMotion] Error initializing services:", str(e))
            sys.exit(1)

    def wake_up(self):
        """Wake up the robot (enable motors)"""
        try:
            self.motion.wakeUp()
            print("[BaseMotion] Robot woken up")
            return True
        except Exception as e:
            print("[BaseMotion] Error waking up:", str(e))
            return False

    def rest(self):
        """Put robot to rest (disable motors)"""
        try:
            self.motion.rest()
            print("[BaseMotion] Robot at rest")
            return True
        except Exception as e:
            print("[BaseMotion] Error resting:", str(e))
            return False

    def go_to_posture(self, posture_name, speed=1.0):
        """
        Move robot to a predefined posture

        Args:
            posture_name: str - Name of posture (Stand, StandInit, StandZero, Sit, Crouch, etc.)
            speed: float - Speed of movement (0.0 to 1.0)

        Returns:
            bool - True if successful
        """
        try:
            self.posture.goToPosture(posture_name, speed)
            print("[BaseMotion] Posture changed to:", posture_name)
            return True
        except Exception as e:
            print("[BaseMotion] Error changing posture:", str(e))
            return False

    def get_posture(self):
        """
        Get current robot posture

        Returns:
            str - Current posture name
        """
        try:
            current = self.posture.getPosture()
            return current
        except Exception as e:
            print("[BaseMotion] Error getting posture:", str(e))
            return None

    def emergency_stop(self):
        """Emergency stop - kills all motion immediately"""
        try:
            self.motion.killAll()
            print("[BaseMotion] EMERGENCY STOP executed")
            return True
        except Exception as e:
            print("[BaseMotion] Error in emergency stop:", str(e))
            return False

    def enable_movement(self):
        """Enable movement and disable collision protection"""
        try:
            # Try to disable collision protection for all parts
            try:
                # Disable for different body parts
                self.motion.setCollisionProtectionEnabled("Arms", False)
                print("[BaseMotion] Arms collision protection disabled")
            except Exception as e:
                print("[BaseMotion] Arms collision note:", str(e))

            try:
                self.motion.setCollisionProtectionEnabled("Move", False)
                print("[BaseMotion] Move collision protection disabled")
            except Exception as e:
                print("[BaseMotion] Move collision note:", str(e))

            # CRITICAL: Disable external collision protection
            # This is the main blocker for movement!
            try:
                self.motion.setExternalCollisionProtectionEnabled("All", False)
                print("[BaseMotion] External collision protection DISABLED")
                # Verify it was disabled
                try:
                    is_enabled = self.motion.getExternalCollisionProtectionEnabled("All")
                    if is_enabled:
                        print("[BaseMotion] WARNING: External collision still enabled after disable attempt!")
                    else:
                        print("[BaseMotion] External collision successfully disabled")
                except:
                    pass
            except Exception as e:
                print("[BaseMotion] External collision error:", str(e))

            print("[BaseMotion] Movement protection adjusted")
            return True
        except Exception as e:
            print("[BaseMotion] Error enabling movement:", str(e))
            return False

    def check_move_enabled(self):
        """Check if movement is enabled"""
        try:
            # Check autonomous life state
            life_state = self.autonomous_life.getState()
            print("[BaseMotion] Autonomous Life state: {}".format(life_state))

            # Check collision protection
            try:
                collision = self.motion.getCollisionProtectionEnabled("Arms")
                print("[BaseMotion] Collision protection (Arms): {}".format(collision))
            except Exception as e:
                print("[BaseMotion] Collision check note:", str(e))

            return True
        except Exception as e:
            print("[BaseMotion] Error checking move status:", str(e))
            return False

    def disable_autonomous_life(self):
        """Disable autonomous life to allow manual movement control"""
        try:
            current_state = self.autonomous_life.getState()
            print("[BaseMotion] Current Autonomous Life state: {}".format(current_state))

            if current_state != "disabled":
                self.autonomous_life.setState("disabled")
                print("[BaseMotion] Autonomous Life disabled")
            else:
                print("[BaseMotion] Autonomous Life already disabled")

            return True
        except Exception as e:
            print("[BaseMotion] Error disabling autonomous life:", str(e))
            return False

    def enable_autonomous_life(self):
        """Re-enable autonomous life"""
        try:
            self.autonomous_life.setState("solitary")
            print("[BaseMotion] Autonomous Life re-enabled (solitary mode)")
            return True
        except Exception as e:
            print("[BaseMotion] Error enabling autonomous life:", str(e))
            return False


def connect_to_pepper(ip="127.0.0.1", port=9559):
    """
    Helper function to connect to Pepper and return session

    Args:
        ip: str - IP address of Pepper (default: 127.0.0.1 for localhost)
        port: int - NAOqi port (default: 9559)

    Returns:
        qi.Session object or None if connection failed
    """
    try:
        print("[BaseMotion] Connecting to Pepper at {}:{}...".format(ip, port))
        session = qi.Session()
        session.connect("tcp://{}:{}".format(ip, port))
        print("[BaseMotion] Connected successfully!")
        return session
    except RuntimeError as e:
        print("[BaseMotion] Connection failed:", str(e))
        return None
