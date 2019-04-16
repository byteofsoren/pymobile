import pygame, sys
import numpy as np
from time import sleep
from pygame.locals import *

class gobject:
    """This is a common cor object for displaying both cars and walls"""
    def __init__(self, sprite):
        self._sprite = sprite
        self._boundary = None
        self._pos = [0,0]
        self._theta= 0
        self._speed = 0
        self._dxdy = [1,0]
        self._image_rotation=0
        self._tirmer_scaling=1000
        self._timer = lambda : pygame.time.get_ticks()/self._tirmer_scaling
        self._delta_time = self._timer()

    def start(self,pos:list,dxdy:list):
        ''' This sets the start position and the initial direction of the image.
            For example if the car on the image is pointing from left to right then
            dxdy=[1,0] but if the car is from bottom to top then dxdy=[0,1].
            Remember dxdy must be normalised i.e ||dxdy|| = 1.
        '''
        self._pos = pos
        self._dxdy = dxdy

    def set_stearing_angle(self,theta):
        ''' sets the new steering angle this affects the coordinate system.
        '''
        self._theta = theta

    def set_image_rotation(self,angle):
        ''' Sets the rotation of the image around the center.
        '''
        self._image_rotation = np.deg2rad(angle)

    def set_speed(self, speed):
        ''' sets the new speed this affects how fast coordinate system is traversed.
        '''
        self._speed = speed

    def get_newpos(self):
        ''' Calculates the new position of the car rotated and moved based on speed in direction of angle.
        '''
        dtime = self._timer() - self._delta_time
        print("dtime={}".format(dtime))
        rot_c = np.cos( self._image_rotation)
        rot_s = np.sin( self._image_rotation)
        pos_dx = self._dxdy[0] * self._speed * dtime
        pos_dy = self._dxdy[1] * self._speed * dtime
        print("change pos {};{}".format(pos_dx,pos_dy))
        rotate = lambda c,s: np.array([[c,-s,0,0],[s,c,0,0],[0,0,1,0],[0,0,0,1]])
        move   = lambda dx,dy: np.array([[1,0,0,dx],[0,1,0,dy],[0,0,1,0],[0,0,0,1]])
        m1 = move(self._pos[0],self._pos[1])
        r1 = rotate(rot_c,rot_s)
        m2 = move(pos_dx,pos_dy)
        tr = m1@r1@m2
        print(tr)
        new_pos = tuple(tr[:2,3:].T[0])
        # print("new_pos {}".format(new_pos))
        self._delta_time = dtime
        return new_pos


    def set_zero(self,pos):
        ''' zeros are initialized at the top left of the object
            pos changes the zero and also affects the rotation and direction of the car.

            Preferably set_boundary before setting the zero
        '''
        pass


    def set_boundary(self,boundary:list):
        ''' sets boundary box on the object if no boundary set no coalition is detected
            bondary = [(0,0),(0,4),(4,4),(4,0)] is a rectangle with coordinates for tuple in the list.
        '''
        self._boundary = boundary

    def update(self):
        ''' Over write this function to have an update function '''
        pass

    def __str__(self):
        ret = "Speed={},stearing={}\n".format(self._speed,np.degrees(self._theta))
        ret += "Image pos={},angle={}".format(self._pos,np.degrees(self._image_rotation))
        return ret



class render:
    """render is the plane on where cars can travel"""
    def __init__(self, resulution:list, dx:int,dy:int,scale=1):
        ''' Resolution: tex [800,600] will generate a window with 800x600 resolution.
            Size: tex [-10,20,-30,40] will sett the grid layout on that
                  fitt the size of x=[-10,20] and y=[-30,40].
        '''
        self._resulution = resulution
        self._dx = dx
        self._dy = dy
        self._scale = scale
        self._move = lambda dx,dy: np.array([[1,0,0,dx],[0,1,0,dy],[0,0,1,1],[0,0,0,1]])
        self._flip = np.array([[1,0,0,1],[0,-1,0,1],[0,0,0,1],[0,0,0,1]])
        self._trans = lambda dx,dy,scale: self._flip*self._move(dx,dy)
        # --Test of transformation --
        # vector = np.array([[5,2,1,1]]).T
        # t = self._trans(4,3,1).dot(vector)
        # print(t)
        # print(vector)
        # assert(np.size(t) == 4)
        # print('Ok')
        # assert(False)
        self._surface = pygame.display.set_mode((resulution[0],resulution[1]))
        self._surfaceBG = (255,255,255)
        self._surface.fill(self._surfaceBG)
        self._renderobj = list()
        self.fpsClock = pygame.time.Clock()

    def cord(self, pos:tuple):
        ''' Transforms the position of an world coordinate in to a display coordinate.
            pos:= is a tuple that represent position in the world (x,y)

            Returns the screen cordinate of the type tuple
        '''
        # -- Position ---
        x = pos[0]
        y = pos[1]
        t = self._trans(self._dx,self._dy,self._scale)
        v = np.array([[x,y,0,1]]).T
        # do the multiplication and cut of z and the 1 at the end i.e [1,2,3,4] -> [1,2]
        pos = t.dot(v)[0:2,:]
        return tuple(map(int, pos))

    def add_object(self,obj, worldcord=True):
        self._renderobj.append([obj, worldcord])

    def update(self):
        for inedx_object in self._renderobj:
            pos = tuple(map(int,inedx_object[0]._pos))
            if inedx_object[1] == True:
                pos = self.cord(pos)
            sprite = pygame.transform.rotate(inedx_object[0]._sprite, np.degrees(inedx_object[0]._image_rotation))
            self._surface.blit(sprite, pos)
            # print("time={}, Wrote sprite={} to pos={}".format(pygame.time.get_ticks(), i[0]._sprite, pos))
        pygame.display.update()
        self.fpsClock.tick(10)
        self._surface.fill(self._surfaceBG)



if __name__ == '__main__':
    class mytest(gobject):
        """testing the car with an own object"""
        def __init__(self, pos:list):
            super(mytest, self).__init__(pygame.image.load('blue_car.png'))
            self._pos = pos
            # self._angle = angle
            self.set_image_rotation(120)
            self._temp = np.arange(0,360,10)
            self.count = 0
            self.set_speed(20)

        def update(self):
            new_pos = self.get_newpos()
            self._pos=new_pos
            # self.set_image_rotation(self._temp[self.count%36])
            self.count += 1


    blue_car = mytest([0,0])
    myrender = render([800,600],dx=800//2,dy=600//2)
    myrender.add_object(blue_car)
    while True:
        blue_car.update()
        print(blue_car)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        myrender.update()











