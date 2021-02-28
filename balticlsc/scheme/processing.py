import abc
from typing import Dict

from balticlsc.scheme.pin import Pin


class ProcessingInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'process') and
                callable(subclass.process) or
                NotImplemented)

    def __init__(self, output_pin_name_to_value: Dict[str, Pin]):
        self._output_pin_name_to_value = output_pin_name_to_value

    def run(self, msg_uid: str, input_pin: Pin):
        self.process(msg_uid, input_pin, self._output_pin_name_to_value)

    @abc.abstractmethod
    def process(self, msg_uid: str, input_pin: Pin, output_pin_name_to_value: Dict[str, Pin]) -> None:
        """Process input token and send the output (data + tokens)."""
        pass
