import json
from collections import defaultdict
from typing import List, Dict, Any

from balticlsc.scheme.logger import logger
from balticlsc.scheme.utils import JsonRepr, camel_to_snake


class PinType:
    INPUT = 'input'
    OUTPUT = 'output'


class AccessType:
    FTP = 'ftp'


class PinAttribute:
    NAME = 'pin_name'
    TYPE = 'pin_type'
    ACCESS_PATH = 'access_path'
    ACCESS_TYPE = 'access_type'
    ACCESS_CREDENTIAL = 'access_credential'
    TOKEN_MULTIPLICITY = 'token_multiplicity'
    DATA_MULTIPLICITY = 'data_multiplicity'
    VALUES = 'values'


class ValuesAttribute:
    RESOURCE_PATH = 'resource_path'


class Pin(JsonRepr):
    __required_attributes = [
        PinAttribute.NAME,
        PinAttribute.TYPE,
    ]
    __optional_attributes = [
        PinAttribute.ACCESS_PATH,
        PinAttribute.ACCESS_TYPE,
        PinAttribute.ACCESS_CREDENTIAL,
        PinAttribute.TOKEN_MULTIPLICITY,
        PinAttribute.DATA_MULTIPLICITY,
        PinAttribute.VALUES,
    ]

    def __init__(self, attributes: Dict[str, Any]):
        for attribute_name in Pin.__required_attributes:
            if attribute_name in attributes:
                attribute_value = attributes[attribute_name]

                if attribute_name == PinAttribute.TYPE and attribute_value not in {PinType.INPUT, PinType.OUTPUT}:
                    raise ValueError(f'unknown pin type = "{attribute_value}"')

                self.__setattr__('_' + attribute_name, attribute_value)
            else:
                raise ValueError('required attribute "' + attribute_name + '" is missing in config')

        for attribute_name, attribute_value in attributes.items():
            if attribute_name in Pin.__required_attributes:
                continue
            elif attribute_name in self.__optional_attributes:
                self.__setattr__('_' + attribute_name, attribute_value)
            else:
                logger.warning(f'unknown attribute "{attribute_name}" in the config file, omitting')

    def getattr(self, name: str) -> Any:
        try:
            return self.__getattribute__('_' + name)
        except AttributeError:
            logger.info(f'pin {self.__repr__()} do not have attribute "{name}"')
            return None

    # set value of an optional attribute
    def set_opt_attr(self, name: str, value: Any) -> Any:
        if name in self.__optional_attributes:
            return self.__setattr__('_' + name, value)
        else:
            error_msg = f'{name} is not an optional argument of a Pin'
            logger.error(error_msg)
            raise ValueError(error_msg)


class Pins:
    def __init__(self):
        self._type_to_pins = defaultdict(set)

    def add_pin(self, pin: Pin):
        self._type_to_pins[pin.getattr(PinAttribute.TYPE)].add(pin)

    def get_name_to_pin(self, pin_type: PinType) -> Dict[str, Pin]:
        return {pin.getattr(PinAttribute.NAME): pin for pin in self._type_to_pins[pin_type]}


def _load_pin(pin_json: dict) -> Pin:
    try:
        pin_meta_data = Pin({camel_to_snake(key): value for key, value in pin_json.items()})
    except BaseException as exception:
        error_msg: str = 'wrong config for pin json:' + str(pin_json) + ', error: ' + str(exception)
        raise ValueError(error_msg) from exception

    return pin_meta_data


def _load_pins(config_file_path: str) -> Pins:
    with open(config_file_path) as json_file:
        try:
            return _load_pins_from_json(json.load(json_file))
        except BaseException as exception:
            error_msg = 'error while loading config from ' + config_file_path + ': ' + str(exception)
            raise ValueError(error_msg) from exception


def _load_pins_from_json(config: List[dict]) -> Pins:
    pins = Pins()

    for pin_json in config:
        pins.add_pin(_load_pin(pin_json))

    return pins


class MissingPin(Exception):
    """Exception raised when specific pin is missing.

    Attributes:
        pins -- set of pins where we look for a specific pin
        missing_pin_name -- the name of a missing pin
    """

    def __init__(self, pins: List[Pin], missing_pin_name: str):
        self._message = f'missing pin "{missing_pin_name}" in {pins}'
        super().__init__(self._message)

    def __str__(self):
        return self._message
