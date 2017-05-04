# Jessica Cioffi
# Daniel Jasek
# Programmiing Paradigms Final

import os, sys
import pygame
import math
from math import sin, pi, cos
from pygame.locals import *

from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor

class GameSpace:
    def main(self):

        # init window
        pygame.init()
        self.size = 600
        self.screen = pygame.display.set_mode((self.size,self.size)) # sets the window size
        pygame.display.set_caption('Paradigms Final') # sets the window caption
        pygame.mouse.set_visible(1) # makes the mouse visible

        self.clock = pygame.time.Clock() # initializes the clock

        # set up game variables
        self.done = False # sets the loop determinant
        self.keys = pygame.key.set_repeat(1,50) # helps with lag
        self.lasers = []
        self.explode = None
        self.tester = 0

        # intialize game objects
        self.snake = Snake(5, 100, 100, self)
        self.food = Food(self)

        # init network stuff
        if sys.argv[1] == 1:
            reactor.connectTCP("ash.campus.nd.edu", 41064, ClientConnectionFactory())
        else:
            reactor.connectTCP(41064, ServerConnectionFactory())
        reactor.run()

        while not self.done:
            self.clock.tick(60)
            for event in pygame.event.get(): # accounts for the different possible events
                if event.type == pygame.QUIT: # quit
                    sys.exit()
                    
                '''if event.type == MOUSEBUTTONDOWN: #if the mouse is clicked
                     self.player.shooter = True
                 elif event.type == MOUSEBUTTONUP: # if the mouse is released
                     self.player.shooter = False'''

            self.keys = pygame.key.get_pressed() # if the arrow keys are pressed
            self.snake.changeDirection(self.keys)
            if self.tester == 0:
                self.tester = self.snake.increaselen()
            self.snake.tick()
            
            # blits sprites to screen
            self.screen.fill((0, 0, 0)) # fills the background with black
            self.screen.blit(self.food.image, self.food.rect)

            # display each block in the snake body
            # don't display the first block, because it is just an invisible "leader" 
            # of the rest of the body
            for i in range(len(self.snake.blocks)):
                if i > 0:
                    b = self.snake.blocks[i]
                    self.screen.blit(b.image, b.rect)
            
            # update the display
            pygame.display.flip()

''''''''''''''''''''''''' Game Objects '''''''''''''''''''''''''''''''''

class ClientConnection(Protocol):
    
    def connectionMade(self):
        print "service connection made on client side"

    def dataReceived(self, data):
        print("data: ", data)

class ClientConnectionFactory(ClientFactory):
    def __init__(self):
        self.myconn = ClientConnection()
        
    def buildProtocol(self, addr):
        return self.myconn

class ServerConnection(Protocol):
    
    def connectionMade(self):
        print "service connection made on client side"

    def dataReceived(self, data):
        print("data: ", data)

class ServerConnectionFactory(Factory):
    def __init__(self):
        self.myconn = ServerConnection()
        
    def buildProtocol(self, addr):
        return self.myconn

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# class for blocks that make up the snake
# each has an image, rect, and a movement direction
class Block(pygame.sprite.Sprite):
    def __init__(self, image, rect, direction):
        self.image = image
        self.rect = rect
        self.dir = direction

class Food(pygame.sprite.Sprite):
    def __init__(self, gs=None):
        pygame.sprite.Sprite.__init__(self)
        self.gs = gs
        self.image = pygame.image.load('food.png')
        self.rect = self.image.get_rect()
        self.rect.topleft = [200, 100]

class Snake(pygame.sprite.Sprite):
    def __init__(self, length, xpos, ypos, gs=None):
        pygame.sprite.Sprite.__init__(self)
        self.gs = gs

        # load images
        self.image = pygame.image.load('laser.png')
        self.head = pygame.image.load('head.png')
        self.orig = pygame.image.load('laser.png')

        self.vel = 10
        self.blocks = [] # represents the body of the snake
        self.currdir = 'right' # intial direction
        self.length = length

        '''push blocks into the blocks array
        the second block (index 1) is the "head" because the first block
        will not be displayed, and only acts as a guide for the next 
        movement direction'''
        for i in range(0,self.length + 1):
            rect = self.image.get_rect()
            rect.topleft = [xpos, ypos]
            rect = rect.move((i*-10), 0) # translate the block to the left
            if i == 1: # the "head"
                self.blocks.append(Block(self.head, rect, 'right'))
            else:
                self.blocks.append(Block(self.image, rect, 'right'))

    # changes the direction of the head movement based on a keypress
    def changeDirection(self, keys): 
        if keys[K_LEFT]:
            self.blocks[0].dir = "left"
        elif keys[K_RIGHT]:
            self.blocks[0].dir = "right"
        elif keys[K_DOWN]:
            self.blocks[0].dir = "down"
        elif keys[K_UP]:
            self.blocks[0].dir = "up"
        
    def increaselen(self):
        if self.blocks[0].rect.topleft == (200, 100): 
            
            # make a copy of the last block rect, and move it 10 units left
            rect = self.blocks[-1].rect
            rect = rect.move(-10, 0)

            # add block to array
            self.blocks.append(Block(self.image, rect, 'right'))
            
            return 1
        return 0

    def tick(self):

        i = len(self.blocks)-1 # start with last block

        # interate over all blocks and set the direction equal to the 
        # block ahead of it
        while i > 0:
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



