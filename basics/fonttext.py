#!../pygamevenv/bin/python
import pygame, sys
from pygame.locals import *

pygame.init()

DISPLAYSURF = pygame.display.set_mode((400,300))
pygame.display.set_caption('Font text.')

BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

fontObj = pygame.font.Font('freesansbold.ttf', 32)
#render(text, antialias, color, background=None) -> Surface
textSurfaceObj = fontObj.render('Hello World!',False, BLUE,GREEN)
textRectObj = textSurfaceObj.get_rect()
textRectObj.center = (200,150)

#Main game loop
while True:
	DISPLAYSURF.fill(WHITE)
	DISPLAYSURF.blit(textSurfaceObj,textRectObj)
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
	
	pygame.display.update()