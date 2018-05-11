import socket
import threading


class Client:
    _sock = None

    def __init__(self, host, port):
        Client.setup_socket()
        self.flag = True
        self.addr = (host, port)

    @classmethod
    def setup_socket(cls):
        cls._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def setup_threads(self):
        input_thread = threading.Thread(name='input_thread',
                                        target=self.send_input)
        input_thread.start()
        output_thread = threading.Thread(name='output_thread',
                                         target=self.recv_output)
        output_thread.start()

        return input_thread, output_thread

    def send_input(self):
        while True:
            if self.flag:
                message = self.process_input()
                print(message)
                self._sock.sendto(message, self.addr)
                self.flag = False
                print(f'Sending to {self.addr}...')

    def recv_output(self):
        while True:
            output, address = self._sock.recvfrom(1400)
            print(output.decode('utf-8'))
            self.flag = True

    def process_input(self):
        cmd = self.process_cmd()
        key = self.process_key()
        value = self.process_value(cmd)

        return ' '.join([cmd, key, value]).encode('utf-8')

    def process_cmd(self):
        cmd = ''
        valid_ops = ['create', 'read', 'update', 'delete']

        cmd = input('Create, Read, Update or Delete?\n').lower()
        while cmd not in valid_ops:
            print('Invalid operation!')
            cmd = input().lower()
        return cmd

    def process_key(self):
        print('Type your key:')
        while True:
            key = input()
            try:
                int(key)
            except ValueError:
                print("Key must be an integer!")

            # Smallest 'int' object is of size 24 bytes
            # For that reason I am considering 24 + 20 bytes for key size check
            if int(key) < (2 ** 150):
                return key
            else:
                print('Key cannot exceed 20 bytes!')

    def process_value(self, cmd):
        value = ''
        if cmd in ['create', 'update']:
            value = input("Type a value for your key:")
        while(len(value.encode('utf-8')) > 1450):
            print('Value cannot exceed 1400 bytes!')
            value = input()
        return value
