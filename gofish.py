# Dafna Margalit ECEN 2703 
#Code modified from https://rosettacode.org/wiki/Go_Fish/Python 
import itertools
import random
from copy import deepcopy
from operator import attrgetter
from typing import (Counter,
                    Iterable,
                    Iterator,
                    List,
                    NamedTuple,
                    NewType,
                    Sequence,
                    Set,
                    Tuple,
                    TypeVar)
 
Card = NewType('Card', str)
Hand = Counter[Card]
Deck = Tuple[Card, ...]
Watchlist = Set[Card]
Repeat = Set[Card]
T = TypeVar('T')
 
SUITS_COUNT = 4
RANKS = ('2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A')
DECK = RANKS * SUITS_COUNT
 
EMPTY_HAND_MESSAGE = "{} has run out of cards. They go fishing."
CARD_REQUEST_MESSAGE = "{player_name} asks for {card}"
NO_CARD_MESSAGE = "{player_name} doesn't have {card}. Go Fish!"
BOOK_COMPLETED_MESSAGE = "{player_name} completed the book of {card}'s."
FISHING_RESULT_MESSAGE = "{player_name} fished a {card}"
difficulty = False

class Player(NamedTuple):
    name: str
    hand: Hand
    is_human: bool
    score: int = 0
    watchlist: Watchlist = set()  # used by AI to track enemy's cards
    repeat: Repeat = set() #also used by AI to track how many times a card repeats
 
 
def play(deck: Deck = DECK,
         *,
         first_hand_count: int = 10) -> None:
    # create  deck in shuffled order
    deck = shuffle(deck)
    #create hands
    deck, (human_hand, ai_hand) = deal_first_hands(deck, count=first_hand_count)
    # choose player name and deal first hands to AI and human
    human = Player(name=input('What is your name?: '),
                   hand=human_hand,
                   is_human=True)
    ai = Player(name='Computer',
                hand=ai_hand,
                is_human=False)
    human = check_hand_for_books(human)
    ai = check_hand_for_books(ai)
    choose_level()
    player, opponent = ai, human
    for turn in itertools.count(1):
        player, opponent = opponent, player
        print_turn_stats(turn=turn,
                         players=(player, opponent),
                         cards_left=len(deck))
        #while deck is true
        while cards_in_game(deck, hands=(player.hand, opponent.hand)):
            player, opponent, deck = play_turn(player,
                                               opponent,
                                               deck)
            break
        else:
            print_final_stats((player, opponent))
            return
 
 
def choose_level():
    level = input('Choose difficulty (easy or hard):')

    if level == 'easy':
        difficulty = False
    elif level == 'hard':
        difficulty = True
    else:
        print("Error! You can only input 'easy' or 'hard'")
        choose_level()
        
def shuffle(deck: Deck) -> Deck:
    """Returns a shuffled deck"""
    deck = list(deck)
    random.shuffle(deck)
    return tuple(deck)
 
 
def deal_first_hands(deck: Deck,
                     count: int) -> Tuple[Deck, Tuple[Hand, Hand]]:
    """Gives count cards to each player"""
    hands = (Hand(), Hand())  # type: Tuple[Hand, Hand]
    for hand in ncycles(hands, count):
        card, deck = fish(deck)
        hand[card] += 1
    return deck, hands
 
 
def fish(deck: Deck) -> Tuple[Card, Deck]:
    """Returns a fished card from a deck, and a new deck"""
    return deck[-1], deck[:-1]
 
 
def ncycles(iterable: Iterable[T], n: int) -> Iterator[T]:
    """Returns the sequence elements n times"""
    repeat = itertools.repeat(tuple(iterable), n)
    return itertools.chain.from_iterable(repeat)
 
 
