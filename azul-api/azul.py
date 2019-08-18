import os
import random
import time
import numpy as np
import tensorflow as tf
import operator
import time
import random

batches = 1000
weightMod = 0.02
class Game():
     '''
          The game sets up a factory, some players, and keeps track of the turn. 
          It also determines what phase of the game we are in depending on the 
          factory.
     '''
     def __init__(self, numPlayers):
          self.numPlayers = numPlayers
          if self.numPlayers == 2:
               self.factDisplays = 5
          elif self.numPlayers == 3:
               self.factDisplays = 7
          elif self.numPlayers == 4:
               self.factDisplays = 9
          else:
               print("Incorrect number of players entered.")
          
          self.fact = Factory(self.factDisplays)
          self.fact.fillDisplays()

          self.playArray = list()
          for i in range(0,numPlayers):
               if i == 0:
                    self.playArray.append(Player(self.fact))
               elif i == 1:
                    self.playArray.append(NNPlayer(self.fact, newMod=True))
               else:
                    self.playArray.append(NNPlayer(self.fact, newMod=True))

          self.playersTurn = random.randint(0,numPlayers-1)

     def display(self, ply, trn):
          
          print(ply.name, " *** ", trn)
          for i,j in zip(ply.board.wall,ply.board.garage):
               print("***","    "*(5-len(j)),j,"***",i,"***")
          print(" ")
          print(ply.board.floor)
          print(" ")
          print(ply.fact.factDisps)
          print(" ")
          print("table center:")
          print(ply.fact.tableCenter)
          print(" ")
          print("score is",ply.score)
          print(" ")
          print(" ")
          #time.sleep(5)

     def nextTurn(self):

          maxA = 1 if len(self.fact.tableCenter) > 0 else -1
          for i in range(len(self.fact.factDisps)):
               temp = max(self.fact.factDisps[i])
               maxA = max(temp,maxA)
          if maxA == -1:
               # end the game if we can't refill the factory
               self.fact.fillDisplays()
               for i, player in enumerate(self.playArray):
                    player.score += player.board.rowToWall()
                    if len(player.board.floor) > 0:
                         player.score -= len(player.board.floor)
                         player.board.floor = list()
                    if 5 in player.board.floor:
                         self.playersTurn = i - 1
               for player in self.playArray:
                    if player.board.checkEnd():
                         print("Trying to end the game!")
                         return False
               
          else:
               self.playArray[self.playersTurn].pickTiles()
               #self.display(self.playArray[self.playersTurn], self.playersTurn)
          return True


     def startGame(self):
          keepGoing = True
          while keepGoing:
               keepGoing = self.nextTurn()
               self.playersTurn = (self.playersTurn + 1)%self.numPlayers
          return self.endGame()

     def endGame(self):
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
          if len(bestNNPlayer) > 0:
               print("NN winner is",max(bestNNPlayer.items(), key=operator.itemgetter(1))[0])
               self.playArray[max(bestNNPlayer.items(), key=operator.itemgetter(1))[0]].saveWinner()
          
          print("The scores for each player:",bestPlayer)
          print("The winner is", max(bestPlayer.items(), key=operator.itemgetter(1))[0])
          return max(bestPlayer.items(), key=operator.itemgetter(1))[0]

class GenericPlayer:
     def __init__(self, fact, name="default"):
          self.score = 0
          self.name = name
          self.board = Board()
          self.fact = fact 
          self.model_save_path = os.getcwd() + 'model.h5'

     def endOfGame(self):
          self.score += self.board.getScore()
          return self.score 




