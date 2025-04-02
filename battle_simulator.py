# This program simulates battles between different decks.
# The decks are composed of cards from Pokemon TCG Pocket.

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
        if (card_data["cardType"] == "Pokemon") or (card_data.get("trainerType") == "playableItem"):
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
    
    # Dictionary that can be put into json files.
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "max_hp": self.max_hp,
            "current_hp": self.current_hp,
            "type": self.type,
            "evolution_stage": self.evolution_stage,
            "ability": self.ability,
            "moves": self.moves,
            "weakness": self.weakness,
            "retreat": self.retreat,
            "attached_energy": self.attached_energy,
            "status_condition": self.status_condition
            }
    
    # A function for whenever a Pokemon takes damage.
    def PokemonDamage(offender, defender, damage):
        if defender.weakness and offender.type == defender.weakness["type"]:
            defender.current_hp -= damage + 20
        else:
            defender.current_hp -= damage
        
        if defender.current_hp < 0:
            defender.current_hp = 0
        
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
        
        if self.current_hp > self.max_hp:
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
        self.startplayer = False
        self.energy_generated = None
        self.points = 0
    
    # Dictionary that can be put into json files.
    def to_dict(self):
        return {
            "deck": self.deck,
            "hand": self.hand,
            "discard_pile": self.discard_pile,
            "energy_zone": self.energy_zone,
            "active_pokemon": self.active_pokemon.to_dict() if self.active_pokemon else None,
            "bench_pokemon": [poke.to_dict() for poke in self.bench_pokemon],
            "startplayer": self.startplayer,
            "energy_generated": self.energy_generated,
            "points": self.points
            }
    
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
            if(deck_lookup[card_id].get("cardType") == "Pokemon") and (deck_lookup[card_id].get("evolutionStage") == 0): # is this card a basic pokemon
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
        player1.startplayer = True
    elif coin == 0:
        player2.startplayer = True
    
    return

# Creates a function to be run at the beginning for each player to play the first active Pokemon.
def PokemonActive(player, pokemon):
    deck_lookup = {card["id"]: card for card in cardPool}
    if(deck_lookup[pokemon].get("cardType") == "Pokemon") and (deck_lookup[pokemon].get("evolutionStage") == 0):
        player.hand.remove(pokemon)
        player.active_pokemon = Pokemon(deck_lookup.get(pokemon))
    else:
        print("F@AB")
    
    return

# Generates a randomised energy from the energies present in the energy zone.
def EnergyZoneGeneration(player):
    player.energy_generated = random.choice(player.energy_zone)
    
    return

# Checks if the Pokemon in question can use a certain move and has the prerequist energies attached.
def CanUseMove(pokemon, move):
    required = move["energyCost"]
    attached = pokemon.attached_energy.copy()
    
    # Checks if the required amount for each energy is present.
    for energy_type, cost in required.items():
        if energy_type != "Normal":
            if attached.get(energy_type, 0) < cost:
                return False
            attached[energy_type] -= cost
    
    normal_energy_cost = required.get("Normal", 0)
    total_left = sum(attached.values())
    
    # As normal energy is not an actual energy it checks it's cost against all remaining energies.
    if normal_energy_cost > total_left:
        return False
    
    return True

# Creates a log of the current game state for neural network training at a later date.
# Currently logs are not recorded as it would be counter-productive this early on, however the ability to do so is here.
# This function currently is used to detect which player won the match.
def RecordCurrentGameState(player1, player2, turn, result, winner = None):
    if player1.startplayer == False:
        p = player1
        player1 = player2
        player2 = p
    
    state = {
        "turn": turn,
        "player1": player1.to_dict(),
        "player2": player2.to_dict(),
        "result": result,
        "winner": winner
        }
    
    return state

