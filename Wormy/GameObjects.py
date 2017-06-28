#!venv/bin/python
import pygame, sys, time, random
from pygame.locals import *
from enum import Enum

class Colors(Enum):
	BLACK = (0,0,0)
	WHITE = (255,255,255)
	RED = (255,0,0)
	DARKRED = (100,0,0)
	GREEN = (0,255,0)
	DARKGREEN = (0,100,0)
	BLUE = (0,0,255)
	DARKBLUE = (0,0,100)
	YELLOW = (255,255,0)
	DARKYELLOW = (100,100,0)
	GRAY = (100,100,100)
	DARKGREY = (50,50,50)
	NAVYBLUE = (60,60,100)

class GameRect(object):
	def __init__(self,surface,posx,posy,width,height,forecolor=Colors.GRAY,bgcolor=Colors.GRAY,legend=None,fontcolor=Colors.BLACK,font='freesansbold.ttf',fontsize=32,rectwidth=0):
		self.x = posx
		self.y = posy
		self._width = width
		self._height = height
		self._surface = surface
		self._forecolor = forecolor
		self._bgcolor = bgcolor
		self._rectwidth = rectwidth
		self._font = font
		self.fontObj = pygame.font.Font(font, fontsize)
		self.legend = legend
		self.fontcolor=fontcolor
	def __contains__(self,otherobj):
		if (self.x <= otherobj.x) and ((self.x + self._width) >= (otherobj.x + otherobj._width)) and (self.y <= otherobj.y) and ((self.y + self._height) >= (otherobj.y + otherobj._height)):
			return True
		else:
			return False
	def erase(self):
		pygame.draw.rect(self._surface,self._bgcolor, (self.x,self.y,self._width,self._height))
		pygame.display.update()
	def _drawtext(self):
		if self.legend:
			textSurfaceObj = self.fontObj.render(self.legend,True, self.fontcolor)
			textRectObj = textSurfaceObj.get_rect()
			textRectObj.center = (self.x + self._width/2,self.y + self._height/2)
			self._surface.blit(textSurfaceObj,textRectObj)
	def draw(self):
		pygame.draw.rect(self._surface,self._forecolor, (self.x,self.y,self._width,self._height),self._rectwidth)
		self._drawtext()
		pygame.display.update()
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

class Block(GameRect):
	def __init__(self,surface,x,y,length=10,color=Colors.WHITE,bgcolor=Colors.BLACK):
		GameRect.__init__(self,surface,x,y,length,length,forecolor=color,bgcolor=bgcolor)


class Container(GameRect):
	def __init__(self,surface,posx,posy,width,height,color=Colors.BLACK,bgcolor=Colors.BLACK,rectwidth=5):
		GameRect.__init__(self,surface,posx,posy,width,height,color,bgcolor,rectwidth=rectwidth)
		self._objects = list()
	def redrawall(self):
		for obj in self._objects:
			assert isinstance(obj,GameRect)
			obj.redraw()
	def addobject(self,obj):
		assert obj in self
		self._objects.append(obj)
	def handleclick(self,x,y,classaction=None):
		for obj in self._objects:
			if obj.mouseinside(x,y):
				obj.animatepress(classaction=classaction)	

class Text(object):
	def __init__(self,surface,display,posx,posy,legend,fontsize=32,fontcolor=Colors.BLACK,bgcolor=Colors.GRAY,font='freesansbold.ttf'):
		self._surface = surface
		self._display = display
		self._x = posx
		self._y = posy
		self.legend = legend
		self._fontsize = fontsize
		self._fontcolor = fontcolor
		self._bgcolor = bgcolor
		self.fontObj = pygame.font.Font(font, fontsize)
		self._textSurfaceObj = self.fontObj.render(self.legend,True, self._fontcolor)
		self._textRectObj = self._textSurfaceObj.get_rect()
	def erase(self):
		pygame.draw.rect(self._surface,self._bgcolor, (self._textRectObj.x,self._textRectObj.y,self._textRectObj.width,self._textRectObj.height))
		self._display.update()
	def draw(self):
		self._textSurfaceObj = self.fontObj.render(self.legend,True, self._fontcolor)
		self._textRectObj = self._textSurfaceObj.get_rect()
		self._textRectObj.x = self._x
		self._textRectObj.y = self._y
		self._surface.blit(self._textSurfaceObj,self._textRectObj)
		self._display.update()
	def redraw(self):
		self.erase()
		self.draw()

class Score(Text):
	def __init__(self,surface,display,posx,posy,score=0,fontsize=32,bgcolor=Colors.GRAY):
		Text.__init__(self,surface,display,posx,posy,'Score: {0}'.format(score),fontsize=fontsize,bgcolor=bgcolor)
		self.score = score
	def modifyScore(self,newscore):
		self.score += newscore
		self.legend = 'Score: {0}'.format(self.score)
	def resetScore(self):
		self.score = 0
		self.legend = 'Score: {0}'.format(self.score)

class Button(GameRect):
	def __init__(self,surface,display,posx,posy,width,height,buttonaction=None,forecolor=Colors.GRAY,bgcolor=Colors.GRAY,pressedcolor=Colors.GRAY,legend=None,fontcolor=Colors.BLACK,font='freesansbold.ttf',fontsize=32,sound=None):
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