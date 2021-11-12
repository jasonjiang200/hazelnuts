import socket
import os
from _thread import *
from cmu_112_graphics import *
import numpy as np
from pickle import dumps, loads





##################################################^^^^^^^ Don't touch VVV
connections = []
winnerIndex = None
threadCount = 0
stack = 0
stackCards = []
gameState = []
turn = 0
consecutivePasses = 0
teams = []
typeOfPlay = None
hands = []
scores = [0, 0, 0, 0] # how many points
full_deck = []
for suit in ['clubs', 'diamonds', 'hearts', 'spades']:
    for number in range(3, 16):
        full_deck.append([number, suit])
######################## Sockets VVV
ServerSocket = socket.socket()

# pick one
host = socket.gethostbyname(socket.gethostname())
# host = '10.74.6.24'
print(host)

port = 14641

try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Server waitiing for a Connection..')
ServerSocket.listen(5)


############################### ALL GAME CODE

def startGame() -> list: 
    global turn
    global hands
    global stack
    global stackCards
    global consecutivePasses
    global typeOfPlay
    global teams

    teams = []
    stack = 0
    stackCards = []
    consecutivePasses = 0
    typeOfPlay = None
    hands = []
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
    return([hands, turn, stack, stackCards, consecutivePasses, typeOfPlay])


########### What each player has


def threaded_client(connection):
    global connections
    global consecutivePasses
    global gameState
    global winnerIndex
    global stack
    global stackCards
    global hands
    global turn
    global teams
    global scores
    global threadCount
    global typeOfPlay
    if threadCount == 5: # too many players, kick this person
        connection.close()
        threadCount -= 1
    else:
        print(connection)
        #### VVVV Allows for disconnect and reconnect
        if 'disconnected' in connections: #someone else disconnected, take their place
            i = connections.index('disconnected')
            connections[i] = connection
        else: #join as normal
            connections.append(connection)
        connection.sendall(str.encode('{}'.format(connections.index(connection)+1)))
        #####

        while True:
            

            data = (connection.recv(2048))
            if data == b'':
                break 
            data = loads(data)
            print(data)
            
            if data[0] == 'update':
                if gameState == ['game over']:
                    reply = dumps([gameState, scores, winnerIndex+1]) 
                    print(reply)
                    connection.sendall(reply)
                else:
                    reply = dumps(gameState) 
                    connection.sendall(reply)
            
            
            elif data[0] == 'pass':
                consecutivePasses += 1

                # If we rotated, next player has free play
                if consecutivePasses == 3:
                    consecutivePasses = 0
                    stackCards = []
                    stack = 0
                    typeOfPlay = None

                # Go to next player
                turn += 1
                turn %= 4
                if turn == 0:
                    turn = 4

                gameState = [hands, turn, stack, stackCards, consecutivePasses, typeOfPlay] #Update for each new thing
                reply = dumps(gameState) 
                connection.sendall(reply)

            elif data[0] == "Start":
                print("ya")
                if gameState in [[], ['game over']]:
                    gameState = startGame()
                    
                    

                    #### Check everyone's hands for aces, assign them teams
                    for hand in gameState[0]: # loop through each players hands
                        aces = 0 #count aces
                        color = None #consider color
                        for card in hand:
                            if card[0] == 14: #ace
                                aces += 1
                                if color == None: #first ace, we care about color. if 2nd+, we won't use it later
                                    if card[1] in ['hearts', 'diamonds']:
                                        color = 'red'
                                    else:
                                        color = 'black'
                                elif color in ['black', 'red']: # second ace
                                    color = 'solo'

                        #looped through all cards, know color of ace (if only 1)
                        teams.append([aces, color])
                reply = dumps(gameState) 
                connection.sendall(reply)

            elif data[0] == 'WE WON': #gotta update scores
                gameState = ['game over'] #jerries game (need to have the update one do something when the gameState is "game over")
                winnerIndex = data[1] - 1 #can properly index now

                for i in range(4): #loop through 4 scores
                    aceScore = 5 - teams[i][0] # 5 - #aces  (teams has 4 lists, each list is [aces, color])

                    if teams[i][1] == 'solo': #on your own
                        teamScore = 3
                    else: # part of a team, maybe
                        teamScore = 4 
                        for j in range(4):
                            if teams[j][1] == teams[i][1]:
                                teamScore -= 1
                    
                    # score points
                    if i == winnerIndex: # winner
                        scores[i] += aceScore * teamScore
                    elif teams[i][1] != 'solo' and teams[i][1] == teams[winnerIndex][1]:      
                        scores[i] += aceScore * teamScore     

                reply = dumps([gameState, scores, winnerIndex+1]) 
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

                    typeOfPlay = data[4]
                    gameState = [hands, turn, stack, stackCards, consecutivePasses, typeOfPlay] #Update for each new thing
                    reply = dumps(gameState) 
                    connection.sendall(reply)

    connection.close()
    connections[connections.index(connection)] = 'disconnected'
    threadCount -= 1
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