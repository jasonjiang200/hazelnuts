import socket
import os
from _thread import *
from cmu_112_graphics import *
import numpy as np
from pickle import dumps, loads
import time


##################################################^^^^^^^ Don't touch VVV
connections = []
gameState = []
turn = 0
consecutivePasses = 0
hands = []
scores = [0, 0, 0, 0] # how many points
full_deck = []
for suit in ['clubs', 'diamonds', 'hearts', 'spades']:
    for number in range(3, 16):
        full_deck.append([number, suit])
######################## Sockets VVV
ServerSocket = socket.socket()
host = '127.0.0.1'
port = 1233

try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waitiing for a Connection..')
ServerSocket.listen(5)


############################### ALL GAME CODE

def startGame() -> list: 
    global turn
    global hands
    global stack
    global stackCards
    global consecutivePasses
    p1, p2, p3, p4 = [], [], [], []
    deal_seed = np.random.permutation(52)
    for i in range(13): 
        p1.append(full_deck[deal_seed[4*i]])
        p2.append(full_deck[deal_seed[4*i+1]])
        p3.append(full_deck[deal_seed[4*i+2]])
        p4.append(full_deck[deal_seed[4*i+3]])
    p1 = sorted(p1, key=lambda x: x[0])
    p2 = sorted(p2, key=lambda x: x[0])
    p3 = sorted(p3, key=lambda x: x[0])
    p4 = sorted(p4, key=lambda x: x[0])
    hands.append(p1)
    hands.append(p2)
    hands.append(p3)
    hands.append(p4)
    if [3, 'hearts'] in p1:
        turn = 1
    elif [3, 'hearts'] in p2:
        turn = 2
    elif [3, 'hearts'] in p3:
        turn = 3
    else:
        turn = 4
    print(hands)
    return([hands, turn, stack, stackCards, consecutivePasses])


########### What each player has
threadCount = 0
stack = 0
stackCards = []

def threaded_client(connection):
    global connections
    global consecutivePasses
    global gameState
    global stack
    global hands
    global turn
    connections.append(connection)
    connection.sendall(str.encode('{}'.format(threadCount)))
    while True:
        

        data = (connection.recv(2048))
        if data == b'':
            break 
        data = loads(data)
        print(data)
        
        if data[0] == 'update':
            reply = dumps(gameState) 
            connection.sendall(reply)
        
        elif data[0] == 'pass':
            consecutivePasses += 1

            # If we rotated, next player has free play
            if consecutivePasses == 3:
                consecutivePasses = 0
                stackCards = []
                stack = 0

            # Go to next player
                turn += 1
                turn %= 4
                if turn == 0:
                    turn = 4
                    
            reply = dumps(gameState) 
            connection.sendall(reply)

        elif data[0] == "Start1" and threadCount == 4:
            print("ya")
            gameState = startGame()
            reply = dumps(gameState) 
            connection.sendall(reply)

        elif data[0] in ["Start2", "Start3", "Start4"]:
            print(gameState)
            # time.sleep(1)
            reply = dumps(gameState)
            connection.sendall(reply)
        else:
            if data[0] == 'play':
                print("we're making a play!")
                stackCards = []
                consecutivePasses = 0
                cards, stack, playerNumber = data[1], data[2], data[3]
                for card in cards:
                    hands[playerNumber - 1].remove(card) # remove every card played
                    stackCards.append(card) #add it to the stack
                    stackCards = sorted(stackCards, key=lambda x: x[0])

                # Go to next player
                turn += 1
                turn %= 4
                if turn == 0:
                    turn = 4

                gameState = [hands, turn, stack, stackCards, consecutivePasses] #Update for each new thing
                reply = dumps(gameState) 
                connection.sendall(reply)

    connection.close()
    print("good bye!")





    







###### Ignore, adds new connections
while True:
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    threadCount += 1
    start_new_thread(threaded_client, (Client, ))
    
    print('Thread Number: ' + str(threadCount))
##########





ServerSocket.close()