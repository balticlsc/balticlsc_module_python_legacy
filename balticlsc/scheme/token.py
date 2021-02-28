from typing import List

from balticlsc.scheme.utils import JsonRepr


class Token(JsonRepr):
    pass


class InputToken(Token):
    def __init__(self, msg_uid: str, pin_name: str, values: str,
                 access_type: dict = None, token_seq_stack: List[dict] = None):
        self._msg_uid = msg_uid
        self._pin_name = pin_name
        self._values = values
        self._access_type = access_type

        if token_seq_stack is None:
            self._seq_stack = None
        else:
            seq_stack = []

            for seq_token in token_seq_stack:
                seq_stack.append(XSeqToken(**seq_token))

            self._seq_stack = seq_stack

    def get_values(self) -> str:
        return self._values

    def get_pin_name(self) -> str:
        return self._pin_name

    def get_msg_uid(self) -> str:
        return self._msg_uid


class OutputToken(Token):
    def __init__(self, pin_name: str, sender_uid: str, values: str, base_msg_uid: str, is_final: bool):
        self._pin_name = pin_name
        self._sender_uid = sender_uid
        self._values = values
        self._base_msg_uid = base_msg_uid
        self._is_final = is_final


class XSeqToken(Token):
    def __init__(self, seq_uid: str, no: int, is_final: bool):
        self._seq_uid = seq_uid
        self._no = no
        self._is_final = is_final


class AckToken(Token):
    def __init__(self, sender_uid: str, msg_uids: List[str], note: str, is_final: bool, is_failed: bool = False):
        self._sender_uid = sender_uid
        self._msg_uids = msg_uids
        self._note = note
        self._is_final = is_final
        self._is_failed = is_failed
