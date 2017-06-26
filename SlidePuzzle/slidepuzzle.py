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
	def __init__(self,surface,display,posx,posy,width,height,forecolor=Colors.GRAY,bgcolor=Colors.GRAY,pressedcolor=Colors.GRAY,legend='Button',fontcolor=Colors.BLACK,font='freesansbold.ttf',fontsize=32,sound=None):
		GameRect.__init__(self,surface,display,posx,posy,width,height,forecolor,bgcolor,legend,fontcolor,font,fontsize)
		self.__pressedcolor = pressedcolor
		self.__pressed = False
		self.__sound = sound
		self.fontObj = pygame.font.Font(font, fontsize)
	def animatepress(self,wait=0.1):
		if self.__pressed:
			self.unpress()
		if self.__sound:
			self.__sound.play()
		self.press()
		time.sleep(wait)
		self.unpress()
	def press(self):
		pygame.draw.rect(self._surface,self.__pressedcolor, (self._x,self._y,self._width,self._height))
		self._drawtext()
		self._display.update()
		self.__pressed = True
	def unpress(self):
		pygame.draw.rect(self._surface,self._forecolor, (self._x,self._y,self._width,self._height))
		self._drawtext()
		self._display.update()
		self.__pressed = False

class Slab(GameRect):
	def __init__(self,surface,display,posx,posy,length,legend,bgcolor=Colors.GRAY,fontsize=32,color=Colors.YELLOW,sound=None):
		GameRect.__init__(self,surface,display,posx,posy,length,length,color,bgcolor,legend,fontsize=fontsize)
		self.__sound = sound
		self.fontObj = pygame.font.Font(self._font, fontsize)
	def __len__(self):
		return self._length
	def move(self,direction):
		if direction == Direction.UP:
			self.erase()
			self._y -= self._height
			assert self._y >= 0
			self.draw()
		elif direction == Direction.DOWN:
			self.erase()
			self._y += self._height
			self.draw()
		elif direction == Direction.LEFT:
			self.erase()
			self._x -= self._width
			assert self._x >= 0
			self.draw()
		elif direction == Direction.RIGHT:
			self.erase()
			self._x += self._width
			self.draw()
		self.__sound.play()


class Container(GameRect):
	def __init__(self,surface,display,posx,posy,width,height,color=Colors.BLACK,bgcolor=Colors.GRAY,rectwidth=5):
		GameRect.__init__(self,surface,display,posx,posy,width,height,color,bgcolor,rectwidth=rectwidth)
		self._objects = list()
	def redrawall(self):
		for obj in self.__objects:
			assert isinstance(obj,GameRect)
			obj.redraw()
	def _addobject(self,obj):
		assert obj in self
		self._objects.append(obj)
	def handleclick(self,x,y):
		for obj in self._objects:
			if obj.mouseinside(x,y):
				obj.animatepress()
	def addButton(self,relx,rely,width,height,forecolor=Colors.GRAY,pressedcolor=Colors.GRAY,legend='Button',fontcolor=Colors.BLACK,font='freesansbold.ttf',fontsize=32,sound=None):
		self._addobject(Button(self._surface,self._display,self._x+relx,self._y+rely,width,height,bgcolor=self._bgcolor,forecolor=forecolor,pressedcolor=pressedcolor,legend=legend,fontsize=fontsize,sound=sound))
	def addSlab(self,relx,rely,length,legend,fontsize=32,color=Colors.YELLOW,sound=None):
		self._addobject(Slab(self._surface,self._display,self._x + relx,self._y + rely,length,legend,bgcolor=self._bgcolor,fontsize=fontsize,color=color,sound=sound))

class Board(Container):
	def __init__(self,surface,display,posx,posy,width,height,color=Colors.BLACK,bgcolor=Colors.GRAY,rectwidth=5,slabsize=32):
		Container.__init__(surface,display,posx,posy,width,height,color=color,bgcolor=bgcolor,rectwidth=rectwidth)
		self.__matrix = [None*4]*4
		for number in random.shuffle([x for x in range(1,16)]):
			i = 0
			j = 0
			for i in range(4): 
				for j in range(4):
					if not self.__matrix[i][j]:
						self.__matrix[i][j] = number
						



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


	menu = Container(DISPLAYSURF,pygame.display,WINDOWWIDTH-170,20+4*SLABSIZE+5*MARGIN-150,150,150,color=Colors.BLACK,bgcolor=BGCOLOR)
	menu.draw()
	menu.addButton(25,20,100,50,forecolor=Colors.GRAY,pressedcolor=Colors.DARKGREY,legend='New Game',fontsize=16,sound=clicksound)
	menu.addButton(25,85,100,50,forecolor=Colors.GRAY,pressedcolor=Colors.DARKGREY,legend='Reset',fontsize=16,sound=clicksound)
	menu.redrawall()

	grid = Container(DISPLAYSURF,pygame.display,20,20,4*SLABSIZE+5*MARGIN,4*SLABSIZE+5*MARGIN,color=Colors.BLACK,bgcolor=BGCOLOR)
	grid.draw()
	grid.addSlab(MARGIN,MARGIN,SLABSIZE,'1')
	grid.addSlab(MARGIN*2+SLABSIZE,MARGIN,SLABSIZE,'2')
	grid.addSlab(MARGIN*3+SLABSIZE*2,MARGIN,SLABSIZE,'3')
	grid.addSlab(MARGIN*4+SLABSIZE*3,MARGIN,SLABSIZE,'4')
	grid.addSlab(MARGIN,MARGIN*2+SLABSIZE,SLABSIZE,'5')
	grid.addSlab(MARGIN*2+SLABSIZE,MARGIN*2+SLABSIZE,SLABSIZE,'6')
	grid.addSlab(MARGIN*3+SLABSIZE*2,MARGIN*2+SLABSIZE,SLABSIZE,'7')
	grid.addSlab(MARGIN*4+SLABSIZE*3,MARGIN*2+SLABSIZE,SLABSIZE,'8')
	grid.addSlab(MARGIN,MARGIN*3+SLABSIZE*2,SLABSIZE,'9')
	grid.addSlab(MARGIN*2+SLABSIZE,MARGIN*3+SLABSIZE*2,SLABSIZE,'10')
	grid.addSlab(MARGIN*3+SLABSIZE*2,MARGIN*3+SLABSIZE*2,SLABSIZE,'11')
	grid.addSlab(MARGIN*4+SLABSIZE*3,MARGIN*3+SLABSIZE*2,SLABSIZE,'12')
	grid.addSlab(MARGIN,MARGIN*4+SLABSIZE*3,SLABSIZE,'13')
	grid.addSlab(MARGIN*2+SLABSIZE,MARGIN*4+SLABSIZE*3,SLABSIZE,'14')
	grid.addSlab(MARGIN*3+SLABSIZE*2,MARGIN*4+SLABSIZE*3,SLABSIZE,'15')
	grid.redrawall()

	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.mixer.music.stop()
				pygame.quit()
				sys.exit()
			elif event.type == KEYDOWN:
				pass
			elif event.type == MOUSEBUTTONDOWN:
				x, y = event.pos
				menu.handleclick(x,y)
		FPSCLOCK.tick(FPS)

if __name__ == '__main__':
	main()