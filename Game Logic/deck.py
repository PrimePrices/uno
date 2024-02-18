import random
import copy
class colour():
    __slots__=["vaule"]
    value=""
    def __str__(self):return self.value
    def __eq__(self, colour): 
        if colour is None: return False
        return (colour.value==self.value) or self.value=="" or colour.value==""
    def __add__(self, str): return self.value+str
class red(colour): value="red"
class blue(colour): value="blue"
class green(colour): value="green"
class yellow(colour): value="yellow"
class ANY(colour): pass

class deck():
    colours=[red(), yellow(), blue(), green()]
    def __init__(self, RULES, players):
        self.players=players
        _4_cards_per_deck=[one, two, three, four, five, six, seven, eight, nine, skip, reverse, draw2]
        self.cards=[zero(self, colour=c) for c in self.colours]
        self.cards+=[species(self, colour=c) for c in self.colours for species in _4_cards_per_deck for _ in range(2)]
        self.cards+=[draw4(self) for _ in range(4)]
        self.cards+=[wild(self) for _ in range(4)]
        random.shuffle(self.cards)
        self.discard_pile=[]
        self.RULES=RULES
    def __str__(self):
        return str([str(i) for i in self.cards])
    def draw(self):
        if self.RULES["infinite_deck"]:
            return copy.copy(random.choice(self.cards))
        if len(self.cards)==0:
            random.shuffle(self.discard_pile)
            self.cards=self.discard_pile[:]
            self.discard_pile=[]
        return self.cards.pop(0)
    def change_next_player(self, auto=False):
        player=self.players[0]
        del self.players[0]
        self.players.append(player)

class card():
    __slots__=["colour", "value", "deck", "players"]
    def on_play(self, auto=False, next_player=True):pass
    def __init__(self, deck, colour=ANY()):
        self.colour=colour
        self.deck=deck
    def __str__(self):
        if type(self.colour)==ANY:
            return self.value
        return str(self.colour)+" "+str(self.value)
    def __eq__(self, card):
        return (type(self)==type(card))+(self.colour==card.colour)
    def __call__(self, auto=False, next_player=True):
        self.on_play(auto=auto)
        if next_player:
            self.deck.change_next_player()
    def pick_colour(self, auto=False):
        colour=None
        if auto: 
            self.colour=red()
            return None
        while colour not in self.deck.colours:
            print("what colour:")
            for n,v in enumerate(self.deck.colours):
                print(f"{n}: {str(v)}")
            try:
                colour=self.deck.colours[int(input())]
            except:
                print("please provide a number")
                colour=red()
        self.colour=colour
    def __gt__(self, card):
        if type(self.value)==str:
            return len(self.value)>=len(str(self.value))
        if type(card.value)==str:
            return False
        if self.value>=card.value:
            return True
    def __lt__(self, card):
        return not self>card
class zero(card):value=0
class one(card):value=1
class two(card):value=2
class three(card):value=3
class four(card):value=4
class five(card):value=5
class six(card):value=6
class seven(card):value=7
class eight(card):value=8
class nine(card):value=9
class skip(card):
    def on_play(self, auto=False):
        self.deck.players.reverse()
    value="skip"
class reverse(card):
    def on_play(self, auto=False):
        self.deck.players.reverse()
    value="reverse"
class draw2(card):
    def on_play(self, auto=False):
        self.deck.players[1].draw(2)
        self.deck.change_next_player()
    value="draw2"
class wild(card):
    value="wild"
    def on_play(self, auto=False):
        self.pick_colour(auto=auto)
class draw4(card):
    value="draw4"
    
    def on_play(self, auto=False):
        self.deck.players[1].draw(repeat=4)
        self.deck.change_next_player()
        self.pick_colour(auto=auto)