# Pokemon TCG Pocket Battle Simulator

Simple Python application which simulates battles in a replicated Pokémon TCG Pocket battle system using cards from the first pack of the Pokemon TCG Pocket app. It is meant to create random decks and pit them against each other in simulated basic battles, then with the winning decks mutate them to try create better decks.

# Aims:
- Evaluate each deck's performance based off of winrate.
- Simulate battles between different decks.
- Mutate decks over time to improve them.

# Deck Rules
1. Decks cannot be more than 20 cards.
2. No more than 2 cards of each id.
3. Deck must contain at least 1 basic Pokemon.
4. Must contain at least one energy, but no more than 3.

# Limitations
- Does not use moves that are non-damaging, or account for each move's special effect.
- Does not use abilities.
- Trainer cards do not work.
- Evolved Pokemon evolve instantly if evolved form is in hand for active Pokemon.
- Bench system is only in semi-development, the hand serving as the bench. This means that the algorithm cannot attach energy to the benched Pokemon.

# Future Aims:
- Add evolution timing -cannot evolve if evolved or became active Pokemon this turn.
- Add bench Pokemon implementation fully.
- Add special cards and abilities.

