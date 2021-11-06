import socket
from cmu_112_graphics import *
from buttons import *
from pickle import dumps, loads


ClientSocket = socket.socket()
host = socket.gethostbyname(socket.gethostname())
port = 1233

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
        app.gameState = None
        app.hand = []
        app.time = 0
        app.cardBack = app.scaleImage(app.loadImage('cards/cardback.png'), 1/5)
        app.backX, app.backY = app.cardBack.size

        #In order: start button, play cards button,
        app.buttonColors = ['orange', 'light green', 'tan']
        # app.scores = [0, 0, 0, 0]
        app.cards = []
        app.toggle = [0 for i in range(13)]
        
        
        # Deal out the cards 
        for suit in ['clubs', 'diamonds', 'hearts', 'spades']:
            for number in range(3, 16):
                app.card = app.loadImage('cards/{}_of_{}.png'.format(number, suit))
                app.cards.append(app.scaleImage(app.card, 1/6))
        app.cardx, app.cardy = app.cards[0].size[0], app.cards[0].size[1]
        
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
        print(app.playerNumber)
        if app.gameState == None:
            ClientSocket.sendall(dumps(['Start']))
            app.gameState = loads(ClientSocket.recv(2048))
            app.hand = app.gameState[0][app.playerNumber - 1]
            app.playerTurn = int(app.gameState[1])
        
        app.mode = 'playMode'
            
            

def startScreenMode_redrawAll(app, canvas) -> None:
    canvas.create_text(app.width/2, app.height//5, text = "Welcome to Hazelnuts, Player {}!".format(app.playerNumber), font = f'Times {min(app.height, app.width)//20}')
    drawButton(canvas, app.width//2, app.height*4//5, app.width//8, app.height//12, app.buttonColors[0], 2, 'red')
    canvas.create_text(app.width//2, app.height*4//5, text = "Start Game!", font = f'Times {min(app.height, app.width)//30}')

    

##### ^^^^ START MODE ^^^^

##### VVVVV PLAY MODE VVVVV

def playMode_timerFired(app) -> None:
    '''Update the game if it exists every 0.5s'''

    app.time += 1
    if app.time % 5 == 0:
        if app.gameState == None:
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

                elif ((cards[0][0]) == (cards[1][0] - 1) == (cards[2][0] - 2) == (cards[3][0] - 3) == (cards[4][0] - 4)) and (cards[4][0] != 16): # cant have 2 as part of the straight
                    if cards[0][0] > app.gameState[2] and app.gameState[5] in [None, 'straight']:
                        # 5 length straight
                        typeOfPlay = 'straight'
                        stack = cards[0][0] # can take from first card
                        play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                        print(play)
                        ClientSocket.sendall(dumps(play))
                        # code to update with what comes back
                        app.gameState = loads(ClientSocket.recv(2048))
                        app.hand = app.gameState[0][int(app.playerNumber) - 1]
                        app.playerTurn = int(app.gameState[1])
                        
            elif len(cards) == 6:
                if (cards[0][0] == cards[1][0]) and (cards[2][0] == cards[3][0]) and (cards[4][0] == cards[5][0]) and (cards[0][0] + 2 == cards[2][0] + 1 == cards[4][0]) and (cards[4][0] != 16):
                    # pairs straight
                    if cards[0][0] > app.gameState[2] and app.gameState[5] in [None, 'pairs_straight']:
                        typeOfPlay = 'pairs_straight'
                        stack = cards[0][0] # can take from first card
                        play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                        print(play)
                        ClientSocket.sendall(dumps(play))
                        # code to update with what comes back
                        app.gameState = loads(ClientSocket.recv(2048))
                        app.hand = app.gameState[0][int(app.playerNumber) - 1]
                        app.playerTurn = int(app.gameState[1])
                
                elif (cards[0][0] == cards[1][0] == cards[2][0]) and (cards[3][0] == cards[4][0] == cards[5][0]) and (cards[0][0] + 1 == cards[3][0]) and (cards[3][0] != 16):
                    if cards[0][0] > app.gameState[2] and app.gameState[5] in [None, 'empty_airplane']:
                        typeOfPlay = 'empty_airplane'
                        stack = cards[0][0] # can take from first card
                        play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                        print(play)
                        ClientSocket.sendall(dumps(play))
                        # code to update with what comes back
                        app.gameState = loads(ClientSocket.recv(2048))
                        app.hand = app.gameState[0][int(app.playerNumber) - 1]
                        app.playerTurn = int(app.gameState[1])
                
                elif ((cards[0][0]) == (cards[1][0] - 1) == (cards[2][0] - 2) == (cards[3][0] - 3) == (cards[4][0] - 4) == (cards[5][0] - 5)) and (cards[5][0] != 16): # cant have 2 as part of the straight
                    if cards[0][0] > app.gameState[2] and app.gameState[5] in [None, 'straight']:
                        # 6 length straight
                        typeOfPlay = 'straight'
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
                if ((cards[0][0]) == (cards[1][0] - 1) == (cards[2][0] - 2) == (cards[3][0] - 3) == (cards[4][0] - 4) == (cards[5][0] - 5) == (cards[6][0] - 6)) and (cards[6][0] != 16): # cant have 2 as part of the straight
                    if cards[0][0] > app.gameState[2] and app.gameState[5] in [None, 'straight']:
                        # 7 length straight
                        typeOfPlay = 'straight'
                        stack = cards[0][0] # can take from first card
                        play = ["play", cards, stack, app.playerNumber, typeOfPlay]
                        print(play)
                        ClientSocket.sendall(dumps(play))
                        # code to update with what comes back
                        app.gameState = loads(ClientSocket.recv(2048))
                        app.hand = app.gameState[0][int(app.playerNumber) - 1]
                        app.playerTurn = int(app.gameState[1])














        ## Unselect all cards no matter what
        app.toggle = [0 for i in range(13)]

def playMode_timerFired(app) -> None:
    '''Update the game every half a second'''

    app.time += 1
    if app.time % 5 == 0:
        ClientSocket.sendall(dumps(['update']))
        data = (ClientSocket.recv(2048))
        if data != b'':
            data = loads(data)
            app.gameState = data
            app.hand = app.gameState[0][int(app.playerNumber) - 1]
            app.playerTurn = int(app.gameState[1])       

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
                                app.height*9//10+app.cardy//2-app.toggle[i]*app.height//40, width = 2) 

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
                                app.height*0.5+app.cardy//2, width = 2)
    # Show other player's card totals
    canvas.create_image(app.backX, app.height//2, image=ImageTk.PhotoImage(app.cardBack))
    canvas.create_text(app.backX, app.height//2, text = len(app.gameState[0][(app.playerNumber) % 4]), font = f'Arial {min(app.height, app.width)//20}', fill = "#00FF00")

    canvas.create_image(app.width//2, app.backY, image=ImageTk.PhotoImage(app.cardBack))
    canvas.create_text(app.width//2, app.backY, text = len(app.gameState[0][(app.playerNumber + 1) % 4]), font = f'Arial {min(app.height, app.width)//20}', fill = "#00FF00")
    
    canvas.create_image(app.width - app.backX, app.height//2, image=ImageTk.PhotoImage(app.cardBack))
    canvas.create_text(app.width - app.backX, app.height//2, text = len(app.gameState[0][(app.playerNumber + 2) % 4]), font = f'Arial {min(app.height, app.width)//20}', fill = '#00FF00')

    #TODO: show other black aces

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