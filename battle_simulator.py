# This program simulates battles between different decks.
# The decks are composed of card from Pokemon TCG Pocket.

import json
import collections
import random
from typing import Optional

card_ids = [] # initialises the empty card id pool

# This imports the data from the card pool json.
with open("card_pool.json", "r") as file:
    cardPool = json.load(file)

# Extracts all IDs from the cardPool to be able to identify each Pokemon.
card_ids = [card["id"] for card in cardPool]

# Creates a class for each Pokemon card.
class Pokemon:
    def __init__(self, card_data):
        self.id = card_data["id"]
        self.name = card_data["name"]
        if (card_data["cardType"] == "Pokemon") | (card_data.get("trainerType") == "playableItem"):
            self.max_hp = card_data["hp"]
            self.current_hp = card_data["hp"] # the current hp of the Pokemon (which is initialised as its maximum)
            self.type = card_data["type"]
            self.evolution_stage = card_data["evolutionStage"]
            self.ability = card_data["ability"] # special abilities
            self.moves = card_data["moves"]
            self.weakness = card_data["weakness"]
            self.retreat = card_data["retreat"]
            self.attached_energy = {} # initialises an empty energy field so it can be added to later
            self.status_condition = {} # for status conditions (like poison, sleep, etc.)
        elif card_data["trainerType"] == "Supporter":
            self.ability = card_data["ability"] # the card's effect
    
    # A function for whenever a Pokemon takes damage.
    def PokemonDamage(offender, defender, damage):
        if offender.type == defender.weakness["type"]:
            defender.current_hp -= damage + 20
        else:
            defender.current_hp -= damage
        
        if defender.current_hp < 0:
            defender.current_hp = 0
            Pokemon.PokemonFaint(defender)
        
        return
    
    def PokemonFaint(pokemon):
        return
    
    # A function for adding energy to a Pokemon.
    def AttachEnergy(self, energy_type, amount):
        if energy_type in self.attached_energy:
            self.attached_energy[energy_type] += amount
        else:
            self.attached_energy[energy_type] = amount
        
        return
    
    # A function for removing energy from a Pokemon.
    def RemoveEnergy(self, amount, energy_type: Optional[str] = None):
        if energy_type == None:
            self.attached_energy[list(self.attached_energy)[0]] -= amount
            
            if self.attached_energy[list(self.attached_energy)[0]] < 0:
                self.attached_energy[list(self.attached_energy)[0]] = 0
            
            if self.attached_energy[list(self.attached_energy)[0]] == 0:
                self.attached_energy.pop(list(self.attached_energy)[0])
            
            return
        else:
            self.attached_energy[energy_type] -= amount
        
        if self.attached_energy[energy_type] <= 0:
            self.attached_energy.pop(energy_type)
        
        return
    
    # A function for healing the Pokemon.
    def HealPokemon(self, amount):
        self.current_hp += amount
        
        if self.currrent_hp > self.max_hp:
            self.current_hp = self.max_hp
        
        return
    
    # A function for a status update.
    def AddStatus(self, status):
        self.status_condition[status] = 1
        
        return
    
    # A function for removing a status condition.
    def RemoveStatus(self, status):
        self.status_condition.pop(status)
        
        return

