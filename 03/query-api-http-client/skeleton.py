import http.client
from io import StringIO
import sys
import unittest
import json
from unittest import mock

HOST = 'jsonplaceholder.typicode.com'

def get_post_count():
    connection = http.client.HTTPConnection(HOST)
    
    connection.request('GET', '/posts')
    
    response = connection.getresponse()
    connection.close()

    body = response.read()
    
    json_body = json.loads(body)
    
    count = sum(1 for data in json_body if "voluptate" in data['body'])
    
    return count

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass


def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to {parameter2}')


class TestGetPostCount(unittest.TestCase):
    @mock.patch('http.client.HTTPConnection')
    def test_get_post_count(self, mock_conn):
        # Mock the response
        mock_response = mock.Mock()
        mock_response.read.return_value = b'[{"body": "voluptate"}, {"body": "non-voluptate"}]'
        mock_conn.return_value.getresponse.return_value = mock_response

        # Call the function under test
        result = get_post_count()

        # Assert the connection was made with the correct arguments
        mock_conn.assert_called_once_with('jsonplaceholder.typicode.com')
        print(f"connection called with: {mock_conn.call_args}")

        mock_conn.return_value.request.assert_called_once_with("GET", "/posts")
        print(f"request called with: {mock_conn.return_value.request.call_args}")

        mock_response.read.assert_called_once()
        print(f"response read called with: {mock_response.read.return_value}")

        mock_conn.return_value.close.assert_called_once()
        print(f"connection closed: {mock_conn.return_value.close.call_args}")

        # Assert the result
        assert_equal(result, 2)

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        post_count = get_post_count()
        print(post_count)

    # run unit test to test locally
    # or for domjudge
    runner = unittest.TextTestRunner(stream=NullWriter())
    unittest.main(testRunner=runner, exit=False)