class NNPlayer(GenericPlayer):
     def __init__(self, fact, name="neural", newMod=False):
          GenericPlayer.__init__(self, fact, name=name)
          # initialize the neural net

          # Three separate decisions need to be made:
          #    1. Which square in the wall would we like to fill in?
          #    2. Is it possible to put this color in the garage?
          #    3. How many of this color do we want to grab?
          
          '''
          self.mod1 = tf.keras.models.Sequential([
               # The inputs will be the 5x5 matrix of the wall and 1 channel with the color info
               tf.keras.layers.Conv2D(20, kernel_size=1, activation='relu', input_shape=(5,5,1)),
               tf.keras.layers.Conv2D(5, activation='relu',),
               tf.keras.layers.Dense(5)
               ])
          '''
          wallInput = tf.keras.Input(shape=(5,5,1))
          factInput = tf.keras.Input(shape=(10,4))
          centerInput = tf.keras.Input(shape=(50))

          x = tf.keras.layers.Conv2D(10, 1, activation='relu')(wallInput)
          #x = tf.keras.layers.Conv2D(10, 1, activation='relu')(x)
          #x = tf.keras.layers.Dense(10, activation='relu')(x)
          x = tf.keras.layers.Reshape((250,))(x)
          #x = tf.keras.layers.Flatten()(x)
          x = tf.keras.Model(inputs=wallInput, outputs=x)

          #y = tf.keras.layers.Conv2D(20, 1, activation='relu')(factInput)
          #y = tf.keras.layers.Conv2D(15, 1, activation='relu')(y)
          #y = tf.keras.layers.Dense(10, activation='relu')(y)
          y = tf.keras.layers.Dense(25, activation='relu')(factInput)
          #y = tf.keras.layers.Flatten()(y)
          y = tf.keras.layers.Flatten()(y)
          #y = tf.keras.layers.Reshape((25,))(y)
          y = tf.keras.Model(inputs=factInput, outputs=y)

          
          #q = tf.keras.layers.Conv2D(20, 1, activation='relu')(centerInput)
          #q = tf.keras.layers.Conv2D(15, 1, activation='relu')(q)
          q = tf.keras.layers.Dense(10, activation='relu')(centerInput)
          q = tf.keras.layers.Flatten()(q)          
          q = tf.keras.Model(inputs=centerInput, outputs=q)
          

          combined = tf.keras.layers.concatenate([x.output, 
                                                  y.output, 
                                                  q.output])
          #combined = x.output

          # This output has information about which factory we are taking from
          z1 = tf.keras.layers.Dense(64, activation='relu')(combined)
          z1 = tf.keras.layers.Dense(64, activation='relu')(z1)
          z1 = tf.keras.layers.Dense(8, activation='softmax')(z1)

          # This output tells which color to take
          z2 = tf.keras.layers.Dense(64, activation='relu')(combined)
          z2 = tf.keras.layers.Dense(64, activation='relu')(z2)
          z2 = tf.keras.layers.Dense(5, activation='softmax')(z2)

          # This output tells which row of the garage to place the tiles in
          # If this row is full put it in the next larger row
          z3 = tf.keras.layers.Dense(64, activation='relu')(combined)
          z3 = tf.keras.layers.Dense(64, activation='relu')(z3)
          z3 = tf.keras.layers.Dense(5, activation='softmax')(z3)

          self.mod1 = tf.keras.Model(inputs=[x.input, y.input, q.input], outputs=[z1, z2, z3])
          #self.mod1.summary()

         
          ## ------------------------------------------------
          ##  Load the saved weights from the previous runs
          ##
          self.model_save_path = "s_pred.h5"
          if newMod:
               # Initialize a new model that will compete with the best previous model
               # For now we use a random weight, in the range -weightMod<=n<=weightMod 
               # added to the best previous model's weight [0] and biases [1]
               self.mod1.load_weights(filepath=self.model_save_path)
               for lay in self.mod1.layers:
                    for wet in lay.get_weights():
                         #
                         wet[0] += random.uniform(-weightMod,weightMod)
                         #wet[1] += random.uniform(-weightMod,weightMod)

          else:        
               
               self.mod1.load_weights(filepath=self.model_save_path)
       

     def pickTiles(self):
          #factIns = self.fact.factDisps + self.fact.tableCenter
          factIns = self.fact.factDisps.copy()
          factIns.append([-1,-1,-1,-1])

          centIns = [-1.]*50
          for i, tc in enumerate(self.fact.tableCenter):
               centIns[i] = tc

          wallIns = [[[np.float32(y) for y in x] for x in self.board.wall]]
          factIns = [[[np.float32(y) for y in x] for x in factIns]]
          centIns = [np.float32(y) for y in centIns]
          
          wallIns = np.array(wallIns)
          factIns = np.array(factIns)
          centIns = np.array(centIns)


          #print("wallIns shape",wallIns.shape())
          #print("factIns shape",factIns.shape())
          wallIns = wallIns.reshape((1,5,5,1))
          factIns = factIns.reshape((1,10,4))
          centIns = centIns.reshape((1,50))
          #print("wallIns shape",wallIns.shape())
          #print("factIns shape",factIns.shape())
          fact, col, row = self.mod1([wallIns, factIns, centIns])
          #fact, col, row = self.mod1(wallIns)

          factN = int(fact.numpy()[0,0])
          col = int(col.numpy()[0,0])
          row = int(row.numpy()[0,0])
          
          if factN > 9 or factN < 0:
               factN = random.randint(0,9)
          if col > 4 or col < 0:
               col = random.randint(0,4)
          if row > 4 or row < 0:
               row = random.randint(0,4)
          onlyCenter = True
          for dis in self.fact.factDisps:
               if dis.count(-1) < 4:
                    onlyCenter = False
          if onlyCenter:
               factN = 9
          if factN == 9 and len(self.fact.tableCenter) == 0:
               factN = random.randint(0,8)
          if factN == 9:
               while self.fact.tableCenter.count(col) == 0:
                    col = random.randint(0,4)
                    if self.fact.tableCenter.count(col) > 0:
                         break
               cnt = self.fact.tableCenter.count(col)
               if self.fact.tableCenter.count(5) > 0:
                    self.fact.tableCenter.remove(5)
                    self.board.floor.append(5)
          else:
               while self.fact.factDisps[factN].count(col) == 0:
                    factN = random.randint(0,8)
                    col = random.randint(0,4)

                    if self.fact.factDisps[factN].count(col) > 0:
                         break
                    

               cnt = self.fact.factDisps[factN].count(col)
               for i in range(4):
                    if self.fact.factDisps[factN][i] != col:
                         self.fact.tableCenter.append(self.fact.factDisps[factN][i])
               self.fact.factDisps[factN] = [-1,-1,-1,-1]

          while self.board.garage[row].count(col) == 0 and self.board.garage[row].count(-1) != row+1:

               row = (row+1)%5
          tilesUsed = 0
          #print("picked", cnt, "of", col)
          for j in range(len(self.board.garage[row])):
               if self.board.garage[row][j] == -1:
                    self.board.garage[row][j] = col
                    tilesUsed += 1
          for j in range(cnt-tilesUsed):
               self.board.floor.append(col)
               tilesUsed += 1



     def saveWinner(self):
          self.mod1.save_weights(filepath=self.model_save_path, overwrite=True)



