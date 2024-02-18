from deck import *
def none(self, auto=False, next_player=True): pass

"""
class <card-name>(card):
    value=Value
    def __init__(self, colour=ANY):
        self.colour=colour

"""

rules= {
        "cards":{},
        "+":{"stack-2s": True, "stack-4s": True, "only stack on equal or less": True, "+4 only when only option": True},
        "no-go": {"action": False},
        "reversecard": {"action": "redirected"},
        "draw until play": False,
        "infinite_deck": True   
}


def rotate_hands(self, auto=False, next_player=True):
    hand=self.deck.players[-1].hand
    for i in self.deck.players:
        hand, i.hand=i.hand, hand

zero.on_play=rotate_hands
one.on_play=none #pushup rules

"""
one.stacking = none#
two.stacking = none #doubles/pushup
three.stacking = none #pushup/remove or add chair of choice
four.stacking = none #say card count in different language
five.stacking = none
six.stacking = none
seven.stacking = none
eight.stacking = none
nine.stacking = none

"""