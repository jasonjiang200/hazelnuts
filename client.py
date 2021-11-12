import socket
from cmu_112_graphics import *
from buttons import *
from pickle import dumps, loads


ClientSocket = socket.socket()

# pick one
host = socket.gethostbyname(socket.gethostname())
# host = '10.74.6.24'
print(host)

port = 14641

print('Waiting for connection')
try:
    ClientSocket.connect((host, port))
except socket.error as e:
    print(str(e))

#################################### ALL GAME CODE


class HazelnutsGame(TopLevelApp):
    def appStarted(app) -> None:
        '''Initiate the whole game'''

        ### Required variables
        app.playerNumber = int(playerNumber)
        app.playerTurn = 0
        app.gameState = []
        app.hand = []
        app.time = 0
        app.winner = None # who won the game
        app.cardBack = app.scaleImage(app.loadImage('cards/cardback.png'), 1/5)
        app.backX, app.backY = app.cardBack.size

        #In order: start button, play cards button, pass button, replay button
        app.buttonColors = ['orange', 'light green', 'tan', 'light green']
        app.toggle = [0 for i in range(13)]
        
        
        # Load the card images 
        app.cards = []
        for suit in ['clubs', 'diamonds', 'hearts', 'spades']:
            for number in range(3, 16):
                app.card = app.loadImage('cards/{}_of_{}.png'.format(number, suit))
                app.cards.append(app.scaleImage(app.card, 1/6))
        app.cardx, app.cardy = app.cards[0].size[0], app.cards[0].size[1]
        
        # load a game on start
        ClientSocket.sendall(dumps(['Start']))
        app.gameState = loads(ClientSocket.recv(2048))
        app.hand = app.gameState[0][app.playerNumber - 1]
        app.playerTurn = int(app.gameState[1])

        # Initiate start screen
        
        app.mode = 'startScreenMode'


