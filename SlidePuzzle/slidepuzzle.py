#!venv/bin/python
import pygame, sys, time, random, glob, os
from pygame.locals import *
from enum import Enum
from itertools import chain

def deepcopy(M):
	aux = list()
	for element in M:
		aux.append(element)
	return aux

class Colors(Enum):
	BLACK = (0,0,0)
	WHITE = (255,255,255)
	RED = (255,0,0)
	GREEN = (0,255,0)
	BLUE = (0,0,255)
	YELLOW = (255,255,0)
	GRAY = (100,100,100)
	DARKGREY = (50,50,50)
	NAVYBLUE = (60,60,100)

class Direction(Enum):
	UP = 1
	DOWN = 2
	LEFT = 3
	RIGHT = 4

FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
MARGIN = 10
BGCOLOR = Colors.NAVYBLUE

class GameRect(object):
	def __init__(self,surface,display,posx,posy,width,height,forecolor=Colors.GRAY,bgcolor=Colors.GRAY,legend=None,fontcolor=Colors.BLACK,font='freesansbold.ttf',fontsize=32,rectwidth=0):
		self._x = posx
		self._y = posy
		self._width = width
		self._height = height
		self._display = display
		self._surface = surface
		self._forecolor = forecolor
		self._bgcolor = bgcolor
		self._rectwidth = rectwidth
		self.legend = legend
		self.fontcolor=fontcolor
		self._font = font
		self.fontObj = pygame.font.Font(font, fontsize)
	def __contains__(self,otherobj):
		if (self._x <= otherobj._x) and ((self._x + self._width) >= (otherobj._x + otherobj._width)) and (self._y <= otherobj._y) and ((self._y + self._height) >= (otherobj._y + otherobj._height)):
			return True
		else:
			return False
	def erase(self):
		pygame.draw.rect(self._surface,self._bgcolor, (self._x,self._y,self._width,self._height))
		self._display.update()
	def _drawtext(self):
		if self.legend:
			textSurfaceObj = self.fontObj.render(self.legend,True, self.fontcolor)
			textRectObj = textSurfaceObj.get_rect()
			textRectObj.center = (self._x + self._width/2,self._y + self._height/2)
			self._surface.blit(textSurfaceObj,textRectObj)
	def draw(self):
		pygame.draw.rect(self._surface,self._forecolor, (self._x,self._y,self._width,self._height),self._rectwidth)
		self._drawtext()
		self._display.update()
	def redraw(self):
		self.erase()
		self.draw()
	def changefont(self,font,fontsize=32):
		self.fontObj = pygame.font.Font(font, fontsize)
	def mouseinside(self,mousex,mousey):
		if GameRect(None,None,mousex,mousey,1,1) in self:
			return True
		else:
			return False

class Button(GameRect):
	def __init__(self,surface,display,posx,posy,width,height,buttonaction=None,forecolor=Colors.GRAY,bgcolor=Colors.GRAY,pressedcolor=Colors.GRAY,legend='Button',fontcolor=Colors.BLACK,font='freesansbold.ttf',fontsize=32,sound=None):
		GameRect.__init__(self,surface,display,posx,posy,width,height,forecolor,bgcolor,legend,fontcolor,font,fontsize)
		self.__pressedcolor = pressedcolor
		self.__pressed = False
		self.__sound = sound
		self.__buttonaction = buttonaction
		self.fontObj = pygame.font.Font(font, fontsize)
	def animatepress(self,wait=0.1,classaction=None):
		if self.__pressed:
			self.unpress()
		if self.__sound:
			self.__sound.play()
		self.press(classaction)
		time.sleep(wait)
		self.unpress()
	def press(self,classaction=None):
		pygame.draw.rect(self._surface,self.__pressedcolor, (self._x,self._y,self._width,self._height))
		self._drawtext()
		self._display.update()
		self.__pressed = True
		if self.__buttonaction and classaction:
			method = getattr(classaction, self.__buttonaction)
			method()
	def unpress(self):
		pygame.draw.rect(self._surface,self._forecolor, (self._x,self._y,self._width,self._height))
		self._drawtext()
		self._display.update()
		self.__pressed = False

