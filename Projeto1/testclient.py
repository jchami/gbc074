import client
import json

if __name__ == '__main__':
    with open('config.json') as config:
        data = json.load(config)
    addr = (data['host'], data['port'])
    print(data)

    c = client.Client(*addr)
    print(client.Client._sock)
    c.send_input()
    c.recv_output()
    c.send_input()
    c.recv_output()
    # a = input()
