# Jessica Cioffi
# Daniel Jasek
# Programming Paradigms Final

import os, sys
import pygame
import math
import time
from math import sin, pi, cos
from random import randint

from pygame.locals import *

from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

MAIN_LOOP_DELAY = .016
SYNC_LOOP_DELAY = 2
SNAKE_LENGTH = 3
SNAKE_VEL = 1
BODY1 = "green.png"
BODY2 = "yellow.png"
HEAD1 = "pink.png"
HEAD2 = "blue.png"

HOST = "localhost"

class GameSpace:
    def main(self, connection, player):

        try:

            self.connection = connection
            self.player = player

            # init window
            pygame.init()
            self.keepPlaying = True
            self.size = 600
            self.screen = pygame.display.set_mode((self.size,self.size)) # sets the window size
            pygame.mouse.set_visible(1) # makes the mouse visible

            if self.player == 0:
                pygame.display.set_caption('Player 1')
            else:
                pygame.display.set_caption('Player 2')

            self.clock = pygame.time.Clock() # initializes the clock

            # set up game variables
            self.done = False # sets the loop determinant
            self.keys = pygame.key.set_repeat(1,50) # helps with lag
            
            # intialize game objects
            if self.player == 0:
                self.snake = Snake(SNAKE_LENGTH, BODY1, HEAD1, 100, 100, connection, 0, self)
                self.enemy = Snake(SNAKE_LENGTH, BODY2, HEAD2, 100, 200, 1, self)
            else:
                self.snake = Snake(SNAKE_LENGTH, BODY2, HEAD2, 100, 200, connection, 0, self)
                self.enemy = Snake(SNAKE_LENGTH, BODY1, HEAD1, 100, 100, 1, self)

            if self.player == 0:
                # initializing food
                #self.food = [] # list to store food objects
                self.food = {}
                self.foodlog = [] # list to store food positions on board
                for i in range(0,9): # for number of food objects on board at one time
                    x = randint(1,599)
                    y = randint(1,599)
                    self.foodlog.append((x,y))

                # add food objects to list
                i = 0
                for j in self.foodlog:
                    self.food[i] = Food(j[0], j[1], self)
                    i += 1
                    #self.food.append(Food(j[0], j[1], self))

                self.sendFoodPosition()
            else:
                pass
                self.receiveFoodPosition()

            # init game over messages
            pygame.font.init()
            font = pygame.font.SysFont('monospace', 30)
            self.textsurface = font.render('Game Over', True, (0, 255, 0))
            self.winMessage = font.render('You Won!', True, (0, 255, 0))
            self.loseMessage = font.render('You Lost!', True, (0, 255, 0))
            self.playAgainMessage = font.render('Press "r" to play again', True, (0, 255, 0))

            self.gameover = False
            self.win = False
            self.lose = False
            self.snakecollide = False

        except Exception as ex:
            print ex

    def loop(self):

        self.clock.tick(60)
        for event in pygame.event.get(): # accounts for the different possible events
            if event.type == pygame.KEYDOWN:

                self.key = pygame.key.get_pressed()

                if self.key[K_r]:
                    self.main(self.connection, self.player) # re-initialize the game
                    #signal the other player to also reinitialize their game
                    self.connection.transport.write("restart") 

                else:
                    self.snake.changeDirection(self.key, self.player, self.connection)

            elif event.type == pygame.QUIT: # quit pygame and twisted and exit
                #self.sendQuit()
                self.quit()

        if self.keepPlaying == True:
            self.snake.tick()
            self.enemy.tick()

            # for y in self.food:
            #     y.tick(self.food) # passes in list of positions to update if eaten
      
            self.snake.foodcollide(self.food)
            #self.enemy.foodcollide(self.food)

            # we lose if we hit the wall or we collide with the enemy
            self.lose = self.snake.wallcollide() or self.snake.snakecollide(self.enemy)

            # we win if the enemy hits a wall or collides with us
            self.win = self.enemy.wallcollide() or self.enemy.snakecollide(self.snake)
            
            self.keepPlaying = not(self.lose or self.win)

        # blits sprites to screen
        self.screen.fill((0, 0, 0)) # fills the background with black
        
        for x in self.food:
            # if x.display:
            #     self.screen.blit(x.image, x.rect)
            if self.food[x].display:
                self.screen.blit(self.food[x].image, self.food[x].rect)

        # display end game messages    
        if not self.keepPlaying:
            self.screen.blit(self.textsurface, (self.size/2 - 100, self.size/2 - 100))
            self.screen.blit(self.playAgainMessage, (self.size/2 - 250, self.size/2 + 100))

            if self.lose:
               self.screen.blit(self.loseMessage,(self.size/2 - 100, self.size/2))
            else:
                self.screen.blit(self.winMessage,(self.size/2 - 100, self.size/2))

        # display each block in the snake body
        # don't display the first block, because it is just an invisible "leader" 
        # of the rest of the body
        for i in range(len(self.snake.blocks)):
            if i > 0:
                b = self.snake.blocks[i]
                self.screen.blit(b.image, b.rect)

        for i in range(len(self.enemy.blocks)):
            if i > 0:
                b = self.enemy.blocks[i]
                self.screen.blit(b.image, b.rect)
        
        # update the display
        pygame.display.flip()

    # handler function that update enemy direction when received from network
    def enemyDirectionHandler(self, direction):
        if direction == "right":
            self.enemy.blocks[0].dir = "right"
        elif direction == "left":
            self.enemy.blocks[0].dir = "left"
        elif direction == "up":
            self.enemy.blocks[0].dir = "up"
        elif direction == "down":
            self.enemy.blocks[0].dir = "down"

    # sends each block position in string form to the other player
    # used to sync up players every once in a while
    def sendPosition(self):
        for i in range(len(self.snake.blocks)):
            b = self.snake.blocks[i]
            data = str(i) + ":" + str(b.rect.topleft[0]) + ":" + str(b.rect.topleft[1]) + ":" + b.dir + "\n"
            self.connection.transport.write(data)

    # handler function for receiving full position data
    def receivePosition(self, data):
        data = data.split("\n")
        for d in data: 
            d = d.strip()
            if len(d) > 1: # not a random empty whitespace line
                d = d.strip()
                d = d.split(":")
                #print "--d:", d, "--"

                print d

                if d[0] == "increase length":
                    print "increase length"
                    self.enemy.increaselen()

                if len(d) == 4 and d[0] != "food":

                    # attempt to parse positional and directional data out of line
                    # sometimes the line is malformed, so we need to try/except these cases
                    # and just update the block later
                    try:
                        print "updating position"
                        index = int(d[0])
                        xpos = int(d[1])
                        ypos = int(d[2])
                        self.enemy.blocks[index].rect.topleft = (xpos, ypos) #update the enemy position at the proper index
                        if d[3] == "right" or d[3] == "left" or d[3] == "up" or d[3] == "down":
                            self.enemy.blocks[index].dir = d[3]
                    except Exception as ex:
                        print ex
                        pass

                else:
                    try:
                        print "updating food position"

                        #self.food.append(Food(int(d[0]), int(d[1]), self))
                        index = int(d[1])
                        self.food[index] = Food(int(d[2]), int(d[3]), self)
                        pass

                    except Exception as ex:
                        print ex
                        pass


    def sendQuit(self):
        print "inside send quit"
        print self.connection.transport
        self.connection.transport.write("quit")
        print "after send quit"

    def quit(self):
        pygame.quit()
        reactor.stop()

    def sendFoodPosition(self):
        self.connection.transport.write("food data\n")
        print self.food
        for f in self.food:
            #might need to send in order
            # self.connection.transport.write(str(f.rect.topleft[0]) + ":" + str(f.rect.topleft[1]) + "\n")
            data = "food:" + str(f) + ":" + str(self.food[f].rect.topleft[0]) + ":" + str(self.food[f].rect.topleft[1]) + "\n"
            print "sending data: " + data
            self.connection.transport.write(data)


    def receiveFoodPosition(self):
        self.food = {}
        pass

