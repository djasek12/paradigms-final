# Jessica Cioffi
# PyGame Primer

import os, sys
import pygame
import math
from math import sin, pi, cos
from pygame.locals import *

class GameSpace:
    def main(self):
        pygame.init()
        self.size = 600
        self.screen = pygame.display.set_mode((self.size,self.size)) # sets the window size
        pygame.display.set_caption('PyGame Primer') # sets the window caption
        pygame.mouse.set_visible(1) # makes the mouse visible
        self.clock = pygame.time.Clock() # initializes the clock
        self.done = False # sets the loop determinant
        self.keys = pygame.key.set_repeat(1,50) # helps with lag
        self.lasers = []
        self.explode = None
        self.tester = 0

        #self.enemy = Enemy(self) # creates instance of enemy class
        #self.player = Player(self) # creates an instance of the player class
        self.snake = Snake(self)
        self.food = Food(self)

        while not self.done:
            self.clock.tick(60)
            for event in pygame.event.get(): # accounts for the different possible events
                if event.type == pygame.QUIT: # quit
                    sys.exit()
            #    if event.type == MOUSEBUTTONDOWN: #if the mouse is clicked
             #       self.player.shooter = True
              #  elif event.type == MOUSEBUTTONUP: # if the mouse is released
               #     self.player.shooter = False

            self.keys = pygame.key.get_pressed() # if the arrow keys are pressed
            self.snake.move(self.keys)
            if self.tester == 0:
                self.tester = self.snake.increaselen()
            #self.snake.tick()
            
           # if self.player.shooter == True: # if the player is shooting
            #    self.lasers.append(self.player.tick()) # add lasers to the array
           # else:
            #    self.player.tick()

           # i = 0
          #  while i < len(self.lasers): # loops through while less than size of the lasers array
           #     self.lasers[i].tick()
            #    if self.lasers[i].outOfRange == True: # if we reach a boundary, start deleting
             #       del self.lasers[i]
             #   i += 1

          #  if self.explode == None and self.enemy.tick(self.lasers): # if we start exploding
           #     self.explode = Explosion(self) # create instance of explosion class
          #  if self.explode:
           #     self.explode.tick()

            # blits at the end 
            self.screen.fill((0, 0, 0)) # fills the background with black
            self.screen.blit(self.food.image, self.food.rect)
            for b in self.snake.blocks:
                self.screen.blit(b.image, b.rect)
         #   self.screen.blit(self.player.image, self.player.rect) # puts the deathstar on the screen
          #  for i in range(0, len(self.lasers)): # puts the lasers on the screen
            #    self.screen.blit(self.lasers[i].image, self.lasers[i].rect)
            #self.screen.blit(self.enemy.image, self.enemy.rect) # puts the earth on the screen
            #if self.explode: # sets the explosion
             #   self.screen.blit(self.explode.image, self.explode.rect)
            
            pygame.display.flip() # update the display

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
    def __init__(self, length, gs=None):
        pygame.sprite.Sprite.__init__(self)
        self.gs = gs
        self.image = pygame.image.load('laser.png')
        self.head = pygame.image.load('head.png')
        self.orig = pygame.image.load('laser.png')
        self.rect = self.image.get_rect()
        self.rect.topleft = [100, 100]
        self.vel = 10
        self.blocks = []
        self.currdir = 'right'
        self.length = 5

        for i in range(0,self.length):
            image = self.image
            head = self.head
            rect = image.get_rect()
            rect.topleft = [100, 100]
            rect = rect.move((i*-10), 0)
            if i ==0:
                self.blocks.append(Block(head, rect, 'right'))
            else:
                self.blocks.append(Block(image, rect, 'right'))

    def move(self, keys): 
        if keys[K_LEFT]:
            self.rect = self.rect.move((self.vel*-1), 0)
        elif keys[K_RIGHT]:
            #self.rect = self.rect.move(self.vel, 0)
            #self.blocks[0].rect = self.rect.move(self.vel, 0)
            for x in self.blocks: 
                x.rect = x.rect.move(self.vel, 0)
                #print(self.blocks[0].rect.topleft)
        elif keys[K_DOWN]:
            self.rect = self.rect.move(0, self.vel)
        elif keys[K_UP]:
            self.rect = self.rect.move(0, (self.vel*-1))
        
    def increaselen(self):
        if self.blocks[0].rect.topleft == (200, 100): 
            rect1 = self.blocks[3].rect
            rect2 = self.blocks[4].rect

            rect2.topright = rect1.topleft

            #self.blocks.append(Block(self.image, rect2, 'right')) # in the last slot, there is an unadjusted rectangle stored
            self.blocks.append('') # in the last slot, there is an unadjusted rectangle stored
            
            self.length = 6

            rect3 = rect2
            rect3.topright = rect2.topleft

            self.blocks[3] = Block(self.image, rect1, 'right')
            self.blocks[4] = Block(self.image, rect2, 'right')
            self.blocks[5] = Block(self.image, rect3, 'right')
            
            return 1
        return 0

            #for i in range(0,self.length):
             #   image = self.image
              #  head = self.head
               # rect = image.get_rect()
               # rect.topleft = [100, 100]
               # rect = rect.move((i*-10), 0)
               # if i ==0:
                #    self.blocks.append(Block(head, rect, 'right'))
               # else:
                #    self.blocks.append(Block(image, rect, 'right'))

    def tick(self):
        #for i in range(0, len(self.blocks)-2):
         #   self.blocks[i+1][1] = self.blocks[i][1]
            
        i = len(self.blocks)-1
        while i > 0:
            self.blocks[i][1] = self.blocks[i-1][1]
            i = i-1

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
        return Laser(self.rect.centerx-(30*cos(self.newangle_rads)), self.rect.centery-(30*sin(self.newangle_rads)), self.newangle_rads, self.gs)

if __name__ == '__main__':
    gs = GameSpace()
    gs.main()
