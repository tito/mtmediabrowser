from __future__ import with_statement
from pymt import *
from pdfbook.graphics import *
import pdfbook.mtbook

page_duration   = .5
page_corner     = 100

class Page(MTWidget):
    def __init__(self, **kwargs):
        super(Page, self).__init__(**kwargs)
        self.pdf = kwargs.get('pdf')
        self.line = kwargs.get('LOS')
        self.mode = 'triangle'
        self.p1 = (0,0)
        self.p2 = (0,0)
        self.p3 = (0,0)
        self.p4 = (0,0)
        self.spl1 = (0,0)
        self.spl2 = (0,0)
        self.touches = {}
        self.for_anim = self.p1[0]
        self.other_side = kwargs.get('other_side')
        self.shadow_enabled = True
        self.pctg_turn_compl = 0.0

    def collide_corner(self, x, y):
        if self.reverse:
            return x > self.x + self.width - page_corner and x < self.x + self.width and \
                   y > self.y and y < self.y + self.height
        else:
            return x > self.x and x < self.x + page_corner and \
                   y > self.y and y < self.y + self.height

    def on_touch_down(self, touch):
        if self.collide_corner(*touch.pos):
            self.bring_to_front()
            self.touches[touch.id] = (touch.x, touch.y)
            self.line.pos=(touch.x,self.y)

            self.line.calculate_line_rotation(touch.x,touch.y)
            self.line.calculate_intersection(touch.x,touch.y)
            self.for_anim = self.p1[0]

            # XXX FIXME without 2 time, the first time is wrong.
            self.line.calculate_line_rotation(touch.x,touch.y)
            self.line.calculate_intersection(touch.x,touch.y)
            self.for_anim = self.p1[0]
            return True
        return super(Page, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos) and touch.id in self.touches:
            self.line.pos=(touch.x,self.y)
            self.line.calculate_line_rotation(touch.x,touch.y)
            self.line.calculate_intersection(touch.x,touch.y)
            self.for_anim = self.p1[0]
            return True
        return super(Page, self).on_touch_move(touch)

    @property
    def flip_running(self):
        if (self.fallback_anim_controller is not None and self.fallback_anim_controller.running) \
            or (self.flipcompletely_anim_controller is not None and self.flipcompletely_anim_controller.running):
                return True
        if len(self.touches):
            return True
        return False


