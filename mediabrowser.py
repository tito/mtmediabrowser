from random import random
from os.path import dirname, join, exists, basename
from os import listdir
from collections import deque
from ConfigParser import ConfigParser
from pymt import *

current_directory = dirname(__file__)

class MediaVideo(MTSimpleVideo):
    def __init__(self, filename, **kwargs):
        super(MediaVideo, self).__init__(filename, **kwargs)
        self.size = (300, 300)
        self.opacity = 1.
        self.filename = basename(filename)
        self.firsttime = True
        self.player.play()

    def on_update(self):
        if self.player._videosink and self.firsttime:
            with self.player._buffer_lock:
                if self.player._buffer is not None:
                    self.firsttime = False
                    self.player.stop()
        super(MediaVideo, self).on_update()

    def on_draw(self):
        super(MediaVideo, self).on_draw()
        if self.player.state != 'playing' or self.firsttime:
            set_color(0, 0, 0)
            drawRectangle(size=self.size)
            set_color(1, 1, 1)
            drawLabel(label=self.filename, pos=self.center, font_size=24)


class MediaBrowser(MTBoxLayout):
    def __init__(self, **kwargs):
        super(MediaBrowser, self).__init__(**kwargs)
        self.extensions = {
            'pictures': ('jpg', 'jpeg', 'tga', 'png', 'gif', 'bmp'),
            'movies': ('avi', 'mpg', 'mpeg', 'mkv', 'flv', 'mov'),
            'others': ('pdf', )
        }
        self.objects = []
        self.root = getWindow()
        self.read_configuration()
        self.create_ui()
        self.create_deque()

    def read_configuration(self):
        self.config = config = ConfigParser()
        config.add_section('images')
        config.set('images', 'background', 'images/background.jpg')
        config.set('images', 'icon_book', 'images/btn_book.png')
        config.set('images', 'icon_movie', 'images/btn_movie.png')
        config.set('images', 'icon_picture', 'images/btn_pictures.png')
        config.set('images', 'icon_clear', 'images/btn_shuffle.png')
        config.add_section('directories')
        config.set('directories', 'movies', '')
        config.set('directories', 'pictures', '')
        config.set('directories', 'others', '')

        filename = join(current_directory, 'config.ini')
        if not exists(filename):
            with open(filename, 'w') as fd:
                config.write(fd)
        else:
            config.read(join(current_directory, 'config.ini'))

    def create_ui(self):
        # create the buttons
        config = self.config
        self.layout = layout = MTBoxLayout(orientation='vertical',
                                           size_hint=(None, None))
        for name in ('book', 'movie', 'picture', 'clear'):
            button = MTImageButton(filename=config.get('images', 'icon_%s' % name))
            button.connect('on_press', curry(
                getattr(self, 'on_%s_press' % name), button))
            button.connect('on_release', curry(
                getattr(self, 'on_%s_release' % name), button))
            layout.add_widget(button)
        anchor = MTAnchorLayout(size_hint=(None, 1))
        anchor.add_widget(layout)
        self.add_widget(anchor)

        # create background
        self.style['bg-image'] = Image(config.get('images', 'background'))

    def create_deque(self):
        self.queue = deque()
        getClock().schedule_interval(self.pop_queue, .1)


    #
    # Internals
    #

    def pop_queue(self, *largs):
        try:
            center, filename = self.queue.pop()
        except IndexError:
            return
        self.load_filename(center, filename)

    def load_filename(self, center, filename):
        ext = filename.split('.')[-1].lower()
        if ext in self.extensions['pictures']:
            image = Loader.image(filename)
            m = MTScatterImage(image=image)
        elif ext in self.extensions['movies']:
            video = MediaVideo(filename=filename)
            m = MTScatter()
            m.add_widget(video)
            video.connect('on_resize', m, 'size')
        elif ext in self.extensions['others']:
            pass
        else:
            print 'Ignore <%s>' % filename

        m.scale = .01
        m.pos = center
        radius = 400
        cx, cy = getWindow().center
        rpos = cx + random() * radius * 2 - radius, cy + random() * radius * 2 - radius
        rotation = random() * 360
        m.do(Animation(scale=.2, center=rpos, rotation=rotation, f='ease_out_cubic'))
        self.root.add_widget(m)
        self.objects.append(m)

    def error(self, message):
        self.root.add_widget(MTModalPopup(
            size=(300, 300),
            title='Error',
            content=message
        ))


    #
    # Actions
    #

    def clear(self):
        def on_complete(widget):
            self.root.remove_widget(widget)
        for obj in self.objects:
            if isinstance(obj, MTScatterImage):
                anim = Delay(duration=random() / 2.) + Animation(opacity=0.)
            else:
                anim = Delay(duration=random() / 2.) + Animation(scale=0.01)
            anim.connect('on_complete', on_complete)
            obj.do(anim)
        del self.objects[:]

    def load_directory(self, center, filtertype, path):
        if not path:
            return self.error(
                'You must configure the directory for this icon. '
                'Please edit the config.ini file in the mediabrowser '
                'directory'
            )
        try:
            filenames = listdir(path)
        except OSError, e:
            self.error(str(e))
            return

        extensions = self.extensions[filtertype]
        for filename in filenames:
            ext = filename.split('.')[-1].lower()
            if not ext in extensions:
                continue
            self.queue.appendleft((center, join(path, filename)))


    #
    # Buttons handlers
    #

    def on_book_press(self, button, *largs):
        pass

    def on_book_release(self, button, *largs):
        self.clear()
        self.load_directory(button.center, 'others', self.config.get('directories', 'others'))

    def on_movie_press(self, button, *largs):
        pass

    def on_movie_release(self, button, *largs):
        self.clear()
        self.load_directory(button.center, 'movies', self.config.get('directories', 'movies'))

    def on_picture_press(self, button, *largs):
        pass

    def on_picture_release(self, button, *largs):
        self.clear()
        self.load_directory(button.center, 'pictures', self.config.get('directories', 'pictures'))

    def on_clear_press(self, button, *largs):
        pass

    def on_clear_release(self, button, *largs):
        self.clear()

if __name__ == '__main__':
    runTouchApp(MediaBrowser())