# A supporting function for Mutate(), changes the cards randomly to other cards.
def NumberOfMutatedCards(deck, cardPool, n):
    for i in range(1000): # high range is only here to prevent infinity looping
        shadow_deck = Player(deck.deck[:], deck.energy_zone[:])
        for j in range(n):
            shadow_deck.deck.pop(random.randrange(len(shadow_deck.deck)))
        new_deck_ids = [card["id"] for card in random.choices(cardPool, k = n)]
        shadow_deck.deck.extend(new_deck_ids)
        
        if Player.DeckValidation(shadow_deck):
            winrate = DeckEvaluation(shadow_deck, cardPool, 10, deck)
            if winrate > 50:
                return shadow_deck
            else:
                continue
    
    return deck

# This mutates the deck to swap out cards until it gets a better deck, the amount swapped out is determined by winrate.
def Mutate(deck, winrate, cardPool):
    if winrate == 100:
        return deck
    elif winrate >= 75:
        deck = NumberOfMutatedCards(deck, cardPool, 4)
    elif winrate >= 50:
        deck = NumberOfMutatedCards(deck, cardPool, 8)
    elif winrate >= 25:
        deck = NumberOfMutatedCards(deck, cardPool, 12)
    else:
        deck = NumberOfMutatedCards(deck, cardPool, 16)
    return deck

# Creates a random deck with a random energy_pool, this is used to provide the nueral network with immediate/easy/unsure of what word to use here data.
def GenerateRandomDecks(cardPool, size = 1):
    decks = []
    
    while len(decks) < size:
        deck_ids = [card["id"] for card in random.choices(cardPool, k = 20)]
        energy_zone = random.choices(["Grass", "Fire", "Water", "Electric", "Psychic", "Fighting", "Dark", "Metal"], k = random.randint(1, 3))
        player = Player(deck_ids, energy_zone)
        if player.DeckValidation() == True:
            if size == 1:
                return player
            elif size > 1:
                decks.append(player)
    
    return decks

# Evaluates each deck by making it battle random decks.
def DeckEvaluation(deck, cardPool, n = 10, deck2 = None):
    wins = 0
    
    for i in range(n):
        if deck2 != None:
            mutated_deck = Player(deck.deck[:], deck.energy_zone[:])
            original_deck = Player(deck2.deck[:], deck2.energy_zone[:])
            
            log = Battle(mutated_deck, original_deck)
        else:
            evaluating_deck = Player(deck.deck[:], deck.energy_zone[:])
            random_opponent = GenerateRandomDecks(cardPool)
        
            log = Battle(evaluating_deck, random_opponent)
        
        if log[-1]["winner"] == "player1":
            wins += 1
            print(wins)
    
    winrate = (wins / n) * 100
    if winrate >= 0.2 * 100:
        print("Good Deck.")
        print("Win Rate is {}%.".format(winrate))
    
    return winrate

# Creates generations that begin with 2^n (number of generations), this is a sort of lastman standing type of elimination of the worst decks.
def Generations(generations, cardPool):
    decks_generated = GenerateRandomDecks(cardPool, pow(2, generations))
    
    for i in range(generations):
        winrates = []
        
        for j in range(len(decks_generated)):
            winrates.append(DeckEvaluation(decks_generated[j], cardPool))
        
        range_for_k = int(len(decks_generated) / 2)
        for k in range(range_for_k):
            if winrates[k + 1] < winrates[k]:
                decks_generated[k] = Mutate(decks_generated[k], winrates[k], cardPool)
                
                decks_generated.pop(k + 1)
                winrates.pop(k + 1)
            elif winrates[k + 1] > winrates[k]:
                decks_generated[k + 1] = Mutate(decks_generated[k + 1], winrates[k + 1], cardPool)
                
                decks_generated.pop(k)
                winrates.pop(k)
            elif winrates[k + 1] == winrates[k]: # as one of them have to be done away with I decided to get rid of [k + 1]
                decks_generated[k] = Mutate(decks_generated[k], winrates[k], cardPool)
                
                decks_generated.pop(k + 1)
                winrates.pop(k + 1)
    
    print(decks_generated)
    print(winrates)
    return decks_generated[0]
        

