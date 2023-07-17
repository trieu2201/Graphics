import OpenGL.GL as GL              # standard Python OpenGL wrapper
import glfw                         # lean windows system wrapper for OpenGL
from itertools import cycle   # cyclic iterator to easily toggle polygon rendering modes

import glm

from camera import *
from planet import *
from solarsystem.sphere import *
from solarsystem.solar import *
from solarsystem.orbit import *

# ------------  Viewer class & windows management ------------------------------

camera = Camera()


def frame_buffer_callback(window, w, h):
    ratio = w / h
    camera.set_projection(45.0, ratio, 0.1, 8000.0)


class Viewer:
    """ GLFW viewer windows, with classic initialization & graphics loop """
    def __init__(self, width=800, height=800):
        self.fill_modes = cycle([GL.GL_LINE, GL.GL_POINT, GL.GL_FILL])
        
        # version hints: create GL windows with >= OpenGL 3.3 and core profile
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        # glfw.window_hint(glfw.RESIZABLE, False)
        glfw.window_hint(glfw.DEPTH_BITS, 16)
        glfw.window_hint(glfw.DOUBLEBUFFER, True)
        self.win = glfw.create_window(width, height, 'Viewer', None, None)

        # make win's OpenGL context current; no OpenGL calls can happen before
        glfw.make_context_current(self.win)
        self.mouse = (0, 0)

        glfw.set_framebuffer_size_callback(self.win, frame_buffer_callback)

        # register event handlers
        glfw.set_key_callback(self.win, self.on_key)
        glfw.set_cursor_pos_callback(self.win, self.on_mouse_move)
        glfw.set_scroll_callback(self.win, self.on_scroll)

        # useful message to check OpenGL renderer characteristics
        print('OpenGL', GL.glGetString(GL.GL_VERSION).decode() + ', GLSL',
              GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode() +
              ', Renderer', GL.glGetString(GL.GL_RENDERER).decode())

        # initialize GL by setting viewport and default render characteristics
        GL.glClearColor(0.02, 0.04, 0.06, 0.1)
        # GL.glClearColor(0.5, 0.5, 0.5, 0.5)
        # GL.glEnable(GL.GL_CULL_FACE)   # enable backface culling (Exercise 1)
        # GL.glFrontFace(GL.GL_CCW) # GL_CCW: default

        GL.glEnable(GL.GL_DEPTH_TEST)  # enable depth test (Exercise 1)
        GL.glDepthFunc(GL.GL_LESS)   # GL_LESS: default

        w, h = glfw.get_window_size(self.win)
        frame_buffer_callback(self.win, w, h)

        # initially empty list of object to draw
        self.drawables = []
        self.transforms = []

        self.delta_time = 0.0
        self.last_frame = 0.0

    def run(self, on_frame):
        """ Main render loop for this OpenGL windows """
        while not glfw.window_should_close(self.win):
            # clear draw buffer
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            w, h = glfw.get_window_size(self.win)
            GL.glViewport(0, 0, w, h)

            view = camera.get_view_matrix()
            projection = camera.get_projection()

            current_frame = glfw.get_time()
            self.delta_time = current_frame - self.last_frame
            self.last_frame = current_frame
            on_frame(self.delta_time, self)

            # draw our scene objects
            for i in range(0, len(self.drawables)):
                self.drawables[i].draw(projection, view, self.transforms[i])

            # flush render commands, and swap draw buffers
            glfw.swap_buffers(self.win)

            # Poll for and process events
            glfw.poll_events()

    def add(self, drawable, tf=glm.mat4(1.0)):
        """ add objects to draw in this windows """
        entity = len(self.drawables)
        self.drawables.append(drawable)
        self.transforms.append(tf)

        return entity

    def set_transform(self, entity, tf):
        self.transforms[entity] = tf

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

            camera.relative_drag(offsetX, offsetY)

    def on_scroll(self, win, _deltax, deltay):
        """ Scroll controls the camera distance to trackball center """
        # self.trackball.zoom(deltay, glfw.get_window_size(win)[1])
        camera.relative_zoom(deltay)

# -------------- main program and scene setup --------------------------------


# MERCURY
def mercury_x(angle):
    return MERCURY_SEMI_MAJOR * glm.cos(angle)


def mercury_y(angle):
    return MERCURY_SEMI_MINOR * glm.sin(angle)


mercury_orientation = glm.vec3(-0.1219, 0.0, 0.9925)
mercury_entity = 0
mercury_revolve_angle = 0.0
mercury_rotate_angle = 0.0


