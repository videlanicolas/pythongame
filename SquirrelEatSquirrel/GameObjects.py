#!venv/bin/python3
import pygame, sys, random, itertools, math
from pygame.locals import *
from enum import Enum
from pygame.display import update as UPDATE

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
	TRANSPARENT = (0,0,0,255)
	PURPLE = (168,143,172)
	SALMON = (233,128,110)
	CYAN = (140,210,219)
	ORANGE = (255,149,5)

class Directions(Enum):
	UP = 0
	DOWN = 1
	LEFT = 2
	RIGHT = 3

class Entity(object):
	def __init__(self,surface,x,y,drawable_surface):
		self.__surface = surface
		self.__mysurface = Surface((x,y))
		self.image = pygame.image.load(image) if image else None
		self.__noimage_color = noimage_color
	def draw(self):
		if self.image:
			self.__surface.blit(self.image,(0,0))
		else:
			self.__surface.fill(self.__noimage_color)

class Blob(object):
	def __init__(self,surface,x,y,color=(random.randint(100,255),random.randint(100,255),random.randint(100,255))):
		self.x = x
		self.y = y
		self.__surface = surface
		self.bot = True
		#Random color
		self.color = color
		self.radius = random.randint(30,100)
		self.direction = random.choice(list(Directions))
	def __contains__(self,otherobj):	
		return True if math.sqrt(math.pow((otherobj.x-self.x),2) + math.pow((otherobj.y-self.y),2)) < self.radius else False
	def draw(self,camera):
		pygame.draw.circle(self.__surface,self.color, (self.x + camera[0],self.y + camera[1]),self.radius,0)

class ContinuousMap(object):
	def __init__(self,screen,x,y):
		self.__screen = screen
		self.__screen_size_x, self.__screen_size_y = screen.get_size()
		self.__map = pygame.Surface((x,y))
		self.__map_size_x, self.__map_size_y = (x,y)
		self.__map.fill((40,40,40))
		self.__objects = list()
		self.speed = 1
		#Generate a background
		for _ in range(1000):
			c = random.randint(20,60)
			_x = random.randint(0,x)
			_y = random.randint(0,y)
			r = random.randint(x // 20, y // 10)
			pygame.draw.circle(self.__map,(c,c,c),(_x,_y),r)
		self.camera = ((self.__screen_size_x - x) // 2, (self.__screen_size_y - y) // 2)
		self.character = Blob(self.__screen,x // 2,y // 2)
		self.character.bot = False
		self.__objects.append(self.character)
	def __object_on_screen(self,obj):
		return True if 	(self.camera[0]+2*obj.radius >= (obj.radius - obj.x) >= (self.camera[0] - self.__screen_size_x)) or \
						(self.camera[1]+2*obj.radius >= (obj.radius - obj.y) >= (self.camera[1] - self.__screen_size_y)) else False
	def has_lost(self):
		return self.character not in self.__objects
	def animate(self):
		for obj in self.__objects:
			if not obj.bot:
				continue
			d = random.choice(list(Directions))
			if d == Directions.UP:
				obj.y = max(obj.y - 1,obj.radius)
			elif d == Directions.DOWN:
				obj.y = min(obj.y + 1,self.__map_size_y-obj.radius)
			elif d == Directions.LEFT:
				obj.x = max(obj.x - 1,obj.radius)
			elif d == Directions.RIGHT:
				obj.x = min(obj.x + 1,self.__map_size_x-obj.radius)
	def character_move(self,direction):
		if direction == Directions.UP:
			for i in range(self.speed):
				self.pan_camera(direction)
				self.character.y = max(self.character.y - 1,self.character.radius)
		elif direction == Directions.DOWN:
			for i in range(self.speed):
				self.pan_camera(direction)
				self.character.y = min(self.character.y + 1,self.__map_size_y-self.character.radius)
		elif direction == Directions.LEFT:
			for i in range(self.speed):
				self.pan_camera(direction)
				self.character.x = max(self.character.x - 1,self.character.radius)
		elif direction == Directions.RIGHT:
			for i in range(self.speed):
				self.pan_camera(direction)
				self.character.x = min(self.character.x + 1,self.__map_size_x-self.character.radius)
	def pan_camera(self,direction):
		if direction == Directions.UP:
			if self.__map_size_y - (self.__screen_size_y // 2) >= self.character.y >= (self.__screen_size_y // 2):
				self.camera = (self.camera[0], min(self.camera[1] + 1,0))
		elif direction == Directions.DOWN:
			if (self.__screen_size_y // 2) <= self.character.y <= self.__map_size_y - (self.__screen_size_y // 2):
				self.camera = (self.camera[0], max(self.camera[1] - 1,self.__screen_size_y - self.__map_size_y))
		elif direction == Directions.LEFT:
			if self.__map_size_x - (self.__screen_size_x // 2) >= self.character.x >= (self.__screen_size_x // 2):
				self.camera = (min(self.camera[0] + 1,0), self.camera[1])
		elif direction == Directions.RIGHT:
			if (self.__screen_size_x // 2) <= self.character.x <= self.__map_size_x - (self.__screen_size_x // 2):
				self.camera = (max(self.camera[0] - 1,self.__screen_size_x - self.__map_size_x), self.camera[1])
	def add_object(self,x,y):
		self.__objects.append(Blob(self.__screen,x,y))
	def draw(self):
		#Pan the camera to target
		self.__screen.blit(self.__map,self.camera)
		#Order objects by increasing radius
		self.__objects.sort(key=lambda x: x.radius, reverse=False)
		for obj in self.__objects:
			for _obj in self.__objects[self.__objects.index(obj) + 1:]:
				if obj in _obj:
					_obj.radius = int(math.sqrt(math.pow(obj.radius,2) + math.pow(_obj.radius,2)))
					self.__objects.remove(obj)
			#Draw if it's on screen
			if self.__object_on_screen(obj):
				obj.draw(self.camera)