class Player(GenericPlayer):
     '''
          The player sets up a board and is in charge of making decisions about what to 
          grab from the factory.
     '''
     def __init__(self, fact, name="default"):
          GenericPlayer.__init__(self, fact, name=name)
     

     def pickTiles(self):
          turnR = 0
          for i in self.fact.factDisps:
               if max(self.fact.factDisps[turnR]) < 0:
                    turnR += 1

          if turnR < len(self.fact.factDisps):

               for i in self.fact.factDisps[turnR]:
                    if self.fact.factDisps[turnR].count(i) > 1 and i > 0:
                         self.board.addToGarage(i,self.fact.factDisps[turnR].count(i))
                         for j in self.fact.factDisps[turnR]:
                              if j != i and j != -1:
                                   self.fact.tableCenter.append(j)
                         self.fact.factDisps[turnR] = [-1,-1,-1,-1]
                         return True

               for i in self.fact.factDisps[turnR]:
                    if i > 0:
                         self.board.addToGarage(i, self.fact.factDisps[turnR].count(i))
                         for j in self.fact.factDisps[turnR]:
                              if j != i and j != -1:
                                   self.fact.tableCenter.append(j)
                         self.fact.factDisps[turnR] = [-1,-1,-1,-1]
                         return True
          else:
               for i in self.fact.tableCenter:
                    if i > -1 and i < 5:
                         #print("taking",self.fact.tableCenter.count(i), "tiles from center",i)
                         if 5 in self.fact.tableCenter:
                              self.fact.tableCenter.remove(5)
                              self.board.floor.append(5)
                         self.board.addToGarage(i, self.fact.tableCenter.count(i))
                         for j in range(0,self.fact.tableCenter.count(i)):
                              self.fact.tableCenter.remove(i)
                         return True

          return False
          