# Creates a Player class.
class Player:
    def __init__(self, deck, energy_zone):
        self.deck = deck[:] # makes a copy of the deck
        self.hand = [] # initialises an empty hand
        self.discard_pile = [] # initialises an empty discard pile
        self.energy_zone = energy_zone[:] # transfers the energies
        self.active_pokemon = None
        self.bench_pokemon = []
        self.turn = False
        self.energy_generated = None
        self.points = 0
    
    # Shuffles the deck into a randomised order.
    def DeckShuffle(self):
        return random.shuffle(self.deck)

    # Removes the top card from the deck and adds it to the designated array (hand or discards).
    def DeckDraw(self, n):
        for i in range(n): # removes the n amount of cards from the deck
            if not self.deck:
                return
            else:
                self.hand.append(self.deck.pop(0))
        return

    # Draws the starting hand for each player.
    def StartDeckDraw(self):
        if not Player.DeckValidation(self): # checks if the deck is valid
            return
        
        basicInHand = False # currently no basic Pokemon in the player's hand
        
        # While there is not a basic Pokemon in the hand this loop shall continue indefinitely.
        while not basicInHand:
            self.deck.extend(self.hand) # puts the cards from the hand back into the deck
            self.hand.clear() # removes the cards from the hand
            
            Player.DeckShuffle(self) # shuffles the deck
            Player.DeckDraw(self, 5) # draws 5 cards (the starting amount) from the deck
            
            # Checks for the basic Pokemon.
            hand_lookup = {card["id"]: card for card in cardPool} # creates a dictionary of the hand cards
            for card_id in self.hand:
                if(hand_lookup[card_id].get("evolutionStage") == 0): # checks if the hand contains a basic Pokemon
                    basicInHand = True # in order to stop the while loop
                    break
        
        return
    
    # Defines the deck rules and checks them against proposed deck.
    def DeckValidation(self):
        deck_ids = self.deck
        
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
            if(deck_lookup[card_id].get("cardType") == "Pokemon") & (deck_lookup[card_id].get("evolutionStage") == 0): # is this card a basic pokemon
                break
        else:
            print("F@B") # failure at containing a basic Pokemon
            return False
        
        # Rule 4: Must contain at least one energy, but no more than 3.
        if(not 0 < len(self.energy_zone) < 4):
            print("F@E") # failure at containing the appropiate amount of energies
            return False
        
        return True # this deck is valid

# Creates the game setting and starting positions of each side.
def GameBegin(player1, player2):
    # Determines starting hands.
    Player.StartDeckDraw(player1)
    Player.StartDeckDraw(player2)
    
    # Determines who goes first.
    coin = random.randint(0, 1)
    if coin == 1:
        player1.turn = True
    elif coin == 0:
        player2.turn = True
    
    return

# Creates a function to be run at the beginning for each player to play the first active Pokemon.
def PokemonActive(player, pokemon):
    deck_lookup = {card["id"]: card for card in cardPool}
    if(deck_lookup[pokemon].get("cardType") == "Pokemon") & (deck_lookup[pokemon].get("evolutionStage") == 0):
        player.hand.remove(pokemon)
        player.active_pokemon = Pokemon(deck_lookup.get(pokemon))
    else:
        print("F@AB")
    
    return

def EnergyZoneGeneration(player):
    player.energy_generated = random.choice(player.energy_zone)
    
    return

points_needed = 3 # how many points are needed to be scored to win a match