class Slab(GameRect):
	def __init__(self,surface,display,posx,posy,length,legend,margin=5,bgcolor=Colors.GRAY,fontsize=32,color=Colors.YELLOW,sound=None):
		GameRect.__init__(self,surface,display,posx,posy,length,length,color,bgcolor,legend,fontsize=fontsize)
		self.__sound = sound
		self.__length = length
		self.__margin = margin
		self.fontObj = pygame.font.Font(self._font, fontsize)
	def __len__(self):
		return self.__length
	def move(self,direction):
		if direction == Direction.UP:
			self.erase()
			self._y -= self._height + self.__margin
			assert self._y >= 0
			self.draw()
		elif direction == Direction.DOWN:
			self.erase()
			self._y += self._height + self.__margin
			self.draw()
		elif direction == Direction.LEFT:
			self.erase()
			self._x -= self._width + self.__margin
			assert self._x >= 0
			self.draw()
		elif direction == Direction.RIGHT:
			self.erase()
			self._x += self._width + self.__margin
			self.draw()
		if self.__sound:
			self.__sound.play()

class Container(GameRect):
	def __init__(self,surface,display,posx,posy,width,height,color=Colors.BLACK,bgcolor=Colors.GRAY,rectwidth=5):
		GameRect.__init__(self,surface,display,posx,posy,width,height,color,bgcolor,rectwidth=rectwidth)
		self._objects = list()
	def redrawall(self):
		for obj in self._objects:
			assert isinstance(obj,GameRect)
			obj.redraw()
	def _addobject(self,obj):
		assert obj in self
		self._objects.append(obj)
	def handleclick(self,x,y,classaction=None):
		for obj in self._objects:
			if obj.mouseinside(x,y):
				obj.animatepress(classaction=classaction)
	def addButton(self,relx,rely,width,height,buttonaction=None,forecolor=Colors.GRAY,pressedcolor=Colors.GRAY,legend='Button',fontcolor=Colors.BLACK,font='freesansbold.ttf',fontsize=32,sound=None):
		self._addobject(Button(self._surface,self._display,self._x+relx,self._y+rely,width,height,buttonaction=buttonaction,bgcolor=self._bgcolor,forecolor=forecolor,pressedcolor=pressedcolor,legend=legend,fontsize=fontsize,sound=sound))