def startScreenMode_mouseMoved(app, event) -> None:
    if isInside(event.x, event.y, app.width//2, app.height*4//5, app.width//8, app.height//12):
        app.buttonColors[0] = 'yellow'
    else:
        app.buttonColors[0] = 'orange'

def startScreenMode_mousePressed(app, event) -> None:
    '''Starts the game if button is pressed.'''
    if isInside(event.x, event.y, app.width//2, app.height*4//5, app.width//8, app.height//12):

        # for games, this button loads a game if needed
        if app.gameState == []:
            ClientSocket.sendall(dumps(['Start']))
            app.gameState = loads(ClientSocket.recv(2048))
            app.hand = app.gameState[0][app.playerNumber - 1]
            app.playerTurn = int(app.gameState[1])

            
                
        
        
        app.mode = 'playMode'
            
            

def startScreenMode_redrawAll(app, canvas) -> None:
    canvas.create_text(app.width/2, app.height//5, text = "Welcome to Hazelnuts, Player {}!".format(app.playerNumber), font = f'Times {min(app.height, app.width)//20}')
    drawButton(canvas, app.width//2, app.height*4//5, app.width//8, app.height//12, app.buttonColors[0], 2, 'red')
    canvas.create_text(app.width//2, app.height*4//5, text = "Start Game!", font = f'Times {min(app.height, app.width)//24}')

    ### TODO: Move Displays scores to end mode
    # canvas.create_text(app.width//2, app.height*0.4, text = "Scores: {} - {} - {} - {}".format(app.gameState[6][0], app.gameState[6][1], app.gameState[6][2], app.gameState[6][3]))
    

##### ^^^^ START MODE ^^^^

#### END MODE VVVVVVVVV

def endMode_mousePressed(app, event) -> None:
    '''if replay button clicked, go to app.playMode and start a new game'''
    if isInside(event.x, event.y, app.width*0.75, app.height*0.75, app.width//10, app.height//12):
        ClientSocket.sendall(dumps(['Start']))
        app.gameState = loads(ClientSocket.recv(2048))
        app.hand = app.gameState[0][app.playerNumber - 1]
        app.playerTurn = int(app.gameState[1])
        #start  new game
        app.mode = 'playMode'

def endMode_mouseMoved(app, event) -> None:
    '''if hovering over the replay button, change color'''
    if isInside(event.x, event.y, app.width*0.75, app.height*0.75, app.width//10, app.height//12):
        app.buttonColors[3] = 'green'
    else:
        app.buttonColors[3] = 'light green'
    

def endMode_redrawAll(app, canvas) -> None:
    # show stats
    canvas.create_text(app.width//2, app.height//4, text = 'Round Over!', font = f'Times {min(app.height, app.width)//20}')
    canvas.create_text(app.width//2, app.height//2, text = 'Winner: Player {}!'.format(app.winner))
    canvas.create_text(app.width//2, app.height*3/4, text = "Scores: {} - {} - {} - {}".format(app.scores[0], app.scores[1], app.scores[2], app.scores[3]))

    # replay button
    drawButton(canvas, app.width*0.75, app.height*0.75, app.width//10, app.height//12, app.buttonColors[3], 2, 'green')
    canvas.create_text(app.width*0.75, app.height*0.75, text = 'Play Again!', font = f'Times {min(app.height, app.width)//30}')
##### END MODE ^^^^^^^^

##### VVVVV PLAY MODE VVVVV

def playMode_timerFired(app) -> None:
    '''Update the game if it exists every 0.5s'''

    app.time += 1
    if app.time % 5 == 0:
        ClientSocket.sendall(dumps(['update']))
        data = (ClientSocket.recv(2048))
        if data != b'':
            data = loads(data)
            app.gameState = data
            app.hand = app.gameState[0][int(app.playerNumber) - 1]
            app.playerTurn = int(app.gameState[1]) 
            
         

def playMode_mouseMoved(app, event) -> None:
    '''Change colors of buttons when hovering.'''

    ### play button color
    if isInside(event.x, event.y, app.width*0.9, app.height*4//5, app.width//10, app.height//12):
        app.buttonColors[1] = 'green'
    else:
        app.buttonColors[1] = 'light green'
    
    ### pass button color
    if isInside(event.x, event.y, app.width*0.9, app.height*0.9, app.width//10, app.height//12):
        app.buttonColors[2] = 'pink'
    else:
        app.buttonColors[2] = 'tan'



def playMode_mousePressed(app, event) -> None:
    '''Where the game takes place; play cards'''
    # Toggles cards to be played
    for j, card in enumerate(reversed(app.hand)):
        i = len(app.hand) - j - 1
        cx = app.width//20*(i+1)
        cy = app.height*9//10-app.toggle[i]*app.height//40
        wx = app.cardx
        wy = app.cardy
        if isInside(event.x, event.y, cx, cy, wx, wy):
            if app.toggle[i] == 1:
                app.toggle[i] = 0
            else:
                app.toggle[i] = 1
            return 0 # only click the rightmost card

    # # Attempts to pass
    if isInside(event.x, event.y, app.width*0.9, app.height*0.9, app.width//10, app.height//12): # pass button clicked
        if app.playerNumber == app.gameState[1] and app.gameState[2] != 0: # you can only pass on your turn, and when someone else has played
            ClientSocket.sendall(dumps(['pass']))
            app.gameState = loads(ClientSocket.recv(2048))
            app.hand = app.gameState[0][int(app.playerNumber) - 1]
            app.playerTurn = int(app.gameState[1])
        app.toggle = [0 for i in range(13)] # reset hand view

    # # Attempts to play cards
    if isInside(event.x, event.y, app.width*0.9, app.height*4//5, app.width//10, app.height//12): # inside play button
        if app.playerNumber == app.playerTurn: # it must be your turn
            cards = []
            for i in range(len(app.hand)):
                if app.toggle[i]:
                    cards.append(app.hand[i])
            cards = sorted(cards, key=lambda x: x[0]) # sort the cards for easy comparison
            
        #     # Now check if the card set is playable
        #     ##### Played a single
            if len(cards) == 1: 
                if cards[0][0] > app.gameState[2] and app.gameState[5] in [None, 'single']:
                    typeOfPlay = 'single'
                    stack = cards[0][0]
                    play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                    print(play)
                    ClientSocket.sendall(dumps(play))
                    app.gameState = loads(ClientSocket.recv(2048))
                    app.hand = app.gameState[0][int(app.playerNumber) - 1]
                    app.playerTurn = int(app.gameState[1])

            ##### Played a pair
            elif len(cards) == 2:
                # cards are equal, playable, on a pair
                if cards[0][0] == cards[1][0] and cards[0][0] > app.gameState[2] and app.gameState[5] in [None, 'pair']:
                    typeOfPlay = 'pair'
                    stack = cards[0][0] # can take from first card
                    play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                    print(play)
                    ClientSocket.sendall(dumps(play))

                    # code to update with what comes back
                    app.gameState = loads(ClientSocket.recv(2048))
                    app.hand = app.gameState[0][int(app.playerNumber) - 1]
                    app.playerTurn = int(app.gameState[1])

            ### Played a triple with nothing        
            elif len(cards) == 3:
                # cards are equal, playable, on a triple
                if (cards[0][0] == cards[1][0] == cards[2][0]) and cards[0][0] > app.gameState[2] and app.gameState[5] in [None, 'triple']:
                    typeOfPlay = 'triple'
                    stack = cards[0][0] # can take from first card
                    play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                    print(play)
                    ClientSocket.sendall(dumps(play))

                    # code to update with what comes back
                    app.gameState = loads(ClientSocket.recv(2048))
                    app.hand = app.gameState[0][int(app.playerNumber) - 1]
                    app.playerTurn = int(app.gameState[1])
            
            ### Bomb or triple with single
            elif len(cards) == 4:

                # Bomb: cards are equal, playable, on a anything
                if (cards[0][0] == cards[1][0] == cards[2][0] == cards[3][0]):
                    if app.gameState[5] == 'bomb': #last played was bomb
                        if cards[0][0] > app.gameState[2]: # bigger bomb being played
                            typeOfPlay = 'bomb'
                            stack = cards[0][0] # can take from first card
                            play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                            print(play)
                            ClientSocket.sendall(dumps(play))
                    else:
                        typeOfPlay = 'bomb'
                        stack = cards[0][0] # can take from first card
                        play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                        print(play)
                        ClientSocket.sendall(dumps(play))

                    # code to update with what comes back
                    app.gameState = loads(ClientSocket.recv(2048))
                    app.hand = app.gameState[0][int(app.playerNumber) - 1]
                    app.playerTurn = int(app.gameState[1])
                
                elif (cards[0][0] == cards[1][0] == cards[2][0]) or (cards[1][0] == cards[2][0] == cards[3][0]):
                    # check a middle card in the sort, which is always part of the triple
                    if cards[1][0] > app.gameState[2] and app.gameState[5] in [None, 'triple_with_single']:
                        typeOfPlay = 'triple_with_single'
                        stack = cards[0][0] # can take from second card, always part of the triple
                        play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                        print(play)
                        ClientSocket.sendall(dumps(play))
                        # code to update with what comes back
                        app.gameState = loads(ClientSocket.recv(2048))
                        app.hand = app.gameState[0][int(app.playerNumber) - 1]
                        app.playerTurn = int(app.gameState[1])

            elif len(cards) == 5:
                if ((cards[0][0] == cards[1][0] == cards[2][0]) and (cards[3][0] == cards[4][0])) or ((cards[2][0] == cards[3][0] == cards[4][0]) and (cards[0][0] == cards[1][0])):
                    # triple with pair
                    if cards[2][0] > app.gameState[2] and app.gameState[5] in [None, 'triple_with_pair']:
                        typeOfPlay = 'triple_with_pair'
                        stack = cards[2][0] # can take from third card, always part of the triple
                        play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                        print(play)
                        ClientSocket.sendall(dumps(play))
                        # code to update with what comes back
                        app.gameState = loads(ClientSocket.recv(2048))
                        app.hand = app.gameState[0][int(app.playerNumber) - 1]
                        app.playerTurn = int(app.gameState[1])

                elif ((cards[0][0]) == (cards[1][0] - 1) == (cards[2][0] - 2) == (cards[3][0] - 3) == (cards[4][0] - 4)) and (cards[-1][0] != 15): # cant have 2 as part of the straight
                    if cards[0][0] > app.gameState[2] and app.gameState[5] in [None, '5_straight']:
                        # 5 length straight
                        typeOfPlay = '5_straight'
                        stack = cards[0][0] # can take from first card
                        play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                        print(play)
                        ClientSocket.sendall(dumps(play))
                        # code to update with what comes back
                        app.gameState = loads(ClientSocket.recv(2048))
                        app.hand = app.gameState[0][int(app.playerNumber) - 1]
                        app.playerTurn = int(app.gameState[1])
                        
            elif len(cards) == 6:
                if (cards[0][0] == cards[1][0]) and (cards[2][0] == cards[3][0]) and (cards[4][0] == cards[5][0]) and (cards[0][0] == cards[2][0] - 1 == cards[4][0] - 2) and (cards[-1][0] != 15):
                    # pairs straight
                    if cards[0][0] > app.gameState[2] and app.gameState[5] in [None, '3_pairs_straight']:
                        typeOfPlay = '3_pairs_straight'
                        stack = cards[0][0] # can take from first card
                        play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                        print(play)
                        ClientSocket.sendall(dumps(play))
                        # code to update with what comes back
                        app.gameState = loads(ClientSocket.recv(2048))
                        app.hand = app.gameState[0][int(app.playerNumber) - 1]
                        app.playerTurn = int(app.gameState[1])
                
                elif (cards[0][0] == cards[1][0] == cards[2][0]) and (cards[3][0] == cards[4][0] == cards[5][0]) and (cards[0][0] == cards[3][0] - 1) and (cards[-1][0] != 15):
                    if cards[0][0] > app.gameState[2] and app.gameState[5] in [None, '2_empty_airplane']:
                        typeOfPlay = '2_empty_airplane'
                        stack = cards[0][0] # can take from first card
                        play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                        print(play)
                        ClientSocket.sendall(dumps(play))
                        # code to update with what comes back
                        app.gameState = loads(ClientSocket.recv(2048))
                        app.hand = app.gameState[0][int(app.playerNumber) - 1]
                        app.playerTurn = int(app.gameState[1])
                
                elif ((cards[0][0]) == (cards[1][0] - 1) == (cards[2][0] - 2) == (cards[3][0] - 3) == (cards[4][0] - 4) == (cards[5][0] - 5)) and (cards[-1][0] != 15): # cant have 2 as part of the straight
                    if cards[0][0] > app.gameState[2] and app.gameState[5] in [None, '6_straight']:
                        # 6 length straight
                        typeOfPlay = '6_straight'
                        stack = cards[0][0] # can take from first card
                        play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                        print(play)
                        ClientSocket.sendall(dumps(play))
                        # code to update with what comes back
                        app.gameState = loads(ClientSocket.recv(2048))
                        app.hand = app.gameState[0][int(app.playerNumber) - 1]
                        app.playerTurn = int(app.gameState[1])

            elif len(cards) == 7:
                # only straights
                if ((cards[0][0]) == (cards[1][0] - 1) == (cards[2][0] - 2) == (cards[3][0] - 3) == (cards[4][0] - 4) == (cards[5][0] - 5) == (cards[6][0] - 6)) and (cards[-1][0] != 15): # cant have 2 as part of the straight
                    if cards[0][0] > app.gameState[2] and app.gameState[5] in [None, '7_straight']:
                        # 7 length straight
                        typeOfPlay = '7_straight'
                        stack = cards[0][0] # can take from first card
                        play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                        print(play)
                        ClientSocket.sendall(dumps(play))
                        # code to update with what comes back
                        app.gameState = loads(ClientSocket.recv(2048))
                        app.hand = app.gameState[0][int(app.playerNumber) - 1]
                        app.playerTurn = int(app.gameState[1])
            
            elif len(cards) == 8: #pair straight, straight, airplane with wings
                if ((cards[0][0]) == (cards[1][0] - 1) == (cards[2][0] - 2) == (cards[3][0] - 3) == (cards[4][0] - 4) == (cards[5][0] - 5) == (cards[6][0] - 6) == (cards[7][0] - 7)) and (cards[-1][0] != 15): # cant have 2 as part of the straight
                    if cards[0][0] > app.gameState[2] and app.gameState[5] in [None, '8_straight']:
                        # 8 length straight
                        typeOfPlay = '8_straight'
                        stack = cards[0][0] # can take from first card
                        play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                        print(play)
                        ClientSocket.sendall(dumps(play))
                        # code to update with what comes back
                        app.gameState = loads(ClientSocket.recv(2048))
                        app.hand = app.gameState[0][int(app.playerNumber) - 1]
                        app.playerTurn = int(app.gameState[1])
                
                elif (cards[0][0] == cards[1][0]) and (cards[2][0] == cards[3][0]) and (cards[4][0] == cards[5][0]) and (cards[6][0] == cards[7][0]) and (cards[0][0] == cards[2][0] - 1 == cards[4][0] - 2 == cards[6][0] - 3) and (cards[-1][0] != 15):
                    # pairs straight
                    if cards[0][0] > app.gameState[2] and app.gameState[5] in [None, '4_pairs_straight']:
                        typeOfPlay = '4_pairs_straight'
                        stack = cards[0][0] # can take from first card
                        play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                        print(play)
                        ClientSocket.sendall(dumps(play))
                        # code to update with what comes back
                        app.gameState = loads(ClientSocket.recv(2048))
                        app.hand = app.gameState[0][int(app.playerNumber) - 1]
                        app.playerTurn = int(app.gameState[1])
                
                else: #must be airplane with wings, need manipulation
                    # TODO: get a test of this, currently no clue if it works
                    cardNumbers = []
                    seenTriples, seenSingles = [], []
                    for card in cards:
                        cardNumbers.append(card[0])
                    for num in cardNumbers:
                        if (num not in seenTriples) and (num not in seenSingles): #haven't seen this before
                            if cardNumbers.count(num) == 3:
                                seenTriples.append(num)
                            elif cardNumbers.count(num) == 1:
                                seenSingles.append(num)
                    if 15 not in seenTriples and abs(seenTriples[0] - seenTriples[1]) == 1:
                        if app.gameState[5] in [None, '2_airplane_with_singles']:
                            typeOfPlay = '2_airplane_with_singles'
                            stack = min(seenTriples) # can take from smaller card in the triples
                            play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                            print(play)
                            ClientSocket.sendall(dumps(play))
                            # code to update with what comes back
                            app.gameState = loads(ClientSocket.recv(2048))
                            app.hand = app.gameState[0][int(app.playerNumber) - 1]
                            app.playerTurn = int(app.gameState[1])
            
            elif len(cards) == 9:
                if ((cards[0][0]) == (cards[1][0] - 1) == (cards[2][0] - 2) == (cards[3][0] - 3) == (cards[4][0] - 4) == (cards[5][0] - 5) == (cards[6][0] - 6) == (cards[7][0] - 7) == (cards[8] - 8)) and (cards[-1][0] != 15): # cant have 2 as part of the straight 
                    if cards[0][0] > app.gameState[2] and app.gameState[5] in [None, '9_straight']:
                        # 9 length straight
                        typeOfPlay = '9_straight'
                        stack = cards[0][0] # can take from first card
                        play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                        print(play)
                        ClientSocket.sendall(dumps(play))
                        # code to update with what comes back
                        app.gameState = loads(ClientSocket.recv(2048))
                        app.hand = app.gameState[0][int(app.playerNumber) - 1]
                        app.playerTurn = int(app.gameState[1])
                    
                elif (cards[0][0] == cards[1][0] == cards[2][0]) and (cards[3][0] == cards[4][0] == cards[5][0] and (cards[6][0] == cards[7][0] == cards[8][0])) and (cards[0][0] == cards[3][0] - 1 == cards[6][0] - 2) and (cards[-1][0] != 15): #no 2 as top
                    if cards[0][0] > app.gameState[2] and app.gameState[5] in [None, '3_empty_airplane']:
                        typeOfPlay = '3_empty_airplane'
                        stack = cards[0][0] # can take from first card
                        play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                        print(play)
                        ClientSocket.sendall(dumps(play))
                        # code to update with what comes back
                        app.gameState = loads(ClientSocket.recv(2048))
                        app.hand = app.gameState[0][int(app.playerNumber) - 1]
                        app.playerTurn = int(app.gameState[1])

            elif len(cards) == 10: #TODO: fix up
                if ((cards[0][0]) == (cards[1][0] - 1) == (cards[2][0] - 2) == (cards[3][0] - 3) == (cards[4][0] - 4) == (cards[5][0] - 5) == (cards[6][0] - 6) == (cards[7][0] - 7) == (cards[8][0] - 8) == (cards[9][0] - 9)) and (cards[-1][0] != 15): # cant have 2 as part of the straight
                    if cards[0][0] > app.gameState[2] and app.gameState[5] in [None, '10_straight']:
                        # 10 length straight
                        typeOfPlay = '10_straight'
                        stack = cards[0][0] # can take from first card
                        play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                        print(play)
                        ClientSocket.sendall(dumps(play))
                        # code to update with what comes back
                        app.gameState = loads(ClientSocket.recv(2048))
                        app.hand = app.gameState[0][int(app.playerNumber) - 1]
                        app.playerTurn = int(app.gameState[1])
                
                elif (cards[0][0] == cards[1][0]) and (cards[2][0] == cards[3][0]) and (cards[4][0] == cards[5][0]) and (cards[6][0] == cards[7][0]) and (cards[8][0] == cards[9][0]) and (cards[0][0] == cards[2][0] - 1 == cards[4][0] - 2 == cards[6][0] - 3 == cards[8] - 4) and (cards[-1][0] != 15):
                    # pairs straight
                    if cards[0][0] > app.gameState[2] and app.gameState[5] in [None, '5_pairs_straight']:
                        typeOfPlay = '5_pairs_straight'
                        stack = cards[0][0] # can take from first card
                        play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                        print(play)
                        ClientSocket.sendall(dumps(play))
                        # code to update with what comes back
                        app.gameState = loads(ClientSocket.recv(2048))
                        app.hand = app.gameState[0][int(app.playerNumber) - 1]
                        app.playerTurn = int(app.gameState[1])
                
                else: #must be airplane with thicc wings, need manipulation
                    # TODO: get a test of this, currently no clue if it works
                    cardNumbers = []
                    seenTriples, seenDoubles = [], []
                    for card in cards:
                        cardNumbers.append(card[0])
                    for num in cardNumbers:
                        if (num not in seenTriples) and (num not in seenDoubles): #haven't seen this before
                            if cardNumbers.count(num) == 3:
                                seenTriples.append(num)
                            elif cardNumbers.count(num) == 2:
                                seenDoubles.append(num)
                    if 15 not in seenTriples and abs(seenTriples[0] - seenTriples[1]) == 1:
                        if app.gameState[5] in [None, '2_airplane_with_pairs']:
                            typeOfPlay = '2_airplane_with_pairs'
                            stack = min(seenTriples) # can take from smaller card in the triples
                            play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                            print(play)
                            ClientSocket.sendall(dumps(play))
                            # code to update with what comes back
                            app.gameState = loads(ClientSocket.recv(2048))
                            app.hand = app.gameState[0][int(app.playerNumber) - 1]
                            app.playerTurn = int(app.gameState[1])

            elif len(cards) == 11: #only straights
                if ((cards[0][0]) == (cards[1][0] - 1) == (cards[2][0] - 2) == (cards[3][0] - 3) == (cards[4][0] - 4) == (cards[5][0] - 5) == (cards[6][0] - 6) == (cards[7][0] - 7) == (cards[8][0] - 8) == (cards[9][0] - 9) == (cards[10][0] - 10)) and (cards[-1][0] != 15): # cant have 2 as part of the straight
                    if cards[0][0] > app.gameState[2] and app.gameState[5] in [None, '11_straight']:
                            # 11 length straight
                            typeOfPlay = '11_straight'
                            stack = cards[0][0] # can take from first card
                            play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                            print(play)
                            ClientSocket.sendall(dumps(play))
                            # code to update with what comes back
                            app.gameState = loads(ClientSocket.recv(2048))
                            app.hand = app.gameState[0][int(app.playerNumber) - 1]
                            app.playerTurn = int(app.gameState[1])
            
            elif len(cards) == 12: #straight, 6 pairs, 3 airplane with singles, 4 empty airplane
                if ((cards[0][0]) == (cards[1][0] - 1) == (cards[2][0] - 2) == (cards[3][0] - 3) == (cards[4][0] - 4) == (cards[5][0] - 5) == (cards[6][0] - 6) == (cards[7][0] - 7) == (cards[8][0] - 8) == (cards[9][0] - 9) == (cards[10][0] - 10) == (cards[11][0] - 11)) and (cards[-1][0] != 15): # cant have 2 as part of the straight
                    if cards[0][0] > app.gameState[2] and app.gameState[5] in [None, '12_straight']:
                            # 12 length straight
                            typeOfPlay = '12_straight'
                            stack = cards[0][0] # can take from first card
                            play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                            print(play)
                            ClientSocket.sendall(dumps(play))
                            # code to update with what comes back
                            app.gameState = loads(ClientSocket.recv(2048))
                            app.hand = app.gameState[0][int(app.playerNumber) - 1]
                            app.playerTurn = int(app.gameState[1])

                elif (cards[0][0] == cards[1][0]) and (cards[2][0] == cards[3][0]) and (cards[4][0] == cards[5][0]) and (cards[6][0] == cards[7][0]) and (cards[8][0] == cards[9][0]) and (cards[10][0] == cards[11][0]) and (cards[0][0] == cards[2][0] - 1 == cards[4][0] - 2 == cards[6][0] - 3 == cards[8] - 4 == cards[10] - 5) and (cards[-1][0] != 15):
                    # 6 pairs straight
                    if cards[0][0] > app.gameState[2] and app.gameState[5] in [None, '6_pairs_straight']:
                        typeOfPlay = '6_pairs_straight'
                        stack = cards[0][0] # can take from first card
                        play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                        print(play)
                        ClientSocket.sendall(dumps(play))
                        # code to update with what comes back
                        app.gameState = loads(ClientSocket.recv(2048))
                        app.hand = app.gameState[0][int(app.playerNumber) - 1]
                        app.playerTurn = int(app.gameState[1])
                
                elif (cards[0][0] == cards[1][0] == cards[2][0]) and (cards[3][0] == cards[4][0] == cards[5][0] and (cards[6][0] == cards[7][0] == cards[8][0]) and (cards[9][0] == cards[10][0] == cards[11][0])) and (cards[0][0] == cards[3][0] - 1 == cards[6][0] - 2 == cards[9][0] - 3) and (cards[-1][0] != 15): #no 2 as top
                    if cards[0][0] > app.gameState[2] and app.gameState[5] in [None, '4_empty_airplane']:
                        typeOfPlay = '4_empty_airplane'
                        stack = cards[0][0] # can take from first card
                        play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                        print(play)
                        ClientSocket.sendall(dumps(play))
                        # code to update with what comes back
                        app.gameState = loads(ClientSocket.recv(2048))
                        app.hand = app.gameState[0][int(app.playerNumber) - 1]
                        app.playerTurn = int(app.gameState[1])
                else: #must be airplane with wings, need manipulation
                    # TODO: get a test of this, currently no clue if it works
                    cardNumbers = []
                    seenTriples, seenSingles = [], []
                    for card in cards:
                        cardNumbers.append(card[0])
                    for num in cardNumbers:
                        if (num not in seenTriples) and (num not in seenSingles): #haven't seen this before
                            if cardNumbers.count(num) == 3:
                                seenTriples.append(num)
                            elif cardNumbers.count(num) == 1:
                                seenSingles.append(num)
                    seenTriples = sorted(seenTriples, key=lambda x: x[0])
                    if 15 not in seenTriples and (seenTriples[0] == seenTriples[1] - 1 == seenTriples[2] - 2):
                        if app.gameState[5] in [None, '3_airplane_with_singles']:
                            typeOfPlay = '3_airplane_with_singles'
                            stack = min(seenTriples) # can take from smaller card in the triples
                            play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                            print(play)
                            ClientSocket.sendall(dumps(play))
                            # code to update with what comes back
                            app.gameState = loads(ClientSocket.recv(2048))
                            app.hand = app.gameState[0][int(app.playerNumber) - 1]
                            app.playerTurn = int(app.gameState[1])
                

            # Check for a win after each play
            if app.hand == []: #this player won
                ClientSocket.sendall(dumps(['WE WON', app.playerNumber]))
                data = loads(ClientSocket.recv(2048))
                app.mode = 'endMode'
                app.hand = []
                app.playerTurn = 0
                app.scores = data[1]
                app.winner = data[2]
                












        ## Unselect all cards no matter what
        app.toggle = [0 for i in range(13)]

def playMode_timerFired(app) -> None:
    '''Update the game every half a second'''

    # if app.gameState == ['game over']:
    #     ClientSocket.sendall(dumps(['I need scores']))
    #     data = (ClientSocket.recv(2048)) #### TODO: fix
    #     app.mode = 'endMode' 
    app.time += 1
    if app.time % 5 == 0:
        ClientSocket.sendall(dumps(['update']))
        data = (ClientSocket.recv(2048))
        if data != b'':
            data = loads(data)
            app.gameState = data
            if data[0] != ['game over']:
                print(app.gameState)
                app.hand = app.gameState[0][int(app.playerNumber) - 1]
                app.playerTurn = int(app.gameState[1])  
            else:
                app.hand = []
                app.playerTurn = 0
                app.scores = data[1]
                app.winner = data[2]
                app.mode = 'endMode'
                    

def playMode_redrawAll(app, canvas) -> None: 
    '''Redraw the board with the updated game.'''
    # Show the player number
    canvas.create_text(40, 10, text = "Player {}".format(app.playerNumber), font = f'Times {min(app.height, app.width)//50}')

    # Show turn 
    canvas.create_text(app.width//2, 30, text = "Player {}'s turn!".format(app.playerTurn))

    # Show the hand
    for i, card in enumerate(app.hand):
        # canvas.create_text(app.width//20 * (i + 1), app.height*9//10, text = "{}{}".format(card[0], card[1]))
        if card[1] == 'clubs':
            canvas.create_image(app.width//20*(i+1), app.height*9//10-app.toggle[i]*app.height//40, image=ImageTk.PhotoImage(app.cards[card[0]-3]))
        elif card[1] == 'diamonds':
            canvas.create_image(app.width//20*(i+1), app.height*9//10-app.toggle[i]*app.height//40, image=ImageTk.PhotoImage(app.cards[10+card[0]]))
        elif card[1] == 'hearts':
            canvas.create_image(app.width//20*(i+1), app.height*9//10-app.toggle[i]*app.height//40, image=ImageTk.PhotoImage(app.cards[23+card[0]]))
        else:
            canvas.create_image(app.width//20*(i+1), app.height*9//10-app.toggle[i]*app.height//40, image=ImageTk.PhotoImage(app.cards[36+card[0]]))
        canvas.create_rectangle(app.width//20*(i+1)-app.cardx//2, 
                                app.height*9//10-app.cardy//2-app.toggle[i]*app.height//40, 
                                app.width//20*(i+1)+app.cardx//2, 
                                app.height*9//10+app.cardy//2-app.toggle[i]*app.height//40, width = 1) 

    #Play button
    drawButton(canvas, app.width*0.9, app.height*4//5, app.width//10, app.height//12, app.buttonColors[1], 2, 'green')
    canvas.create_text(app.width*0.9, app.height*4//5, text="Play", font = f'Times {min(app.height, app.width)//30}')

    # Pass button
    drawButton(canvas, app.width*0.9, app.height*0.9, app.width//10, app.height//12, app.buttonColors[2], 2, 'tan')
    canvas.create_text(app.width*0.9, app.height*0.9, text="Pass", font = f'Times {min(app.height, app.width)//30}')
    
    # Display the stack
    for i, card in enumerate(app.gameState[3]):
        if card[1] == 'clubs':
            canvas.create_image(app.width//20*(i+3)+app.cardx, app.height*0.5, image=ImageTk.PhotoImage(app.cards[card[0]-3]))
        elif card[1] == 'diamonds':
            canvas.create_image(app.width//20*(i+3)+app.cardx, app.height*0.5, image=ImageTk.PhotoImage(app.cards[10+card[0]]))
        elif card[1] == 'hearts':
            canvas.create_image(app.width//20*(i+3)+app.cardx, app.height*0.5, image=ImageTk.PhotoImage(app.cards[23+card[0]]))
        else:
            canvas.create_image(app.width//20*(i+3)+app.cardx, app.height*0.5, image=ImageTk.PhotoImage(app.cards[36+card[0]]))
        canvas.create_rectangle(app.width//20*(i+3)+app.cardx*0.5, 
                                app.height*0.5-app.cardy//2, 
                                app.width//20*(i+3)+app.cardx*1.5, 
                                app.height*0.5+app.cardy//2, width = 1)
    # Show other player's card totals
    canvas.create_image(app.backX, app.height//2, image=ImageTk.PhotoImage(app.cardBack))
    canvas.create_text(app.backX, app.height//2, text = len(app.gameState[0][(app.playerNumber) % 4]), font = f'Arial {min(app.height, app.width)//20}', fill = "#00FF00")

    canvas.create_image(app.width//2, app.backY, image=ImageTk.PhotoImage(app.cardBack))
    canvas.create_text(app.width//2, app.backY, text = len(app.gameState[0][(app.playerNumber + 1) % 4]), font = f'Arial {min(app.height, app.width)//20}', fill = "#00FF00")
    
    canvas.create_image(app.width - app.backX, app.height//2, image=ImageTk.PhotoImage(app.cardBack))
    canvas.create_text(app.width - app.backX, app.height//2, text = len(app.gameState[0][(app.playerNumber + 2) % 4]), font = f'Arial {min(app.height, app.width)//20}', fill = '#00FF00')

    # show a square below the person whose turn it is
    # turn is 1, 2, 3 or 4
    # app.playerNumber is 1, 2, 3, or 4
    chip = (app.gameState[1] - app.playerNumber) % 4
    if chip == 1: #player is on left
        canvas.create_rectangle(2*app.backX-10, app.height//2-10, 2*app.backX+10, app.height//2+10, fill = 'red' )
    elif chip == 2:
        canvas.create_rectangle(app.width//2-10, (1.5*app.backY + 10), app.width//2+10, (1.5*app.backY +30), fill = 'red' )
    elif chip == 3:
        canvas.create_rectangle(app.width-(2*app.backX-10), app.height//2-10, app.width-(2*app.backX+10), app.height//2+10, fill = 'red' )


###############################################################




######## Player joined!
playerNumber = ClientSocket.recv(2048).decode('utf-8')

    
# while True:
#     Input = input('Say Something: ')
#     ClientSocket.send(str.encode(Input))
#     Response = ClientSocket.recv(1024)
#     print(Response.decode('utf-8'))

HazelnutsGame(width=1792, height=995)
    

ClientSocket.close()