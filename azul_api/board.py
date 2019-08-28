class Board():
    def __init__(self):
        self.garage = [[-1],
                       [-1, -1],
                       [-1, -1, -1],
                       [-1, -1, -1, -1],
                       [-1, -1, -1, -1, -1]]
        self.floor = list()
        self.wall = list()

        for i in range(0, 5):
            self.wall.append([-1, -1, -1, -1, -1])

    def check_end(self):
        for row in self.wall:
            if min(row) > -1:
                return True
        return False

    # The default board looks like this
    # 0 1 2 3 4
    # 4 0 1 2 3
    # 3 4 0 1 2
    # 2 3 4 0 1
    # 1 2 3 4 0
    def check_adjacents(self, row, col):
        score = 0
        # check how many are in the row and adjacent to the placed tile
        if row < 4:
            for i in range(row + 1, 5):
                if self.wall[i][col] > -1:
                    score += 1
                else:
                    break
        if row > 0:
            for i in range(row - 1, -1, -1):
                if self.wall[i][col] > -1:
                    score += 1
                else:
                    break
        if col < 4:
            for i in range(col + 1, 5):
                if self.wall[row][i] > -1:
                    score += 1
                else:
                    break
        if col > 0:
            for i in range(col - 1, -1, -1):
                if self.wall[row][i] > -1:
                    score += 1
                else:
                    break
        return score

    def row_to_wall(self):
        # This verifies that the garage row is full and moves the tile into the
        # wall at the appropriate place for the standard tiling

        # It also returns an update to the score for mid game score changes
        scoreChange = 0
        for i, row in enumerate(self.garage):
            if min(row) > -1:
                if self.wall[i][(self.garage[i][0] + i) % 5] == -1:
                    self.wall[i][(self.garage[i][0] + i) %
                                 5] = self.garage[i][0]
                    scoreChange += self.check_adjacents(
                        i, (self.garage[i][0] + i) % 5)
                for k in range(len(self.garage[i])):
                    self.garage[i][k] = -1
        return scoreChange

    def add_to_garage(self, tile, cnt):
        tilesUsed = 0
        # print("picked", cnt, "of", tile)
        for i, row in enumerate(self.garage):

            if tile in row and -1 in row and (cnt - tilesUsed) > 0:
                for j in range(len(self.garage[i])):
                    if self.garage[i][j] == -1:
                        self.garage[i][j] = tile
                        tilesUsed += 1
                for j in range(cnt - tilesUsed):
                    self.floor.append(tile)
                    tilesUsed += 1
        if cnt < 5:
            if self.wall[cnt - 1][(tile + cnt - 1) % 5] == -1 and \
                    max(self.garage[cnt - 1]) < 0 and (
                    cnt - tilesUsed) > 0:
                for i in range(len(self.garage[cnt - 1])):
                    self.garage[cnt - 1][i] = tile
                    tilesUsed += 1
                for j in range(cnt - tilesUsed):
                    self.floor.append(tile)
                    tilesUsed += 1

        for i, row in enumerate(self.garage):
            if self.wall[i][(tile + i) % 5] == -1 and (cnt -
                                                       tilesUsed) > 0 and max(row) == -1:
                for j in range(len(self.garage[i])):
                    if (cnt - tilesUsed) == 0:
                        break
                    if self.garage[i][j] == -1:
                        self.garage[i][j] = tile
                        tilesUsed += 1
                for j in range(cnt - tilesUsed):
                    self.floor.append(tile)
                    tilesUsed += 1
        for i in range(cnt - tilesUsed):
            self.floor.append(tile)

    def get_score(self):
        bonusScore = 0
        colorCount = [0, 0, 0, 0, 0]
        # count 5 color occurences
        for row in self.wall:
            for tile in row:
                if tile > -1:
                    colorCount[tile] += 1
        for cc in colorCount:
            if cc == 5:
                bonusScore += 10

        # count rows
        for row in self.wall:
            if min(row) > -1:
                bonusScore += 2

        # count columns
        for i in range(len(self.wall[0])):
            if min(self.wall[:][i]) > -1:
                bonusScore += 7

        return bonusScore
