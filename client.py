import socket

HEADER = 4096
PORT = 5006
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'
SERVER = "192.168.0.109"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def inputPiecePosition(text):
    row = col = -1
    while True:
        try:
            row = int(input(f'Enter {text} row: '))
        except KeyboardInterrupt:
            print('\n\nGood Bye\n')
        
        if 1 <= row <= 8:
            break
        else:
            print('\nInvalid number! Try again!\n')
    
    while True:
        try:
            col = int(input(f'Enter {text} column: '))
        except KeyboardInterrupt:
            print('\n\nGood Bye\n')

        if 1 <= col <= 8:
            break
        else:
            print('\nInvalid number! Try again!\n')
    
    return row, col


def selectPlayer():
    starter = ''
    while starter not in 'wWbB':
        try:
            starter = str(input('Who starts?\nW - White\nB - Black\n--> ')).lower()
        except KeyboardInterrupt:
            print('\n\nGood Bye\n')
            client.close()
            exit()

    client.send(starter.encode(FORMAT))


def send():
    """
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    print(client.recv(2048).decode(FORMAT))

    msg_length = client.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        msg = client.recv(msg_length).decode(FORMAT)
        print(msg)
    """
    
    while True:
        server_input = client.recv(HEADER).decode(FORMAT)
        server_input = str(server_input)
        print(server_input)
        if server_input == 'CLEAR':
            clear = client.recv(HEADER).decode(FORMAT)
            clear = str(clear)
            # print(clear)
        if server_input == 'SELECT':
            selection = selectPlayer()
            client.send(selection.encode(FORMAT))


send()
