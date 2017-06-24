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

pygame.mixer.music.load('got.mp3')

#play(loops=0, start=0.0)
pygame.mixer.music.play(-1, 0.0)

while True:
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.mixer.music.stop()
			pygame.quit()
			sys.exit()
	pygame.display.update()