import sys
import os
from ctypes import Structure, c_int32, c_int, c_char_p,\
                   create_string_buffer, memmove,\
                   c_void_p, POINTER, byref, c_double, cdll
from ctypes.util import find_library
from pymt import *

current_dir = os.path.dirname(__file__)

class PdfPopplerException(Exception):
    pass

class PdfBase(object):
    def __init__(self, filename):
        self._cache_texture = {}
        self._cache_image = {}
        self.filename = filename
        self.open()

    def __del__(self):
        self.close()

    def open(self):
        pass

    def close(self):
        pass

    def get_n_pages(self):
        return 0

    def get_page_size(self, index):
        return (0, 0)

    def render_page(self, index):
        pass

    def get_page_texture(self, index):
        if not index in self._cache_texture:
            self._cache_texture[index] = self.render_page(index)
        return self._cache_texture[index]

    def get_page_image(self, index):
        if not index in self._cache_image:
            texture = self.get_page_texture(index)
            self._cache_image[index] = Image(texture)
        return self._cache_image[index]

class PdfPoppler(PdfBase):

    l_poppler   = None
    l_cairo     = None
    l_gdk       = None

    def __init__(self, *largs, **kwargs):
        self._doc = None
        self._init_poppler()
        super(PdfPoppler, self).__init__(*largs, **kwargs)

    def _init_poppler(self):
        if self.l_poppler is not None:
            return

        if sys.platform in ('win32', 'cygwin'):
            filename = 'libpoppler-glib-4.dll'
            filename = os.path.join(current_dir, '..', filename)
            self.l_poppler = cdll.LoadLibrary(filename)
        else:
            filename = find_library('poppler-glib')
            if filename is None:
                raise PdfPopplerException('Unable to found poppler-glib library')
            self.l_poppler = cdll.LoadLibrary(filename)
        if self.l_poppler is None:
            raise PdfPopplerException('Unable to load poppler-glib library')

        p = self.l_poppler
        p.poppler_get_version.restype = c_char_p
        p.poppler_document_new_from_file.restype = c_void_p
        p.poppler_document_get_page.restype = c_void_p
        p.poppler_document_get_page.argtypes = [c_void_p, c_int]
        p.poppler_page_render.argtypes = [c_void_p, c_void_p]

        if sys.platform in ('win32', 'cygwin'):
            filename = 'libgobject-2.0-0.dll'
            filename = os.path.join(current_dir, '..', filename)
            self.l_gobject = cdll.LoadLibrary(filename)
        else:
            self.l_gobject = self.l_poppler

        self.l_gobject.g_type_init()

        backend = self.l_poppler.poppler_get_backend()

        print 'PdfPoppler: using version', self.l_poppler.poppler_get_version()
        print 'PdfPoppler: backend is', backend

        if backend == 2: # Cairo
            self._init_poppler_cairo()
        elif backend == 1: # GdkPixbuf
            self._init_poppler_gdk()
        else:
            raise PdfPopplerException('Unknown backend number %d' % backend)

    def _init_poppler_cairo(self):
        print 'PdfPoppler: use Cairo'
        c = self.l_cairo = self.l_poppler
        c.cairo_create.restype = c_void_p
        c.cairo_create.argtypes = [c_void_p]
        c.cairo_image_surface_create.restype = c_void_p
        c.cairo_image_surface_get_data.restype = c_void_p
        c.cairo_image_surface_get_data.argtypes = [c_void_p]
        c.cairo_status.argtypes = [c_void_p]
        c.cairo_surface_status.argtypes = [c_void_p]
        c.cairo_scale.argtypes = [c_void_p, c_double, c_double]
        c.cairo_destroy.argtypes = [c_void_p]


    def _init_poppler_gdk(self):
        print 'PdfPoppler: use GDK'
        if sys.platform in ('win32', 'cygwin'):
            filename = 'libgdk_pixbuf-2.0-0.dll'
            #filename = os.path.join(current_dir, filename)
            self.l_gdk = cdll.LoadLibrary(filename)
        else:
            self.l_gdk = self.l_poppler
        self.l_gdk.gdk_pixbuf_new.restype = c_void_p

    def open(self):
        class GError(Structure):
            _fields_ = [('domain', c_int32),
                        ('code', c_int),
                        ('message', c_char_p)]

        filename = 'file://'
        if sys.platform in ('win32', 'cygwin'):
            filename += '/'
        filename += self.filename

        error = POINTER(GError)()
        self.l_poppler.poppler_document_new_from_file.argtypes = [
            c_char_p, c_char_p, c_void_p]
        self._doc = self.l_poppler.poppler_document_new_from_file(
                c_char_p(filename), None, byref(error))
        if self._doc is None:
            raise PdfPopplerException(str(error.contents.message))

    def close(self):
        pass

    def get_n_pages(self):
        return int(self.l_poppler.poppler_document_get_n_pages(self._doc))

    def get_page_size(self, index):
        w = c_double(0)
        h = c_double(0)

        page = self.l_poppler.poppler_document_get_page(self._doc, index)
        assert( page is not None )

        self.l_poppler.poppler_page_get_size(page, byref(w), byref(h))
        return ( w.value, h.value )

    def render_page(self, index):
        w, h = map(int, self.get_page_size(index))
        zoom = 1
        w, h = map(lambda x: x * zoom, (w, h))

        page = self.l_poppler.poppler_document_get_page(self._doc, index)
        assert( page is not None )

        # use cairo ?
        if self.l_cairo is not None:

            # create a cairo surface
            # first argument 0 is ARGB32
            surface = self.l_cairo.cairo_image_surface_create(0, w, h)
            assert( surface is not None )

            # create cairo context
            context = self.l_cairo.cairo_create(surface)
            assert( context is not None )

            # apply zoom
            self.l_cairo.cairo_scale(context, c_double(zoom), c_double(zoom))

            # render to cairo
            self.l_poppler.poppler_page_render(page, context)

            # dump cairo to texture
            data = self.l_cairo.cairo_image_surface_get_data(surface)
            size = int(4 * w * h)
            buffer = create_string_buffer(size)
            memmove(buffer, data, size)

            # release cairo
            self.l_cairo.cairo_surface_destroy(surface)
            self.l_cairo.cairo_destroy(context)

        # use gdk ?
        else:

            # 1: GDK_COLORSPACE_RGB (0)
            # 2: has_alpha (1)
            # 3: bit per samples
            self.l_gdk.gdk_pixbuf_new.restype = c_void_p
            surface = self.l_gdk.gdk_pixbuf_new(0, 1, 8, w, h)

            assert( surface is not None )

            # render to pixbuf (fix 6 arg)
            self.l_poppler.poppler_page_render_to_pixbuf.argtypes = [
                    c_void_p, c_int, c_int, c_int, c_int, c_double, c_int, c_void_p]
            self.l_poppler.poppler_page_render_to_pixbuf(page, 0, 0,
                    w, h, zoom, 0, surface)

            # get data
            class GdkPixdata(Structure):
                _fields_ = [('magic', c_int),
                        ('length', c_int),
                        ('pixdata_type', c_int),
                        ('rowstride', c_int),
                        ('width', c_int),
                        ('height', c_int),
                        ('pixel_data', c_void_p)]

            pixdata = (GdkPixdata)()

            # get a pixdata
            self.l_gdk.gdk_pixdata_from_pixbuf.argtypes = [
                    c_void_p, c_void_p, c_int]
            self.l_gdk.gdk_pixdata_from_pixbuf(byref(pixdata), surface, 0)

            # convert to buffer
            size = int(4 * w * h)
            buffer = create_string_buffer(size)
            memmove(buffer, pixdata.pixel_data, size)

            # unref
            self.l_gobject.g_object_unref(surface)

        # use pymt

        # picking only RGB
        texture = Texture.create(w, h)#, mipmap=True)
        texture.blit_buffer(buffer, mode='RGBA')
        texture.flip_vertical()

        return texture

Pdf = PdfPoppler

if __name__ == '__main__':
    import os
    curdir = os.path.dirname(__file__)
    if curdir == '':
        curdir = os.getcwd()
    filename = os.path.join(curdir, 'pdfs', 'NUIPaint.pdf')
    pdf = Pdf(filename)
    image = pdf.get_page_image(0)
    runTouchApp(MTScatterContainer(image))
