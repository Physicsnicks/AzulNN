import random


class Factory():
    """
          At the start there are 20 of each color and 5 colors in the bag.
          Cheese, Blue, Black, Snowflake, Red
     """

    def __init__(self, disps):
        # These are the number of tiles in the bag
        self.numBlue = 20  # 0
        self.numCheese = 20  # 1
        self.numRed = 20  # 2
        self.numBlack = 20  # 3
        self.numSnowflake = 20  # 4
        self.totNum = self.numBlack + self.numBlue + self.numCheese + self.numRed + self.numSnowflake
        # This is all the tiles on displays, -1 is no tile
        self.factDisps = list()
        for i in range(0, disps):
            self.factDisps.append([-1, -1, -1, -1])
        # Add the "go first tile" to the center of the table
        self.tableCenter = [5]

    def fillDisplays(self):
        # from the bag put tiles on all the displays
        # print("The total length of factDisps is",len(self.factDisps))
        if self.totNum < 10:
            self.numBlue = 20  # 0
            self.numCheese = 20  # 1
            self.numRed = 20  # 2
            self.numBlack = 20  # 3
            self.numSnowflake = 20  # 4
            self.totNum = 100
        for i, disp in enumerate(self.factDisps):
            for j, tile in enumerate(disp):
                if self.totNum == 0:
                    break
                choice = random.randint(1, self.totNum + 1)
                if choice <= self.numBlue:
                    self.numBlue -= 1
                    self.totNum -= 1
                    self.factDisps[i][j] = 0
                elif choice <= self.numBlue + self.numCheese:
                    self.numCheese -= 1
                    self.totNum -= 1
                    self.factDisps[i][j] = 1
                elif choice <= self.numBlue + self.numCheese + self.numRed:
                    self.numRed -= 1
                    self.totNum -= 1
                    self.factDisps[i][j] = 2
                elif choice <= self.numBlue + self.numCheese + self.numRed + self.numBlack:
                    self.numBlack -= 1
                    self.totNum -= 1
                    self.factDisps[i][j] = 3
                else:
                    self.numSnowflake -= 1
                    self.totNum -= 1
                    self.factDisps[i][j] = 4

        self.tableCenter = [5]
        # print("After filling the dipslays:")
        # print(self.factDisps)
        return True