''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

class Explosion(pygame.sprite.Sprite): # the explosion class
    def __init__(self, gs=None):
        pygame.sprite.Sprite.__init__(self)
        self.gs = gs
        self.image = pygame.image.load('explosion/frames016a.png')
        self.rect = self.image.get_rect()
        self.rect.topleft = (350, 350) # positions the explosion
        self.frame = 0
        self.num = 0

    def tick(self):
        self.num += 1
        if self.num == 3:
            if self.frame < 16: # set what should be displayed
                filename = 'explosion/frames{0:03d}a.png'.format(self.frame)
                self.image = pygame.image.load(filename)
                self.frame += 1
            else:
                self.image = pygame.image.load('empty.png')
            self.num = 0

class Enemy(pygame.sprite.Sprite): # enemy class
    def __init__(self, gs=None):
        pygame.sprite.Sprite.__init__(self)
        self.gs = gs
        self.image = pygame.image.load('globe.png')
        self.rect = self.image.get_rect()
        self.rect.topleft = (350, 350)
        self.points = 300
        self.collision = 0

    def tick(self, lasers):
        for i in range(0, len(lasers)):
            if self.rect.colliderect(lasers[i].rect): # if the lasers are detected
                self.points -= 1 # adjust the hitpoints

        if self.points <= 100: # account for the red earth
            self.image = pygame.image.load('globe_red100.png')
            self.rect = self.image.get_rect()
            self.rect.topleft = (350, 350)
        if self.points <= 0:
            self.image = pygame.image.load('empty.png') # clear once the earth has been "destroyed"
            return True

class Laser(pygame.sprite.Sprite): # laser class
    def __init__(self, x, y, angle, gs=None):
        pygame.sprite.Sprite.__init__(self)
        self.gs = gs
        self.image = pygame.image.load('laser.png')
        self.rect = self.image.get_rect()
        self.cannonX = x
        self.cannonY = y
        self.angle = angle
        self.rect.center = self.cannonX*cos(self.angle), self.cannonY*sin(self.angle)
        self.outOfRange = False

    def tick(self):
        self.cannonX = self.cannonX - (8*cos(self.angle))
        self.cannonY = self.cannonY - (8*sin(self.angle))
        self.rect.center = (self.cannonX, self.cannonY) # calculates new center
        if self.cannonX < 0 or self.cannonX > self.gs.size or self.cannonY < 0 or self.cannonY > self.gs.size: # sets the laser bounds
            self.outOfRange = True


class Player(pygame.sprite.Sprite): # player class
    def __init__(self, gs=None):
        pygame.sprite.Sprite.__init__(self)
        self.gs = gs
        self.image = pygame.image.load('deathstar.png')
        self.original = pygame.image.load('deathstar.png') # sets original image for rotation
        self.rect = self.image.get_rect()
        self.rect.topleft = (170, 170)
        self.newangle_degrees = 0
        self.newangle_rads = 0
        self.shooter = False

    def move(self, keys): # moving based on the arrow keys
        if keys[K_LEFT]:
            self.rect = self.rect.move(-7, 0)
        elif keys[K_RIGHT]:
           self.rect = self.rect.move(7, 0)
        elif keys[K_DOWN]:
            self.rect = self.rect.move(0, 7)
        elif keys[K_UP]:
            self.rect = self.rect.move(0, -7)

    def tick(self): # handles if the death star is shooting and rotating based on the mouse

        if self.shooter == True:
            return self.shoot()
        else:
            xpos, ypos = pygame.mouse.get_pos()
            newx = self.rect.centerx - xpos
            newy = self.rect.centery - ypos

            self.newangle_rads = math.atan2(newx, newy) # uses trig to calculate the angle to rotate
            self.newangle_degrees = ((180/math.pi)* self.newangle_rads)+45

            orig_rect = self.rect
            rot_image = pygame.transform.rotate(self.original, self.newangle_degrees) # rotates
            rot_rect = orig_rect.copy() # creates a copy of the rectangle

            rot_rect.center = rot_image.get_rect().center
            rot_image = rot_image.subsurface(rot_rect).copy()
            self.image = rot_image # sets the rotated image to the image displayed

    def shoot(self): # if shooting, return a laser object
        return Laser(self.rect.centerx-(30*cos(self.newangle_riads)), self.rect.centery-(30*sin(self.newangle_rads)), self.newangle_rads, self.gs)

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

if __name__ == '__main__':
    gs = GameSpace()
    gs.main()
