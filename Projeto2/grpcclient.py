import json
import grpc

import signalupdate_pb2
import signalupdate_pb2_grpc


def process_value():
    value = input("Type a value for your key:")
    while(len(value.encode('utf-8')) > 1450):
        print('Value cannot exceed 1400 bytes!')
        value = input()
    return value


def process_key():
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
            return int(key)
        else:
            print('Key cannot exceed 20 bytes!')


def process_cmd():
    cmd = ''
    valid_ops = ['create', 'read', 'update', 'delete', 'track']

    cmd = input('Create, Read, Update, Delete or Track?\n').lower()
    while cmd not in valid_ops:
        print('Invalid operation!')
        cmd = input().lower()
    return cmd


def run():
    while True:
        name = process_cmd()
        if name in ['read', 'delete']:
            key = process_key()
            response = stub.SignalUpdate(signalupdate_pb2.UpdateRequest(name=name, key=key))
        if name in ['create', 'update']:
            key = process_key()
            value = process_value()
            response = stub.SignalUpdate(signalupdate_pb2.UpdateRequest(name=name, key=key, value=value))
        if name == 'track':
            response = stub.SignalUpdate(signalupdate_pb2.UpdateRequest(name=name))
        if response.message:
            print(response.message)


if __name__ == '__main__':
    print("=====================GRPC-CLIENT=====================")
    with open('config.json') as config:
        data = json.load(config)

    addr = f"{data['host']}:{data['grpc_port']}"
    channel = grpc.insecure_channel(addr)
    stub = signalupdate_pb2_grpc.GreeterStub(channel)
    run()
