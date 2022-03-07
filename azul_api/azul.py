import random

# from player import Player
from nnPlayer import NNPlayer
from player import HumanPlayer
from factory import Factory

# If the NN is being trained the following are parameters for the training
batches = 1000
weightMod = 0.02


class Game:
    """
          The game sets up a factory, some players, and keeps track of the turn.
          It also determines what phase of the game we are in depending on the
          factory.
          numPlayers: The total number of players in the game. Valid values are
            [2,4].

          humanPlayer: A boolean indicating whether it is an all computer game
            (False) or a game including a human player (True).

     """

    def __init__(self, numPlayers, save_iteration = True, humanPlayer=False):
        self.numPlayers = numPlayers
        self.save_iteration = save_iteration
        if self.numPlayers == 2:
            self.factDisplays = 5
        elif self.numPlayers == 3:
            self.factDisplays = 7
        elif self.numPlayers == 4:
            self.factDisplays = 9
        else:
            print("Incorrect number of players entered.")

        self.fact = Factory(self.factDisplays)
        self.fact.fill_displays()

        self.playArray = list()
        for i in range(0, numPlayers):
            # if i == 0:
            #     self.playArray.append(Player(self.fact))
            # elif i == 1:
            #     self.playArray.append(
            #         NNPlayer(
            #             self.fact,
            #             newMod=True,
            #             weightMod=weightMod))
            # elif humanPlayer:
            #     self.playArray.append(HumanPlayer(self.fact, name="Hoomun"))
            #     i += 1
            # else:
            self.playArray.append(
                NNPlayer(
                    self.fact,
                    self.factDisplays,
                    newMod=True,
                    weightMod=weightMod,
                    id=i))

        self.playersTurn = random.randint(0, numPlayers - 1)
        self.gameWinner = -1  # This is -1 until someone wins the game
        self.round_num = 0

    def get_facts(self):
        return self.fact

    def display(self, ply, trn):

        print(ply.name, " *** ", trn)
        for i, j in zip(ply.board.wall, ply.board.garage):
            print("***", "    " * (5 - len(j)), j, "***", i, "***")
        print(" ")
        print(ply.board.floor)
        print(" ")
        print(ply.fact.factDisps)
        print(" ")
        print("table center:")
        print(ply.fact.tableCenter)
        print(" ")
        print("score is", ply.score)
        print(" ")
        print(" ")
        # time.sleep(5)

    def next_turn(self):
        self.round_num = self.round_num + 1

        # Verify there are still some available tiles in the factory
        for turn, player in enumerate(self.playArray):
            maxA = 1 if len(self.fact.tableCenter) > 0 else -1
            for i in range(len(self.fact.factDisps)):
                temp = max(self.fact.factDisps[i])
                maxA = max(temp, maxA)
            if maxA == -1:
                # end the game if we can't refill the factory
                self.fact.fill_displays()
                for i, player in enumerate(self.playArray):
                    player.score += player.board.row_to_wall()
                    if len(player.board.floor) > 0:
                        player.score -= len(player.board.floor)
                        player.board.floor = list()
                    if 5 in player.board.floor:
                        self.playersTurn = i - 1

            else:
                turnNum = (self.playersTurn + turn) % self.numPlayers
                self.playArray[turnNum].pickTiles(self.round_num)
                # self.display(self.playArray[self.playersTurn], self.playersTurn)
        
            if player.board.check_end():
                print("Trying to end the game!")
                return False
        return True

    # TODO: This is now outdated because of playersTurn
    def start_game(self):
        keepGoing = True
        while keepGoing:
            keepGoing = self.next_turn()
            self.playersTurn = (self.playersTurn + 1) % self.numPlayers
        return self.end_game()

    def end_game(self):
        bestNNPlayer = {}
        bestPlayer = {}
        for i, player in enumerate(self.playArray):
            score = player.endOfGame()
            if "neural" in player.name:
                bestNNPlayer[i] = score
            bestPlayer[i] = score
            '''
               print("The score for",i,"is",score)
               for i,j in zip(player.board.wall,player.board.garage):
                    print("***","    "*(5-len(j)),j,"***",i,"***")
               print(" ")
               '''
        # Finally, save the winning player to use in the next run
        print("")
        if((len(bestNNPlayer) > 0) & (self.save_iteration)):
            print(
                "NN winner is", max(
                    bestNNPlayer.items(), key=operator.itemgetter(1))[0])
            self.playArray[max(bestNNPlayer.items(),
                               key=operator.itemgetter(1))[0]].saveWinner()

        self.gameWinner = max(
            bestPlayer.items(),
            key=operator.itemgetter(1))[0]
        print("The scores for each player:", bestPlayer)
        print("The winner is", self.gameWinner)
        return self.gameWinner


# gm = Game(4)
'''
totWins = [0, 0, 0, 0]
for i in range(batches):
    gm = Game(4)
    bp = gm.startGame()
    print("bp", bp)
    print("")
    print("")
    print("")
    print("================================================================")
    totWins[bp] += 1
print("Total Wins:")
for i, score in enumerate(totWins):
    print("\tPlayer", i, " score:", score)
'''
