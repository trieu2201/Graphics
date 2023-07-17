import OpenGL.GL as GL              # standard Python OpenGL wrapper
import glfw                         # lean windows system wrapper for OpenGL
import glm
import numpy as np                  # all matrix manipulations & OpenGL args
from itertools import cycle   # cyclic iterator to easily toggle polygon rendering modes
from libs.transform import Trackball
from tetra import *
from camera import *
# ------------  Viewer class & windows management ------------------------------
class Viewer:
    """ GLFW viewer windows, with classic initialization & graphics loop """
    def __init__(self, width=800, height=800):
        self.fill_modes = cycle([GL.GL_LINE, GL.GL_POINT, GL.GL_FILL])
        
        # version hints: create GL windows with >= OpenGL 3.3 and core profile
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, False)
        glfw.window_hint(glfw.DEPTH_BITS, 16)
        glfw.window_hint(glfw.DOUBLEBUFFER, True)
        self.win = glfw.create_window(width, height, 'Viewer', None, None)

        # make win's OpenGL context current; no OpenGL calls can happen before
        glfw.make_context_current(self.win)

        # initialize trackball
        self.camera = Camera()
        # self.trackball = Trackball()
        self.mouse = (0, 0)

        # register event handlers
        glfw.set_key_callback(self.win, self.on_key)
        glfw.set_cursor_pos_callback(self.win, self.on_mouse_move)
        glfw.set_scroll_callback(self.win, self.on_scroll)

        # useful message to check OpenGL renderer characteristics
        print('OpenGL', GL.glGetString(GL.GL_VERSION).decode() + ', GLSL',
              GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode() +
              ', Renderer', GL.glGetString(GL.GL_RENDERER).decode())

        # initialize GL by setting viewport and default render characteristics
        GL.glClearColor(0.5, 0.5, 0.5, 0.1)
        # GL.glEnable(GL.GL_CULL_FACE)   # enable backface culling (Exercise 1)
        # GL.glFrontFace(GL.GL_CCW) # GL_CCW: default

        GL.glEnable(GL.GL_DEPTH_TEST)  # enable depth test (Exercise 1)
        GL.glDepthFunc(GL.GL_LESS)   # GL_LESS: default

        # initially empty list of object to draw
        self.drawables = []
        self.transforms = []

    def run(self):
        """ Main render loop for this OpenGL windows """
        while not glfw.window_should_close(self.win):
            # clear draw buffer
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            w, h = glfw.get_window_size(self.win)
            ratio = w / h
            self.camera.set_projection(45.0, ratio, 0.1, 100.0)
            view = self.camera.get_view_matrix()
            projection = self.camera.get_projection()

            # draw our scene objects
            for i in range(0, len(self.drawables)):
                self.drawables[i].draw(projection, view, self.transforms[i])

            # flush render commands, and swap draw buffers
            glfw.swap_buffers(self.win)

            # Poll for and process events
            glfw.poll_events()

    def add(self, drawable, tf):
        """ add objects to draw in this windows """
        self.drawables.append(drawable)
        self.transforms.append(tf)

    def on_key(self, _win, key, _scancode, action, _mods):
        """ 'Q' or 'Escape' quits """
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
                glfw.set_window_should_close(self.win, True)

            if key == glfw.KEY_W:
                GL.glPolygonMode(GL.GL_FRONT_AND_BACK, next(self.fill_modes))

            for drawable in self.drawables:
                if hasattr(drawable, 'key_handler'):
                    drawable.key_handler(key)

    def on_mouse_move(self, win, xpos, ypos):
        """ Rotate on left-click & drag, pan on right-click & drag """
        old = self.mouse
        self.mouse = (xpos, glfw.get_window_size(win)[1] - ypos)
        if glfw.get_mouse_button(win, glfw.MOUSE_BUTTON_LEFT):
            # self.trackball.drag(old, self.mouse, glfw.get_window_size(win))
            offsetX = self.mouse[0] - old[0]
            offsetY = old[1] - self.mouse[1]

            self.camera.relative_drag(offsetX, offsetY)

    def on_scroll(self, win, _deltax, deltay):
        """ Scroll controls the camera distance to trackball center """
        # self.trackball.zoom(deltay, glfw.get_window_size(win)[1])
        self.camera.relative_zoom(deltay)



# -------------- main program and scene setup --------------------------------
def main():

    """ create windows, add shaders & scene objects, then run rendering loop """
    viewer = Viewer()
    # place instances of our basic objects

    model_gouraud = Tetra("./gouraud.vert", "./gouraud.frag").setup()
    gouraudPos = glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0))

    model_phong = Tetra("./phong.vert", "./phong.frag").setup()
    phongPos = glm.translate(glm.mat4(1.0), glm.vec3(-4.0, 0.0, 0.0))

    model_textured = Tetra("./phong.vert", "./phong.frag").setup(1)
    texturedPos = glm.translate(glm.mat4(1.0), glm.vec3(4.0, 0.0, 0.0))

    viewer.add(model_gouraud, gouraudPos)
    viewer.add(model_phong, phongPos)
    viewer.add(model_textured, texturedPos)

    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    glfw.init()                # initialize windows system glfw
    main()                     # main function keeps variables locally scoped
    glfw.terminate()           # destroy all glfw windows and GL contexts
