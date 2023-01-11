import socket
import numpy as np
from threading import Thread

class Connect4:
    firstPort = 65432
    secondPort = 65433

    def __init__(self):
        self.gameBoard = np.array(["O"] * 42).reshape(6,7)
        self.turn = 1
        self.playing = True
        self.winner = "No winner"
        self.fullColumns = []
        self.first = self.getTurnOrder()
        self.targetIP = 'localhost'
        self.server = self.startServer()
        self.client = None
        self.conn = None

    def startServer(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = self.secondPort if self.first else self.firstPort
        server.bind(('localhost',port))
        server.listen()
        return server

    def establishHandshake(self):
        listenThread = Thread(target=self.listen)
        shoutThread = Thread(target=self.shout)
        
        listenThread.start()
        shoutThread.start()
        
        listenThread.join()
        shoutThread.join()

    def listen(self):
        conn = None
        while True:
            try:
                conn, addr = self.server.accept()
                break
            except:    
                pass
        
        self.conn = conn
        print("\nConnection Established")

    def shout(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = self.firstPort if self.first else self.secondPort

        while True:
            try:
                client.connect((self.targetIP,port))
                break
            except:    
                pass
        
        self.client = client

    def getTurnOrder(self):
        inp = input("Press 1 for First or 2 for Second: ")
        while not inp.isnumeric() or int(inp) != 1 and int(inp) != 2:
            inp = input("Press 1 for First or 2 for Second: ")

        return int(inp) == 1

    def printBoard(self):
        print('Connect4\n\n' + self.formatNumpyArray(self.gameBoard) + '\n')
        print(self.formatNumpyArray(self.getXCoordinateLine()))
        if not self.first and self.winner == "No winner":
            print("\nAwaiting Opponents Move...\n")

    @staticmethod
    def formatNumpyArray(list):
        string = str(list)
        string = " " + string[1:len(string)-1]
        return string

    @staticmethod
    def getXCoordinateLine():
        line = []
        for i in range(7):
            line.append(str(i))

        line = np.array(line).reshape(1,7)
        return line

    def playGame(self):
        while self.playing:
            self.playRound()
            self.checkGameState()
            self.printBoard()

        print('\n' + self.winner + " has won this game of Connect4")

    def playRound(self):
        gamePiece = "R" if self.turn % 2 == 0 else "Y"
        inp = self.getInput()
        self.placePiece(inp,gamePiece)
        self.turn += 1

    def placePiece(self, col, gamePiece):
        for row in reversed(range(len(self.gameBoard))):
            if self.gameBoard[row][col] == "O":
                self.gameBoard[row][col] = gamePiece
                if row == 0:
                    self.fullColumns.append(col) 
                break

    def getInput(self):
        inp = None
        if self.first:
            inp = input('\nEnter Column To Drop Piece: ')
            while not inp.isnumeric() or not 0 <= int(inp) <= 6 or int(inp) in self.fullColumns:
                inp = input('Enter Valid Column Between 0 and 6 To Drop Piece: ')
            self.client.sendall(bytes(inp, 'utf-8'))
        else:
            inp = self.conn.recv(1024).decode("utf-8")
        
        self.first = not self.first
        return int(inp)

    def checkGameState(self):
        for row in range(len(self.gameBoard)):
            for col in range(len(self.gameBoard[0])):
                if self.gameBoard[row][col] != "O":
                    gamePiece = self.gameBoard[row][col]
                    if self.checkWinner(row,col,gamePiece):
                        self.playing = False
                        self.winner = gamePiece
                        break
        
        if len(self.fullColumns) == 7:
            self.playing = False
            return

    def checkWinner(self, row, col, gamePiece):
        for theta in range(0,360,45):
            if self.check(row,col,gamePiece,theta) >= 4:
                return True
        
        return False

    def check(self,row,col,gamePiece,angle):    
        if self.isInBounds(row,col) and self.gameBoard[row][col] == gamePiece:
            match angle:
                case 0:
                    col += 1
                case 45:
                    row -= 1
                    col += 1
                case 90:
                    row -= 1
                case 135:
                    row -= 1
                    col -= 1
                case 180:
                    col -= 1
                case 225:
                    row += 1
                    col -= 1
                case 270:
                    row += 1
                case 315:
                    row += 1
                    col += 1
            return 1 + self.check(row, col,gamePiece,angle)
        else:
            return 0

    @staticmethod
    def isInBounds(x,y):
        return 0 <= x < 6 and 0 <= y < 7