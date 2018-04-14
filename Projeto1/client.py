import socket
import threading


class Client:
    _sock = None

    def __init__(self, host, port):
        Client.setup_socket()
        self.addr = (host, port)

    @classmethod
    def setup_socket(cls):
        cls._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_input(self):
        message = self.process_input()
        self._sock.sendto(message.encode('utf-8'), self.addr)

    def recv_output(self):
        output, address = self._sock.recvfrom(1400)
        print(output.decode('utf-8'))

    def process_input(self):
        valid_ops = ['create', 'read', 'update', 'delete']
        cmd = key = value = ''

        print('Create, Read, Update or Delete?')
        while cmd not in valid_ops:
            cmd = input()
            cmd = cmd.lower()

        print('Type your key:')
        while True:
            key = input()
            try:
                int(key)
                break
            except ValueError:
                pass
            print('Invalid key value')

        if cmd in ['create', 'update']:
            value = input("Type a value for your key:")

        return ' '.join([cmd, key, value])
