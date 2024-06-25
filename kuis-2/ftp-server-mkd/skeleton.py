from datetime import datetime
from io import StringIO
import logging
import socket
import pickle
import sys
import json
import select
import unittest
from unittest import mock
from unittest.mock import MagicMock, patch


class FTPServer:
    def __init__(self, host='127.0.0.1', port=2000):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind
        self.sock.bind((self.host, self.port))
        # listen
        self.sock.listen(5)

        self.sock.setblocking(False)
        self.inputs = [self.sock]
        self.client_data = {}

        print(f"Listening on {self.host}:{self.port}")

    def start(self):
        while True:
            readable, _, _ = select.select([], [], self.inputs)
            for s in readable:
                if s is self.sock:
                    # accept client
                    client_sock, client_address = self.sock.accept()
                    client_sock.setblocking(False)

                    # append to inputs
                    self.inputs.append(client_sock)

                    # initiate a value client_data dictionary 
                    # key: client_sock, value: b''
                    self.client_data[client_sock] = b''

                    print(f"?")

                    # send welcome message
                    client_sock.sendall("welcome")
                else:
                    # receive data
                    data = s.recv(1024)
                    if data:
                        self.client_data[s] += data
                        if b'\r\n' in self.client_data[s]:
                            break
                    else:
                        # remove socket from inputs
                        self.inputs.remove(s)
                        # delete from client_data dict
                        del self.client_data[s]

                        # close socket
                        s.close()

    def handle_client(self, client_sock):
        # decode data and don't forget to strip
        data = self.client_data[client_sock].decode('utf-8').strip()
        self.client_data[client_sock] = b''
        print(f"Received command: {data}")

        # use startswith to fill in the blanks
        if data.upper().startswith('USER'):
            client_sock.sendall(b'331 Username OK, need password\r\n')
        elif data.upper().startswith('PASS'):
            client_sock.sendall(b'230 User logged in\r\n')
        elif data.upper().startswith('MKD'):
            dirname = data.split()[1]
            try:
                # create directory


                # send success message
                client_sock.sendall(f'257 Directory "{dirname}" created\r\n'.encode('utf-8'))
            except Exception as e:
                client_sock.sendall(f'550 Failed to create directory "{dirname}": {e}\r\n'.encode('utf-8'))
        
        elif data.upper().startswith('QUIT'):
            # send goodbye message
            client_sock.sendall(b'221 Goodbye\r\n')
            # remove socket from inputs
            self.inputs.remove(client_sock)
            # delete from client_data dict
            del self.client_data[client_sock]
            # close socket
            client_sock.close()
        else:
            client_sock.sendall(b'502 Command not implemented\r\n')


# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass


class TestFTPServer(unittest.TestCase):
    def setUp(self):
        self.server = FTPServer()

    def tearDown(self):
        self.server.sock.close()

    def test_handle_client_user(self):
        client_sock = mock.Mock()
        self.server.client_data = {client_sock: b'USER valid_username\r\n'}
        self.server.handle_client(client_sock)
        client_sock.sendall.assert_called_with(b'331 Username OK, need password\r\n')

    def test_handle_client_pass(self):
        client_sock = mock.Mock()
        self.server.client_data = {client_sock: b'PASS valid_password\r\n'}
        self.server.handle_client(client_sock)
        client_sock.sendall.assert_called_with(b'230 User logged in\r\n')

    def test_handle_client_mkd_success(self):
        client_sock = mock.Mock()
        self.server.client_data = {client_sock: b'MKD valid_path/test_dir\r\n'}
        self.server.handle_client(client_sock)
        client_sock.sendall.assert_called_with(b'257 Directory "valid_path/test_dir" created\r\n')

    def test_handle_client_quit(self):
        client_sock = mock.Mock()
        self.server.client_data = {client_sock: b'QUIT\r\n'}
        self.server.inputs.append(client_sock)
        self.server.handle_client(client_sock)
        client_sock.sendall.assert_called_with(b'221 Goodbye\r\n')
        self.assertEqual(self.server.inputs, [self.server.sock])
        self.assertNotIn(client_sock, self.server.client_data)
        client_sock.close.assert_called_once()

    def test_handle_client_unknown_command(self):
        client_sock = mock.Mock()
        self.server.client_data = {client_sock: b'UNKNOWN_COMMAND\r\n'}
        self.server.handle_client(client_sock)
        client_sock.sendall.assert_called_with(b'502 Command not implemented\r\n')

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        ftp_server = FTPServer()
        ftp_server.start()
    
    else:
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)
