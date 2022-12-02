import socket

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

def main():
    s.connect(("192.168.0.143", 5000))
    while True:
        messaggio = input("Inserisci istruzione: ")
        s.sendall(messaggio.encode())

if __name__ == "__main__":
    main()