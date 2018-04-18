import socket
import threading
from queue import Queue


class Server:
    _sock = None

    def __init__(self, host, port):
        Server.setup_socket(host, port)
        self.host = host
        self.port = port
        self.flag = True
        self.cmd_queue = Queue()
        self.exec_queue = Queue()
        self.log_queue = Queue()
        self.cmd_map = {}
        self.read_map_log()

    @classmethod
    def setup_socket(cls, host, port):
        cls._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cls._sock.bind((host, port))

    def setup_threads(self):
        recv_thread = threading.Thread(name='recv_thread',
                                       target=self.recv_cmd)
        recv_thread.start()
        exec_thread = threading.Thread(name='process_thread',
                                       target=self.process_cmd)
        exec_thread.start()

        return recv_thread, exec_thread

    def write_map_log(self):
        with open('map.log', 'w') as logfile:
            for key in self.cmd_map.keys():
                logfile.write(f'{key} {self.cmd_map[key]}\n')

    def read_map_log(self):
        with open('map.log') as logfile:
            for line in logfile:
                line = line.split()
                if len(line) >= 2:
                    line[1] = ' '.join([i for i in line if line.index(i) > 0])
                self.cmd_map.update({int(line[0]): line[1]})

    def recv_cmd(self):
        while True:
            data, addr = self._sock.recvfrom(1400)
            print(f"Receiving request from {addr}")
            data = data.decode('utf-8').split()

            data[1] = int(data[1])
            if len(data) > 2:
                data[2] = ' '.join([i for i in data if data.index(i) >= 2])

            self.cmd_queue.put((addr, data))

    def process_cmd(self):
        while True:
            if not self.cmd_queue.empty():
                next_cmd = self.cmd_queue.get()
                self.exec_queue.put(next_cmd)
                self.log_queue.put(next_cmd)
                self.flag = False
                self.exec_cmd()

    def exec_cmd(self):
        if self.exec_queue.empty():
            return

        result = ''
        dequeue = self.exec_queue.get()
        success = 0
        entry = dequeue[1]
        key = entry[1]
        value = ''
        key_exists = self.cmd_map.get(key)

        if len(entry) > 2:
            value = entry[2]

        if entry[0] == 'create' and not key_exists:
            self.cmd_map.update({key: value})
            success = 1

        if key_exists:
            if entry[0] == 'read':
                value = key_exists
                success = 1
            elif entry[0] == 'update':
                self.cmd_map.update({key: value})
                success = 1
            elif entry[0] == 'delete':
                value = key_exists
                self.cmd_map.pop(key)
                success = 1

        log_entry = f'{entry[0]} {{{key}: {value}}}'
        if success:
            result = f'success: {log_entry}'
        else:
            result = f'failed to {entry[0]} key {key}.'
        print(result)
        self.flag = True
        self._sock.sendto(result.encode('utf-8'), dequeue[0])
        self.write_map_log()
