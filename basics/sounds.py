#!../pygamevenv/bin/python
import pygame, sys, time
from pygame.locals import *

pygame.init()

DISPLAYSURF = pygame.display.set_mode((400,300))
pygame.display.set_caption('Sounds')

BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

#pygame has trouble loading mp3 files, if it loads then it might reproduce the sound with lower bps. Use OGG or WAV instead.
soundObj = pygame.mixer.Sound('beep.wav')
#Asynchronicaly play sound
soundObj.play()
time.sleep(2)
soundObj.stop()