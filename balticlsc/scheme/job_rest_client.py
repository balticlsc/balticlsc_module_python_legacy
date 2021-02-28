from typing import List

import requests
import json

from balticlsc.scheme.logger import logger
from balticlsc.scheme.status import JobStatus, ComputationStatus
from balticlsc.scheme.token import AckToken, OutputToken, Token
from balticlsc.scheme.utils import snake_to_camel


class JobRestClient:
    def __init__(self, url_token: str, url_ack: str, sender_uid: str):
        self._url_token = url_token
        self._url_ack = url_ack
        self._sender_uid = sender_uid
        self._module_status = JobStatus()

    def send_output_token(self, base_msg_uid: str, values: dict, output_pin_name, is_final=True):
        msg = OutputToken(
            pin_name=output_pin_name,
            sender_uid=self._sender_uid,
            values=json.dumps({snake_to_camel(key): value for key, value in values.items()}),
            base_msg_uid=base_msg_uid,
            is_final=is_final)
        JobRestClient.__send_msg_to_batch_manager(msg, self._url_token)

    def send_ack_token(self, msg_uids: List[str], is_final=False, is_failed=False, note=''):
        msg = AckToken(
            sender_uid=self._sender_uid,
            msg_uids=msg_uids,
            is_final=is_final,
            is_failed=is_failed,
            note=note)
        JobRestClient.__send_msg_to_batch_manager(msg, self._url_ack)

    def get_job_status(self) -> JobStatus:
        return self._module_status

    def get_computation_status(self) -> ComputationStatus:
        return self._module_status.get_computation_status()

    def update_status(self, status: ComputationStatus = ComputationStatus.Working, job_progress: float = 0.0):
        self._module_status.update(status, job_progress)

    @staticmethod
    def __send_msg_to_batch_manager(token: Token, url):
        token_json = token.to_json()
        logger.info(f'sending message to batch manager, url={url}, message={token_json}')
        requests.post(url, data=token_json, headers={'content-type': 'application/json'})