def check_hand_for_books(player: Player) -> Player:
    """
    Walks through cards in the hand,
    removes books and adds corresponding score
    """
 
    def is_book(card_and_count: Tuple[Card, int]) -> bool:
        """
        For a pair of card-count
        checks if count equals the number of suits
        """
        card_and_count[1] == SUITS_COUNT
           
    player = deepcopy(player)
    cards_counts = player.hand.items()
    books = list(filter(is_book, cards_counts))  # type: List[Tuple[Card, int]]
    for card, _ in books:
        player.hand.pop(card)
    return player._replace(score=player.score + len(books))
 
 
def print_turn_stats(*,
                     turn: int,
                     players: Sequence[Player],
                     cards_left: int) -> None:
    """Prints stats of the current turn"""
    name_score = name_score_pairs(players, sep=' ')
    print(f'\nTurn {turn} ({name_score}) {cards_left} cards remaining.')
 
 
def name_score_pairs(players: Sequence[Player],
                     *,
                     sep: str) -> str:
    """Returns a string of pairs of 'name: score'; human goes first"""
    players = sorted(players,
                     key=attrgetter('is_human'),
                     reverse=True)
    name_score_generator = map('{0.name}: {0.score}'.format, players)
    return sep.join(name_score_generator)
 
 
def cards_in_game(deck: Deck,
                  hands: Iterable[Hand]) -> bool:
    """Checks if hands or the deck have any cards"""
    return deck or any(hands)
 
 
def play_turn(player: Player,
              opponent: Player,
              deck: Deck) -> Tuple[Player, Player, Deck]:
    """Plays one turn"""
    player, deck = replenish_card(player, deck=deck)
    opponent, deck = replenish_card(opponent, deck=deck)
    
    #if hard
    if difficulty:
        if player.is_human:
            requested_card, watchlist = human_asks_card(
                hand=player.hand,
                watchlist=opponent.watchlist)
            opponent = opponent._replace(watchlist=watchlist)
        else:
            requested_card = ai_asks_card(hand=player.hand, player=player)
    
        if requested_card in opponent.hand:
            player, opponent = correct_guess_actions(player=player,
                                                    opponent=opponent,
                                                    card=requested_card)
        else:
            player, deck = wrong_guess_actions(
                player=player,
                opponent=opponent,
                requested_card=requested_card,
                deck=deck)
        return player, opponent, deck
    #if easy
    else: 
        if player.is_human: 
            requested_card, watchlist = human_asks_card(
                hand=player.hand,
                watchlist=player.watchlist)
            opponent = opponent._replace(watchlist=watchlist)
        else:
            requested_card = ai_asks_card(hand=player.hand, player=player)
    
        if requested_card in opponent.hand:
            player, opponent = correct_guess_actions(player=player,
                                                    opponent=opponent,
                                                    card=requested_card)
        else:
            player, deck = wrong_guess_actions(
                player=player,
                opponent=opponent,
                requested_card=requested_card,
                deck=deck)
        return player, opponent, deck
    
 
def print_final_stats(players: Sequence[Player]) -> None:
    """Prints final stats"""
    name_score = name_score_pairs(players, sep='\n')
    print(f'\nScores: \n{name_score}\n')
    scores = list(map(attrgetter('score'), players))
    if all(score == scores[0] for score in scores):
        print('Draw!')
    else:
        winning_player = max(players, key=attrgetter('score'))
        print(winning_player.name, 'won!')
 
 
def replenish_card(player: Player,
                   *,
                   deck: Deck) -> Tuple[Player, Deck]:
    """Returns a player with a card drawn from a deck"""
    player = deepcopy(player)
    if not player.hand:
        print(EMPTY_HAND_MESSAGE.format(player.name))
        card, deck = fish(deck)
        player.hand[card] += 1
        print_fishing_result(player=player,
                             card=card)
    return player, deck
 
 
def human_asks_card(*,
                    hand: Hand,
                    watchlist: Watchlist) -> Tuple[Card, Watchlist]:
    """Set of actions for when human asks a card from computer"""
    watchlist = watchlist.copy()
    print_hand(hand)
    requested_card = ask_for_card(hand=hand)
    watchlist.add(requested_card)
    return requested_card, watchlist
 
 
