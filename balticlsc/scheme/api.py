import copy
import threading
import json
import os
from typing import Union, Type, Any

from flask import Flask, request, Response

from balticlsc.scheme.processing import ProcessingInterface
from balticlsc.scheme.status import ComputationStatus
from balticlsc.scheme.token import InputToken
from balticlsc.scheme.job_rest_client import JobRestClient
from balticlsc.scheme.pin import _load_pins, PinType, PinAttribute, ValuesAttribute, Pin
from balticlsc.scheme.logger import logger
from balticlsc.scheme.utils import camel_to_snake

SYS_APP_IP = os.getenv('SYS_APP_IP', '0.0.0.0')
SYS_APP_PORT = os.getenv('SYS_APP_PORT', 9100)
SYS_MODULE_INSTANCE_UID = os.getenv('SYS_MODULE_INSTANCE_UID', 'module_uid')
SYS_BATCH_MANAGER_TOKEN_ENDPOINT = os.getenv('SYS_BATCH_MANAGER_TOKEN_ENDPOINT', 'http://127.0.0.1:7000/token')
SYS_BATCH_MANAGER_ACK_ENDPOINT = os.getenv('SYS_BATCH_MANAGER_ACK_ENDPOINT', 'http://127.0.0.1:7000/ack')
SYS_MODULE_NAME = os.getenv('SYS_MODULE_NAME', 'BalticLSC module')
SYS_MODULE_DESCRIPTION = os.getenv('SYS_MODULE_DESCRIPTION', 'BalticLSC module instance.')
SYS_PIN_CONFIG_FILE_PATH = os.getenv('SYS_PIN_CONFIG_FILE_PATH', '/app/module/configs/pins.json')


class __ApiState:
    def __init__(self, processing: Type[ProcessingInterface]):
        self.processing = processing
        self.rest_client = JobRestClient(
            url_token=SYS_BATCH_MANAGER_TOKEN_ENDPOINT,
            url_ack=SYS_BATCH_MANAGER_ACK_ENDPOINT,
            sender_uid=SYS_MODULE_INSTANCE_UID)
        logger.info('working on path=' + os.getcwd())

        try:
            self.pins = _load_pins(SYS_PIN_CONFIG_FILE_PATH)
            self.input_pin_name_to_value = self.pins.get_name_to_pin(PinType.INPUT)
            self.output_pin_name_to_value = self.pins.get_name_to_pin(PinType.OUTPUT)
            logger.info('input pins from config:' + str(self.input_pin_name_to_value))
        except BaseException as exception:
            error_msg = 'error while loading pins: ' + str(exception)
            logger.error(error_msg)
            self.rest_client.send_ack_token(
                msg_uids=['empty'],
                is_final=True,
                is_failed=True,
                note=error_msg,
            )


__api_state: Union[__ApiState, None] = None


def __load_input_pin_attribute(input_pin: Pin, attribute_name: str, value_from_token: Any):
    input_attribute_value = input_pin.getattr(attribute_name)

    if input_attribute_value is None:
        input_attribute_value = value_from_token
        logger.info(f'using input "{attribute_name}" from token values = {input_attribute_value}')
    else:
        logger.info(f'using input "{attribute_name}" from config = {input_attribute_value}')

    if type(input_attribute_value) == dict:
        input_attribute_value = {camel_to_snake(key): value for key, value in input_attribute_value.items()}

    input_pin.set_opt_attr(attribute_name, input_attribute_value)


def init_baltic_api(processing: Type[ProcessingInterface]) -> (Flask, JobRestClient):
    global __api_state
    __api_state = __ApiState(processing)
    app = Flask(SYS_MODULE_NAME)

    @app.route('/token', methods=['POST'])
    def process_token():
        logger.info('received the following token: ' + str(request.json))

        try:
            input_token = InputToken(**{camel_to_snake(key): value for key, value in request.json.items()})
        except TypeError as type_error:
            error_msg = 'error while loading input token: ' + str(type_error)
            logger.error(error_msg)
            __api_state.rest_client.send_ack_token(
                msg_uids=['empty'],
                is_final=True,
                is_failed=True,
                note=error_msg,
            )
            return Response(json.dumps({'success': False, 'data': error_msg}), status=200,
                            mimetype='application/json')

        logger.info('input token: ' + str(input_token))
        input_token_values = {camel_to_snake(key): value for key, value in json.loads(input_token.get_values()).items()}

        if input_token.get_pin_name() not in __api_state.input_pin_name_to_value:
            logger.info('missing pin with name: ' + input_token.get_pin_name())
            return Response(json.dumps(
                {'success': False, 'data': 'missing pin with name ' + input_token.get_pin_name() + ' in the config'}),
                 status=400, mimetype='application/json')
        else:
            try:
                input_pin = copy.deepcopy(__api_state.input_pin_name_to_value[input_token.get_pin_name()])
                __load_input_pin_attribute(input_pin, PinAttribute.ACCESS_CREDENTIAL,
                                           input_token_values.get(PinAttribute.ACCESS_CREDENTIAL))
                __load_input_pin_attribute(input_pin, PinAttribute.ACCESS_PATH,
                                           input_token_values.get(ValuesAttribute.RESOURCE_PATH))
                __load_input_pin_attribute(input_pin, PinAttribute.ACCESS_TYPE,
                                           input_token_values.get(PinAttribute.ACCESS_TYPE))
                module_processing = __api_state.processing(__api_state.output_pin_name_to_value)
                logger.info('running token on pin with name=' + input_token.get_pin_name())
                __api_state.rest_client.update_status(status=ComputationStatus.Working)
                pin_task = threading.Thread(target=module_processing.run,
                                            name=input_token.get_pin_name() + ' pin, id = ' + input_token.get_msg_uid(),
                                            args=(input_token.get_msg_uid(), input_pin))
                pin_task.daemon = True
                pin_task.start()
            except BaseException as exception:
                error_msg = f'processing data error: {str(exception)}'
                logger.error(error_msg)
                __api_state.rest_client.send_ack_token(
                    msg_uids=[input_token.get_msg_uid()],
                    is_final=True,
                    is_failed=True,
                    note=error_msg,
                )

        return Response(status=200)

    @app.route('/status', methods=['GET'])
    def get_status():
        return __api_state.rest_client.get_job_status().to_json()

    return app, __api_state.rest_client
