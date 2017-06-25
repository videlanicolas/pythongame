#!../pygamevenv/bin/python
import pygame, sys, time, random, glob, os
from pygame.locals import *
from enum import Enum


class Colors(Enum):
	BLACK = (0,0,0)
	WHITE = (255,255,255)
	RED = (255,0,0)
	GREEN = (0,255,0)
	BLUE = (0,0,255)
	GRAY = (100,100,100)
	NAVYBLUE = (60,60,100)

FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
MARGIN = 10
BGCOLOR = Colors.NAVYBLUE

class Box(object):
	def __init__(self,display,posx,posy,imgsurf,boxcolor=Colors.GRAY,boxlength=40,_id=0):
		self.__x = posx
		self.__y = posy
		self.id = _id
		self.__imgsurf = imgsurf
		self.__display = display
		self.__boxcolor = boxcolor
		self.__boxlength = boxlength
		self.revealed = False
		self.locked = False
	def __equals__(self,otherbox):
		otherx, othery = otherbox.getpos()
		if otherx == self.__x and othery == self.__y:
			return True
		else:
			return False
	def reveal(self):
		if not self.locked or (self.locked and self.revealed):
			self.__display.blit(self.__imgsurf,(self.__x,self.__y))
			self.revealed = True
	def hide(self):
		if not self.locked or (self.locked and not self.revealed):
			pygame.draw.rect(self.__display,self.__boxcolor, (self.__x,self.__y,self.__boxlength,self.__boxlength))
			self.revealed = False
	def toogle(self):
		if not self.locked:
			if self.revealed:
				self.revealed = False
			else:
				self.revealed = True
	def draw(self):
		if self.revealed:
			self.reveal()
		else:
			self.hide()
	def getimgsurf(self):
		return self.__imgsurf
	def getpos(self):
		return self.__x, self.__y
	def pointInBox(self,x,y):
		if (x > self.__x) and (x < (self.__x+self.__boxlength)) and (y > self.__y) and (y < (self.__y+self.__boxlength)):
			return True
		else:
			return False
	def ispartnerbox(self,otherbox):
		otherx, othery = otherbox.getpos()
		if otherbox.id == self.id and (otherx != self.__x or othery != self.__y):
			return True
		else:
			return False

class Grid():
	def __init__(self,display,posx,posy,width,height,boxlength=64,imgpath='.',margin=10,bgcolor=Colors.WHITE,successfilename='success.wav',errorfilename='error.wav',font='freesansbold.ttf'):
		self.__x = posx
		self.__y = posy
		self.score = 0
		self.__scorepos = (self.__x + width - 150,self.__y - 20)
		self.__display = display
		self.__board = [[None for x in range(width/(boxlength+margin))] for y in range(height/(boxlength+margin))]
		self.__lenboard = 0
		self.__boxes = list()
		self.__selected = None
		self.__bgcolor = bgcolor
		self.__success = pygame.mixer.Sound(successfilename)
		self.__error = pygame.mixer.Sound(errorfilename)
		for boxes in self.__board:
			self.__lenboard += len(boxes)
		assert self.__lenboard%2 == 0
		assert (len([name for name in os.listdir(imgpath) if os.path.isfile(os.path.join(imgpath, name))])*2) <= self.__lenboard
		idnum = 0
		for filename in glob.glob(os.path.join(imgpath, '*.png')):
			j = random.randint(0,(width/(boxlength+margin))-1)
			i = random.randint(0,(height/(boxlength+margin))-1)
			while self.__board[i][j]:
				j = random.randint(0,(width/(boxlength+margin))-1)
				i = random.randint(0,(height/(boxlength+margin))-1)
			self.__board[i][j] = Box(self.__display,self.__x + j*(boxlength+margin),self.__y + i*(boxlength+margin),imgsurf=pygame.image.load(filename),boxlength=boxlength,_id=idnum)
			self.__boxes.append(self.__board[i][j])
			while self.__board[i][j]:
				j = random.randint(0,(width/(boxlength+margin))-1)
				i = random.randint(0,(height/(boxlength+margin))-1)
			self.__board[i][j] = Box(self.__display,self.__x + j*(boxlength+margin),self.__y + i*(boxlength+margin),imgsurf=pygame.image.load(filename),boxlength=boxlength,_id=idnum)
			self.__boxes.append(self.__board[i][j])
			idnum += 1
	def draw(self):
		self.__display.fill(self.__bgcolor)
		for box in self.__boxes:
			box.draw()
		textSurfaceObj = pygame.font.Font('freesansbold.ttf', 32).render('Score: {0}'.format(self.score),False, Colors.BLACK)
		textRectObj = textSurfaceObj.get_rect()
		textRectObj.center = self.__scorepos
		self.__display.blit(textSurfaceObj,textRectObj)
		pygame.display.update()
	def revealAll(self):
		for box in self.__boxes:
			box.reveal()
	def hideAll(self):
		for box in self.__boxes:
			box.hide()
	def handleClick(self,x,y,wait=0):
		for box in self.__boxes:
			if box.pointInBox(x,y):
				if box != self.__selected:
					box.toogle()
					box.locked = True
					self.draw()
					if self.__selected:
						if box.ispartnerbox(self.__selected):
							self.__success.play()
							time.sleep(wait)
							self.__success.stop()
							box.locked = True
							self.__selected.locked = True
							self.__selected = None
							self.score += 10
						else:
							self.__error.play()
							time.sleep(wait)
							self.__error.stop()
							box.locked = False
							self.__selected.locked = False
							box.revealed = False
							self.__selected.revealed = False
							self.__selected = None
							self.score -= 1
					else:
						self.__selected = box
					self.draw()
	def allrevealed(self):
		for box in self.__boxes:
			if not box.revealed:
				return False
		else:
			return True
	def displaywinning(self):
		self.__display.fill(self.__bgcolor)
		for box in self.__boxes:
			box.draw()
		pygame.display.update()
		textSurfaceObj = pygame.font.Font('freesansbold.ttf', 32).render('You Won!',False, Colors.BLACK)
		textRectObj = textSurfaceObj.get_rect()
		textRectObj.center = (WINDOWWIDTH/2,WINDOWHEIGHT/2+140)
		self.__display.blit(textSurfaceObj,textRectObj)
		textSurfaceObj = pygame.font.Font('freesansbold.ttf', 32).render('Score: {0}'.format(self.score),False, Colors.BLACK)
		textRectObj = textSurfaceObj.get_rect()
		textRectObj.center = (WINDOWWIDTH/2,WINDOWHEIGHT/2+180)
		self.__display.blit(textSurfaceObj,textRectObj)
		pygame.display.update()

def main():
	pygame.init()
	DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT))
	pygame.display.set_caption('Memory Puzzle')
	FPSCLOCK = pygame.time.Clock()

	#Generate board
	board = Grid(	DISPLAYSURF,150,60,300,230,\
					imgpath='icons',margin=MARGIN,bgcolor=Colors.NAVYBLUE,\
					successfilename='sounds/success.wav',errorfilename='sounds/error.wav')

	score = 0
	board.draw()
	time.sleep(1)
	board.revealAll()
	board.draw()
	time.sleep(3)
	board.hideAll()
	board.draw()
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.mixer.music.stop()
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEBUTTONDOWN:
				mousex, mousey = event.pos
				board.handleClick(mousex,mousey,1)
		if board.allrevealed():
			board.displaywinning()
			while True:
				for event in pygame.event.get():
					if event.type == KEYDOWN or event.type == QUIT:
						pygame.quit()
						sys.exit()
		FPSCLOCK.tick(FPS)

if __name__ == '__main__':
	main()