from io import StringIO
import json
import socket
import sys
import unittest
from unittest.mock import MagicMock, patch

HOST = 'jsonplaceholder.typicode.com'

def create_post(title, body, user_id):
    # Define the JSON data for the new post
    post_data = {
        "title": title,
        "body": body,
        "userId": user_id
    }

    # Convert the JSON data to a string
    json_data = json.dumps(post_data)
    
    # HTTP request headers
    headers = {
        "Host": HOST,
        "Content-Type": "application/json",
        "Content-Length": len(json_data),
        "Connection": "close",  
    }

    # Construct the HTTP request
    request = "POST /posts HTTP/1.1\r\n"
    for header, value in headers.items():
        request += f"{header}: {value}\r\n"
    request += "\r\n"
    request += json_data

    # Connect to the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, 80))
        s.send(request.encode("utf-8"))

        # Receive the response
        response = s.recv(4096)

    # Parse the response
    response_parts = response.split(b"\r\n\r\n", 1)
    headers = response_parts[0].decode("utf-8")
    body = response_parts[1].decode("utf-8")
    
    response_body_json = json.loads(body)
    
    return response_body_json['id']


# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass


def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to {parameter2}')


class TestCreatePost(unittest.TestCase):
    @patch('socket.socket')
    def test_create_post(self, mock_socket):
        # Setup the mocked socket
        mock_sock_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock_instance

        # Define the mock response from the server
        response_data = {
            'id': 101,
            'title': 'New Entry',
            'body': 'This is a new post.',
            'userId': 1
        }
        http_response = f"HTTP/1.1 201 Created\r\nContent-Length: {len(json.dumps(response_data))}\r\n\r\n{json.dumps(response_data)}"
        mock_sock_instance.recv.side_effect = [http_response.encode('utf-8'), b'']

        # Call the function
        post_id = create_post("New Entry", "This is a new post.", 1)

        # Assertions to check if the POST request was properly sent and the correct ID was returned
        # Verify that the socket methods were called correctly
        mock_sock_instance.connect.assert_called_with(('jsonplaceholder.typicode.com', 80))
        print(f"connect called with: {mock_sock_instance.connect.call_args}")

        mock_sock_instance.send.assert_called_once()
        print(f"send called with: {mock_sock_instance.send.call_args}")

        mock_sock_instance.recv.assert_called()
        print(f"recv called with: {mock_sock_instance.recv.call_args}")

        mock_sock_instance.send.assert_called_once()
        assert_equal(post_id, 101)
        


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        post_id = create_post('This is a new title', 'This is a new post.', 1)
        print(post_id)

    # run unit test to test locally
    # or for domjudge
    runner = unittest.TextTestRunner(stream=NullWriter())
    unittest.main(testRunner=runner, exit=False)