# Network Classes
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# client connection class - used by player 2
class ClientConnection(Protocol):
    def __init__(self, gs):
        self.gs = gs
    
    def connectionMade(self):
        print "service connection made on client side"
        self.gs.main(self, 1) #start playing as player 2

        # set up and start loop to run the main function
        self.mainLoop = LoopingCall(self.gs.loop)
        self.mainLoop.start(MAIN_LOOP_DELAY) #1/60th of a second

        # set up and start loop to run the sync position function
        self.syncLoop = LoopingCall(self.gs.sendPosition)
        self.syncLoop.start(SYNC_LOOP_DELAY)

    def dataReceived(self, data):
        print "data: #", data, "#"

        # check if data is just a direction change
        if data == "right" or data == "left" or data == "up" or data == "down":
            #pass
            self.gs.enemyDirectionHandler(data)
        elif data == "quit":
            self.gs.quit()
        elif data == "game over":
            print "received game over signal"
            self.gs.keepPlaying == False
        elif data == "restart":
            #self.mainLoop.stop()
            self.gs.keepPlaying = True
            self.gs.main(self, 1)
        else:# we are syncing up positions completely
            #print "#" + data.split("\n")[0] + "#"
            self.gs.receivePosition(data)

class ClientConnectionFactory(ClientFactory):
    def __init__(self, gs):
        self.myconn = ClientConnection(gs)
        
    def buildProtocol(self, addr):
        return self.myconn

