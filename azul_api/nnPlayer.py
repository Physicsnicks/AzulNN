import random

import tensorflow as tf
from tensorflow.keras import initializers
from tensorflow import keras
import numpy as np

from player import GenericPlayer


class NNPlayer(GenericPlayer):
    def __init__(self, fact, num_fact_disps, name="neural", id=id, newMod=False, weightMod=0.1):
        GenericPlayer.__init__(self, fact, num_fact_disps, id=id, name=name)
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
        if newMod:
  
            self.mod1 = self.makeModel()
            self.mod_targ = self.makeModel()
            # # Initialize a new model that will compete with the best previous model
            # # For now we use a random weight, in the range -weightMod<=n<=weightMod
            # # added to the best previous model's weight [0] and biases [1]
            # # self.mod1.load_weights(filepath=self.model_save_path)
            # for lay in self.mod1.layers:
            #     for wet in lay.get_weights():
            #         #
            #         wet[0] += random.uniform(-weightMod, weightMod)
            #         # wet[1] += random.uniform(-weightMod,weightMod)

        else:
            if(id < 2):
                model_path = 's_pred_1.h5'
            else:
                model_path = 's_pred_2.h5'
            self.mod1 = tf.keras.models.load_model(filepath=model_path)
            self.mod_targ = tf.keras.models.load_model(filepath=model_path)
            # # get a random layer that isn't an input layer
            # layer_num = random.randint(4, len(self.mod1.layers)-1)
            # # get the shape of the layer
            # # layer_shape = self.mod1.layers[layer_num].get_output_at(0).get_shape().as_list()[1:]
            # # weight_to_mod = [0]*len(layer_shape)
            # # for layer, layer_size in enumerate(layer_shape):
            # #     weight_to_mod[layer] = random.randint(0,layer_size)
            # if(len(self.mod1.layers[layer_num].get_weights()) > 0):
            #     cur_weights = self.mod1.layers[layer_num].get_weights()[0]
            #     r_weight = random.choice(cur_weights)
            #     cur_biases = self.mod1.layers[layer_num].get_weights()[1]
            #     r_bias = random.choice(cur_biases)
            #     inds = [random.randint(0,i-1) for i in cur_weights.shape]
            #     cur_weights[inds[0],inds[1]] = random.random()
            #     cur_biases[inds[1]] = random.random()
            #     self.mod1.layers[layer_num].set_weights([cur_weights,cur_biases])

        # In the Deepmind paper they use RMSProp however then Adam optimizer
        # improves training time
        self.optimizer = keras.optimizers.Adam(learning_rate=0.00025, clipnorm=1.0)
        self.batch_size = 8
        self.gamma = 0.99
        self.num_turns = 0

        # Experience replay buffers
        self.action_history = []
        self.state_history = []
        self.state_next_history = []
        self.rewards_history = []
        self.done_history = []
        self.episode_reward_history = []
        # self.running_reward = 0
        # self.episode_count = 0
        # Number of frames to take random action and observe output
        # self.epsilon_random_turns = 500
        # Number of frames for exploration
        # self.epsilon_greedy_turns = 10000.0
        # Maximum replay length
        # Note: The Deepmind paper suggests 1000000 however this causes memory issues
        # self.max_memory_length = 100000
        # Train the model after 4 actions
        self.update_after_actions = 4
        # How often to update the target network
        # self.update_target_network = 100
        # Using huber loss for stability
        self.loss_function = keras.losses.Huber()
        self.mod1.compile(loss=self.loss_function, optimizer=self.optimizer)
        self.episode_reward = 0

    def makeModel(self):
        wallInput = tf.keras.Input(shape=(5, 5, 1))
        factInput = tf.keras.Input(shape=(10, 4))
        centerInput = tf.keras.Input(shape=(50))

        x = tf.keras.layers.Dense(10, kernel_initializer=initializers.RandomNormal(stddev=0.01), activation='relu')(wallInput)
        # x = tf.keras.layers.Conv2D(10, 1, activation='relu')(wallInput)
        # x = tf.keras.layers.Conv2D(10, 1, activation='relu')(x)
        x = tf.keras.layers.Dense(10, kernel_initializer=initializers.RandomNormal(stddev=0.01), activation='relu')(x)
        x = tf.keras.layers.Reshape((250,))(x)
        # x = tf.keras.layers.Flatten()(x)
        x = tf.keras.Model(inputs=wallInput, outputs=x)

        # y = tf.keras.layers.Conv2D(20, 1, activation='relu')(factInput)
        # y = tf.keras.layers.Conv2D(15, 1, activation='relu')(y)
        # y = tf.keras.layers.Dense(10, activation='relu')(y)
        y = tf.keras.layers.Dense(25, kernel_initializer=initializers.RandomNormal(stddev=0.01), activation='relu')(factInput)
        # y = tf.keras.layers.Flatten()(y)
        y = tf.keras.layers.Flatten()(y)
        # y = tf.keras.layers.Reshape((25,))(y)
        y = tf.keras.Model(inputs=factInput, outputs=y)

        # q = tf.keras.layers.Conv2D(20, 1, activation='relu')(centerInput)
        # q = tf.keras.layers.Conv2D(15, 1, activation='relu')(q)
        q = tf.keras.layers.Dense(10, kernel_initializer=initializers.RandomNormal(stddev=0.01), activation='relu')(centerInput)
        q = tf.keras.layers.Flatten()(q)
        q = tf.keras.Model(inputs=centerInput, outputs=q)

        combined = tf.keras.layers.concatenate([x.output,
                                                y.output,
                                                q.output])
        # combined = x.output

        # This output has information about which factory we are taking from
        z1 = tf.keras.layers.Dense(64, kernel_initializer=initializers.RandomNormal(stddev=0.01), activation='relu')(combined)
        z1 = tf.keras.layers.Dense(64, kernel_initializer=initializers.RandomNormal(stddev=0.01), activation='relu')(z1)
        z1 = tf.keras.layers.Dense(self.num_fact_disps+1, kernel_initializer=initializers.RandomNormal(stddev=0.01), activation='softmax')(z1)

        # This output tells which color to take
        z2 = tf.keras.layers.Dense(64, kernel_initializer=initializers.RandomNormal(stddev=0.01), activation='relu')(combined)
        z2 = tf.keras.layers.Dense(64, kernel_initializer=initializers.RandomNormal(stddev=0.01), activation='relu')(z2)
        z2 = tf.keras.layers.Dense(5, kernel_initializer=initializers.RandomNormal(stddev=0.01), activation='softmax')(z2)

        # This output tells which row of the garage to place the tiles in
        # If this row is full put it in the next larger row
        z3 = tf.keras.layers.Dense(64, kernel_initializer=initializers.RandomNormal(stddev=0.01), activation='relu')(combined)
        z3 = tf.keras.layers.Dense(64, kernel_initializer=initializers.RandomNormal(stddev=0.01), activation='relu')(z3)
        z3 = tf.keras.layers.Dense(5, kernel_initializer=initializers.RandomNormal(stddev=0.01), activation='softmax')(z3)

        return tf.keras.Model(
                inputs=[
                    x.input, y.input, q.input], outputs=[
                    z1, z2, z3])

    def takeFromTableCenter(self,col):
        cnt = self.fact.tableCenter.count(col)
        if(cnt == 0):
            col = random.choice(self.fact.tableCenter)
            cnt = self.fact.tableCenter.count(col)
        self.fact.tableCenter.remove(col)
        self.fact.tableCenter = [value for value in self.fact.tableCenter if value != col]
        if self.fact.tableCenter.count(5) > 0:
            self.fact.tableCenter.remove(5)
            if(len(self.board.floor) < 6):
                self.board.floor.append(5)
        return cnt


    def pickTiles(self,turn_num):
        self.num_turns = turn_num
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
        wallIns = wallIns.reshape((1, 5, 5, 1))
        factIns = factIns.reshape((1, 10, 4))
        centIns = centIns.reshape((1, 50))

        state = [wallIns,factIns,centIns]
        # state_tensor = tf.convert_to_tensor(state)
        # state_tensor = tf.expand_dims(state_tensor, 0)
        fact, col, row  = self.mod1(state, training=False)
        max_action = [tf.argmax(fact), tf.argmax(col), tf.argmax(row)]
        self.action_history.append(max_action)
        self.state_history.append(state)
        self.take_turn(fact,col,row)
        if(turn_num%self.update_after_actions == 0):
            self.train_model()

    def take_turn(self,fact,col,row):
        old_score = self.score
        # Take best action
        # action = tf.argmax(action_probs[0]).numpy()

        # fact, col, row = self.mod1([wallIns, factIns, centIns])
        # fact, col, row = self.mod1(wallIns)

        if(np.shape(fact.numpy())[0] == self.num_fact_disps+1):
            orderedFacts = np.argsort(fact.numpy())
        else:
            orderedFacts = np.argsort(fact.numpy()[0])
        factIdx = 0
        factN = orderedFacts[factIdx]
        if(np.shape(col.numpy())[0] == 5):
            orderedCols = np.argsort(col.numpy())
        else:
            orderedCols = np.argsort(col.numpy()[0])
        colIdx = 0
        col = orderedCols[colIdx]
        if(np.shape(row.numpy())[0] == 5):
            orderedRows = np.argsort(row.numpy())
        else:
            orderedRows = np.argsort(row.numpy()[0])
        rowIdx = 0
        row = orderedRows[rowIdx]
        
        onlyCenter = False
        flat_list = [item for sublist in self.fact.factDisps for item in sublist]
        if flat_list.count(-1) == 4*self.num_fact_disps:
            onlyCenter = True
        if onlyCenter:
            if(self.fact.tableCenter.count(-1) == len(self.fact.tableCenter)):
                # Refill because the factories and table are empty
                self.fact.fill_displays()
            elif(self.fact.tableCenter.count(col) == 0):
                factN = self.num_fact_disps
                random.choice(self.fact.tableCenter)
            else:
                factN = self.num_fact_disps

        if factN == self.num_fact_disps and len(self.fact.tableCenter) == 0:
            factN = random.randint(0, self.num_fact_disps)
        elif factN == self.num_fact_disps:            
            cnt = self.takeFromTableCenter(col)
        else:
            while( self.fact.factDisps[factN].count(col) == 0):
                # take one of the cols available in that factory
                if(max(self.fact.factDisps[factN]) > -1):
                    col = random.choice(self.fact.factDisps[factN])
                else:
                    factIdx = (factIdx + 1)%self.num_fact_disps
                    factN = orderedFacts[factIdx]
                if(factN == self.num_fact_disps):
                    if(self.fact.tableCenter.count(col) == 0):
                        factIdx = (factIdx + 1)%self.num_fact_disps
                        factN = orderedFacts[factIdx]
                    else:
                        break

            if factN == self.num_fact_disps:            
                cnt = self.takeFromTableCenter(col)  
            else:
                cnt = self.fact.factDisps[factN].count(col)
                for i in range(4):
                    if self.fact.factDisps[factN][i] != col:
                        self.fact.tableCenter.append(self.fact.factDisps[factN][i])
                self.fact.factDisps[factN] = [-1, -1, -1, -1]

        # see if the garage row has other colors in it
        # of if the wall for that row already has this color occupied
        check5 = 0
        tilesUsed = 0
        while ((self.board.garage[row].count(
                col) == 0 and self.board.garage[row].count(-1) != row + 1) or
                (self.board.wall[row][(col+row)%5] == 1)):
            rowIdx = (rowIdx + 1)%5
            row = orderedRows[rowIdx]
            check5 = check5 + 1
            # The garage is full and the colors go on the floor
            if(check5 == 5):
                for tileNum in range(cnt):
                    if(len(self.board.floor) < 6):
                        self.board.floor.append(col)
                tilesUsed = cnt
                cnt = 0
                break

        
        # print("picked", cnt, "of", col)
        for j in range(len(self.board.garage[row])):
            if((self.board.garage[row][j] == -1) &
               (tilesUsed < cnt)):
                self.board.garage[row][j] = col
                tilesUsed += 1
        for j in range(cnt - tilesUsed):
            if(len(self.board.floor) < 6):
                self.board.floor.append(col)
            tilesUsed += 1

        # now tile the wall and reset the garage
        for num, row in enumerate(self.board.garage):
            if(row.count(-1) == 0):
                col = row[0]
                self.board.wall[num][(col+num)%5] = 1
                self.board.garage[num] = [-1]*(num+1)
                self.score = self.score + GenericPlayer.get_round_score(self,num,(col+num)%5)

        factIns_next = self.fact.factDisps.copy()
        factIns_next.append([-1, -1, -1, -1])

        centIns_next = [-1.] * 50
        for i, tc in enumerate(self.fact.tableCenter):
            centIns_next[i] = tc
            
        wallIns_next = [[[np.float32(y) for y in x] for x in self.board.wall]]
        factIns_next = [[[np.float32(y) for y in x] for x in factIns_next]]
        centIns_next = [np.float32(y) for y in centIns_next]
        wallIns_next = np.array(wallIns_next)
        factIns_next = np.array(factIns_next)
        centIns_next = np.array(centIns_next)
        wallIns_next = wallIns_next.reshape((1, 5, 5, 1))
        factIns_next = factIns_next.reshape((1, 10, 4))
        centIns_next = centIns_next.reshape((1, 50))

        state_next = [wallIns_next,factIns_next,centIns_next]
        self.state_next_history.append(state_next)
        # self.done_history.append()
        self.rewards_history.append(old_score-self.score)
        return old_score-self.score

    def train_model(self):
        indices = np.random.choice(range(len(self.rewards_history)), size=self.batch_size)

        wall_state = np.array([self.state_history[i][0][0] for i in indices])
        fact_state = np.array([self.state_history[i][1][0] for i in indices])
        cent_state = np.array([self.state_history[i][2][0] for i in indices])
        state_sample = [wall_state,fact_state,cent_state]
        # state_sample = np.array([self.state_history[i] for i in indices])
        wall_state_next = np.array([self.state_next_history[i][0][0] for i in indices])
        fact_state_next = np.array([self.state_next_history[i][1][0] for i in indices])
        cent_state_next = np.array([self.state_next_history[i][2][0] for i in indices])
        state_sample_next = [wall_state_next,fact_state_next,cent_state_next]
        # state_sample_next = np.array([self.state_next_history[i] for i in indices])
        rewards_sample = [self.rewards_history[i] for i in indices]
        action_sample = [self.action_history[i][0] for i in indices]
        # Build the updated Q-values for the sampled future states
        # Use the target model for stability
        # future_rewards = self.mod1.predict(state_sample_next)
        next_fact, next_col, next_row  = self.mod1(state_sample_next)

        # save old values enter future states, calculate rewards, then reset the values
        cur_wall = self.board.wall
        cur_factDisps = self.fact.factDisps
        cur_fact_tableCenter = self.fact.tableCenter
        cur_garage = self.board.garage
        cur_floor = self.board.floor
        cur_score = self.score

        # This needs to be done for all samples in state_next_sample, then compiled back into the 
        # updated q values so that they contain the current q value + an update for potential future
        # rewards
        next_rewards = []
        for f,c,r in zip(next_fact,next_col,next_row):
            next_rewards.append(self.take_turn(f,c,r))

            self.board.wall = cur_wall
            self.fact.factDisps = cur_factDisps        
            self.fact.tableCenter = cur_fact_tableCenter 
            self.board.garage = cur_garage
            self.board.floor = cur_floor
            self.score = cur_score
        

        # Q value = reward + discount factor * expected future reward
        updated_q_values = rewards_sample + self.gamma*np.array(next_rewards)

        # masks = tf.one_hot(action_sample, [self.num_fact_disps+1,5,5])

        with tf.GradientTape() as tape:
            # Train the model on the states and updated Q-values
            cur_wall = self.board.wall
            cur_factDisps = self.fact.factDisps
            cur_fact_tableCenter = self.fact.tableCenter
            cur_garage = self.board.garage
            cur_floor = self.board.floor
            cur_score = self.score

            fact,col,row = self.mod1(state_sample)
            # rewards = self.take_turn(fact,col,row)
            rewards = []
            for f,c,r in zip(fact,col,row):
                rewards.append(self.take_turn(f,c,r))

                self.board.wall = cur_wall
                self.fact.factDisps = cur_factDisps        
                self.fact.tableCenter = cur_fact_tableCenter 
                self.board.garage = cur_garage
                self.board.floor = cur_floor
                self.score = cur_score

            # self.board.wall = cur_wall            
            # self.fact.factDisps = cur_factDisps        
            # self.fact.tableCenter = cur_fact_tableCenter 
            # self.board.garage = cur_garage
            # self.board.floor = cur_floor
            # self.score = cur_score
            
            # Calculate loss between new Q-value and old Q-value
            loss = self.loss_function(updated_q_values, np.array(rewards))

        # Backpropagation
        grads = tape.gradient(loss, self.mod1.trainable_variables)
        self.optimizer.apply_gradients(zip(grads, self.mod1.trainable_variables))

    def saveWinner(self,model_save_path):
        self.rewards_history[-1] = self.score/self.num_turns
        self.train_model()
        self.mod_targ
        self.mod1.save(filepath=model_save_path, overwrite=True)
