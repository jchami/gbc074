import client
import json

if __name__ == '__main__':
    with open('config.json') as config:
        data = json.load(config)
    addr = (data['host'], data['port'])

    print("=====================CLIENT-SIDE=====================")
    c = client.Client(*addr)
    c1, c2 = c.setup_threads()
