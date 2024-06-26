from io import StringIO
import os
import select
import socket
import sys
import unittest
from unittest import mock
import zlib


def handle_client(client_socket):
    # Send the welcome message
    client_socket.sendall("welcome")
    
    # Receive and process commands
    while True:
        # Receive the command
        data = client_socket.recv(1024)
        data = data.decode('utf-8')
        
        print(f'Received: {data.strip()}')

        # Send the response
        # if data starts with 'EHLO'  send '250 Hello\r\n'
        # etc.
        # Handle the FTP command
        if data.upper().startswith('EHLO'):
            client_socket.sendall(b'250 Hello\r\n')
        elif data.upper().startswith('PASS'):
            client_socket.sendall(zlib.compress(b'230 User logged in\r\n'))
        elif data.upper().startswith('PWD'):
            working_dir =  os.getcwd()

            # send success message
            client_socket.sendall(zlib.compress(f'257 "{working_dir}"\r\n'.encode('utf-8')))
        else:
            client_socket.sendall(zlib.compress(b'502 Command not implemented\r\n'))

    # close the socket
    client_socket.close()

def start_smtp_server(address='localhost', port=1025):
    # create a socket, bind it to the address and port, and start listening
    server_address = (address, port)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(server_address)
    server_socket.listen(5)

    inputs = [server_socket]
    client_data = {}

    while True:
        # accept a connection
        readable, _, _ = select.select(inputs, [], [])
        for s in readable:
            if s is server_socket:
                # accept client
                client_sock, client_address = server_socket.accept()
                client_sock.setblocking(False)

                # append to inputs
                inputs.append(client_sock)
                
                # initiate a value client_data dictionary 
                # key: client_sock, value: b''
                client_data[client_sock] = b''

                print(f"?")

                # send welcome message
                client_sock.sendall("welcome")
            else:
                # receive data
                data = s.recv(1024)
                if data:
                    client_data[s] += data
                    if b'\r\n' in self.client_data[s]:
                        break
                else:
                    # remove socket from inputs
                    inputs.remove(s)
                    # delete from client_data dict
                    del client_data[s]

                    # close socket
                s.close()

        # handle the client
        for client in inputs:
            handle_client(client)

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

class TestSMTPServer(unittest.TestCase):

    @mock.patch('socket.socket')
    def test_handle_client(self, mock_socket):
        # Mock the client socket
        mock_client_socket = mock.Mock()

        # Simulate a sequence of client commands and expected responses
        command_response_pairs = [
            (b'EHLO example.com\r\n', b'250 Hello\r\n'),
            (b'MAIL FROM:<test@example.com>\r\n', b'250 OK\r\n'),
            (b'RCPT TO:<recipient@example.com>\r\n', b'250 OK\r\n'),
            (b'DATA\r\n', b'354 End data with <CR><LF>.<CR><LF>\r\n'),
            (b'.\r\n', b'250 OK: message accepted for delivery\r\n'),
            (b'QUIT\r\n', b'221 Bye\r\n'),
        ]

        # Configure the mock to return each command in sequence when recv is called
        mock_client_socket.recv.side_effect = [command for command, _ in command_response_pairs] + [b'']

        # Call the handle_client function with the mock socket
        handle_client(mock_client_socket)

        # Check that send was called with the expected responses
        expected_calls = [call(response) for _, response in command_response_pairs]
        mock_client_socket.send.assert_has_calls(expected_calls, any_order=False)
        print(f"sending calls: {mock_client_socket.send.call_args_list}")

        # Check that the socket was closed
        mock_client_socket.close.assert_called_once()
        print(f"closing calls: {mock_client_socket.close.call_args_list}")

if __name__ == '__main__':
    runner = unittest.TextTestRunner(stream=NullWriter())
    unittest.main(testRunner=runner, exit=False)
