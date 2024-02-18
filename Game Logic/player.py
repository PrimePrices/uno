class player:
    __slots__=["auto", "name", "deck", "hand"]
    def __init__(self, name, cards, auto=False):
        self.auto=auto
        self.name=name
        self.deck=cards
        self.hand=[cards.draw() for _ in range(7)]
        self.hand.sort()
    def __str__(self):
        return self.name+": "+", ".join([str(i) for i in self.hand])
    def draw(self, repeat=1):
        for i in range(repeat):
            self.hand.append(self.deck.draw())
            self.hand.sort()
    def bot_move(self, playable, discard):
        if playable:
            card_n = playable[0][1]
            card=self.hand[card_n]
            print(card, "was played")
            del self.hand[card_n]
            card(auto=True)
            return card
        else:
            self.draw_a_card()
            return discard
    def playable(self, discard):
        return [[v,n] for n,v in enumerate(self.hand) if v==discard]
    def __call__(self, discard):
        playable=self.playable(discard)
        if self.auto:
            print(str(self)+"; "+f"discard={str(discard)}")
            card=self.bot_move(playable, discard)
        else:
            card_n=self.options(playable, discard)
            if card_n in range(len(playable)):
                card=playable[card_n][0]
                card_n=playable[card_n][1]
                card()
                del self.hand[card_n]
            else:
                self.draw_a_card()
                card=discard
        return card, bool(self.hand)
    def draw_a_card(self):
        if self.deck.RULES["draw until play"]:
            self.draw()
            #doesn't run nex player
        else:
            self.draw()
            self.deck.change_next_player()
        print("This player drew a card: ", self.hand[-1])
    def options(self, playable, discard):
            print(self)
            print(f"discard={str(discard)}")
            print("you can play: ", list(str(i[0]) for i in playable), "or you can pick up")
            print(f"Which option do you want out of ") ###get action here
            for n,v in enumerate(playable):
                print(f"{n}:  {v[0]}")
            print(f"{len(playable)}: pick up")
            card_n=int(input())
            return card_n

