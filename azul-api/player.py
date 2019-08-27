import graphene
import os
from board import Board


class GenericPlayer(graphene.ObjectType):
    def __init__(self, fact, name="default", id=id):
        self.score = 0
        self.name = name
        self.id = id
        self.board = Board()
        self.fact = fact
        self.model_save_path = os.getcwd() + 'model.h5'

    def endOfGame(self):
        self.score += self.board.getScore()
        return self.score


class HumanPlayer(GenericPlayer):
    def __init__(self, fact, name="Player"):
        GenericPlayer.__init__(self, fact, name=name)
