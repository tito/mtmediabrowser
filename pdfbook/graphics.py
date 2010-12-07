from __future__ import with_statement
from pymt import *
from OpenGL.GL import *
from pymt.texture import Texture, TextureRegion

def drawTR(texture, pos=(0,0), tex_coords=None):
    set_color(1, 1, 1)
    with gx_begin(GL_QUADS):
        glVertex2f(pos[0], pos[1])
        glVertex2f(pos[2], pos[3])
        glVertex2f(pos[4], pos[5])
        glVertex2f(pos[6], pos[7])
    set_color(1, 1, 1, blend=True)
    with gx_texture(texture):
        if type(texture) in (Texture, TextureRegion):
            texcoords = texture.tex_coords
        else:
            texcoords = (0.0,0.0, 1.0,0.0, 1.0,1.0, 0.0,1.0)
        if tex_coords:
            texcoords = tex_coords
        pos = ( pos[0], pos[1],
                pos[2], pos[3],
                pos[4], pos[5],
                pos[6], pos[7]
              )
        with gx_begin(GL_QUADS):
            glTexCoord2f(texcoords[0], texcoords[1])
            glVertex2f(pos[0], pos[1])
            glTexCoord2f(texcoords[2], texcoords[3])
            glVertex2f(pos[2], pos[3])
            glTexCoord2f(texcoords[4], texcoords[5])
            glVertex2f(pos[4], pos[5])
            glTexCoord2f(texcoords[6], texcoords[7])
            glVertex2f(pos[6], pos[7])

def drawTT(texture, pos=(0,0), tex_coords=None):
    set_color(1, 1, 1)
    with gx_begin(GL_TRIANGLES):
        glVertex2f(pos[0], pos[1])
        glVertex2f(pos[2], pos[3])
        glVertex2f(pos[4], pos[5])
    set_color(1, 1, 1, blend=True)
    with gx_texture(texture):
        if type(texture) in (Texture, TextureRegion):
            t = texture.tex_coords
            texcoords = (t[0], t[1], t[3], t[4], t[6])
        else:
            texcoords = (0.0,0.0, 1.0,0.0, 1.0,1.0)
        if tex_coords:
            texcoords = tex_coords
        pos = ( pos[0], pos[1], pos[2], pos[3], pos[4], pos[5])
        with gx_begin(GL_TRIANGLES):
            glTexCoord2f(texcoords[0], texcoords[1])
            glVertex2f(pos[0], pos[1])
            glTexCoord2f(texcoords[2], texcoords[3])
            glVertex2f(pos[2], pos[3])
            glTexCoord2f(texcoords[4], texcoords[5])
            glVertex2f(pos[4], pos[5])

