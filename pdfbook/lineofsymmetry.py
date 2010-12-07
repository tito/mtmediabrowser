from __future__ import with_statement
from pymt import *
from math import sin,cos,radians,sqrt,tan

debug_los = False

class LOS(MTWidget):
    def __init__(self, **kwargs):
        super(LOS, self).__init__(**kwargs)
        self.rotation = self._initial_rotation
        self.page = kwargs.get('page_ref')
        self.p1 = Vector(self.pos[0], self.pos[1])
        self._initial_pos = self.p1
        self.slope = 1.0

    @property
    def rotation_radians(self):
        return radians(self.rotation)

    @property
    def p2(self):
        if self.reverse:
            out = Vector(sin(self.rotation_radians), cos(self.rotation_radians))
        else:
            out = Vector(cos(self.rotation_radians), sin(self.rotation_radians))
        return out * 1000. + self.p1

    def reset(self):
        self.rotation = self._initial_rotation
        self.page.p1 = self.p1 = self._initial_pos
        self.page.p2 = self.p2
        self.page.mode = 'triangle'
        self.page.p3 = (0,0)
        self.page.p4 = (0,0)
        self.page.spl1 = (0,0)
        self.page.spl2 = (0,0)

    def draw(self):
        if debug_los:
            set_color(1,0,0,1)
            drawLine((self.p1[0],self.p1[1],self.p2[0],self.p2[1]), width=1)

    def find_reflection(self,point,line):
        if not self.reverse:
            try:
                slope = float(line[3]-line[1])/float(line[2]-line[0])
            except ZeroDivisionError:
                slope = -1000000000000.000
        else:
            slope = tan(radians(90.0-self.rotation))

        # XXX BUG if slope is 16846 (big values)
        if abs(slope < 180):
            self.slope = slope

        d = -point[0]-slope*point[1]

        a1 = -slope
        b1 = 1
        c1 = float(line[1])-slope * float(line[0])

        a2 = -1
        b2 = -slope
        c2 = d
        x1 = abs((float(b1*c2)-float(b2*c1))/(float(a1*b2)-float(a2*b1)))
        y1 = abs((float(c1*a2)-float(c2*a1))/(float(a1*b2)-float(a2*b1)))

        Y = Vector((x1,y1))
        X = Vector(point)
        X1 = Y-(X-Y)
        return X1

    def calculate_line_rotation(self,x,y):
        if self.reverse:
            self.rotation = 45.0*(x-self.page.pos[0])/self.page.width
        else:
            self.rotation = 135.0-45.0*(x-self.page.pos[0])/self.page.width

        self.p1 = self.page.p1 = Vector(x, self.page.pos[1])

        # calculate percentage turn complete
        if self.reverse:
            p = (self.page.pos[0]+self.page.width-self.page.p1[0])/self.page.width
        else:
            p = (self.page.p1[0]-self.page.pos[0])/self.page.width
        self.page.pctg_turn_compl = 1.0 - (p ** 4)

    def calculate_intersection(self,x,y):
        dx = 0
        if self.reverse:
            dx = self.page.width

        d = (self.page.pos[1]+self.page.height-self.p1[1]) - \
            self.slope*(self.page.pos[0]+dx-self.p1[0])
        if d >= 0:
            self.page.mode = 'triangle'
            ix = Vector.line_intersection(
                                            (self.page.pos[0]+dx,self.page.pos[1]),
                                            (self.page.pos[0]+dx,self.page.pos[1]+self.page.height),
                                            (self.p1[0],self.p1[1]),
                                            (self.p2[0],self.p2[1])
                                         )
            if ix is None:
                return

            if ix[1] >= self.page.pos[1]+self.page.height :
                self.page.p2 = (self.page.pos[0]+dx,self.page.pos[1]+self.page.height)
            else:
                self.page.p2 = (int(ix[0]),int(ix[1]))

            self.page.spl1 = self.find_reflection(point=(self.page.pos[0]+dx,self.page.pos[1]),line=(self.p1[0],self.p1[1],self.p2[0],self.p2[1]))
        else:
            self.page.mode = 'quad'
            ix = Vector.line_intersection(
                                            (self.page.pos[0],self.page.pos[1]+self.page.height),
                                            (self.page.pos[0]+self.page.width,self.page.pos[1]+self.page.height),
                                            (self.p1[0],self.p1[1]),
                                            (self.p2[0],self.p2[1])
                                         )
            self.page.p4 = ix
            self.page.spl1 = self.find_reflection(point=(self.page.pos[0]+dx,self.page.pos[1]),line=(self.p1[0],self.p1[1],self.p2[0],self.p2[1]))
            self.page.spl2 = self.find_reflection(point=(self.page.pos[0]+dx,self.page.pos[1]+self.page.height),line=(self.p1[0],self.p1[1],self.p2[0],self.p2[1]))



class LOS_Left(LOS):
    def __init__(self, **kwargs):
        self.reverse = False
        self._initial_rotation = 135.0
        super(LOS_Left, self).__init__(**kwargs)

class LOS_Right(LOS):
    def __init__(self, **kwargs):
        self.reverse = True
        self._initial_rotation = 45.0
        super(LOS_Right, self).__init__(**kwargs)

