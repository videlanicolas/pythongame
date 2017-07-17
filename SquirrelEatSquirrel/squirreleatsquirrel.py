#!venv/bin/python3
import pygame, sys, random
from pygame.locals import *
from pygame.display import update as UPDATE
from GameObjects import *

MAP_LENGTH = 10000

def main():
	DISPLAYSURF = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
	pygame.display.set_caption('Agario')
	FPSCLOCK = pygame.time.Clock()
	FOODAMOUNT = 300
	FPS = 1000

	world_map = ContinuousMap(DISPLAYSURF,MAP_LENGTH,MAP_LENGTH)
	world_map.speed = 10
	world_map.character.radius = 100
	for _ in range(FOODAMOUNT):
		world_map.add_object(random.randint(0,MAP_LENGTH),random.randint(0,MAP_LENGTH))

	f = pygame.font.Font(None, 64)
	while True:
		for e in pygame.event.get():
			if e.type == KEYDOWN:
				if e.key == K_ESCAPE:
					pygame.quit()
					sys.exit()
		k = pygame.key.get_pressed()
		if k[K_UP]:
			world_map.character_move(Directions.UP)
		if k[K_DOWN]:
			world_map.character_move(Directions.DOWN)
		if k[K_LEFT]:
			world_map.character_move(Directions.LEFT)
		if k[K_RIGHT]:
			world_map.character_move(Directions.RIGHT)
		if k[K_p]:
			world_map.character.radius += 1
		if k[K_l]:
			world_map.character.radius -= 1
		#world_map.animate()
		world_map.draw()
		FPSCLOCK.tick(FPS)
		UPDATE()
		if world_map.has_lost():
			DISPLAYSURF.blit(f.render("GAME OVER", True, (255, 255, 255)), (0,0))
			"""
			while not any(e.type == KEYDOWN and e.key == K_ESCAPE for e in pygame.event.get()):
				pass
			pygame.quit()
			sys.exit()
			"""

if __name__ == '__main__':
	pygame.init()
	main()