class Board(Container):
	def __init__(self,surface,display,posx,posy,width,height,color=Colors.BLACK,bgcolor=Colors.GRAY,rectwidth=5,slabsize=32,margin=5):
		Container.__init__(self,surface,display,posx,posy,width,height,color=color,bgcolor=bgcolor,rectwidth=rectwidth)
		self.__matrix = None
		self.__slabsize = slabsize
		self.__margin = margin
		self.initmatrix()
		self.__backupmatrix = None
		self.__makebackupmatrix()
	def __makebackupmatrix(self):
		self.__backupmatrix = list()
		for i in self.__matrix:
			self.__backupmatrix.append(i[:])
	def initmatrix(self):
		if self.__matrix:
			self.eraseall()
		self.__matrix = [[None for x in range(4)] for y in range(4)]
		numbers = list()
		for i in range(4):
			for j in range(4):
				if i == 3 and j == 3:
					break
				num = random.randint(1,15)
				while num in numbers:
					num = random.randint(1,15)
				numbers.append(num)
				self.__addSlab(i,j,str(num))
		self.redrawall()
	def resetmatrix(self):
		self.eraseall()
		self.__matrix = [[None for x in range(4)] for y in range(4)]
		for i in range(4):
			for j in range(4):
				if i == 3 and j == 3:
					continue
				self.__addSlab(i,j,self.__backupmatrix[i][j].legend)
		self.redrawall()
	def redrawall(self):
		for slab in chain.from_iterable(zip(*self.__matrix)):
			if slab:
				slab.redraw()
		self.draw()
	def eraseall(self):
		for slab in chain.from_iterable(zip(*self.__matrix)):
			if slab:
				slab.erase()
	def haswon(self):
		winningmatrix = [['1','2','3','4'],['5','6','7','8'],['9','10','11','12'],['13','14','15',None]]
		for i in range(4):
			for j in range(4):
				if not self.__matrix[i][j]:
					if i != 3 or j != 3:
						return False
				elif winningmatrix[i][j] != self.__matrix[i][j].legend:
					return False
		return True
	def handleclick(self,x,y):
		for i in range(4):
			for j in range(4):
				if not self.__matrix[i][j]:
					continue
				if self.__matrix[i][j].mouseinside(x,y):
					#Search the None
					#Is it below?
					if i < 3:
						if not self.__matrix[i+1][j]:
							self.__matrix[i][j].move(Direction.DOWN)
							self.__matrix[i+1][j] = self.__matrix[i][j]
							self.__matrix[i][j] = None
							return
					#Is it left?
					if j > 0:
						if not self.__matrix[i][j-1]:
							self.__matrix[i][j].move(Direction.LEFT)
							self.__matrix[i][j-1] = self.__matrix[i][j]
							self.__matrix[i][j] = None
							return
					#Is it right?
					if j < 3:
						if not self.__matrix[i][j+1]:
							self.__matrix[i][j].move(Direction.RIGHT)
							self.__matrix[i][j+1] = self.__matrix[i][j]
							self.__matrix[i][j] = None
							return
					#Is it up?
					if i > 0:
						if not self.__matrix[i-1][j]:
							self.__matrix[i][j].move(Direction.UP)
							self.__matrix[i-1][j] = self.__matrix[i][j]
							self.__matrix[i][j] = None
							return
				
	def __addSlab(self,i,j,legend,fontsize=32,color=Colors.YELLOW,sound=None):
		self.__matrix[i][j] = Slab(self._surface,self._display,self._x+self.__margin*(j+1)+self.__slabsize*j,self._y+self.__margin*(i+1)+self.__slabsize*i,self.__slabsize,legend,margin=self.__margin,bgcolor=self._bgcolor,fontsize=fontsize,color=color,sound=sound)

def main():
	pygame.init()
	DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT))
	pygame.display.set_caption('Slide Puzzle')
	FPSCLOCK = pygame.time.Clock()
	DISPLAYSURF.fill(BGCOLOR)
	pygame.display.update()
	clicksound = pygame.mixer.Sound('sounds/click.wav')
	SLABSIZE=100
	MARGIN=5

	board = Board(DISPLAYSURF,pygame.display,20,20,4*SLABSIZE+5*MARGIN,4*SLABSIZE+5*MARGIN,slabsize=SLABSIZE,margin=MARGIN,color=Colors.BLACK,bgcolor=BGCOLOR)
	board.redrawall()

	menu = Container(DISPLAYSURF,pygame.display,WINDOWWIDTH-170,20+4*SLABSIZE+5*MARGIN-150,150,150,color=Colors.BLACK,bgcolor=BGCOLOR)
	menu.draw()
	menu.addButton(25,20,100,50,buttonaction='initmatrix',forecolor=Colors.GRAY,pressedcolor=Colors.DARKGREY,legend='New Game',fontsize=16,sound=clicksound)
	menu.addButton(25,85,100,50,buttonaction='resetmatrix',forecolor=Colors.GRAY,pressedcolor=Colors.DARKGREY,legend='Reset',fontsize=16,sound=clicksound)
	menu.redrawall()

	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.mixer.music.stop()
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEBUTTONDOWN:
				x, y = event.pos
				menu.handleclick(x,y,board)
				if board.mouseinside(x,y):
					board.handleclick(x,y)
		if board.haswon():
			winningsign = GameRect(DISPLAYSURF,pygame.display,(WINDOWWIDTH-350)/2,(WINDOWHEIGHT-150)/2,350,150,forecolor=Colors.GREEN,legend='You Won!',fontsize=64)
			winningsign.redraw()
			while True:
				for event in pygame.event.get():
					if event.type in [QUIT,KEYDOWN,MOUSEBUTTONDOWN]:
						pygame.mixer.music.stop()
						pygame.quit()
						sys.exit()
		FPSCLOCK.tick(FPS)

if __name__ == '__main__':
	main()