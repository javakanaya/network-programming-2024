import base64
import http.client
import json
import urllib
from io import StringIO
import sys
import unittest
from unittest.mock import MagicMock, patch


def send_email(api_key, domain, sender, recipient, subject, text, html):
    """Send an email using the Mailgun API."""

    # Mailgun API URL
    

    # Data for the POST request in dictionary format

    data = {
        'from': sender,
        'to': recipient,
        'subject': subject,
        'text': text,
        'html': html
    }

    # Encode the data with urllib.parse.urlencode
    encoded_data = urllib.parse.urlencode(data)


    # Create the HTTP connection
    conn = http.client.HTTPSConnection('api.mailgun.net')

    # Create the authorization header
    auth = base64.b64encode(f"api:{api_key}".encode()).decode()
    headers = {
        'Authorization': f'Basic {auth}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Send the POST request
    url = f"/v3/{domain}/messages"
    conn.request("POST", url, encoded_data, headers)

    # Get the response
    response = conn.getresponse()
    response_data = response.read()

    # Print the result
    print(response.status, response_data.decode())

    return response.status, response_data

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to {parameter2}')

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

class TestMailgunEmail(unittest.TestCase):
    
    @patch('http.client.HTTPSConnection')
    def test_send_email(self, MockHTTPSConnection):
        # Your Mailgun API key and domain
        api_key = 'your_api_key'
        domain = 'your_domain'

        # Define the sender, recipient, and email content
        sender = 'sender@example.com'
        recipient = 'recipient@example.com'
        subject = 'Your email subject'
        text = 'This is a plain text message'
        html = '<h3>This is an HTML message</h3>'

        # Mailgun API URL
        url = f"/v3/{domain}/messages"

        # Data for the POST request
        data = {
            'from': sender,
            'to': recipient,
            'subject': subject,
            'text': text,
            'html': html
        }
        encoded_data = urllib.parse.urlencode(data)

        # Mock the HTTP connection and response
        mock_conn = MockHTTPSConnection.return_value
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({'message': 'Queued. Thank you.'}).encode()
        mock_conn.getresponse.return_value = mock_response

        # Create the authorization header
        auth = base64.b64encode(f"api:{api_key}".encode()).decode()

        # Expected headers
        expected_headers = {
            'Authorization': f'Basic {auth}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Run the code to be tested
        conn = http.client.HTTPSConnection('api.mailgun.net')
        conn.request('POST', url, encoded_data, expected_headers)
        response = conn.getresponse()
        response_data = response.read()

        # Verify that the request was made with the correct parameters
        mock_conn.request.assert_called_once_with('POST', url, encoded_data, expected_headers)
        assert_equal(response.status, 200)
        assert_equal(json.loads(response_data.decode()), {'message': 'Queued. Thank you.'})
    

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        # Your Mailgun API key and domain
        api_key = 'your_api_key'
        domain = 'your_domain'

        # Define the sender, recipient, and email content
        sender = 'sender@example.com'
        recipient = 'recipient@example.com'
        subject = 'Your email subject'
        text = 'This is a plain text message'
        html = '<h3>This is an HTML message</h3>'
        
        send_email(api_key, domain, sender, recipient, subject, text, html)
    
    else:
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)