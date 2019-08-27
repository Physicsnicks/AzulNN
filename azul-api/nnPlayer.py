import tensorflow as tf
import numpy as np
import random
from player import GenericPlayer

class NNPlayer(GenericPlayer):
    def __init__(self, fact, name="neural", newMod=False, weightMod=0.1):
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
        wallInput = tf.keras.Input(shape=(5, 5, 1))
        factInput = tf.keras.Input(shape=(10, 4))
        centerInput = tf.keras.Input(shape=(50))

        x = tf.keras.layers.Conv2D(10, 1, activation='relu')(wallInput)
        # x = tf.keras.layers.Conv2D(10, 1, activation='relu')(x)
        # x = tf.keras.layers.Dense(10, activation='relu')(x)
        x = tf.keras.layers.Reshape((250,))(x)
        # x = tf.keras.layers.Flatten()(x)
        x = tf.keras.Model(inputs=wallInput, outputs=x)

        # y = tf.keras.layers.Conv2D(20, 1, activation='relu')(factInput)
        # y = tf.keras.layers.Conv2D(15, 1, activation='relu')(y)
        # y = tf.keras.layers.Dense(10, activation='relu')(y)
        y = tf.keras.layers.Dense(25, activation='relu')(factInput)
        # y = tf.keras.layers.Flatten()(y)
        y = tf.keras.layers.Flatten()(y)
        # y = tf.keras.layers.Reshape((25,))(y)
        y = tf.keras.Model(inputs=factInput, outputs=y)

        # q = tf.keras.layers.Conv2D(20, 1, activation='relu')(centerInput)
        # q = tf.keras.layers.Conv2D(15, 1, activation='relu')(q)
        q = tf.keras.layers.Dense(10, activation='relu')(centerInput)
        q = tf.keras.layers.Flatten()(q)
        q = tf.keras.Model(inputs=centerInput, outputs=q)

        combined = tf.keras.layers.concatenate([x.output,
                                                y.output,
                                                q.output])
        # combined = x.output

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
        # self.mod1.summary()

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
                    wet[0] += random.uniform(-weightMod, weightMod)
                    # wet[1] += random.uniform(-weightMod,weightMod)

        else:

            self.mod1.load_weights(filepath=self.model_save_path)

    def pickTiles(self):
        # factIns = self.fact.factDisps + self.fact.tableCenter
        factIns = self.fact.factDisps.copy()
        factIns.append([-1, -1, -1, -1])

        centIns = [-1.] * 50
        for i, tc in enumerate(self.fact.tableCenter):
            centIns[i] = tc

        wallIns = [[[np.float32(y) for y in x] for x in self.board.wall]]
        factIns = [[[np.float32(y) for y in x] for x in factIns]]
        centIns = [np.float32(y) for y in centIns]

        wallIns = np.array(wallIns)
        factIns = np.array(factIns)
        centIns = np.array(centIns)

        # print("wallIns shape",wallIns.shape())
        # print("factIns shape",factIns.shape())
        wallIns = wallIns.reshape((1, 5, 5, 1))
        factIns = factIns.reshape((1, 10, 4))
        centIns = centIns.reshape((1, 50))
        # print("wallIns shape",wallIns.shape())
        # print("factIns shape",factIns.shape())
        fact, col, row = self.mod1([wallIns, factIns, centIns])
        # fact, col, row = self.mod1(wallIns)

        factN = int(fact.numpy()[0, 0])
        col = int(col.numpy()[0, 0])
        row = int(row.numpy()[0, 0])

        if factN > 9 or factN < 0:
            factN = random.randint(0, 9)
        if col > 4 or col < 0:
            col = random.randint(0, 4)
        if row > 4 or row < 0:
            row = random.randint(0, 4)
        onlyCenter = True
        for dis in self.fact.factDisps:
            if dis.count(-1) < 4:
                onlyCenter = False
        if onlyCenter:
            factN = 9
        if factN == 9 and len(self.fact.tableCenter) == 0:
            factN = random.randint(0, 8)
        if factN == 9:
            while self.fact.tableCenter.count(col) == 0:
                col = random.randint(0, 4)
                if self.fact.tableCenter.count(col) > 0:
                    break
            cnt = self.fact.tableCenter.count(col)
            if self.fact.tableCenter.count(5) > 0:
                self.fact.tableCenter.remove(5)
                self.board.floor.append(5)
        else:
            while self.fact.factDisps[factN].count(col) == 0:
                factN = random.randint(0, 8)
                col = random.randint(0, 4)

                if self.fact.factDisps[factN].count(col) > 0:
                    break

            cnt = self.fact.factDisps[factN].count(col)
            for i in range(4):
                if self.fact.factDisps[factN][i] != col:
                    self.fact.tableCenter.append(self.fact.factDisps[factN][i])
            self.fact.factDisps[factN] = [-1, -1, -1, -1]

        while self.board.garage[row].count(col) == 0 and self.board.garage[row].count(-1) != row + 1:
            row = (row + 1) % 5
        tilesUsed = 0
        # print("picked", cnt, "of", col)
        for j in range(len(self.board.garage[row])):
            if self.board.garage[row][j] == -1:
                self.board.garage[row][j] = col
                tilesUsed += 1
        for j in range(cnt - tilesUsed):
            self.board.floor.append(col)
            tilesUsed += 1

    def saveWinner(self):
        self.mod1.save_weights(filepath=self.model_save_path, overwrite=True)