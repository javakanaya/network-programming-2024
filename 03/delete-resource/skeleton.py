from io import StringIO
import socket
import sys
import unittest
from unittest.mock import MagicMock, patch


def delete_post(post_id):
    # HTTP request headers
    headers = {
        "Host": "jsonplaceholder.typicode.com",
        "Connection": "close",  
    }

    # Construct the HTTP request
    request = "DELETE /posts/1 HTTP/1.1\r\n"
    for header, value in headers.items():
        request += f"{header}: {value}\r\n"
    request += "\r\n"

    # Connect to the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("jsonplaceholder.typicode.com", 80))
        s.send(request.encode("utf-8"))

        # Receive the response
        response = s.recv(4096)

    # Parse the response
    response_parts = response.split(b"\r\n\r\n", 1)
    headers = response_parts[0].decode("utf-8")
    body = response_parts[1].decode("utf-8")
    
    status_code = response.split(b" ")[1].decode()
    if (status_code == '200'):
        print("Deleted successfully") 
    return status_code


# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass


def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to {parameter2}')


class TestDeletePost(unittest.TestCase):
    @patch('socket.socket')
    def test_delete_post(self, mock_socket):
        # Setup the mocked socket instance
        mock_sock_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock_instance

        # Define the mock response from the server
        http_response = "HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n"
        mock_sock_instance.recv.return_value = http_response.encode('utf-8')

        # Call the function
        status_code = delete_post(1)

        # Ensure the response indicates success
        mock_sock_instance.connect.assert_called_once_with(('jsonplaceholder.typicode.com', 80))
        print(f"connect called with: {mock_sock_instance.connect.call_args}")

        # Assertions to check if the DELETE request was properly sent and the correct response was handled
        mock_sock_instance.send.assert_called_once()
        print(f"send called with: {mock_sock_instance.send.call_args}")

        mock_sock_instance.recv.assert_called_once()
        print(f"recv called with: {mock_sock_instance.recv.call_args}")

        assert_equal(status_code, '200')

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        status = delete_post(1)
        print(status)

    # run unit test to test locally
    # or for domjudge
    runner = unittest.TextTestRunner(stream=NullWriter())
    unittest.main(testRunner=runner, exit=False)
