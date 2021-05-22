import socket
import threading

HEADER = 4096
PORT = 5006
# SERVER = socket.gethostbyname(socket.gethostname())
SERVER = "192.168.0.109"
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


"""
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
--------------------------------------- CHECKERS ---------------------------------------
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
"""
from copy import deepcopy

startBoard = [
    ['B', ' ', 'B', ' ', 'B', ' ', 'B', ' '],
    [' ', 'B', ' ', 'B', ' ', 'B', ' ', 'B'],
    ['B', ' ', 'B', ' ', 'B', ' ', 'B', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', 'W', ' ', 'W', ' ', 'W', ' ', 'W'],
    ['W', ' ', 'W', ' ', 'W', ' ', 'W', ' '],
    [' ', 'W', ' ', 'W', ' ', 'W', ' ', 'W'],
]
board = deepcopy(startBoard)


def clearScreen(conn):
    print('[CLEARING SCREEN]')
    msg = '\n\n\n\n\n\n\n\n'
    message = msg.encode(FORMAT)
    conn.send('CLEAR'.encode(FORMAT))
    conn.send(message)


def set_board_send(board):
    send_board = ''
    for rowIndex, row in enumerate(board):
        if rowIndex != 0:
            send_board += '---+---+---+---+---+---+---+---\n'
        for colIndex, col in enumerate(row):
            if colIndex != 0:
                send_board += '|'
            send_board += f' {col} '
        send_board += '\n'
    
    return send_board


def printBoard(conn, board):
    send_board = set_board_send(board)
    conn.send(send_board.encode(FORMAT))


def inputPiecePosition(conn, text):
    conn.send('INPUT_X'.encode(FORMAT))
    conn.send(f'{text}'.encode(FORMAT))
    row = int(conn.recv(HEADER).decode(FORMAT))
    
    conn.send('INPUT_Y'.encode(FORMAT))
    conn.send(f'{text}'.encode(FORMAT))
    col = int(conn.recv().decode(FORMAT))
    
    return row, col


def validPiece(row, col, currentPlayer, lastPlayed):
    if currentPlayer == 1 and board[row - 1][col - 1] == 'W' and lastPlayed != 'W':
        return True
    elif currentPlayer == -1 and board[row - 1][col - 1] == 'B' and lastPlayed != 'B':
        return True
    else:
        return False


def selectPlayer(conn):
    conn.send('SELECT'.encode(FORMAT))
    starter = str(conn.recv(HEADER).decode(FORMAT))

    if starter == 'w':
        starterPlayer = 1
    else:
        starterPlayer = -1

    return starterPlayer


def checkValidEmptySpace(originRow, originCol, destinationRow, destinationCol, currentPlayer):

    # Wants to move more than 2 spaces
    if abs(originRow - destinationRow) >= 3 or abs(originCol - destinationCol) >= 3:
        return False
    
    # Wants to move out of bounds
    if destinationRow < 1 or destinationRow > 8 or destinationCol < 1 or destinationCol > 8:
        return False
    
    # Wants to move to where there's a piece already
    if board[destinationRow - 1][destinationCol - 1] in 'BW':
        return False
    
    # White player wants to go back down the board
    if currentPlayer == 1 and originRow - destinationRow < 0:
        return False
    
    # Black player wants to go back up the board
    if currentPlayer == -1 and originRow - destinationRow > 0:
        return False
    
    return True


def makeMove(conn, originRow, originCol, currentPlayer):
    destinationRow, destinationCol = inputPiecePosition(conn, 'destination')
    while not checkValidEmptySpace(originRow, originCol, destinationRow, destinationCol, currentPlayer):
        print('\nInvalid move! Try again!\n')
        destinationRow, destinationCol = inputPiecePosition(conn, 'destination')
    
    # Is eating a piece
    if abs(originRow - destinationRow) == 2 and abs(originCol - destinationCol) == 2:
        pass
    else:
        board[destinationRow - 1][destinationCol - 1] = board[originRow - 1][originCol - 1]
        board[originRow - 1][originCol - 1] = ' '


def checkWinner():
    countWhite = countBlack = 0
    for row in board:
        for col in row:
            if col == 'W':
                countWhite += 1
            if col == 'B':
                countBlack += 1

    if countWhite == 0:
        return True, 'B'
    elif countBlack == 0:
        return True, 'W'
    else:
        return False, '-'


def main(conn):
    run = True

    board = deepcopy(startBoard)
    clearScreen(conn)
    currentPlayer = selectPlayer(conn)
    lastPlayed = 'B' if currentPlayer == 1 else 'W'
    while run:
        clearScreen(conn)

        printBoard(conn, board)
        # print('Whites turn!' if currentPlayer == 1 else 'Blacks turn!')

        row, col = inputPiecePosition(conn, 'piece')
        while not validPiece(row, col, currentPlayer, lastPlayed):
            print('\nYou already played, oponents turn!\n')
            row, col = inputPiecePosition(conn, 'piece')
        
        makeMove(conn, row, col, currentPlayer)

        """
        existWinner, whoWin = checkWinner()
        if existWinner:
            print('\nWhite wins!\n' if whoWin == 'W' else '\nBlack wins!\n')
            restart = str(input('Want to restart the game? (y/n) ')).lower()
            while restart not in 'yYnN':
                print('\nInvalid option! Try again!\n')
                restart = str(input('Want to restart the game? (y/n) ')).lower()
        
            if restart == 'y':
                main(conn)
                exit()
            else:
                print('\nGood Bye!\n')
                exit()
        """
        currentPlayer *= -1
        lastPlayed = 'W' if lastPlayed == 'B' else 'B'


"""
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
---------------------------------------- SERVER ----------------------------------------
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
"""

def handle_client(conn, addr):
    print(f'[NEW CONNECTION] {addr} connected.')

    main(conn)
    conn.close()


def start():
    server.listen()
    print(f'[LISTENING] Server is listening on {SERVER}')
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f'[ACTIVE CONNECTIONS] {threading.activeCount() - 1}')


print('[STARTING] server is starting...')
start()