class Page_Left(Page):
    def __init__(self, **kwargs):
        self.reverse = False
        super(Page_Left, self).__init__(**kwargs)
        pagelist = kwargs.get('page_list')

        self.texture1 = pagelist[2].texture
        self.texture2 = pagelist[0].texture
        self.texture3 = pagelist[1].texture

        self.fallback_pos = self.pos[0]
        self.fallback_anim = Animation(for_anim=self.pos[0], pctg_turn_compl=1., d=page_duration)
        self.fallback_anim_controller = None

        self.flipcompletely_pos = self.pos[0]+self.width
        self.flipcompletely_anim = Animation(for_anim=self.pos[0]+self.width, pctg_turn_compl=0., d=page_duration)
        self.flipcompletely_anim_controller = None

        self.start_index = 0
        self.top_page = 0

    def flip(self):
        if self.top_page <= 0 :
            return
        self.bring_to_front()
        self.line.pos=(self.x,self.y)
        self.line.calculate_line_rotation(self.x,self.y)
        self.line.calculate_intersection(self.x,self.y)
        self.for_anim = self.p1[0]
        self.flipcompletely_anim_controller = self.do(self.flipcompletely_anim)

    def on_update(self):
        if (self.fallback_anim_controller is not None and self.fallback_anim_controller.running) \
            or (self.flipcompletely_anim_controller is not None and self.flipcompletely_anim_controller.running):
            self.line.pos=(self.for_anim,self.y)
            self.line.calculate_line_rotation(self.for_anim,self.y)
            self.line.calculate_intersection(self.for_anim,self.y)

    def on_touch_down(self, touch):
        if self.collide_point(touch.x,touch.y) :
            if (self.fallback_anim_controller is not None and self.fallback_anim_controller.running):
                self.fallback_anim_controller.stop()
            if (self.flipcompletely_anim_controller is not None and self.flipcompletely_anim_controller.running):
                self.flipcompletely_anim_controller.generate_event = False
                self.flipcompletely_anim_controller.stop()
        if self.top_page > 0 :
            return super(Page_Left,self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.id in self.touches:
            if self.p1[0] <= self.pos[0]+int(self.width/2):
                self.fallback_anim_controller = self.do(self.fallback_anim)
            else:
                self.flipcompletely_anim_controller = self.do(self.flipcompletely_anim)
            del self.touches[touch.id]
            return True

    def set_new_textures(self,startindex=0,pagelist=[]):
        self.start_index = startindex
        self.top_page = startindex+2

        self.texture1 = pagelist[2].texture
        self.texture2 = pagelist[0].texture
        self.texture3 = pagelist[1].texture

        self.top_page = pagelist[2].pageno

    def on_animation_complete(self, anim):
        if anim == self.fallback_anim:
            return

        self.line.reset()

        ind = self.start_index
        self.other_side.set_new_textures(
            startindex=ind+3,
            pagelist=[
                pdfbook.mtbook.PopplerPDFPage(pdf=self.pdf,pageno=ind+1),
                pdfbook.mtbook.PopplerPDFPage(pdf=self.pdf,pageno=ind+2),
                pdfbook.mtbook.PopplerPDFPage(pdf=self.pdf,pageno=ind+3)
            ]
        )
        self.other_side.bring_to_front()

        if ind == 0:
             self.set_new_textures(
                 startindex=ind,
                 pagelist=[
                     pdfbook.mtbook.PopplerPDFPage(pdf=self.pdf,pageno=0),
                     pdfbook.mtbook.PopplerPDFPage(pdf=self.pdf,pageno=0),
                     pdfbook.mtbook.PopplerPDFPage(pdf=self.pdf,pageno=0)
                 ]
             )
        else:
            self.set_new_textures(
                startindex=ind-2,
                pagelist=[
                    pdfbook.mtbook.PopplerPDFPage(pdf=self.pdf,pageno=ind-2),
                    pdfbook.mtbook.PopplerPDFPage(pdf=self.pdf,pageno=ind-1),
                    pdfbook.mtbook.PopplerPDFPage(pdf=self.pdf,pageno=ind)
                ]
            )

    def draw(self):
        #draw Area A
        texcoords = self.texture1.tex_coords
        drawTR(texture=self.texture1,
               pos=(self.pos[0], self.pos[1],
                    self.pos[0] + self.size[0], self.pos[1],
                    self.pos[0] + self.size[0], self.pos[1] + self.size[1],
                    self.pos[0], self.pos[1] + self.size[1]),
               tex_coords = texcoords
              )

        if not self.flip_running:
            return

        if self.mode == 'triangle':
            #calculate texture coordinates
            test = float(self.width-(self.p1[0]-self.pos[0]))/self.width
            test2 = float(self.height-(self.p2[1]-self.pos[1]))/self.height

            #draw Area B
            texcoords = self.texture2.tex_coords
            drawTT(
                    texture=self.texture2,
                    pos=(self.pos[0],self.pos[1],self.p1[0],self.p1[1],self.p2[0],self.p2[1]),
                    tex_coords = (texcoords[0],texcoords[1], texcoords[2]*(1.0-test),texcoords[3], 0,(test2)*texcoords[1])
                    )

            #draw Area C
            texcoords = self.texture3.tex_coords
            drawTT(
                    texture=self.texture3,
                    pos=(self.p1[0],self.p1[1],self.spl1[0],self.spl1[1],self.p2[0],self.p2[1]),
                    tex_coords = ((test)*texcoords[2],texcoords[1], texcoords[2],texcoords[3], texcoords[4],(test2)*texcoords[1])
                    )

            if self.shadow_enabled:
                with DO(gx_blending, gx_begin(GL_TRIANGLES)):
                    glColor4f(0.0,0.0,0.0,0.0)
                    glVertex2f(self.pos[0], self.pos[1])
                    glColor4f(0.3,0.3,0.3,self.pctg_turn_compl)
                    glVertex2f(*self.p1)
                    glColor4f(0.3,0.3,0.3,self.pctg_turn_compl)
                    glVertex2f(*self.p2)

        else:
            #calculate texture coordinates
            test1 = float(self.width-(self.p1[0]-self.pos[0]))/self.width
            test2 = float(self.width-(self.p4[0]-self.pos[0]))/self.width

            #draw Area B
            texcoords = self.texture2.tex_coords
            drawTR(
                    texture=self.texture2,
                    pos=(
                            self.pos[0],self.pos[1],
                            self.p1[0],self.p1[1],
                            self.p4[0],self.p4[1],
                            self.pos[0],self.pos[1]+self.height
                        ),
                    tex_coords = (texcoords[0],texcoords[1], texcoords[2]*(1.0-test1),texcoords[3], (1.0-test2)*texcoords[4],texcoords[5], texcoords[6],texcoords[7])
                    )

            #draw Area C
            texcoords = self.texture3.tex_coords

            drawTR(
                    texture=self.texture3,
                    pos=(
                            self.p1[0],self.p1[1],
                            self.spl1[0],self.spl1[1],
                            self.spl2[0],self.spl2[1],
                            self.p4[0],self.p4[1]
                        ),
                    tex_coords = ((test1)*texcoords[2],texcoords[1], texcoords[2],texcoords[3], texcoords[4],texcoords[5], (test2)*texcoords[2],texcoords[7])
                    )

            if self.shadow_enabled:
                with DO(gx_blending, gx_begin(GL_QUADS)):
                    glColor4f(0.3,0.3,0.3,self.pctg_turn_compl)
                    glVertex2f(*self.p1)
                    glColor4f(0.3,0.3,0.3,self.pctg_turn_compl)
                    glVertex2f(*self.p4)
                    glColor4f(0.0,0.0,0.0,0.0)
                    glVertex2f(self.pos[0], self.pos[1] + self.size[1])
                    glColor4f(0.0,0.0,0.0,0.0)
                    glVertex2f(self.pos[0], self.pos[1])


class Page_Right(Page):
    def __init__(self, **kwargs):
        self.reverse = True
        super(Page_Right, self).__init__(**kwargs)
        pagelist = kwargs.get('page_list')

        self.texture1 = pagelist[0].texture
        self.texture2 = pagelist[2].texture
        self.texture3 = pagelist[1].texture

        self.fallback_pos = self.pos[0]+self.width
        self.fallback_anim = Animation(for_anim=self.pos[0]+self.width, pctg_turn_compl=1., d=page_duration)
        self.fallback_anim_controller = None

        self.flipcompletely_pos = self.pos[0]
        self.flipcompletely_anim = Animation(for_anim=self.pos[0], pctg_turn_compl=0., d=page_duration)
        self.flipcompletely_anim_controller = None

        self.start_index = 3
        self.top_page = 3

    def flip(self):
        if self.top_page >= self.pdf.maxpages :
            return
        self.bring_to_front()
        self.line.pos=(self.x+self.width,self.y)
        self.line.calculate_line_rotation(self.x+self.width,self.y)
        self.line.calculate_intersection(self.x+self.width,self.y)
        self.for_anim = self.p1[0]
        self.flipcompletely_anim_controller = self.do(self.flipcompletely_anim)

    def on_update(self):
        if (self.fallback_anim_controller is not None and self.fallback_anim_controller.running) \
            or (self.flipcompletely_anim_controller is not None and self.flipcompletely_anim_controller.running):
            self.line.pos=(self.for_anim,self.y)
            self.line.calculate_line_rotation(self.for_anim,self.y)
            self.line.calculate_intersection(self.for_anim,self.y)

    def on_touch_down(self, touch):
        if self.collide_point(touch.x,touch.y) :
            if (self.fallback_anim_controller is not None and self.fallback_anim_controller.running):
                self.fallback_anim_controller.stop()
            if (self.flipcompletely_anim_controller is not None and self.flipcompletely_anim_controller.running):
                self.flipcompletely_anim_controller.generate_event = False
                self.flipcompletely_anim_controller.stop()
        if self.top_page <= self.pdf.maxpages :
            return super(Page_Right,self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.id in self.touches:
            if self.p1[0] >= self.pos[0]+int(self.width/2):
                self.fallback_anim_controller = self.do(self.fallback_anim)
            else:
                self.flipcompletely_anim_controller = self.do(self.flipcompletely_anim)
            del self.touches[touch.id]
            return True

    def set_new_textures(self,startindex=4,pagelist=[]):
        self.start_index = startindex
        self.top_page = startindex

        self.texture1 = pagelist[0].texture
        self.texture2 = pagelist[2].texture
        self.texture3 = pagelist[1].texture

        self.top_page = pagelist[0].pageno

    def on_animation_complete(self, anim):
        if anim == self.fallback_anim:
            return

        self.line.reset()

        ind = self.start_index
        self.other_side.set_new_textures(
            startindex=ind-3,
            pagelist=[
                pdfbook.mtbook.PopplerPDFPage(pdf=self.pdf,pageno=ind-3),
                pdfbook.mtbook.PopplerPDFPage(pdf=self.pdf,pageno=ind-2),
                pdfbook.mtbook.PopplerPDFPage(pdf=self.pdf,pageno=ind-1)
            ]
        )
        self.other_side.bring_to_front()

        if ind == self.pdf.maxpages+1:
            self.set_new_textures(
                startindex=ind,
                pagelist=[
                    pdfbook.mtbook.PopplerPDFPage(pdf=self.pdf,pageno=ind),
                    pdfbook.mtbook.PopplerPDFPage(pdf=self.pdf,pageno=ind),
                    pdfbook.mtbook.PopplerPDFPage(pdf=self.pdf,pageno=ind)
                ]
            )
        else:
            self.set_new_textures(
                startindex=ind+2,
                pagelist=[
                    pdfbook.mtbook.PopplerPDFPage(pdf=self.pdf,pageno=ind),
                    pdfbook.mtbook.PopplerPDFPage(pdf=self.pdf,pageno=ind+1),
                    pdfbook.mtbook.PopplerPDFPage(pdf=self.pdf,pageno=ind+2)
                ]
            )

    def draw(self):
        set_color(1,1,1,1)
        #draw Area A
        drawTR(
               texture=self.texture1,
               pos=(self.pos[0], self.pos[1],
                    self.pos[0] + self.size[0], self.pos[1],
                    self.pos[0] + self.size[0], self.pos[1] + self.size[1],
                    self.pos[0], self.pos[1] + self.size[1]),
              )

        if not self.flip_running:
            return

        if self.mode == 'triangle':
            set_color(1,1,1,1)

            #calculate texture coordinates
            test = float(self.width-(self.p1[0]-self.pos[0]))/self.width
            test2 = float(self.height-(self.p2[1]-self.pos[1]))/self.height

            #draw Area B
            texcoords = self.texture2.tex_coords
            drawTT(
                    texture=self.texture2,
                    pos=(self.p1[0],self.p1[1],self.pos[0]+self.width,self.pos[1],self.p2[0],self.p2[1]),
                    tex_coords = ((1.0-test)*texcoords[2],texcoords[1], texcoords[2],texcoords[3], texcoords[4],(test2)*texcoords[1])
                    )


            #draw Area C
            texcoords = self.texture3.tex_coords
            drawTT(
                    texture=self.texture3,
                    pos=(self.spl1[0],self.spl1[1],self.p1[0],self.p1[1],self.p2[0],self.p2[1]),
                    tex_coords = (texcoords[0],texcoords[1], texcoords[2]*(test),texcoords[3], 0,(test2)*texcoords[1])
                    )
            if self.shadow_enabled:
                with DO(gx_blending, gx_begin(GL_TRIANGLES)):
                    glColor4f(0.0,0.0,0.0,0.0)
                    glVertex2f(self.pos[0] + self.size[0], self.pos[1])
                    glColor4f(0.3,0.3,0.3,self.pctg_turn_compl)
                    glVertex2f(*self.p1)
                    glColor4f(0.3,0.3,0.3,self.pctg_turn_compl)
                    glVertex2f(*self.p2)


        elif self.p4 is not None:
            #calculate texture coordinates
            test1 = float(self.width-(self.p1[0]-self.pos[0]))/self.width
            test2 = float(self.width-(self.p4[0]-self.pos[0]))/self.width
            #draw Area Bself.pos[0]+self.width
            texcoords = self.texture2.tex_coords
            drawTR(
                    texture=self.texture2,
                    pos=(
                            self.p1[0],self.p1[1],
                            self.pos[0]+self.width,self.pos[1],
                            self.pos[0]+self.width,self.pos[1]+self.height,
                            self.p4[0],self.p4[1]
                        ),
                    tex_coords = ((1.0-test1)*texcoords[2],texcoords[1], texcoords[2],texcoords[3], texcoords[4],texcoords[5], (1.0-test2)*texcoords[2],texcoords[7])
                    )

            #draw Area C

            drawTR(
                    texture=self.texture3,
                    pos=(
                            self.spl1[0],self.spl1[1],
                            self.p1[0],self.p1[1],
                            self.p4[0],self.p4[1],
                            self.spl2[0],self.spl2[1]
                        ),
                    tex_coords = (texcoords[0],texcoords[1], texcoords[2]*(test1),texcoords[3], (test2)*texcoords[4],texcoords[5], texcoords[6],texcoords[7])
                    )

            if self.shadow_enabled:
                with DO(gx_blending, gx_begin(GL_QUADS)):
                    glColor4f(0.3,0.3,0.3,self.pctg_turn_compl)
                    glVertex2f(*self.p1)
                    glColor4f(0.3,0.3,0.3,self.pctg_turn_compl)
                    glVertex2f(*self.p4)
                    glColor4f(0.0,0.0,0.0,0.0)
                    glVertex2f(self.pos[0] + self.size[0], self.pos[1] + self.size[1])
                    glColor4f(0.0,0.0,0.0,0.0)
                    glVertex2f(self.pos[0] + self.size[0], self.pos[1])


