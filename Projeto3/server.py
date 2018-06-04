import time
import json
import socket
import threading
import datetime
from os import listdir
from queue import Queue


class Server:
    _SOCK = None
    _SETTINGS = None

    def __init__(self):
        Server.settings_from_json()
        self.host = Server._SETTINGS["HOST"]
        self.port = Server._SETTINGS["PORT"]
        Server.setup_socket(self.host, self.port)
        self.cli_flag = True
        self.log_flag = False
        self.cmd_queue = Queue()
        self.exec_queue = Queue()
        self.log_queue = Queue()
        self.cmd_map = {}
        self.read_from_snapshot()
        self.recover_from_log()

    @classmethod
    def settings_from_json(cls):
        with open('config.json') as config:
            Server._SETTINGS = json.load(config)

    @classmethod
    def setup_socket(cls, host, port):
        cls._SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cls._SOCK.bind((host, port))

    def setup_threads(self):
        recv_thread = threading.Thread(name='recv_thread',
                                       target=self.recv_cmd)
        recv_thread.start()

        exec_thread = threading.Thread(name='process_thread',
                                       target=self.process_cmd)
        exec_thread.start()

        snapshot_thread = threading.Thread(name='snapshot_thread',
                                           target=self.scheduled_snapshots)
        snapshot_thread.start()

        return recv_thread, exec_thread, snapshot_thread

    def scheduled_snapshots(self):
        while True:
            time.sleep(Server._SETTINGS["SNAPSHOT_INTERVAL"])
            print('Writing snapshots...')
            self.write_snapshots()

    def write_cmd_log(self, timestamp, result):
        if self.log_queue.empty():
            return
        next_cmd = self.log_queue.get()
        cmd = next_cmd[1][0]
        key = next_cmd[1][1]
        value = ''
        if len(next_cmd[1]) > 2:
            value = next_cmd[1][2]

        with open('cmd.log', 'a') as cmd_log:
            if result:
                cmd_log.write(f'{str(timestamp)} {cmd} {key} {value}\n')
            else:
                cmd_log.write(f'{str(timestamp)} {cmd} {key} {value}\n')

    def recover_from_log(self):
        print("Recovering commands from logfile...")
        self.log_flag = True
        with open('cmd.log') as logfile:
            for line in logfile:
                next_cmd = line.split()[2:]
                next_cmd[1] = int(next_cmd[1])
                if len(next_cmd) > 2:
                    next_cmd[2] = ' '.join([i for i in next_cmd if next_cmd.index(i) >= 2])
                    next_cmd = next_cmd[:3]
                print(next_cmd)
                self.exec_queue.put((None, next_cmd))
                self.exec_cmd()
        print('State recovered from logfile.')
        self.log_flag = False

    def write_snapshots(self):
        for i in range(0, Server._SETTINGS["NO_OF_SNAPSHOTS"]):
            self.write_snapshot(f'./Snapshots/snap{i+1}.log')

        print("Snapshots saved.")
        input()
        with open('cmd.log', 'w') as logfile:
            logfile.write('')

    def write_snapshot(self, filename):
        with open(filename, 'w') as snapshot:
            for key in self.cmd_map.keys():
                snapshot.write(f'{key} {self.cmd_map[key]}\n')

    def read_from_snapshot(self):
        snapshots = listdir('./Snapshots')
        if not snapshots:
            return
        with open(f'./Snapshots/{snapshots[0]}') as snapshot:
            for line in snapshot:
                line = line.split()
                if len(line) >= 2:
                    line[1] = ' '.join([i for i in line if line.index(i) > 0])
                self.cmd_map.update({int(line[0]): line[1]})

    def recv_cmd(self):
        while True:
            data, addr = self._SOCK.recvfrom(1400)
            print(f"Receiving request from {addr}")
            data = data.decode('utf-8').split()
            print(data)

            data[1] = int(data[1])
            if len(data) > 2:
                data[2] = ' '.join([i for i in data if data.index(i) >= 2])

            self.cmd_queue.put((addr, data))

    def process_cmd(self):
        while True:
            if self.log_flag:
                return
            if not self.cmd_queue.empty():
                return
            self.cli_flag = False
            next_cmd = self.cmd_queue.get()
            self.exec_queue.put(next_cmd)
            timestamp = datetime.datetime.now()
            self.log_queue.put(next_cmd)
            result = self.exec_cmd()
            self.write_cmd_log(timestamp, result)
            self.cli_flag = True

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
        if dequeue[0]:
            self._SOCK.sendto(result.encode('utf-8'), dequeue[0])
        return success