# connection for player 1
class ServerConnection(Protocol):
    def __init__(self, gs):
        self.gs = gs
    
    def connectionMade(self):
        print "service connection made on server side"
        self.gs.main(self, 0) # start playing as player one

        self.mainLoop = LoopingCall(self.gs.loop)
        self.mainLoop.start(MAIN_LOOP_DELAY) #1/60th of a second

        self.syncLoop = LoopingCall(self.gs.sendPosition)
        self.syncLoop.start(SYNC_LOOP_DELAY)

    def dataReceived(self, data):
        #print "data: ", data 
        if data == "right" or data == "left" or data == "up" or data == "down":
            #pass
            self.gs.enemyDirectionHandler(data)
        elif data == "quit":
            self.gs.quit()
        elif data == "restart":
            #self.mainLoop.stop()
            self.gs.keepPlaying = True
            self.gs.main(self, 0)
            #self.mainLoop.start(MAIN_LOOP_DELAY) #1/60th of a second
        else:
            self.gs.receivePosition(data)

class ServerConnectionFactory(Factory):
    def __init__(self, gs):
        self.myconn = ServerConnection(gs)
        
        
    def buildProtocol(self, addr):
        return self.myconn

# Game Objects
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# class for blocks that make up the snake
# each has an image, rect, and a movement direction
class Block(pygame.sprite.Sprite):
    def __init__(self, image, rect, direction):
        self.image = image
        self.rect = rect
        self.dir = direction

class Food(pygame.sprite.Sprite):
    def __init__(self, x, y, gs=None):
        pygame.sprite.Sprite.__init__(self)
        self.gs = gs
        self.image = pygame.image.load('food.png').convert()
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.display = True
        self.rect.center = [self.x, self.y]
    
    def randMove(self):
        self.x = randint(1,599)
        self.y = randint(1,599)
        self.rect.center = [self.x, self.y]
    
    def tick(self, food): # check for being inside snake body - pass in the snake and the enemy
        pass

