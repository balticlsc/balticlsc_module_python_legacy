from typing import List

from .job_rest_client import JobRestClient
from .logger import logger
from .pin import PinMetaData
from .status import ComputationStatus


def _pre_process(msg_uid: str, rest_client: JobRestClient):
    rest_client.update_status(msg_uid, 0.0, ComputationStatus.Working)


def _post_process(msg_uid: str, rest_client: JobRestClient):
    rest_client.update_status(msg_uid, 0.0, ComputationStatus.Idle)


class ProcessingInterface:
    def __init__(self, output_pins: List[PinMetaData]):
        self._output_pins = output_pins

    def run(self, rest_client: JobRestClient, msg_uid: str, input_pin: PinMetaData,
            input_access_details: dict):
        _pre_process(msg_uid, rest_client)

        try:
            self.process(rest_client, msg_uid, input_pin, input_access_details, self._output_pins)
        except BaseException as exception:
            error_msg = 'received  error while processing data: ' + str(exception)
            logger.error(error_msg)
            rest_client.send_ack_token(
                msg_uid=msg_uid,
                is_failed=True,
                is_final=True,
                note=error_msg,
            )

        if rest_client.get_computation_status() != ComputationStatus.Failed:
            _post_process(msg_uid, rest_client)

    def process(self, rest_client: JobRestClient, msg_uid: str,
                input_pin: PinMetaData, input_access_details: dict, output_pins: List[PinMetaData]):
        """Process input token and send the output (data + tokens)."""
        pass
