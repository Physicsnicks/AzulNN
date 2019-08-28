from player import GenericPlayer


class Player(GenericPlayer):
    '''
          The player sets up a board and is in charge of making decisions about what to
          grab from the factory.
     '''

    def __init__(self, fact, name="default", id=-1):
        GenericPlayer.__init__(self, fact, name=name, id=id)

    def pickTiles(self):
        turnR = 0
        for i in self.fact.factDisps:
            if max(self.fact.factDisps[turnR]) < 0:
                turnR += 1

        if turnR < len(self.fact.factDisps):

            for i in self.fact.factDisps[turnR]:
                if self.fact.factDisps[turnR].count(i) > 1 and i > 0:
                    self.board.add_to_garage(
                        i, self.fact.factDisps[turnR].count(i))
                    for j in self.fact.factDisps[turnR]:
                        if j != i and j != -1:
                            self.fact.tableCenter.append(j)
                    self.fact.factDisps[turnR] = [-1, -1, -1, -1]
                    return True

            for i in self.fact.factDisps[turnR]:
                if i > 0:
                    self.board.add_to_garage(
                        i, self.fact.factDisps[turnR].count(i))
                    for j in self.fact.factDisps[turnR]:
                        if j != i and j != -1:
                            self.fact.tableCenter.append(j)
                    self.fact.factDisps[turnR] = [-1, -1, -1, -1]
                    return True
        else:
            for i in self.fact.tableCenter:
                if i > -1 and i < 5:
                    # print("taking",self.fact.tableCenter.count(i), "tiles from center",i)
                    if 5 in self.fact.tableCenter:
                        self.fact.tableCenter.remove(5)
                        self.board.floor.append(5)
                    self.board.add_to_garage(i, self.fact.tableCenter.count(i))
                    for j in range(0, self.fact.tableCenter.count(i)):
                        self.fact.tableCenter.remove(i)
                    return True

        return False