# VENUS
def venus_x(angle):
    return VENUS_SEMI_MAJOR * glm.cos(angle)


def venus_y(angle):
    return VENUS_SEMI_MINOR * glm.sin(angle)


venus_orientation = glm.vec3(-0.0592, 0.0, 0.9982)
venus_entity = 0
venus_revolve_angle = 0.0
venus_rotate_angle = 0.0


# EARTH - earth
def earth_x(angle):
    return EARTH_SEMI_MAJOR * glm.cos(angle)


def earth_y(angle):
    return EARTH_SEMI_MINOR * glm.sin(angle)


earth_entity = 0
earth_revolve_angle = 0.0
earth_rotate_angle = 0.0


# MARS - mars
def mars_x(angle):
    return MARS_SEMI_MAJOR * glm.cos(angle)


def mars_y(angle):
    return MARS_SEMI_MINOR * glm.sin(angle)


mars_orientation = glm.vec3(-0.0323, 0.0, 0.9995)
mars_entity = 0
mars_revolve_angle = 0.0
mars_rotate_angle = 0.0


# JUPITER - jupiter
def jupiter_x(angle):
    return JUPITER_SEMI_MAJOR * glm.cos(angle)


def jupiter_y(angle):
    return JUPITER_SEMI_MINOR * glm.sin(angle)


jupiter_orientation = glm.vec3(-0.0228, 0.0, 0.9997)
jupiter_entity = 0
jupiter_revolve_angle = 0.0
jupiter_rotate_angle = 0.0


# SATURN - saturn
def saturn_x(angle):
    return SATURN_SEMI_MAJOR * glm.cos(angle)


def saturn_y(angle):
    return SATURN_SEMI_MINOR * glm.sin(angle)


saturn_orientation = glm.vec3(-0.0433, 0.0, 0.9991)
saturn_entity = 0
saturn_revolve_angle = 0.0
saturn_rotate_angle = 0.0


# URANUS - uranus
def uranus_x(angle):
    return URANUS_SEMI_MAJOR * glm.cos(angle)


def uranus_y(angle):
    return URANUS_SEMI_MINOR * glm.sin(angle)


uranus_orientation = glm.vec3(-0.0138, 0.0, 0.9999)
uranus_entity = 0
uranus_revolve_angle = 0.0
uranus_rotate_angle = 0.0


# NEPTUNE - neptune
def neptune_x(angle):
    return NEPTUNE_SEMI_MAJOR * glm.cos(angle)


def neptune_y(angle):
    return NEPTUNE_SEMI_MINOR * glm.sin(angle)


neptune_orientation = glm.vec3(-0.0309, 0.0, 0.9995)
neptune_entity = 0
neptune_revolve_angle = 0.0
neptune_rotate_angle = 0.0


# MOON
def moon_x(angle):
    return MOON_SEMI_MAJOR * glm.cos(angle)


def moon_y(angle):
    return MOON_SEMI_MINOR * glm.sin(angle)


moon_orientation = glm.vec3(0.0872, 0.0, 0.9962)
moon_center = glm.vec3(earth_x(earth_revolve_angle), earth_y(earth_rotate_angle), 0.0)
moon_entity = 0
moon_revolve_angle = 0.0
moon_rotate_angle = 0.0