class Snake(pygame.sprite.Sprite):
    def __init__(self, length, bodyIm, headIm, xpos, ypos, connection, player, gs=None):

        pygame.sprite.Sprite.__init__(self)
        self.gs = gs

        # load images
        self.image = pygame.image.load(bodyIm).convert()
        self.head = pygame.image.load(headIm).convert()
        self.orig = pygame.image.load(bodyIm).convert()

        self.vel = SNAKE_VEL
        self.blocks = [] # represents the body of the snake
        self.currdir = 'right' # intial direction
        self.length = length
        self.alive = True

        self.connection = connection
        self.player = player

        # push blocks into the blocks array
        # the second block (index 1) is the "head" because the first block
        # will not be displayed, and only acts as a guide for the next 
        # movement direction
        for i in range(0,self.length + 1):
            rect = self.image.get_rect()
            rect.topleft = [xpos, ypos]
            rect = rect.move((i*-15), 0) # translate the block to the left
            if i == 1: # the "head"
                self.blocks.append(Block(self.head, rect, 'right'))
            else:
                self.blocks.append(Block(self.image, rect, 'right'))

    # changes the direction of the head movement based on a keypress
    # prevent user from going opposite direction of current movement
    # player 1 uses arrow keys, player 2 uses asdw
    def changeDirection(self, keys, player, connection): 
        if player == 0:
            if keys[K_LEFT] and not self.blocks[0].dir == "right":
                self.blocks[0].dir = "left"
                connection.transport.write("left")
            elif keys[K_RIGHT] and not self.blocks[0].dir == "left":
                self.blocks[0].dir = "right"
                connection.transport.write("right")
            elif keys[K_DOWN] and not self.blocks[0].dir == "up":
                self.blocks[0].dir = "down"
                connection.transport.write("down")
            elif keys[K_UP] and not self.blocks[0].dir == "down":
                self.blocks[0].dir = "up"
                connection.transport.write("up")
        else:
            if keys[K_a] and not self.blocks[0].dir == "right":
                self.blocks[0].dir = "left"
                connection.transport.write("left")
            elif keys[K_d] and not self.blocks[0].dir == "left":
                self.blocks[0].dir = "right"
                connection.transport.write("right")
            elif keys[K_s] and not self.blocks[0].dir == "up":
                self.blocks[0].dir = "down"
                connection.transport.write("down")
            elif keys[K_w] and not self.blocks[0].dir == "down":
                self.blocks[0].dir = "up"
                connection.transport.write("up")
        
    def increaselen(self):
        # pass in direction
        # make conditional depending on direction
        # depending on what the direction is, move accordingly

        bodyLen = (len(self.blocks))-1

        if self.blocks[bodyLen].dir == 'right':
            rect = self.blocks[-1].rect
            rect = rect.move(-15, 0)
            self.blocks.append(Block(self.image, rect, 'right'))

        if self.blocks[bodyLen].dir == 'left':
            rect = self.blocks[-1].rect
            rect = rect.move(15, 0)
            self.blocks.append(Block(self.image, rect, 'left'))

        if self.blocks[bodyLen].dir == 'up':
            rect = self.blocks[-1].rect
            rect = rect.move(0, 15)
            self.blocks.append(Block(self.image, rect, 'up'))

        if self.blocks[bodyLen].dir == 'down':
            rect = self.blocks[-1].rect
            rect = rect.move(0, -15)
            self.blocks.append(Block(self.image, rect, 'down'))

    def foodcollide(self, food):
        
        # if the snake collides with the food
        # set the value of the food display to false
        # call the increase len function on the snake
        
        for b in food: # check if our head collides with each of the other snake's blocks
            if self.blocks[1].rect.colliderect(food[b].rect): # if the rectangles collide, returns true
                if self.player == 0:
                    food[b].randMove()
                    print "about to send data"
                    data = "food:" + str(b) + ":" + str(food[b].rect.topleft[0]) + ":" + str(food[b].rect.topleft[1]) + "\n"
                    print "sending data: " + data
                    self.connection.transport.write(data)
                    self.connection.transport.write("increase length")
                    self.increaselen()

                #self.increaselen()

    def wallcollide(self): 
        if self.blocks[1].rect.topleft[1] == 0:
            print "you died on the top of the screen"
            self.alive = False
            print "alive status is now: ", self.alive
        if self.blocks[1].rect.bottomleft[1] == 600:
            print "you died on the bottom of the screen"
            self.alive = False
            print "alive status is now: ", self.alive
        if self.blocks[1].rect.bottomright[0] == 600:
            print "you died on the right of the screen"
            self.alive = False
            print "alive status is now: ", self.alive
        if self.blocks[1].rect.topleft[0] == 0:
            print "you died on the left of the screen"
            self.alive = False
            print "alive status is now: ", self.alive
        return not self.alive

    # returns True if our head has collided with our rival, False otherwise
    def snakecollide(self, rival):
        for b in rival.blocks: # check if our head collides with each of the other snake's blocks
            if self.blocks[1].rect.colliderect(b.rect): # if the rectangles collide, returns true
                self.alive = False
                return True
        return False

    def tick(self):

        i = len(self.blocks)-1 # start with last block

        # interate over all blocks and set the direction equal to the 
        # block ahead of it
        while i > 0:
            # if the next block is moving up or down, wait until until our x position
            # is evenly divisible by the block size (10), and then change direction
            if self.blocks[i-1].dir == "up" or self.blocks[i-1].dir == "down":
                if self.blocks[i].rect.topleft[0] % 15 == 0:
                    self.blocks[i].dir = self.blocks[i-1].dir
            # if the next block is moving left or right, wait until until our y position
            # is evenly divisible by the block size, and then change direction
            else:
                if self.blocks[i].rect.topleft[1] % 15 == 0:
                    self.blocks[i].dir = self.blocks[i-1].dir
            i -= 1

        # move each block based on its current direction
        for b in self.blocks:
            if b.dir == "right":
                b.rect = b.rect.move(self.vel, 0)
            elif b.dir == "left":
                b.rect = b.rect.move(-self.vel, 0)
            elif b.dir == "up":
                b.rect = b.rect.move(0, -self.vel)
            elif b.dir == "down":
                b.rect = b.rect.move(0, self.vel)

if __name__ == '__main__':
    gs = GameSpace()

    if len(sys.argv) < 2:
        print "usage: python snake.py <master | client>"
        sys.exit(1)

    if len(sys.argv) > 2:
        HOST = sys.argv[2]

    # init network stuff
    if sys.argv[1] == "master":
        print "listening..."
        reactor.listenTCP(41064, ServerConnectionFactory(gs))
    else:
        reactor.connectTCP(HOST, 41064, ClientConnectionFactory(gs))

    # start event loop
    try:
        reactor.run()
    except Exception as err:
        print err
