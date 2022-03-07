import pygame
from pygame.locals import *
import azul
import boardLocs
import board
import time
import os

class App:
    def __init__(self):
        self._running = True
        self._display_fact = None
        self._image_surf = None        

    def on_init(self):
        pygame.init()
        # TODO: change the factors of 2 to be dynamic based on number of players
        self.half_board = 1024
        self.tile_size = 86
        self._display_fact = pygame.display.set_mode((2*self.half_board,2*self.half_board), pygame.HWSURFACE)
        self._running = True
        self._fact_square_im = pygame.image.load("./azul/AzulNN/azul_api/imgs/azulBoard.jpg").convert()

        self.num_players = 4
        self.game = azul.Game(self.num_players)
        self.board_colors = board.Board.get_board_colors()
        self.num_facts = self.game.factDisplays
        self.color_to_file = {'b': './azul/AzulNN/azul_api/imgs/blueSquare.png',
                              'y': './azul/AzulNN/azul_api/imgs/yellowSquare.png',
                              'r': './azul/AzulNN/azul_api/imgs/redSquare.png',
                              'k': './azul/AzulNN/azul_api/imgs/blackSquare.png',
                              'w': './azul/AzulNN/azul_api/imgs/whiteSquare.png',
                              'g': './azul/AzulNN/azul_api/imgs/greenSquare.png'}
        self.num_to_file = {0: './azul/AzulNN/azul_api/imgs/blueSquare.png',
                            1: './azul/AzulNN/azul_api/imgs/yellowSquare.png',
                            2: './azul/AzulNN/azul_api/imgs/redSquare.png',
                            3: './azul/AzulNN/azul_api/imgs/blackSquare.png',
                            4: './azul/AzulNN/azul_api/imgs/whiteSquare.png',
                            5: './azul/AzulNN/azul_api/imgs/greenSquare.png'}
        self.test_font = pygame.font.Font(None,50)


    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
            pygame.quit()

    def on_loop(self):
        self._running = self.game.next_turn()
        if(not self._running):
            scores = [0]*self.num_players
            for play in range(self.num_players):
                scores[play] = self.game.playArray[play].get_score()
                print(f'The score for {play} is: {scores[play]}\n')

            # Save the top two scores
            tmp = max(scores)
            index = scores.index(tmp)
            self.game.playArray[play].saveWinner('s_pred_1.h5')
            scores[index] = -100
            tmp = max(scores)
            index = scores.index(tmp)
            self.game.playArray[play].saveWinner('s_pred_2.h5')

            self.game = azul.Game(self.num_players)
            self._running = True
            


    def on_render(self):
        self._display_fact.blit(self._fact_square_im, (0,0))
        self._display_fact.blit(self._fact_square_im, (self.half_board,0))
        self._display_fact.blit(self._fact_square_im, (0,self.half_board))
        self._display_fact.blit(self._fact_square_im, (self.half_board,self.half_board))
        for p in range(self.num_players):
            xOffset = (p%2)*self.half_board
            yOffset = (p>1)*self.half_board
            wall, floor, garage = self.game.playArray[p].board.get_board()

            for x, row in enumerate(garage):
                for y, tile in enumerate(row):
                    if(tile > -1):
                        file = pygame.image.load(self.num_to_file[tile])
                        loc = boardLocs.garage[x][y]
                        loc = (loc[0] + xOffset, loc[1] + yOffset)
                        self._display_fact.blit(file, loc)

            for x, row in enumerate(wall):
                for y, tile in enumerate(row):
                    if(tile > -1):
                        file = pygame.image.load(self.color_to_file[self.board_colors[x][y]])
                        loc = boardLocs.wall[x][y]
                        loc = (loc[0] + xOffset, loc[1] + yOffset)
                        self._display_fact.blit(file, loc)

            for x, tile in enumerate(floor):
                if(tile > -1):
                    file = pygame.image.load(self.num_to_file[tile])
                    loc = boardLocs.floor[x]
                    loc = (loc[0] + xOffset, loc[1] + yOffset)
                    self._display_fact.blit(file, loc)


            facts = self.game.get_facts().factDisps
            for i, circ in enumerate(facts):
                for j, tile in enumerate(circ):
                    if(tile > -1):
                        xLoc = self.half_board + self.tile_size*(i*4 + j/4 - 8)#self.tile_size*((i%(self.num_facts//2))*4 + j/2 - 8)
                        yLoc = self.half_board #+ self.tile_size*(-4 + (i>(self.num_facts//2)*8))
                        loc = (xLoc,yLoc)
                        file = pygame.image.load(self.num_to_file[tile])
                        self._display_fact.blit(file,loc)
            cent = self.game.fact.tableCenter
            for i, tile in enumerate(cent):
                xLoc = self.half_board + self.tile_size*(i/2 - 10)
                yLoc = self.half_board + self.tile_size*2
                loc = (xLoc, yLoc)
                file = pygame.image.load(self.num_to_file[tile])
                self._display_fact.blit(file,loc)

            
            text_surface = self.test_font.render(f'Score {self.game.playArray[p].score}', False, 'Black')
            xLoc = xOffset + 100
            yLoc = yOffset + 100
            loc = (xLoc,yLoc)
            score_rect = text_surface.get_rect(center = (loc[0] + 61, loc[1]+17))
            pygame.draw.rect(self._display_fact,'White',score_rect)
            self._display_fact.blit(text_surface,loc)
                
            pygame.display.flip()
        time.sleep(2)
        
    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):        
        if self.on_init() == False:
            self._running = False

        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

if __name__ == "__main__":
    the_app = App()
    the_app.on_execute()
    # the_game = Game(4)
    # the_game.start_game()

    # while True:
    #     events()
    #     loop()
    #     render()