import server
import json

if __name__ == '__main__':
    with open('config.json') as config:
        data = json.load(config)
    addr = (data['host'], data['port'])
    print(data)

    s = server.Server(*addr)
    print(server.Server._sock)
    s.recv_cmd()
    s.exec_cmd()
    s.recv_cmd()
    s.exec_cmd()
    print(s.cmd_queue.get())
    # a = input()
