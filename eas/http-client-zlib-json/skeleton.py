from io import StringIO
import json
import socket
import sys
import unittest
from unittest.mock import patch
import zlib

def get_first_length(data):
    """Get the length of the first part of the response, including the header and the content if Content-Length is present."""
    header = data.split('\r\n\r\n')[0]
    header_length = len(header)
    content_length = 0
    for line in header.split('\r\n'):
        if line.lower().startswith('content-length:'):
            content_length = line.split(' ')[1]
    
    return header_length + int(content_length)  

def create_socket():
    """Create a client socket and connect to the server."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 8080)
    client_socket.connect(server_address)
    return client_socket

def client():
    """Send a GET request to the server and print the response."""
    # Create socket and Send the request
    client_socket = create_socket()
    
    request_header = b'GET index.html HTTP/1.1\r\nHost: localhost\r\n\r\n'
    client_socket.send(request_header)

    # Receive the response
    response = ''
    while True:
        # Receive data
        received = client_socket.recv(1024)
        decoded_received = received.decode('utf-8')
        print(decoded_received)
        first_length = get_first_length(decoded_received)
        response += decoded_received

        # Break if no more data
        if not received or first_length < 1024:
            break

    # Decode and Print the response
    print(response)

    # Get the status code
    status_code = response.split(' ')[1]

    # Print the status code
    if status_code == 200:
        print(status_code)
    print(status_code)


    # Close the socket 
    client_socket.close()

    # Decompress and parse JSON content
    body = response.split('\r\n\r\n')[1]
    content = zlib.decompress(body)
    json_content = json.loads(content)
    
    print(json_content)

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to {parameter2}')

class TestHttpClient(unittest.TestCase):
    def test_get_first_length_no_content_length(self):
        print('Testing get_first_length_no_content_length ...')
        data = "HTTP/1.1 200 OK\r\nServer: TestServer\r\n\r\n"
        assert_equal(get_first_length(data), len(data.split('\r\n\r\n')[0]))

    def test_get_first_length_with_content_length(self):
        print('Testing get_first_length_with_content_length ...')
        data = "HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\n12345"
        assert_equal(get_first_length(data), len(data.split('\r\n\r\n')[0]) + 5)

    @patch('socket.socket')
    def test_create_socket(self, mock_socket):
        print('Testing create_socket ...')
        create_socket()
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        instance = mock_socket.return_value
        instance.connect.assert_called_once_with(('localhost', 8080))
        print(f"connect called with: {instance.connect.call_args}")

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        client()

    # run unit test to test locally
    # or for domjudge
    runner = unittest.TextTestRunner(stream=NullWriter())
    unittest.main(testRunner=runner, exit=False)
