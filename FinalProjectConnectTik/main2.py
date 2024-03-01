import socket
import threading
import pymongo
from pymongo import MongoClient
import certifi
from bson.json_util import dumps
import json

ca = certifi.where()



cluster = pymongo.MongoClient("mongodb+srv://test:test@cluster0.bf4b9ph.mongodb.net/?retryWrites=true&w=majority",tlsCAFile=ca)
db = cluster["test"]
collection = db["leaderboard"]



class TicTacToe:

    def __init__(self):
        self.board = [[" "," "," "," "],[" "," "," "," "],[" "," "," "," "],[" "," "," "," "]]
        self.turn = "X"
        self.you = "X"
        self.opponent = "O"
        self.winner = "n"
        self.game_over = False
        self.counter = 0

    def host_game(self, host, port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port)) 
        server.listen(1)

        client, addr = server.accept()

        self.you = "X"
        self.opponent = "O"
        threading.Thread(target=self.handle_connection, args=(client,)).start()
        server.close()

    def connect_to_game(self, host , port):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))

        self.you = 'O'
        self.opponent = "X"
        threading.Thread(target=self.handle_connection, args=(client,)).start()

    def handle_connection(self, client):
        while not self.game_over:
            if self.turn == self.you:
                move = input("Enter a move (row, column): ")
                if self.check_valid_move(move.split(',')):
                    client.send(move.encode('utf-8'))
                    self.apply_move(move.split(','),self.you)
                    self.turn = self.opponent
                    

                else:
                    print("Invalid Move!")
            else:
                data = client.recv(1024)
                if not data:
                    break
                else:
                    self.apply_move(data.decode('utf-8').split(','),self.opponent)
                    self.turn = self.you
        client.close()
    
    def apply_move(self,move,player):
        if self.game_over:
            return

        self.counter += 1
        self.board[int(move[0])][int(move[1])] = player
        self.print_board()
        if self.check_if_won():
            if self.winner == self.you:
                print("You win!")
                post = {"winner":"X"}
                collection.insert_one(post)
                resultsx = collection.find({"winner":"X"})
                countx = 0
                for x in resultsx:
                    countx+=1
                resultsy = collection.find({"winner":"O"})
                county = 0
                for x in resultsy:
                    county+=1
                print("X has won",countx,"times")
                print("Y has won",county,"times")

                exit()
            elif self.winner == self.opponent:
                print("You lose!")
                post = {"winner":"O"}
                collection.insert_one(post)
                resultsx = collection.find({"winner":"X"})
                countx = 0
                for x in resultsx:
                    countx+=1
                resultsy = collection.find({"winner":"O"})
                county = 0
                for x in resultsy:
                    county+=1
                print("X has won",countx,"times")
                print("Y has won",county,"times")
                exit()
            else:
                if self.counter == 9:
                    print("It is a tie!")
                    resultsx = collection.find({"winner":"X"})
                    countx = 0
                    for x in resultsx:
                        countx+=1
                    resultsy = collection.find({"winner":"O"})
                    county = 0
                    for x in resultsy:
                        county+=1
                    print("X has won",countx,"times")
                    print("O has won",county,"times")
                    exit()

    def check_valid_move(self,move):
        return self.board[int(move[0])][int(move[1])] == " "

    def check_if_won(self):
        for row in range(4):
            if self.board[row][0] == self.board[row][1] == self.board[row][2] == self.board[row][3] != " ":
                self.winner = self.board[row][0]
                self.game_over = True
                return True

        for col in range(4):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] == self.board[3][col] != " ":
                self.winner = self.board[col][0]
                self.game_over = True
                return True

        if self.board[0][0] == self.board[1][1] == self.board[2][2] == self.board[3][3] != " ":
            self.winner = self.board[0][0]
            self.game_over = True
            return True

        if self.board[0][3] == self.board[1][2] == self.board[2][1] == self.board[3][0] != " ":
            self.winner = self.board[0][2]
            self.game_over = True
            return True
        else:
            return False
    


    def print_board(self):
        for row in range(4):
            print (" | ".join(self.board[row]))
            if row != 3:
                print("-------------") 
        print("\n")

def main():
    

    game = TicTacToe()
    game.host_game("localhost",9999)
    collec = collection.find({})
    with open('collection.json', 'w') as file:
        json.dump(json.loads(dumps(collec)), file)

main()