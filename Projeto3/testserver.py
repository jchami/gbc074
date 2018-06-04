import server

if __name__ == '__main__':
    print("=====================SERVER-SIDE=====================")
    s = server.Server()
    a, b, c = s.setup_threads()
