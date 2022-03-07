import os

# import graphene

from board import Board


class GenericPlayer():#graphene.ObjectType):
    def __init__(self, fact, num_fact_disps, name="default", id=id):
        self.score = 0
        self.name = name
        self.id = id
        self.board = Board()
        self.fact = fact
        self.num_fact_disps = num_fact_disps
        self.model_save_path = os.getcwd() + 'model.h5'

    def get_round_score(self,x,y):
        num_verts = 0
        num_horiz = 0
        right = x + 1
        while((right < 5) and (self.board.wall[right][y] > -1)):
            num_horiz = num_horiz + 1
            right = right + 1
        left = x - 1
        while((left > -1) and (self.board.wall[left][y] > - 1)):
            num_horiz = num_horiz + 1
            left = left - 1
        top = y - 1
        while((top > -1) and (self.board.wall[x][top] > - 1)):
            num_verts = num_verts + 1
            top = top - 1
        bot = y + 1
        while((bot < 5) and (self.board.wall[x][bot] > - 1)):
            num_verts = num_verts + 1
            bot = bot + 1
        if(num_verts > 0):
            num_verts = num_verts + 1
        if(num_horiz > 0):
            num_horiz = num_horiz + 1
        new_score = num_horiz + num_verts
        if(new_score == 0):
            new_score = 1
        return new_score

    def get_final_score(self):
        num_horiz = 0
        num_vert = 0
        for row in self.board.wall:
            if(row.count(-1) == 0):
                num_horiz = num_horiz + 1
        for col in range(5):
            if(self.board.wall[:][col].count(-1) == 0):
                num_vert = num_vert + 1
        diag = [0]*5
        for i in range(5):
            for j in range(5):
                diag[i] = diag[i] + self.board.wall[j][(i+j)%5]
        diag = diag.count(5)

        num_floor = len(self.board.floor)
        if num_floor < 3:
            num_floor = num_floor
        elif(num_floor < 6):
            num_floor = 2 + (num_floor-2)*2
        else:
            num_floor = 2 + 6 + (num_floor - 5)*3

        self.score = self.score + diag*10 + num_vert*7 + num_horiz*2 - num_floor
        return self.score

    def endOfGame(self):
        return self.get_final_score()


class HumanPlayer(GenericPlayer):
    def __init__(self, fact, name="Player"):
        GenericPlayer.__init__(self, fact, name=name)
