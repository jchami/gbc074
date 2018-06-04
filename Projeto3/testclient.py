import client

if __name__ == '__main__':
    print("=====================CLIENT-SIDE=====================")
    c = client.Client()
    c1, c2 = c.setup_threads()
