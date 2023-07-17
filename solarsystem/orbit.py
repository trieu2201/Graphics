import numpy as np

from solarsystem.libs.shader import Shader
from libs import transform as T
from solarsystem.libs.buffer import *
import ctypes
import glfw
import glm
from color import *


class Orbit(object):
    def __init__(self, model, orbit_x, orbit_y, color, segments):
        positions = []
        colors = []
        indices = []

        angle_step = 2.0 * np.pi / segments
        for i in range(segments):
            angle = i * angle_step
            positions.append([orbit_x(angle), orbit_y(angle), 0.0])
            colors.append(color)
        vertex_count = len(positions)
        for i in range(vertex_count):
            indices.append(i)
        indices.append(0)  # Append the first index to close the loop

        self.vertices = np.array(positions, dtype=np.float32)
        self.colors = np.array(colors, dtype=np.float32)
        self.indices = np.array(indices)
        self.indices_count = len(indices)
        self.vao = VAO()

        self.shader = Shader(model)
        self.uma = UManager(self.shader)

    def setup(self):
        self.vao.add_vbo(0, self.vertices, ncomponents=3, stride=0, offset=None)
        self.vao.add_vbo(2, self.colors, ncomponents=4, stride=0, offset=None)

        # setup EBO for drawing cylinder's side, bottom and top
        self.vao.add_ebo(self.indices)

        return self

    def draw(self, projection, view, model):
        GL.glUseProgram(self.shader.render_idx)
        nor_mat = glm.transpose(glm.inverse(view * model))

        self.uma.upload_uniform_matrix4fv(glm.value_ptr(projection), 'projection', False)
        self.uma.upload_uniform_matrix4fv(glm.value_ptr(view), 'view', False)
        self.uma.upload_uniform_matrix4fv(glm.value_ptr(model), 'model', False)
        self.uma.upload_uniform_matrix4fv(glm.value_ptr(nor_mat), 'normalMat', False)

        self.vao.activate()

        GL.glDrawElements(GL.GL_LINE_STRIP, self.indices_count, GL.GL_UNSIGNED_INT, None)

    def key_handler(self, key):

        if key == glfw.KEY_1:
            self.selected_texture = 1
        if key == glfw.KEY_2:
            self.selected_texture = 2

