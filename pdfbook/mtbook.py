from __future__ import with_statement
from pymt import *
from slider import *
from pdfbook import pdf
from pdfbook.lineofsymmetry import *
from pdfbook.page import *

class PopplerPDF(pdf.Pdf):
    def __init__(self, filename, **kwargs):
        super(PopplerPDF, self).__init__(filename, **kwargs)
        self.maxpages = self.get_n_pages()
        self.page_width, self.page_height = \
                map(int, self.get_page_size(0))


class PopplerPDFPage(MTWidget):
    white_texture = None
    def __init__(self, **kwargs):
        super(PopplerPDFPage, self).__init__(**kwargs)
        self.pdf = kwargs.get('pdf')
        self.size = (int(self.pdf.page_width),int(self.pdf.page_height))
        self.texture = None
        self.pageno = int(kwargs.get('pageno'))
        if self.pageno == 0 or self.pageno >= self.pdf.maxpages+1:
            # create a white texture
            if self.white_texture is None:
                self.white_texture = Texture.create(self.size[0], self.size[1])
                self.white_texture.blit_buffer('\xff' * self.size[0] * self.size[1] * 3, mode='RGB')
            self.texture = self.white_texture
        else:
            self.update_to_page(self.pageno-1)


    def update_to_page(self,pageno):
        width = int(self.pdf.page_width)
        height = int(self.pdf.page_height)
        self.texture = self.pdf.get_page_texture(pageno)

class Book(MTWidget):
    def __init__(self, **kwargs):
        super(Book, self).__init__(**kwargs)
        self.pdf = kwargs.get('pdf')
        self.los_l = LOS_Left(pos=(self.x,self.y),page_ref=self)
        self.add_widget(self.los_l)
        self.left_page = Page_Left(page_list=[PopplerPDFPage(pdf=self.pdf,pageno=0),PopplerPDFPage(pdf=self.pdf,pageno=0),PopplerPDFPage(pdf=self.pdf,pageno=0)],pos=(self.x,self.y),size=(self.pdf.page_width,self.pdf.page_height),LOS=self.los_l,pdf=self.pdf)
        self.add_widget(self.left_page)
        self.los_l.page = self.left_page

        self.los_r = LOS_Right(pos=(self.x+self.width,self.y),page_ref=self)
        self.add_widget(self.los_r)
        self.right_page = Page_Right(page_list=[PopplerPDFPage(pdf=self.pdf,pageno=1),PopplerPDFPage(pdf=self.pdf,pageno=2),PopplerPDFPage(pdf=self.pdf,pageno=3)],pos=(self.x+self.pdf.page_width,self.y),size=(self.pdf.page_width,self.pdf.page_height),LOS=self.los_r,pdf=self.pdf)
        self.add_widget(self.right_page)
        self.los_r.page = self.right_page

        self.left_page.other_side = self.right_page
        self.right_page.other_side = self.left_page

    def flip_left_page(self):
        self.left_page.flip()

    def flip_right_page(self):
        self.right_page.flip()

class MTBook(MTScatterWidget):
    def __init__(self, **kwargs):
        super(MTBook, self).__init__(**kwargs)
        pdf_filename = kwargs.get('pdf_filename')
        p = PopplerPDF(pdf_filename)
        self.size = (p.page_width*2+100,p.page_height+160)
        self.book = Book(pos=(50,110),size=(p.page_width*2,p.page_height),pdf=p)
        self.add_widget(self.book)
        toggy = MTToggler(pos=(self.width/2-100,25), size=(200,40))
        self.add_widget(toggy)

        @toggy.event
        def on_slide_right(*largs):
            self.book.flip_left_page()

        @toggy.event
        def on_slide_left(*largs):
            self.book.flip_right_page()

