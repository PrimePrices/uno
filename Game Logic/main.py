from deck import *
from mods import *
from player import player
import sys


class game:
    def __init__(self, players, auto=False):
        self.players=[]
        self.deck=deck(rules, self.players)
        for i in players: 
            self.players.append(player(i, self.deck, auto=auto))
        self.game_loop()
    def won(self, moves=0):
        for i in self.players:
            if len(i.hand)==0:
                print(i.name, "won")
        print(f"This took {moves} moves")
        for i in self.players:
            print(i)
        sys.exit()
    def game_loop(self):
        discard=self.deck.draw()
        discard(auto=True, next_player=False)
        i=0
        while True:
            discard, still_playing = self.players[0](discard)
            self.deck.discard_pile.append(discard)
            i+=1
            print()
            if not still_playing:
                self.won(moves=i)


        

if __name__=="__main__":
    game=game(["Joshua", "Felix", "Morris", "Ryan Kabir"], auto=True)