def main():
    """ create windows, add shaders & scene objects, then run rendering loop """
    viewer = Viewer()
    # place instances of our basic objects
    sun = Sphere(0).setup(unlit="../textures/sun_diffuse_2k-1.jpg")
    sun_tf = glm.scale(glm.mat4(1.0), glm.vec3(SUN_RADIUS, SUN_RADIUS, SUN_RADIUS))

    mercury = Sphere(1).setup(diffuse="../textures/mercury_diffuse_2k.jpg")
    mercury_orbit = Orbit(0, mercury_x, mercury_y, [0.65490, 0.64314, 0.62353, 1.0], 200).setup()
    mercury_orbit_tf = get_orbit_transform(mercury_orientation)

    venus = Sphere(1).setup(diffuse="../textures/venus_diffuse_2k.jpg")
    venus_orbit = Orbit(0, venus_x, venus_y, [0.64314, 0.52549, 0.34902, 1.0], 300).setup()
    venus_orbit_tf = get_orbit_transform(venus_orientation)

    earth = Sphere(1).setup(diffuse="../textures/8k_earth_daymap.jpg")
    earth_orbit = Orbit(0, earth_x, earth_y, [0.21961, 0.46275, 0.47059, 1.0], 400).setup()

    moon = Sphere(1).setup(diffuse="../textures/8k_moon.jpg")

    mars = Sphere(1).setup(diffuse="../textures/mars_diffuse_2k.jpg")
    mars_orbit = Orbit(0, mars_x, mars_y, [0.64314, 0.52549, 0.34902, 1.0], 300).setup()
    mars_orbit_tf = get_orbit_transform(mars_orientation)

    jupiter = Sphere(1).setup(diffuse="../textures/jupiter_diffuse_2k.jpg")
    jupiter_orbit = Orbit(0, jupiter_x, jupiter_y, [0.72157, 0.64706, 0.55294, 1.0], 600).setup()
    jupiter_orbit_tf = get_orbit_transform(jupiter_orientation)

    saturn = Sphere(1).setup(diffuse="../textures/saturn_diffuse_2k.jpg")
    saturn_orbit = Orbit(0, saturn_x, saturn_y, [0.73725, 0.76078, 0.62353, 1.0], 700).setup()
    saturn_orbit_tf = get_orbit_transform(saturn_orientation)

    uranus = Sphere(1).setup(diffuse="../textures/uranus_diffuse_2k.jpg")
    uranus_orbit = Orbit(0, uranus_x, uranus_y, [0.60784, 0.78039, 0.76471, 1.0], 800).setup()
    uranus_orbit_tf = get_orbit_transform(uranus_orientation)

    neptune = Sphere(1).setup(diffuse="../textures/neptune_diffuse_2k.jpg")
    neptune_orbit = Orbit(0, neptune_x, neptune_y, [0.02745, 0.21569, 0.46275, 1.0], 900).setup()
    neptune_orbit_tf = get_orbit_transform(neptune_orientation)

    viewer.add(sun, sun_tf)

    global mercury_entity
    mercury_entity = viewer.add(mercury)
    viewer.add(mercury_orbit, mercury_orbit_tf)

    global venus_entity
    venus_entity = viewer.add(venus)
    viewer.add(venus_orbit, venus_orbit_tf)

    global earth_entity
    earth_entity = viewer.add(earth)
    viewer.add(earth_orbit)

    global moon_entity
    moon_entity = viewer.add(moon)

    global mars_entity
    mars_entity = viewer.add(mars)
    viewer.add(mars_orbit, mars_orbit_tf)

    global jupiter_entity
    jupiter_entity = viewer.add(jupiter)
    viewer.add(jupiter_orbit, jupiter_orbit_tf)

    global saturn_entity
    saturn_entity = viewer.add(saturn)
    viewer.add(saturn_orbit, saturn_orbit_tf)

    global uranus_entity
    uranus_entity = viewer.add(uranus)
    viewer.add(uranus_orbit, uranus_orbit_tf)

    global neptune_entity
    neptune_entity = viewer.add(neptune)
    viewer.add(neptune_orbit, neptune_orbit_tf)

    # start rendering loop
    viewer.run(callback)


def get_delta_angle(speed, delta_time):
    return speed * delta_time


