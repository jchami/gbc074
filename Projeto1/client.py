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
                self._sock.sendto(message.encode('utf-8'), self.addr)
                self.flag = False
                print(f'Sending to {self.addr}...')

    def recv_output(self):
        while True:
            output, address = self._sock.recvfrom(1400)
            print(output.decode('utf-8'))
            self.flag = True

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

        if cmd in ['create', 'update']:
            value = input("Type a value for your key:")

        return ' '.join([cmd, key, value])
