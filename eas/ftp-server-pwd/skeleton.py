from io import StringIO
import os
import select
import socket
import sys
import unittest
from unittest import mock
import zlib


class FTPServer:
    def __init__(self, host='127.0.0.1', port=2000):
        """Create a new FTP server listening on the specified host and port."""
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
            readable, _, _ = select.select(self.inputs, [], [])
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
        """Handle a new client connection."""
        # Read the data from the client socket and decompress
        data = zlib.decompress(self.client_data[client_sock]).decode('utf-8').strip()
        self.client_data[client_sock] = b''
        print(f"Received command: {data}")

        # Handle the FTP command
        if data.upper().startswith('USER'):
            client_sock.sendall(zlib.compress(b'331 Username OK, need password\r\n'))
        elif data.upper().startswith('PASS'):
            client_sock.sendall(zlib.compress(b'230 User logged in\r\n'))
        elif data.upper().startswith('PWD'):
            working_dir =  os.getcwd()

            # send success message
            client_sock.sendall(zlib.compress(f'257 "{working_dir}"\r\n'.encode('utf-8')))
        elif data.upper().startswith('QUIT'):
            # send goodbye message
            client_sock.sendall(zlib.compress(b'221 Goodbye\r\n'))
            # remove socket from inputs
            self.inputs.remove(client_sock)
            # delete from client_data dict
            del self.client_data[client_sock]
            # close socket
            client_sock.close()
        else:
            client_sock.sendall(zlib.compress(b'502 Command not implemented\r\n'))


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
        self.server.client_data = {client_sock: zlib.compress(b'USER valid_username\r\n')}
        self.server.handle_client(client_sock)
        client_sock.sendall.assert_called_with(zlib.compress(b'331 Username OK, need password\r\n'))

    def test_handle_client_pass(self):
        client_sock = mock.Mock()
        self.server.client_data = {client_sock: zlib.compress(b'PASS valid_password\r\n')}
        self.server.handle_client(client_sock)
        client_sock.sendall.assert_called_with(zlib.compress(b'230 User logged in\r\n'))

    def test_handle_client_pwd(self):
        client_sock = mock.Mock()
        self.server.client_data = {client_sock: zlib.compress(b'PWD\r\n')}
        with mock.patch('os.getcwd', return_value='/mock/directory'):
            self.server.handle_client(client_sock)
            client_sock.sendall.assert_called_with(zlib.compress(b'257 "/mock/directory"\r\n'))

    def test_handle_client_quit(self):
        client_sock = mock.Mock()
        self.server.client_data = {client_sock: zlib.compress(b'QUIT\r\n')}
        self.server.inputs.append(client_sock)
        self.server.handle_client(client_sock)
        client_sock.sendall.assert_called_with(zlib.compress(b'221 Goodbye\r\n'))
        self.assertEqual(self.server.inputs, [self.server.sock])
        self.assertNotIn(client_sock, self.server.client_data)
        client_sock.close.assert_called_once()

    def test_handle_client_unknown_command(self):
        client_sock = mock.Mock()
        self.server.client_data = {client_sock: zlib.compress(b'UNKNOWN_COMMAND\r\n')}
        self.server.handle_client(client_sock)
        client_sock.sendall.assert_called_with(zlib.compress(b'502 Command not implemented\r\n'))

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        ftp_server = FTPServer()
        ftp_server.start()
    
    else:
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)
