

##When  a player plays a card like +2 or +4, this creates a stack object

class stack:
    def __init__(self, players, card, origin):
        self.terminate_on=[]#vote, 10s without play, deserving players turn, card