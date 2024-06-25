import datetime
from io import StringIO
import socket
import time
import sys
import pickle
import json
import unittest
from unittest.mock import MagicMock, patch

class Message:
    def __init__(self, username, text):
        self.username = username
        self.text = text
        self.timestamp = time.asctime(time.localtime(time.time()))

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(serialized_message):
        message_dict = pickle.loads(serialized_message)
        message = message_dict
        return message

def main():
    username = str(input())
    text = str(input())

    message = Message(username, text)
    serialized_message = message.serialize()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # connect to server
        s.connect(('localhost', 12345))
        # send message to server
        s.sendall(serialized_message)
        print("Message sent to the server.")


# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to {parameter2}')


class TestChatClient(unittest.TestCase):

    def test_message_serialization(self):
        username = "Alice"
        text = "Hello, World!"
        message = Message(username, text)
        serialized_message = message.serialize()
        
        # Deserialize to verify
        deserialized_message = Message.deserialize(serialized_message)
        
        assert_equal(deserialized_message.username, username)
        assert_equal(deserialized_message.text, text)
        self.assertIsInstance(datetime.strptime(deserialized_message.timestamp, '%Y-%m-%d %H:%M:%S.%f'), datetime)

    @patch('builtins.input', side_effect=['Alice', 'Hello, World!'])
    @patch('socket.socket')
    def test_client_main(self, mock_socket_class, mock_input):
        mock_socket_instance = MagicMock()
        mock_socket_class.return_value.__enter__.return_value = mock_socket_instance
        
        main()
        
        # Check if the connect method was called with the correct parameters
        mock_socket_instance.connect.assert_called_once_with(('localhost', 12345))
        # Check if the sendall method was called at least once
        self.assertTrue(mock_socket_instance.sendall.called, "sendall was not called")
        
        # Get the arguments with which sendall was called
        sent_data = mock_socket_instance.sendall.call_args[0][0]
        deserialized_message = Message.deserialize(sent_data)
        
        assert_equal(deserialized_message.text, 'Hello, World!')
        assert_equal(deserialized_message.username, 'Alice')
        self.assertIsInstance(datetime.strptime(deserialized_message.timestamp, '%Y-%m-%d %H:%M:%S.%f'), datetime)

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        main()
    
    else:
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)