def callback(delta_time, viewer: Viewer):
    # MERCURY
    global mercury_revolve_angle
    global mercury_rotate_angle
    mercury_tf = get_planet_transform(mercury_revolve_angle, mercury_rotate_angle, glm.radians(MERCURY_TILTING),
                                      MERCURY_RADIUS, mercury_x, mercury_y, mercury_orientation)
    viewer.set_transform(mercury_entity, mercury_tf)
    mercury_revolve_angle = mercury_revolve_angle + get_delta_angle(MERCURY_REVOLVING_SPEED, delta_time)
    mercury_rotate_angle = mercury_rotate_angle + get_delta_angle(MERCURY_ROTATING_SPEED, delta_time)

    # VENUS - venus
    global venus_revolve_angle
    global venus_rotate_angle
    venus_tf = get_planet_transform(venus_revolve_angle, venus_rotate_angle, glm.radians(VENUS_TILTING), VENUS_RADIUS,
                                    venus_x, venus_y, venus_orientation)
    viewer.set_transform(venus_entity, venus_tf)
    venus_revolve_angle = venus_revolve_angle + get_delta_angle(VENUS_REVOLVING_SPEED, delta_time)
    venus_rotate_angle = venus_rotate_angle + get_delta_angle(VENUS_ROTATING_SPEED, delta_time)

    # EARTH - earth
    global earth_revolve_angle
    global earth_rotate_angle
    earth_tf = get_planet_transform(earth_revolve_angle, earth_rotate_angle, glm.radians(EARTH_TILTING),
                                    EARTH_RADIUS, earth_x, earth_y)
    viewer.set_transform(earth_entity, earth_tf)
    earth_revolve_angle = earth_revolve_angle + get_delta_angle(EARTH_REVOLVING_SPEED, delta_time)
    earth_rotate_angle = earth_rotate_angle + get_delta_angle(EARTH_ROTATING_SPEED, delta_time)

    # MOON
    global moon_revolve_angle
    global moon_rotate_angle
    global moon_center
    moon_center = glm.vec3(earth_x(earth_revolve_angle), earth_y(earth_revolve_angle), 0.0)
    moon_tf = get_planet_transform(moon_revolve_angle, moon_rotate_angle, glm.radians(MOON_TILTING),
                                   MOON_RADIUS, moon_x, moon_y, moon_orientation, moon_center)
    viewer.set_transform(moon_entity, moon_tf)
    moon_revolve_angle = moon_revolve_angle + get_delta_angle(MOON_REVOLVING_SPEED, delta_time)
    moon_rotate_angle = moon_rotate_angle + get_delta_angle(MOON_ROTATING_SPEED, delta_time)

    # MARS - mars
    global mars_revolve_angle
    global mars_rotate_angle
    mars_tf = get_planet_transform(mars_revolve_angle, mars_rotate_angle, glm.radians(MARS_TILTING),
                                   MARS_RADIUS, mars_x, mars_y, mars_orientation)
    viewer.set_transform(mars_entity, mars_tf)
    mars_revolve_angle = mars_revolve_angle + get_delta_angle(MARS_REVOLVING_SPEED, delta_time)
    mars_rotate_angle = mars_rotate_angle + get_delta_angle(MARS_ROTATING_SPEED, delta_time)

    # JUPITER - jupiter
    global jupiter_revolve_angle
    global jupiter_rotate_angle
    jupiter_tf = get_planet_transform(jupiter_revolve_angle, jupiter_rotate_angle, glm.radians(JUPITER_TILTING),
                                      JUPITER_RADIUS, jupiter_x, jupiter_y, mars_orientation)
    viewer.set_transform(jupiter_entity, jupiter_tf)
    jupiter_revolve_angle = jupiter_revolve_angle + get_delta_angle(JUPITER_REVOLVING_SPEED, delta_time)
    jupiter_rotate_angle = jupiter_rotate_angle + get_delta_angle(JUPITER_ROTATING_SPEED, delta_time)

    # SATURN - saturn
    global saturn_revolve_angle
    global saturn_rotate_angle
    saturn_tf = get_planet_transform(saturn_revolve_angle, saturn_rotate_angle, glm.radians(SATURN_TILTING),
                                     SATURN_RADIUS, saturn_x, saturn_y, saturn_orientation)
    viewer.set_transform(saturn_entity, saturn_tf)
    saturn_revolve_angle = saturn_revolve_angle + get_delta_angle(SATURN_REVOLVING_SPEED, delta_time)
    saturn_rotate_angle = saturn_rotate_angle + get_delta_angle(SATURN_ROTATING_SPEED, delta_time)

    # URANUS - uranus
    global uranus_revolve_angle
    global uranus_rotate_angle
    uranus_tf = get_planet_transform(uranus_revolve_angle, uranus_rotate_angle, glm.radians(URANUS_TILTING),
                                     URANUS_RADIUS, uranus_x, uranus_y, uranus_orientation)
    viewer.set_transform(uranus_entity, uranus_tf)
    uranus_revolve_angle = uranus_revolve_angle + get_delta_angle(URANUS_REVOLVING_SPEED, delta_time)
    uranus_rotate_angle = uranus_rotate_angle + get_delta_angle(URANUS_ROTATING_SPEED, delta_time)

    # NEPTUNE - neptune
    global neptune_revolve_angle
    global neptune_rotate_angle
    neptune_tf = get_planet_transform(neptune_revolve_angle, neptune_rotate_angle, glm.radians(NEPTUNE_TILTING),
                                      NEPTUNE_RADIUS, neptune_x, neptune_y, neptune_orientation)
    viewer.set_transform(neptune_entity, neptune_tf)
    neptune_revolve_angle = neptune_revolve_angle + get_delta_angle(NEPTUNE_REVOLVING_SPEED, delta_time)
    neptune_rotate_angle = neptune_rotate_angle + get_delta_angle(NEPTUNE_ROTATING_SPEED, delta_time)


if __name__ == '__main__':
    glfw.init()                # initialize windows system glfw
    main()                     # main function keeps variables locally scoped
    glfw.terminate()           # destroy all glfw windows and GL contexts
