# This program simulates battles between different decks.
# The decks are composed of card from Pokemon TCG Pocket.

import json
import collections
import random

card_ids = [] # initialises the empty card id pool

# This imports the data from the card pool json.
with open("card_pool.json", "r") as file:
    cardPool = json.load(file)

# Extracts all IDs from the cardPool to be able to identify each Pokemon.
card_ids = [card["id"] for card in cardPool]

# Defines the deck rules and checks them against proposed deck.
def DeckValidation(deck_composition, deck_energies):
    deck_ids = deck_composition
    
    # Rule 1: Decks cannot be more than 20 cards.
    if(len(deck_ids) != 20): # checks whether the deck is the appropiate length
        print("F@20") # failure at deck size 20
        return False
    
    deck_freq = collections.Counter(deck_ids) # creates a frequency array of the deck_ids
    
    # Rule 2: No more than 2 cards of each id.
    for (key, value) in deck_freq.items():
        if(value > 2): # checks if the frequency is more than 2
            print(key, value)
            print("F@<2") # failure at frequency of each being less than 2
            return False
    
    # Rule 3: Deck must contain at least 1 basic Pokemon.
    deck_lookup = {card["id"]: card for card in cardPool} # creates a dictionary of the deck cards
    for card_id in deck_ids:
        if(deck_lookup[card_id].get("evolutionStage") == 0): # is this card a basic pokemon
            break
    else:
        print("F@B") # failure at containing a basic Pokemon
        return False
    
    # Rule 4: Must contain at least one energy, but no more than 3.
    if(not 0 < len(deck_energies) < 4):
        print("F@E") # failure at containing the appropiate amount of energies
        return False
    
    return True # this deck is valid   

# Shuffles the deck into a randomised order.
def DeckShuffle(deck):
    return random.shuffle(deck)

# Removes the top card from the deck and adds it to the designated array (hand or discards).
def DeckDraw(deck, cardTargettedArray, n):
    for i in range(n): # removes the n amount of cards from the deck
        if(not deck):
            return
        else:
            cardTargettedArray.append(deck.pop(0))
    return

# Draws the starting hand for each player.
def StartDeckDraw(deck, hand, energies):
    if not DeckValidation(deck, energies): # checks if the deck is valid
        return
    
    basicInHand = False # currently no basic Pokemon in the player's hand
    
    # While there is not a basic Pokemon in the hand this loop shall continue indefinitely.
    while not basicInHand:
        deck.extend(hand) # puts the cards from the hand back into the deck
        hand.clear() # removes the cards from the hand
        
        DeckShuffle(deck) # shuffles the deck
        DeckDraw(deck, hand, 5) # draws 5 cards (the starting amount) from the deck
        
        # Checks for the basic Pokemon.
        hand_lookup = {card["id"]: card for card in cardPool} # creates a dictionary of the hand cards
        for card_id in hand:
            if(hand_lookup[card_id].get("evolutionStage") == 0): # checks if the hand contains a basic Pokemon
                basicInHand = True # in order to stop the while loop
                break
        else:
            print("redraw")
    
    return

# Creates the game setting and starting positions of each side.
def GameBegin(p1Deck, p2Deck, p1Hand, p2Hand, p1Energy, p2Energy):
    # Determines starting hands.
    StartDeckDraw(p1Deck, p1Hand, p1Energy)
    print("P1", p1Hand)
    StartDeckDraw(p2Deck, p2Hand, p2Energy)
    print("P2", p2Hand)
    
    # Determines who goes first.
    coin = randint(0, 1)
    if coin == 1:
        
    
    return

test = ["168", "002", "003", "003", "004", "004", "006", "006", "007", "007",
        "009", "169", "010", "010", "012", "012", "005", "013", "226", "226"]
test2 = ["001", "002", "003", "003", "004", "004", "006", "006", "007", "007",
        "009", "169", "010", "010", "012", "012", "013", "013", "226", "226"]
energy = ["Grass", "Water", "Fire"]
energy2 = ["Grass", "Water", "Fire"]
handTemp = []
handTemp2 = []


GameBegin(test, test2, handTemp, handTemp2, energy, energy2)
