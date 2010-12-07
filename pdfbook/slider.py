from __future__ import with_statement
from pymt import *
import os

current_dir = os.path.dirname(__file__)

class MTToggler(MTWidget):
    def __init__(self, **kwargs):
        super(MTToggler, self).__init__(**kwargs)
        self.bound_points = self.x+10,self.y+20, self.x+self.width-10,self.y+20
        self.button = MTImageButton(filename=os.path.join(current_dir, 'data', 'button.png'))
        self.add_widget(self.button)
        self.button.center = self.center
        self.register_event_type('on_slide_left')
        self.register_event_type('on_slide_right')
        self._anim = None

    def on_draw(self):
        set_color(*self.style['bg-color'])
        drawCSSRectangle(pos=self.pos,size=self.size,style={'border-radius':20})
        set_color(0,0,0,1)
        drawLine(points=self.bound_points,width=5)
        self.button.draw()

    def collide_point(self, x, y):
        return (x >= self.x+10 and x <= self.x+self.width-10) and (y >= self.y and y<=self.y+self.height)

    def on_touch_down(self,touch):
        if self.collide_point(touch.x, touch.y):
            if self._anim is not None:
                self._anim.stop()
                self._anim = None
            return True

    def on_touch_move(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.button.x = touch.x - self.button.width/2
            return True

    def on_touch_up(self, touch):
        if self.button.center[0] == self.center[0]:
            return
        if self.button.center[0] < self.center[0]:
            self.dispatch_event('on_slide_left', touch)
        elif self.button.center[0] > self.center[0]:
            self.dispatch_event('on_slide_right', touch)
        self._anim = self.button.do(Animation(duration=.2, f='ease_in_cubic', center=self.center))

    def on_slide_left(self, touch):
        pass

    def on_slide_right(self, touch):
        pass