# What will actually happen when each battle begins and is processed.
def Battle(player1, player2):
    turn = 1
    
    GameBegin(player1, player2)
    
    # Puts a basic pokemon in the active spot.
    looking1 = True
    while looking1:
        # Checks for the basic Pokemon.
        hand_lookup = {card["id"]: card for card in cardPool} # creates a dictionary of the hand cards
        for card_id in player1.hand:
            if(hand_lookup[card_id].get("evolutionStage") == 0): # checks if the hand contains a basic Pokemon
                potentialactive1 = card_id
                looking1 = False # in order to stop the while loop
                break
    
    # Puts a basic pokemon in the active spot.
    looking2 = True
    while looking2:
        # Checks for the basic Pokemon.
        hand_lookup = {card["id"]: card for card in cardPool} # creates a dictionary of the hand cards
        for card_id in player2.hand:
            if(hand_lookup[card_id].get("evolutionStage") == 0): # checks if the hand contains a basic Pokemon
                potentialactive2 = card_id
                looking2 = False # in order to stop the while loop
                break
    
    PokemonActive(player1, potentialactive1)
    PokemonActive(player2, potentialactive2)
    
    # These are set to the inverse as the while loop will swap positions.
    if player1.turn == True:
        offender = player2
        defender = player1
    else:
        offender = player1
        defender = player2
    
    # Temporary test, just does a run through of the entire battle and what is meant to happen.
    battleWon = False
    while not battleWon:
        p = offender
        offender = defender
        defender = p
        
        # What happens every turn.
        Player.DeckDraw(offender, 1)
        if turn != 1:
            EnergyZoneGeneration(offender)
            Pokemon.AttachEnergy(offender.active_pokemon, offender.energy_generated, 1)
            offender.energy_generated = None
        
        # Chooses the first damaging move and uses it.
        for move in offender.active_pokemon.moves:
            if move.get("damage") > 0:
                Pokemon.PokemonDamage(offender.active_pokemon, defender.active_pokemon, move.get("damage"))
        
        # Attributes points depending on if the defeating Pokemon was an ex or not.
        if defender.active_pokemon.current_hp <= 0:
            if defender.active_pokemon.name.endswith(" ex"):
                offender.points += 2
            else:
                offender.points += 1
            
            defender.discard_pile.append(defender.active_pokemon.id)
            defender.active_pokemon = None
        
        # Substitutes the old active -which is now discarded- with a new active Pokemon.
        if defender.active_pokemon == None:
            promoted = False
            
            # Checks for the basic Pokemon.
            hand_lookup = {card["id"]: card for card in cardPool} # creates a dictionary of the hand cards
            for card_id in defender.hand:
                if(hand_lookup[card_id].get("evolutionStage") == 0): # checks for a basic Pokemon
                    PokemonActive(defender, card_id)
                    promoted = True
                    break
            if not promoted:
                print(offender.active_pokemon.name, "Won")
                print(turn)
                return
        
        # To prevent infinite games.
        if turn == 20:
            print("Battle Drawn")
            print(turn)
            return
        
        # Checks if win condition (getting three points) is complete.
        if offender.points >= 3:
            print(offender.active_pokemon.name, " Won")
            print(turn)
            return
        
        turn += 1
    
    return

test = ["168", "002", "003", "003", "004", "004", "006", "006", "007", "007",
        "009", "169", "010", "010", "012", "012", "005", "013", "226", "226"]
test2 = ["001", "002", "003", "003", "004", "004", "006", "006", "007", "007",
        "009", "169", "010", "010", "012", "012", "013", "013", "226", "226"]
energy = ["Grass", "Water", "Fire"]
energy2 = ["Grass", "Water", "Fire"]
player1 = Player(test, energy)
player2 = Player(test, energy)

print(player1.__dict__)
print(player2.__dict__)
Battle(player1, player2)
print(player1.__dict__)
print(player2.__dict__)


# print(player1.turn, "|", player2.turn)

# card_lookup = {card["id"]: card for card in cardPool} # creates a dictionary of the hand cards

# player1pokemon = []
# player1pokemon = [Pokemon(card_lookup[card]) for card in player1.deck]

# print(player1.hand)

# print(player1.__dict__)


# # test charizard and blastoise and also charmander now... yay!
# charizard = Pokemon(card_lookup["035"])
# blastoise = Pokemon(card_lookup["055"])
# charmander = Pokemon(card_lookup["033"])

# player1.hand.append("033")

# print(charizard.attached_energy)
# Pokemon.AttachEnergy(charizard, "Grass", 3)
# Pokemon.AttachEnergy(charizard, "Fire", 3)
# print(charizard.attached_energy)
# Pokemon.RemoveEnergy(charizard, 2)
# Pokemon.RemoveEnergy(charizard, 2, "Fire")
# Pokemon.RemoveEnergy(charizard, 2)
# print(charizard.attached_energy)

# print(charizard.status_condition)
# Pokemon.AddStatus(charizard, "Sleep")
# print(charizard.status_condition)
# Pokemon.AddStatus(charizard, "Paralyse")
# print(charizard.status_condition)
# Pokemon.AddStatus(charizard, "Sleep")
# print(charizard.status_condition)
# Pokemon.RemoveStatus(charizard, "Sleep")
# print(charizard.status_condition)
# Pokemon.RemoveStatus(charizard, "Paralyse")
# print(charizard.status_condition)

# print(player1.hand)
# print(player1.active_pokemon)
# PokemonActive(player1, "033")
# print(player1.hand)
# print(player1.active_pokemon.name)
# print(player1.active_pokemon.__dict__)
# print(player1.__dict__)
