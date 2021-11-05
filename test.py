import numpy as np
full_deck = []
for suit in ['clubs', 'diamonds', 'hearts', 'spades']:
    for number in range(3, 16):
        full_deck.append([number, suit])
hands = []
p1, p2, p3, p4 = [], [], [], []
deal_seed = np.random.permutation(52)
for i in range(13): 
    p1.append(full_deck[deal_seed[i]])
    p2.append(full_deck[deal_seed[i+1]])
    p3.append(full_deck[deal_seed[i+2]])
    p4.append(full_deck[deal_seed[i+3]])
p1 = sorted(p1, key=lambda x: x[0])
p2 = sorted(p2, key=lambda x: x[0])
p3 = sorted(p3, key=lambda x: x[0])
p4 = sorted(p4, key=lambda x: x[0])
hands.append(p1)
hands.append(p2)
hands.append(p3)
hands.append(p4)
print(hands)