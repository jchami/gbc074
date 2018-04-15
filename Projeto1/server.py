import socket
import threading
from queue import Queue


class Server:
    _sock = None

    def __init__(self, host, port):
        Server.setup_socket(host, port)
        self.host = host
        self.port = port
        self.cmd_queue = Queue()
        self.cmd_map = {}
        self.read_log()

    @classmethod
    def setup_socket(cls, host, port):
        cls._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cls._sock.bind((host, port))

    def setup_threads(self):
        recv_thread = threading.Thread(name='recv_thread',
                                       target=self.recv_cmd)
        recv_thread.start()
        exec_thread = threading.Thread(name='exec_thread',
                                       target=self.exec_cmd)
        exec_thread.start()

        return recv_thread, exec_thread

    def write_log(self):
        with open('map.log', 'w') as logfile:
            for key in self.cmd_map.keys():
                logfile.write(f'{key} {self.cmd_map[key]}\n')

    def read_log(self):
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

    def exec_cmd(self):
        while True:
            try:
                result = ''
                if not self.cmd_queue.empty():
                    dequeue = self.cmd_queue.get()
                    flag = 0
                    entry = dequeue[1]
                    key = entry[1]
                    if len(entry) > 2:
                        value = entry[2]
                    key_exists = self.cmd_map.get(key)

                    if entry[0] == 'create' and not key_exists:
                        self.cmd_map.update({key: value})
                        flag = 1

                    if key_exists:
                        if entry[0] == 'read':
                            value = key_exists
                            flag = 1
                        elif entry[0] == 'update':
                            self.cmd_map.update({key: value})
                            flag = 1
                        elif entry[0] == 'delete':
                            value = key_exists
                            self.cmd_map.pop(key)
                            flag = 1

                    if flag:
                        result = f'success: {entry[0]} {{{key}: {value}}}'
                    else:
                        result = f'failed to perform {entry[0]} operation.'
                    print(result)
                    self._sock.sendto(result.encode('utf-8'), dequeue[0])
                    self.write_log()
            except Exception:
                pass
