from io import StringIO
import sys
import unittest
from unittest.mock import MagicMock, patch
import xmlrpc.client

# The function to be tested
def perform_xmlrpc_calls():
    # Connect to the server
    with xmlrpc.client.ServerProxy("http://localhost:8000/") as proxy:
        # Call gcd function
        gcd = proxy.gcd(54,24)
        print("GCD of 54 and 24 is", gcd)
        
        # Call fibonacci function
        fib = proxy.fibonacci(13)
        print("Fibonacci sequence up to 13 is", fib)

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to {parameter2}')

# Unit test class
class TestPerformXmlrpcCalls(unittest.TestCase):
    @patch('xmlrpc.client.ServerProxy')
    def test_perform_xmlrpc_calls(self, MockServerProxy):
        # Create a mock instance of ServerProxy
        mock_proxy = MagicMock()
        
        # Configure the mock to return specific values
        mock_proxy.gcd.return_value = 6
        mock_proxy.fibonacci.return_value = [0, 1, 1, 2, 3, 5, 8, 13]
        
        # Assign the mock instance to the ServerProxy patch
        MockServerProxy.return_value.__enter__.return_value = mock_proxy
        
        perform_xmlrpc_calls()
        
        # Check if the gcd method was called with expected arguments
        mock_proxy.gcd.assert_called_once_with(54, 24)
        assert_equal(mock_proxy.gcd(54, 24), 6)

        # Check if the fibonacci method was called with expected arguments
        mock_proxy.fibonacci.assert_called_once_with(13)
        assert_equal(mock_proxy.fibonacci(13), [0, 1, 1, 2, 3, 5, 8, 13])

# Run the unit tests
if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        perform_xmlrpc_calls()
    else:
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)