# What will actually happen when each battle begins and is processed.
def Battle(player1, player2):
    battle_log = [] # a log for the battle that will happen
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
    if player1.startplayer == True:
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
        
        # In case no basic Pokemon replacement was found for some reason
        if (offender.active_pokemon == None) or (defender.active_pokemon == None):
            battle_log.append(RecordCurrentGameState(defender, offender, turn, "win/lose"))
            print("Something Happened @ not battleWon beginning")
            print(turn - 1)
            return battle_log
            
        # What happens every turn.
        Player.DeckDraw(offender, 1)
        if turn != 1:
            EnergyZoneGeneration(offender)
            Pokemon.AttachEnergy(offender.active_pokemon, offender.energy_generated, 1)
            offender.energy_generated = None
        
        # Check if evolution possible, and evolve.
        hand_lookup = {card["id"]: card for card in cardPool}
        for card_id in offender.hand:
            if hand_lookup[card_id].get("evolvesFrom") == offender.active_pokemon.id:
                reduced_hp = offender.active_pokemon.max_hp - offender.active_pokemon.current_hp
                attached_energy = offender.active_pokemon.attached_energy
                status_condition = offender.active_pokemon.status_condition
                
                offender.hand.remove(card_id)
                offender.active_pokemon = Pokemon(hand_lookup.get(card_id))
                
                offender.active_pokemon.current_hp = offender.active_pokemon.max_hp - reduced_hp
                offender.active_pokemon.attached_energy = attached_energy
                offender.active_pokemon.status_condition = status_condition
        
        # Chooses the first damaging move and uses it.
        for move in offender.active_pokemon.moves:
            if move.get("damage") > 0 and CanUseMove(offender.active_pokemon, move):
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
                if id(offender) == id(player1):
                    winner = "player1"
                elif id(defender) == id(player1):
                    winner = "player2"
                battle_log.append(RecordCurrentGameState(offender, defender, turn, "win/lose", winner))
                print(offender.active_pokemon.name, "Won")
                print(turn)
                return battle_log
            else:
                battle_log.append(RecordCurrentGameState(offender, defender, turn, "continued after promotion"))
                turn += 1
                continue
        
        # To prevent infinite games.
        if turn == 50:
            battle_log.append(RecordCurrentGameState(offender, defender, turn, "draw"))
            print("Battle Drawn")
            print(turn)
            return battle_log
        
        # Checks if win condition (getting three points) is complete.
        if offender.points >= 3:
            if id(offender) == id(player1):
                winner = "player1"
            elif id(defender) == id(player1):
                winner = "player2"
            battle_log.append(RecordCurrentGameState(offender, defender, turn, "win/lose", winner))
            print(offender.active_pokemon.name, "Won")
            print(turn)
            return battle_log
        
        battle_log.append(RecordCurrentGameState(offender, defender, turn, "ongoing"))
        
        turn += 1
    
    return battle_log

test = ["047", "047", "003", "003", "004", "004", "006", "006", "007", "007",
        "009", "169", "010", "010", "012", "012", "005", "013", "226", "226"]
test2 = ["001", "002", "003", "003", "004", "004", "006", "006", "007", "007",
        "009", "169", "010", "010", "012", "012", "013", "013", "226", "226"]
energy = ["Fire"]
energy2 = ["Grass", "Water", "Fire"]

tester_deck = Player(test, energy)

DeckEvaluation(tester_deck, cardPool)

top_deck = Generations(5, cardPool)

print("Before:", tester_deck.deck)
tester_deck = Mutate(tester_deck, 55, cardPool)
print("After:", tester_deck.deck)

with open("top_decks.json", "a") as f:
    json.dump(top_deck.to_dict(), f, indent = 2)
    f.write("\n")
