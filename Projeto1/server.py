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

    @classmethod
    def setup_socket(cls, host, port):
        cls._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cls._sock.bind((host, port))

    def recv_cmd(self):
        data, addr = self._sock.recvfrom(1400)
        print(f"Receiving from {addr}")
        data = data.decode('utf-8').split()

        # Formatar dados (chave deve ser um int, valor pode ter sido splitado)
        data[1] = int(data[1])
        if len(data) > 2:
            data[2] = ' '.join([i for i in data if data.index(i) >= 2])

        self.cmd_queue.put((addr, data))

    def exec_cmd(self):
        log = ''

        if not self.cmd_queue.empty():
            flag = 0
            dequeue = self.cmd_queue.get()
            entry = dequeue[1]
            key = entry[1]
            if len(entry) > 2:
                value = entry[2]
            key_exists = self.cmd_map.get(key)
            # create só ocorre somente se chave ainda não existir
            if entry[0] == 'create' and not key_exists:
                self.cmd_map.update({key: value})
                flag = 1
            # outras operações são possíveis somente se a chave já existe
            if key_exists:
                if entry[0] == 'read':
                    value = key_exists
                    flag = 1
                elif entry[0] == 'update':
                    self.cmd_map.update({key: value})
                    flag = 1
                elif entry[0] == 'delete':
                    self.cmd_map.pop(key)
                    flag = 1
        # flag (sucesso da operação) determina o conteudo do log
        if flag:
            log = f'success: {entry[0]} {{{key}: {value}}}'
        else:
            log = f'failed to perform {entry[0]} operation.'
        print(log)
        self._sock.sendto(log.encode('utf-8'), dequeue[0])
