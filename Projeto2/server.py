import socket
import threading
from queue import Queue

import time
import grpc
from concurrent import futures

import crud_pb2
import crud_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class gRPC_server():
    server = None

    def __init__(self, grpc_port):
        gRPC_server.setup(grpc_port)

    @classmethod
    def setup(cls, grpc_port):
        cls.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        crud_pb2_grpc.add_MapServicer_to_server(Map(), cls.server)
        port = f'[::]:{grpc_port}'
        cls.server.add_insecure_port(port)

    def serve(self):
        gRPC_server.server.start()
        try:
            while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            gRPC_server.server.stop(0)


class Server:
    _sock = None

    def __init__(self, host='localhost', port=8000, grpc_port=50051):
        Server.setup_socket(host, port)
        self.grpc = gRPC_server(grpc_port)
        self.host = host
        self.port = port
        self.flag = True
        self.cmd_queue = Queue()
        self.exec_queue = Queue()
        self.log_queue = Queue()
        self.tracked = set()
        self.cmd_map = Map()
        self.read_map_log()

    @classmethod
    def setup_socket(cls, host, port):
        cls._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cls._sock.bind((host, port))

    def setup_threads(self):
        recv_thread = threading.Thread(name='recv_thread',
                                       target=self.recv_cmd)
        recv_thread.start()
        exec_thread = threading.Thread(name='queues_thread',
                                       target=self.organize_queues)
        exec_thread.start()

        grpc_thread = threading.Thread(name='grpc_thread',
                                       target=self.grpc.serve)
        grpc_thread.start()

        return recv_thread, exec_thread, grpc_thread

    def write_cmd_log(self, result):
        if self.log_queue.empty():
            return
        req = self.log_queue.get()
        origin = req[0]
        cmd = req[1][0]
        key = req[1][1]

        with open('cmd.log', 'a') as cmd_log:
            if result:
                cmd_log.write(f'{origin}: success: {cmd} key {key}\n')
            else:
                cmd_log.write(f'{origin}: failed to {cmd} key {key}\n')

    def read_map_log(self):
        with open('map.log') as logfile:
            for line in logfile:
                line = line.split()
                if len(line) >= 2:
                    line[1] = ' '.join([i for i in line if line.index(i) > 0])
                self.cmd_map.cmd_map.update({int(line[0]): line[1]})

    def recv_cmd(self):
        while True:
            data, addr = self._sock.recvfrom(1400)
            print(f"Receiving request from {addr}")
            data = data.decode('utf-8').split()
            print(data)

            data[1] = int(data[1])
            if len(data) > 2:
                data[2] = ' '.join([i for i in data if data.index(i) >= 2])

            self.cmd_queue.put((addr, data))

    def organize_queues(self):
        while True:
            if not self.cmd_queue.empty():
                return

            self.flag = False

            next_cmd = self.cmd_queue.get()
            self.exec_queue.put(next_cmd)
            self.log_queue.put(next_cmd)
            result = self.process_cmd()
            self.write_cmd_log(result)

            self.flag = True

    def process_cmd(self):
        if self.exec_queue.empty():
            return

        command = self.exec_queue.get()
        origin = command[0]
        entry = command[1]

        operation = entry[0]
        key = entry[1]
        value = entry[2] if len(entry) > 2 else ''
        success, result = self.cmd_map.exec_cmd(operation, key, value)
        print(result)

        if key in self.tracked:
            self.grpc.add_update(result)
        self._sock.sendto(result.encode('utf-8'), origin)
        self.cmd_map.write_log()
        return success


class Map(crud_pb2_grpc.MapServicer):
    def __init__(self):
        self.flag = False
        self.cmd_map = {}
        self.tracked = {}
        self.read_map_log()

    def exec_cmd(self, operation, key, value):
        key_in_map = self.cmd_map.get(key)
        success = False
        result = ''

        if operation == 'track' and key not in self.tracked:
            self.tracked.update({key: []})
            success = True
        elif operation == 'create' and not key_in_map:
            self.cmd_map.update({key: value})
            success = True
        elif operation != 'create' and key_in_map:
            if operation == 'read':
                value = key_in_map
            elif operation == 'update':
                self.cmd_map.update({key: value})
            elif operation == 'delete':
                value = key_in_map
                self.cmd_map.pop(key)
            success = True

        log_entry = f'{operation} {{{key}: {value}}}'
        if success:
            result = f'success: {log_entry}'
        else:
            result = f'failed to {operation} key {key}.'

        if key in self.tracked:
            self.tracked[key].append(result)
            self.flag = True
        return success, result

    def Crud(self, request, context):
        op = request.name
        key = request.key
        value = request.value
        success, result = self.exec_cmd(op, key, value)
        return crud_pb2.CommandReply(message=result)
        self.write_log()

    def Track(self, request, context):
        updates = self.tracked[request.key]
        while True:
            if updates and self.flag:
                for command in updates:
                    updates.pop(0)
                    yield crud_pb2.CommandReply(message=command)
                self.flag = False
            else:
                continue

    def write_log(self):
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