def ai_asks_card(*, hand: Hand, player: Player) -> Card:
    """Set of actions for when computer asks a card from human"""
    # print_hand(hand) #temporary to verify it is correct
    requested_card = request_card(hand=player.hand,
                                  watchlist=player.watchlist,repeat=player.repeat)
    print_message(CARD_REQUEST_MESSAGE,
                  player_name=player.name,
                  card=requested_card)
    return requested_card
 
 
def correct_guess_actions(player: Player,
                          opponent: Player,
                          card: Card):
    """
    Set of actions for when player guesses correctly card
    in a hand of an opponent
    """
    player = deepcopy(player)
    opponent = deepcopy(opponent)
    card_count = opponent.hand.pop(card)
    print(f'{player.name} got {card_count} more {card} '
          f'from {opponent.name}.')
    player.hand[card] += card_count
    player = check_book(player, card)
    if not player.is_human:
        player.watchlist.discard(card)
    return player, opponent
 
 
def wrong_guess_actions(*,
                        player: Player,
                        opponent: Player,
                        requested_card: Card,
                        deck: Deck) -> Tuple[Player, Deck]:
    """
    Set of actions for when player guesses incorrectly card
    in a hand of an opponent.
    """
    player = deepcopy(player)
    print_message(NO_CARD_MESSAGE,
                  player_name=opponent.name,
                  card=requested_card)
    card, deck = fish(deck)
    player.hand[card] += 1
    print_fishing_result(player=player,
                         card=card)
    player = check_book(player, card)
    return player, deck
 
 
def print_hand(hand: Hand) -> None:
    """Prints a hand in the following form: 'Q Q 7 7 7 3'"""
    ranks = itertools.starmap(itertools.repeat, hand.items())
    print(*itertools.chain.from_iterable(ranks))
 
 
def ask_for_card(hand: Hand) -> Card:
    """Asks user for a card, and checks if it is in their hand"""
    while True:
        asked_card = Card(input('What card do you ask for? '))
        if asked_card in hand:
            return asked_card
        print("You don't have that card. Try again!")

def count_cards(player: Player) -> Player:
    """
    Walks through cards in the hand,
    sees which shows up the most
    """
    def does_repeat(card_and_count: Tuple[Card, int]) -> bool:
        """
        Checks if a card shows up more than once
        """
        card_and_count[1] > 1
           
    player = deepcopy(player)
    cards_counts = player.hand.items()
    repeats = list(filter(does_repeat, cards_counts))  # type: List[Tuple[Card, int]]
    for card, _ in repeats:
        player.hand.pop(card)
    return player._replace(repeat=repeats)
 
 
def request_card(hand: Hand, watchlist: Watchlist,repeat:Repeat) -> Card:
    """AI-like choice for a card that will be asked from a human"""
    if difficulty:
        candidates = list(watchlist & repeat)
        if not candidates:
            candidates = list(hand.keys())
        return random.choice(candidates)
    else:
        candidates = list(hand.keys())
        return random.choice(candidates)
 
def print_message(message: str,
                  *,
                  player_name: str,
                  card: str) -> None:
    """Prints a template message"""
    print(message.format(player_name=player_name,
                         card=card))
 
 
def check_book(player: Player,
               card: Card) -> Player:
    """
    Checks if player has all cards of specified type,
    removes them if true, and adds +1 to score
    """
    player = deepcopy(player)
    if player.hand[card] == SUITS_COUNT:
        print_message(BOOK_COMPLETED_MESSAGE,
                      player_name=player.name,
                      card=card)
        player.hand.pop(card)
        player = player._replace(score=player.score + 1)
    return player
 
 
def print_fishing_result(*,
                         player: Player,
                         card: Card) -> None:
    """
    Prints result of fishing.
    Showing card or not depends on if a player is a human.
    """
    card_stub = str(card) if player.is_human else 'card'
    print_message(FISHING_RESULT_MESSAGE,
                  player_name=player.name,
                  card=card_stub)
 
 
if __name__ == "__main__":
    play()
 



