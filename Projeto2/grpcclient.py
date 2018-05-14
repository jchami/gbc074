import json
import grpc

import signalupdate_pb2
import signalupdate_pb2_grpc


def run():
    while True:
        response = stub.SignalUpdate(signalupdate_pb2.UpdateRequest())
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