class Board():
     def __init__(self):
          self.garage = [[-1], 
                         [-1, -1], 
                         [-1, -1, -1], 
                         [-1, -1, -1, -1], 
                         [-1, -1, -1, -1, -1]]
          self.floor = list()
          self.wall = list()

          for i in range(0,5):
               self.wall.append([-1, -1, -1, -1, -1])

     def checkEnd(self):
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
     def checkAdjacents(self,row,col):
          score = 0
          #check how many are in the row and adjacent to the placed tile
          if row < 4:
               for i in range(row+1,5):
                    if self.wall[i][col] > -1:
                         score += 1
                    else:
                         break
          if row > 0:
               for i in range(row-1,-1,-1):
                    if self.wall[i][col] > -1:
                         score += 1
                    else:
                         break
          if col < 4:
               for i in range(col+1,5):
                    if self.wall[row][i] > -1:
                         score += 1
                    else:
                         break
          if col > 0:
               for i in range(col-1,-1,-1):
                    if self.wall[row][i] > -1:
                         score += 1 
                    else:
                         break
          return score

     def rowToWall(self):
          # This verifies that the garage row is full and moves the tile into the
          # wall at the appropriate place for the standard tiling

          # It also returns an update to the score for mid game score changes
          scoreChange = 0
          for i, row in enumerate(self.garage):
               if min(row) > -1:
                    if self.wall[i][(self.garage[i][0]+i)%5] == -1:
                         self.wall[i][(self.garage[i][0]+i)%5] = self.garage[i][0]
                         scoreChange += self.checkAdjacents(i,(self.garage[i][0]+i)%5)
                    for k in range(len(self.garage[i])):
                         self.garage[i][k] = -1
          return scoreChange
          


     def addToGarage(self,tile,cnt):
          tilesUsed = 0
          #print("picked", cnt, "of", tile)
          for i, row in enumerate(self.garage):

               if tile in row and -1 in row and (cnt-tilesUsed) > 0:
                    for j in range(len(self.garage[i])):
                         if self.garage[i][j] == -1:
                              self.garage[i][j] = tile
                              tilesUsed += 1
                    for j in range(cnt-tilesUsed):
                         self.floor.append(tile)
                         tilesUsed += 1
          if cnt < 5:
               if self.wall[cnt-1][(tile+cnt-1)%5] == -1 and max(self.garage[cnt-1]) < 0 and (cnt-tilesUsed) > 0:
                    for i in range(len(self.garage[cnt-1])):
                         self.garage[cnt-1][i] = tile
                         tilesUsed += 1
                    for j in range(cnt-tilesUsed):
                         self.floor.append(tile)
                         tilesUsed += 1

          for i, row in enumerate(self.garage):
               if self.wall[i][(tile+i)%5] == -1 and (cnt-tilesUsed) > 0 and max(row) == -1:
                    for j in range(len(self.garage[i])):
                         if (cnt-tilesUsed) == 0:
                              break
                         if self.garage[i][j] == -1:
                              self.garage[i][j] = tile
                              tilesUsed += 1
                    for j in range(cnt-tilesUsed):
                         self.floor.append(tile)
                         tilesUsed += 1
          for i in range(cnt-tilesUsed):
               self.floor.append(tile)

     def getScore(self):
          bonusScore = 0
          colorCount = [0,0,0,0,0]
          #count 5 color occurences
          for row in self.wall:
               for tile in row:
                    if tile > -1:
                         colorCount[tile] += 1
          for cc in colorCount:
               if cc == 5:
                    bonusScore += 10

          #count rows
          for row in self.wall:
               if min(row) > -1:
                    bonusScore += 2

          #count columns
          for i in range(len(self.wall[0])):
               if min(self.wall[:][i]) > -1:
                    bonusScore += 7

          return bonusScore

class Factory():
     '''
          At the start there are 20 of each color and 5 colors in the bag.
          Cheese, Blue, Black, Snowflake, Red
     '''
     def __init__(self, disps):
          # These are the number of tiles in the bag          
          self.numBlue = 20      # 0
          self.numCheese = 20    # 1
          self.numRed = 20       # 2
          self.numBlack = 20     # 3
          self.numSnowflake = 20 # 4
          self.totNum = self.numBlack + self.numBlue + self.numCheese + self.numRed + self.numSnowflake 
          # This is all the tiles on displays, -1 is no tile
          self.factDisps = list()
          for i in range(0,disps):
               self.factDisps.append([-1,-1,-1,-1])
          # Add the "go first tile" to the center of the table
          self.tableCenter = [5]

     def fillDisplays(self):
          # from the bag put tiles on all the displays
          #print("The total length of factDisps is",len(self.factDisps))
          if self.totNum < 10:
               self.numBlue = 20      # 0
               self.numCheese = 20    # 1
               self.numRed = 20       # 2
               self.numBlack = 20     # 3
               self.numSnowflake = 20 # 4
               self.totNum = 100
          for i, disp in enumerate(self.factDisps):
               for j, tile in enumerate(disp):
                    if self.totNum == 0:                         
                         break
                    choice = random.randint(1,self.totNum+1)
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
          #print("After filling the dipslays:")
          #print(self.factDisps)
          return True


totWins = [0,0,0,0]
for i in range(batches):
     gm = Game(4)
     bp = gm.startGame() 
     print("bp",bp)
     print("")
     print("")
     print("")
     print("================================================================")
     totWins[bp] += 1    
print("Total Wins:")
for i, score in enumerate(totWins):
     print("\tPlayer",i," score:",score)
     