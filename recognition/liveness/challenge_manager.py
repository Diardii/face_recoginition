import random
import time

from config import (
    LIVENESS_CHALLENGE_TIMEOUT,
    LIVENESS_CONFIRM_FRAMES
)

from recognition.liveness.head_pose import HeadPoseEstimator


class ChallengeManager:

    STATE_IDLE = "IDLE"
    STATE_WAITING = "WAITING"
    STATE_PASSED = "PASSED"
    STATE_FAILED = "FAILED"

    def __init__(
        self,
        timeout=LIVENESS_CHALLENGE_TIMEOUT,
        confirm_frames=LIVENESS_CONFIRM_FRAMES
    ):
        self.timeout = float(timeout)
        self.confirm_frames = int(confirm_frames)

        self.pose_estimator = HeadPoseEstimator()

        self.person_id = None
        self.challenge = None
        self.state = self.STATE_IDLE
        self.started_at = None
        self.match_count = 0

    def start(self, person_id):
        """
        Memulai tantangan baru untuk satu person.
        """

        self.person_id = person_id
        self.challenge = random.choice([
            HeadPoseEstimator.LEFT,
            HeadPoseEstimator.RIGHT
        ])

        self.state = self.STATE_WAITING
        self.started_at = time.time()
        self.match_count = 0

        return self.get_status()

    def reset(self):
        self.person_id = None
        self.challenge = None
        self.state = self.STATE_IDLE
        self.started_at = None
        self.match_count = 0

    def process(self, face, person_id):
        """
        Memproses landmark wajah pada setiap frame.
        """

        if not person_id:
            self.reset()
            return self.get_status(
                message="Person ID tidak tersedia."
            )

        # Tantangan baru jika belum ada atau person berubah
        if (
            self.state == self.STATE_IDLE
            or self.person_id != person_id
        ):
            return self.start(person_id)

        if self.state in (
            self.STATE_PASSED,
            self.STATE_FAILED
        ):
            return self.get_status()

        elapsed = time.time() - self.started_at
        remaining = max(0.0, self.timeout - elapsed)

        if elapsed > self.timeout:
            self.state = self.STATE_FAILED

            return self.get_status(
                message="Waktu tantangan habis."
            )

        pose = self.pose_estimator.estimate(face)

        if not pose["valid"]:
            self.match_count = 0

            return self.get_status(
                direction=pose["direction"],
                offset=pose["offset"],
                remaining=remaining,
                message=pose["message"]
            )

        direction = pose["direction"]

        if direction == self.challenge:
            self.match_count += 1
        else:
            self.match_count = 0

        if self.match_count >= self.confirm_frames:
            self.state = self.STATE_PASSED

            return self.get_status(
                direction=direction,
                offset=pose["offset"],
                remaining=remaining,
                message="Tantangan berhasil."
            )

        return self.get_status(
            direction=direction,
            offset=pose["offset"],
            remaining=remaining,
            message="Menunggu gerakan yang sesuai."
        )

    def instruction(self):
        if self.challenge == HeadPoseEstimator.LEFT:
            return "Silakan menoleh ke kiri."

        if self.challenge == HeadPoseEstimator.RIGHT:
            return "Silakan menoleh ke kanan."

        return "Menunggu tantangan."

    def get_status(
        self,
        direction=HeadPoseEstimator.UNKNOWN,
        offset=0.0,
        remaining=None,
        message=None
    ):
        if remaining is None:
            if self.started_at is None:
                remaining = self.timeout
            else:
                elapsed = time.time() - self.started_at
                remaining = max(0.0, self.timeout - elapsed)

        return {
            "person_id": self.person_id,
            "challenge": self.challenge,
            "instruction": self.instruction(),
            "state": self.state,
            "passed": self.state == self.STATE_PASSED,
            "failed": self.state == self.STATE_FAILED,
            "direction": direction,
            "offset": round(float(offset), 4),
            "match_count": self.match_count,
            "confirm_frames": self.confirm_frames,
            "remaining": round(float(remaining), 1),
            "message": message or self.state
        }
