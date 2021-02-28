from enum import Enum

from balticlsc.scheme.utils import JsonRepr


class ComputationStatus(Enum):
    Idle = 1,
    Working = 2,
    Completed = 3,
    Failed = 4,
    Rejected = 5,
    Aborted = 6,
    Neglected = 7


class JobStatus(JsonRepr):
    def __init__(self, status: ComputationStatus = ComputationStatus.Idle, job_progress: float = 0.0):
        self._status = status
        self._job_progress = job_progress

    def get_computation_status(self):
        return self._status

    def get_job_progress(self):
        return self._job_progress

    def update(self, status: ComputationStatus, job_progress: float = 0.0):
        self._status = status

        if job_progress != 0.0:
            self._job_progress = job_progress
