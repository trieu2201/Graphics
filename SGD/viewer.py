import OpenGL.GL as GL              # standard Python OpenGL wrapper
import glfw                         # lean windows system wrapper for OpenGL
import numpy as np                  # all matrix manipulations & OpenGL args
import glm
from itertools import cycle   # cyclic iterator to easily toggle polygon rendering modes
from libs.transform import Trackball
from mesh import *
from sphere import *
from DescentIterator import *
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
        #GL.glEnable(GL.GL_CULL_FACE)   # enable backface culling (Exercise 1)
        #GL.glFrontFace(GL.GL_CCW) # GL_CCW: default

        GL.glEnable(GL.GL_DEPTH_TEST)  # enable depth test (Exercise 1)
        GL.glDepthFunc(GL.GL_LESS)   # GL_LESS: default


        # initially empty list of object to draw
        self.drawables = []
        self.transforms = []
        
        self.sgd = DescentIterator(gradientX, gradientY, 0.08)

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
            # view = self.trackball.view_matrix()
            # projection = self.trackball.projection_matrix(win_size)

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

            if key == glfw.KEY_R:
                self.sgd.random_state(8.0, 8.0)
                x, y = self.sgd.get_state()
                global ballAngle
                ballAngle = 0.0
                trans = get_ball_transform(x, y, ballRadius, 0.0, objective, gradientX, gradientY)
                self.transforms[1] = trans

            if key == glfw.KEY_SPACE:
                prevX, prevY = self.sgd.get_state()
                self.sgd.iterate()
                x,y =self.sgd.get_state()
                distance = glm.distance(glm.vec2(prevX, prevY), glm.vec2(x, y))
                trans = get_ball_transform(x, y, ballRadius, distance, objective, gradientX, gradientY)
                self.transforms[1] = trans

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
        # if glfw.get_mouse_button(win, glfw.MOUSE_BUTTON_RIGHT):
            # self.trackball.pan(old, self.mouse)

    def on_scroll(self, win, _deltax, deltay):
        """ Scroll controls the camera distance to trackball center """
        # self.trackball.zoom(deltay, glfw.get_window_size(win)[1])
        self.camera.relative_zoom(deltay)

# The objective function
def objective(x, y):
    return (x*x + y*y) / 40.0 + 2.0 * np.exp(-(np.cos(x / 2.0) + y * y / 4.0)) - np.cos(x / 1.5) - np.sin(y / 1.5)

# Gradient with respect to x
def gradientX(x, y):
    return (x / 20.0) + np.exp(-(np.cos(x / 2.0) + y * y / 4.0)) * np.sin(x / 2.0) + (np.sin(x / 1.5) / 1.5)

# Gradient with respect to y
def gradientY(x, y):
    return (y / 20.0) - np.exp(-(np.cos(x / 2.0) + y * y / 4.0)) * y - (np.cos(y / 1.5) / 1.5)

ballAngle = 0.0
ballRadius = 0.4

def get_ball_transform(x, y, ball_radius, distance, objective, gradient_x, gradient_y):
    global ballAngle
    z = objective(x, y)
    # Get the normal vector at this position
    dirX = gradient_x(x, y)
    dirY = gradient_y(x, y)
    norm = -glm.normalize(glm.vec3(dirX, dirY, -1.0))
    # Finally, translate the ball in the normal direction so that the ball will barely touch the mesh.
    trans = glm.translate(glm.mat4(1.0), norm * ball_radius)
    # Then, we translated the ball to the new position.
    trans = glm.translate(trans, glm.vec3(x, y, z))
    # Then, we rotate the ball according to the distance, updating the global angle (for the time being).
    ballAngle = ballAngle +(distance / ball_radius)
    rollDirection = glm.normalize(glm.vec3(-dirX, -dirY, 0.0))
    rotationAxis = glm.cross(glm.vec3(0.0, 0.0, 1.0), rollDirection)
    quaternion = glm.angleAxis(ballAngle, rotationAxis)
    rotationMat = glm.mat4_cast(quaternion)
    trans = trans * rotationMat
    # We first scale the ball uniformly to its radius.
    trans = glm.scale(trans, glm.vec3(ball_radius, ball_radius, ball_radius))
    return trans



# -------------- main program and scene setup --------------------------------
def main():

    """ create windows, add shaders & scene objects, then run rendering loop """
    viewer = Viewer()
    # place instances of our basic objects
    func = lambda x, y : np.sin(x) + np.cos(y)
    model = mesh("./phong.vert", "./phong.frag", objective).setup()
    ball = Sphere("./phong.vert", "./phong.frag").setup()



    viewer.add(model, glm.mat4(1.0))
    trans = get_ball_transform(0.0, 0.0, ballRadius, 0.0, objective, gradientX, gradientY)
    viewer.add(ball, trans)

    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    glfw.init()                # initialize windows system glfw
    main()                     # main function keeps variables locally scoped
    glfw.terminate()           # destroy all glfw windows and GL contexts
