#!venv/bin/python
import pygame, sys, time, random
from GameObjects import *
from pygame.locals import *

WINDOWWIDTH = 800
WINDOWHEIGHT = 600
WINDOWX = 10
WINDOWY = 10

def displaygameover(surface,score):
	ax = 200
	ay = 80
	display = GameRect(surface,(WINDOWWIDTH/2) - ax/2,(WINDOWHEIGHT/2) - ay/2,ax,ay,forecolor=Colors.WHITE,legend='Score: {0}'.format(score))
	display.draw()

class Grid(object):
	def __init__(self,surface,x,y,x_blocks,y_blocks,blocksize=10,bgcolor=Colors.BLACK):
		self.__x = x
		self.__y = y
		self.__x_blocks = x_blocks
		self.__y_blocks = y_blocks
		self.__surface = surface
		self.__blocksize = blocksize
		self.__bgcolor = bgcolor
		self.__container = Container(self.__surface,self.__x,self.__y,self.__blocksize*self.__x_blocks,self.__blocksize*self.__y_blocks,color=Colors.WHITE,rectwidth=5)
		self.__container.draw()
		self.__snake = list()
		self.resetsnake()
		self.__apple = None
		self.randomapple()
	def resetsnake(self):
		x = random.choice([_ for _ in range(self.__x+20*self.__blocksize,self.__x+(self.__x_blocks - 20)*self.__blocksize,self.__blocksize)])
		y = random.choice([_ for _ in range(self.__y+20*self.__blocksize,self.__y+(self.__y_blocks - 20)*self.__blocksize,self.__blocksize)])
		for i in range(3):
			self.__snake.append(Block(self.__surface,x-i*self.__blocksize,y,self.__blocksize,color=Colors.YELLOW,bgcolor=self.__bgcolor))
	def randomapple(self):
		c = True
		while c:
			x = random.choice([_ for _ in range(self.__x+self.__blocksize,self.__x+(self.__x_blocks - 1)*self.__blocksize,self.__blocksize)])
			y = random.choice([_ for _ in range(self.__y+self.__blocksize,self.__y+(self.__y_blocks - 1)*self.__blocksize,self.__blocksize)])
			self.__apple = Block(self.__surface,x,y,length=self.__blocksize,color=Colors.RED)
			for s in self.__snake:
				if self.__apple in s:
					break
			else:
				c = False
	def movesnake(self,direction):
		self.__snake[-1].erase()
		if direction == K_UP:
			self.__snake = [Block(self.__surface,self.__snake[0].x,self.__snake[0].y-self.__blocksize,self.__blocksize,color=Colors.YELLOW,bgcolor=self.__bgcolor)] + self.__snake[:-1]
		elif direction == K_DOWN:
			self.__snake = [Block(self.__surface,self.__snake[0].x,self.__snake[0].y+self.__blocksize,self.__blocksize,color=Colors.YELLOW,bgcolor=self.__bgcolor)] + self.__snake[:-1]
		elif direction == K_RIGHT:
			self.__snake = [Block(self.__surface,self.__snake[0].x+self.__blocksize,self.__snake[0].y,self.__blocksize,color=Colors.YELLOW,bgcolor=self.__bgcolor)] + self.__snake[:-1]
		elif direction == K_LEFT:
			self.__snake = [Block(self.__surface,self.__snake[0].x-self.__blocksize,self.__snake[0].y,self.__blocksize,color=Colors.YELLOW,bgcolor=self.__bgcolor)] + self.__snake[:-1]
		self.__snake[0].draw()
	def __selfcollision(self):
		for obj in self.__snake[2:]:
			if self.__snake[0] in obj:
				return True
		else:
			return False
	def checkcollision(self):
		if 	(self.__snake[0].x <= self.__x) or ((self.__x + (self.__x_blocks - 1)*self.__blocksize) <= self.__snake[0].x) or \
			(self.__snake[0].y <= self.__y) or ((self.__y + (self.__y_blocks - 1)*self.__blocksize) <= self.__snake[0].y) or \
			self.__selfcollision():
			return -1
		elif self.__snake[0] in self.__apple:
			return 1
		else:
			return 0
	def growsnake(self):
		self.__snake.append(self.__snake[-1])
	def drawapple(self):
		self.__apple.draw()

def main():
	pygame.init()
	DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT))
	BGCOLOR = Colors.BLACK
	BLOCKSIZE = 10
	FPS = 20
	pygame.display.set_caption('Wormy')
	FPSCLOCK = pygame.time.Clock()
	pygame.mixer.music.load('music/background.wav')
	pygame.mixer.music.play(-1, 0.0)

	board = Grid(DISPLAYSURF,WINDOWX,WINDOWY,(WINDOWWIDTH-WINDOWX*2)/BLOCKSIZE,(WINDOWHEIGHT-WINDOWY*2)/BLOCKSIZE)
	board.drawapple()

	score = 0

	DIRECTION = K_RIGHT
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.mixer.music.stop()
				pygame.quit()
				sys.exit()
			elif event.type == KEYDOWN:
				if event.key in [K_UP, K_DOWN, K_LEFT, K_RIGHT]:
					if 	(event.key != K_LEFT and DIRECTION == K_RIGHT) or (event.key != K_RIGHT and DIRECTION == K_LEFT) or \
						(event.key != K_DOWN and DIRECTION == K_UP) or (event.key != K_UP and DIRECTION == K_DOWN):
						DIRECTION = event.key
						break
		board.movesnake(DIRECTION)
		ret = board.checkcollision()
		if  ret == 1:
			board.growsnake()
			board.growsnake()
			board.growsnake()
			board.growsnake()
			board.growsnake()
			board.randomapple()
			board.drawapple()
			score += 1
		elif ret == -1:
			displaygameover(DISPLAYSURF,score)
			while True:
				for event in pygame.event.get():
					if event.type == QUIT:
						pygame.mixer.music.stop()
						pygame.quit()
						sys.exit()
		
		FPS = 20 + score/10
		pygame.display.update()
		FPSCLOCK.tick(FPS)

if __name__ == '__main__':
	main()