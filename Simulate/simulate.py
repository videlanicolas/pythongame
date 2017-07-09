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

class GameRect(object):
	def __init__(self,surface,display,posx,posy,width,height,bgcolor=Colors.GRAY,legend=None,fontcolor=Colors.BLACK,font='freesansbold.ttf',fontsize=32,rectwidth=0):
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

class Sim(object):
	def __init__(self,surface,display,buttons):
		self.__sequence = list()
		self.__sequence.append(random.randint(0,3))
		self.__buttons = buttons
		self._surface = surface
		self._display = display
	def animate(self):
		for i in self.__sequence:
			self.__buttons[i].animatepress(wait=0.5)
			time.sleep(0.5)
	def resetsequence(self):
		self.__sequence = list()
		self.__sequence.append(random.randint(0,3))
	def addsequence(self):
		self.__sequence.append(random.randint(0,3))
	def guess(self,g,index):
		if index < len(self.__sequence):
			if g == self.__sequence[index]:
				return True
			else:
				return False
		else:
			return False
	def redrawall(self):
		for slab in self.__buttons:
			slab.redraw()
	def handleclick(self,x,y):
		for slab in self.__buttons:
			if slab.mouseinside(x,y):
				slab.animatepress(wait=0.3)
				return self.__buttons.index(slab)
		return None

def main():
	pygame.init()
	WINDOWWIDTH = 640
	WINDOWHEIGHT = 480
	DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT))
	BGCOLOR = Colors.NAVYBLUE
	SLABSIZE = 200
	MARGIN = 5
	FPS = 30
	endround = pygame.mixer.Sound('sounds/round_end.wav')
	gameover = pygame.mixer.Sound('sounds/game_over.wav')
	pygame.display.set_caption('Simulate')
	FPSCLOCK = pygame.time.Clock()
	DISPLAYSURF.fill(BGCOLOR)
	pygame.display.update()

	score = Score(DISPLAYSURF,pygame.display,WINDOWHEIGHT-20,10,score=0,bgcolor=BGCOLOR)
	score.draw()

	buttons = [	Button(DISPLAYSURF,pygame.display,50,50,SLABSIZE,SLABSIZE,forecolor=Colors.DARKYELLOW,bgcolor=Colors.NAVYBLUE,pressedcolor=Colors.YELLOW,sound=pygame.mixer.Sound('sounds/tone1.wav')),\
				Button(DISPLAYSURF,pygame.display,50+SLABSIZE+MARGIN,50,SLABSIZE,SLABSIZE,forecolor=Colors.DARKGREEN,bgcolor=Colors.NAVYBLUE,pressedcolor=Colors.GREEN,sound=pygame.mixer.Sound('sounds/tone2.wav')),\
				Button(DISPLAYSURF,pygame.display,50,50+SLABSIZE+MARGIN,SLABSIZE,SLABSIZE,forecolor=Colors.DARKBLUE,bgcolor=Colors.NAVYBLUE,pressedcolor=Colors.BLUE,sound=pygame.mixer.Sound('sounds/tone3.wav')),\
				Button(DISPLAYSURF,pygame.display,50+SLABSIZE+MARGIN,50+SLABSIZE+MARGIN,SLABSIZE,SLABSIZE,forecolor=Colors.DARKRED,bgcolor=Colors.NAVYBLUE,pressedcolor=Colors.RED,sound=pygame.mixer.Sound('sounds/tone4.wav'))]

	sim = Sim(DISPLAYSURF,pygame.display,buttons)
	sim.redrawall()

	targetnumber = 1
	lost = False
	while True:
		time.sleep(1)
		seqnumber = 0	
		sim.animate()
		pygame.event.get()
		while seqnumber < targetnumber and not lost:
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.mixer.music.stop()
					pygame.quit()
					sys.exit()
				elif event.type == MOUSEBUTTONDOWN:
					x, y = event.pos
					slabindex = sim.handleclick(x,y)
					if slabindex != None:
						if sim.guess(slabindex,seqnumber):
							seqnumber += 1
						else:
							lost = True
		if not lost:
			sim.addsequence()
			targetnumber += 1
			endround.play()
			score.modifyScore(1)
			score.redraw()
		else:
			gameover.play()
			time.sleep(1)
			targetnumber = 1
			score.resetScore()
			sim.resetsequence()
			score.redraw()
			lost = False
		FPSCLOCK.tick(FPS)

if __name__ == '__main__':
	main()