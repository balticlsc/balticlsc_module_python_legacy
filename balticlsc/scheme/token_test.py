import unittest

from balticlsc.scheme.token import InputToken
from balticlsc.scheme.utils import camel_to_snake


class TestInputToken(unittest.TestCase):
    def test_simple_correct_json(self):
        token_json: dict = {
            'MsgUid': '1',
            'PinName': 'Input',
            'Values': '{\"ResourcePath\": \"/files/recogniser/in\"}'
        }
        try:
            InputToken(**{camel_to_snake(key): value for key, value in token_json.items()})
        except BaseException as exception:
            self.assert_(False, exception)

    def test_incorrect_json(self):
        token_json: dict = {
            'MsgUid': '2',
            'PinName': 'Input1',
            'Values': '{\"ResourcePath\": \"/files/recogniser/in\"}',
            'SthElse': ''
        }
        try:
            InputToken(**{camel_to_snake(key): value for key, value in token_json.items()})
            self.assert_(False, 'test failed, should raise an error')
        except BaseException as exception:
            print(exception)


if __name__ == '__main__':
    unittest.main()
