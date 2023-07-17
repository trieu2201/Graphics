import OpenGL.GL as GL              # standard Python OpenGL wrapper
import numpy as np
import pandas as pd

from libs.shader import *
from libs import transform as T
from libs.buffer import *
import ctypes




class Patch(object):
    def __init__(self, vert_shader1, frag_shader1, vert_shader2, frag_shader2,):
        """
        self.vertex_attrib:
        each row: v.x, v.y, v.z, c.r, c.g, c.b, n.x, n.y, n.z
        =>  (a) stride = nbytes(v0.x -> v1.x) = 9*4 = 36
            (b) offset(vertex) = ctypes.c_void_p(0); can use "None"
                offset(color) = ctypes.c_void_p(3*4)
                offset(normal) = ctypes.c_void_p(6*4)
        """
        vertex_color = np.array([
            [0,  0,  0,   0.0, 0.0, 0.0],  # A
            [0,  1,  0,   1.0, 0.0, 0.0],  # B
            [1,  0,  0,   0.0, 1.0, 0.0],  # C
            [1,  1,  0,   0.0, 0.0, 1.0],  # D
            [2,  0,  0,   1.0, 0.0, 0.0],  # E
            [2,  1,  0,   1.0, 1.0, 1.0]   # F
        ], dtype=np.float32)

        # random normals (facing +z)
        normals = np.random.normal(0, 5, (vertex_color.shape[0], 3)).astype(np.float32)
        normals[:, 2] = np.abs(normals[:, 2])  # (facing +z)
        normals = normals / np.linalg.norm(normals, axis=1, keepdims=True)
        self.vertex_attrib = np.concatenate([vertex_color, normals], axis=1)

        # indices
        self.indices = np.arange(self.vertex_attrib.shape[0]).astype(np.int32)

        self.vao = VAO()

        self.shader1 = Shader(vert_shader1, frag_shader1)
        self.shader2 = Shader(vert_shader2, frag_shader2)
        self.uma1 = UManager(self.shader1)
        self.uma2 = UManager(self.shader2)
        #

    def setup(self):
        stride = 9*4
        offset_v = ctypes.c_void_p(0)  # None
        offset_c = ctypes.c_void_p(3*4)
        offset_n = ctypes.c_void_p(6*4)
        self.vao.add_vbo(0, self.vertex_attrib, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=stride, offset=offset_v)
        self.vao.add_vbo(1, self.vertex_attrib, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=stride, offset=offset_c)
        self.vao.add_vbo(2, self.vertex_attrib, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=stride, offset=offset_n)
        self.vao.add_ebo(self.indices)


        normalMat = np.identity(4, 'f')
        projection = T.ortho(-0.5, 2.5, -0.5, 1.5, -1, 1)
        modelview = np.identity(4, 'f')

        # Light
        I_light = np.array([
            [0.9, 0.4, 0.6],  # diffuse
            [0.9, 0.4, 0.6],  # specular
            [0.9, 0.4, 0.6]  # ambient
        ], dtype=np.float32)
        light_pos = np.array([0, 0.5, 0.9], dtype=np.float32)

        # Materials
        K_materials = np.array([
            [0.6, 0.4, 0.7],  # diffuse
            [0.6, 0.4, 0.7],  # specular
            [0.6, 0.4, 0.7]  # ambient
        ], dtype=np.float32)

        shininess = 100.0
        mode = 1

        GL.glUseProgram(self.shader1.render_idx)
        self.uma1.upload_uniform_matrix4fv(normalMat, 'normalMat', True)
        self.uma1.upload_uniform_matrix4fv(projection, 'projection', True)
        self.uma1.upload_uniform_matrix4fv(modelview, 'modelview', True)

        self.uma1.upload_uniform_matrix3fv(I_light, 'I_light', False)
        self.uma1.upload_uniform_vector3fv(light_pos, 'light_pos')

        self.uma1.upload_uniform_matrix3fv(K_materials, 'K_materials', False)
        self.uma1.upload_uniform_scalar1f(shininess, 'shininess')
        self.uma1.upload_uniform_scalar1i(mode, 'mode')


        ####
        GL.glUseProgram(self.shader2.render_idx)
        self.uma2.upload_uniform_matrix4fv(normalMat, 'normalMat', True)
        self.uma2.upload_uniform_matrix4fv(projection, 'projection', True)
        self.uma2.upload_uniform_matrix4fv(modelview, 'modelview', True)

        self.uma2.upload_uniform_matrix3fv(I_light, 'I_light', False)
        self.uma2.upload_uniform_vector3fv(light_pos, 'light_pos')

        self.uma2.upload_uniform_matrix3fv(K_materials, 'K_materials', False)
        self.uma2.upload_uniform_scalar1f(shininess, 'shininess')
        self.uma2.upload_uniform_scalar1i(mode, 'mode')

        return self

    def draw(self, projection, view, model):
        self.vao.activate()
        GL.glUseProgram(self.shader1.render_idx)
        GL.glDrawElements(GL.GL_TRIANGLE_STRIP, 4, GL.GL_UNSIGNED_INT, None)

        GL.glUseProgram(self.shader2.render_idx)
        offset = ctypes.c_void_p(2*4)  # None
        GL.glDrawElements(GL.GL_TRIANGLE_STRIP, 4, GL.GL_UNSIGNED_INT, offset)




class PatchEx(object):
    def __init__(self, vert_shader, frag_shader):
        """
        self.vertex_attrib:
        each row: v.x, v.y, v.z, c.r, c.g, c.b, n.x, n.y, n.z
        =>  (a) stride = nbytes(v0.x -> v1.x) = 9*4 = 36
            (b) offset(vertex) = ctypes.c_void_p(0); can use "None"
                offset(color) = ctypes.c_void_p(3*4)
                offset(normal) = ctypes.c_void_p(6*4)
        """
        vertex_color = np.array([
            [0,  0,  0,   0.0, 0.0, 0.0],  # A
            [0,  1,  0,   1.0, 0.0, 0.0],  # B
            [1,  0,  0,   0.0, 1.0, 0.0],  # C
            [1,  1,  0,   0.0, 0.0, 1.0],  # D
            [2,  0,  0,   1.0, 0.0, 0.0],  # E
            [2,  1,  0,   1.0, 1.0, 1.0]   # F
        ], dtype=np.float32)

        # random normals (facing +z)
        normals = np.random.normal(0, 5, (vertex_color.shape[0], 3)).astype(np.float32)
        normals[:, 2] = np.abs(normals[:, 2])  # (facing +z)
        normals = normals / np.linalg.norm(normals, axis=1, keepdims=True)
        self.vertex_attrib = np.concatenate([vertex_color, normals], axis=1)

        # indices
        self.indices = np.arange(self.vertex_attrib.shape[0]).astype(np.int32)

        self.vao = VAO()

        self.shader = Shader(vert_shader, frag_shader)
        self.uma = UManager(self.shader)
        #

    def setup(self):
        stride = 9*4
        offset_v = ctypes.c_void_p(0)  # None
        offset_c = ctypes.c_void_p(3*4)
        offset_n = ctypes.c_void_p(6*4)
        self.vao.add_vbo(0, self.vertex_attrib, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=stride, offset=offset_v)
        self.vao.add_vbo(1, self.vertex_attrib, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=stride, offset=offset_c)
        self.vao.add_vbo(2, self.vertex_attrib, ncomponents=3, dtype=GL.GL_FLOAT, normalized=False, stride=stride, offset=offset_n)
        self.vao.add_ebo(self.indices)


        normalMat = np.identity(4, 'f')
        projection = T.ortho(-0.5, 2.5, -0.5, 1.5, -1, 1)
        modelview = np.identity(4, 'f')

        # Light
        I_light = np.array([
            [0.9, 0.4, 0.6],  # diffuse
            [0.9, 0.4, 0.6],  # specular
            [0.9, 0.4, 0.6]  # ambient
        ], dtype=np.float32)
        light_pos = np.array([0, 0.5, 0.9], dtype=np.float32)

        # Materials
        K_materials_1 = np.array([
            [0.5, 0.0, 0.7],  # diffuse
            [0.5, 0.0, 0.7],  # specular
            [0.5, 0.0, 0.7]  # ambient
        ], dtype=np.float32)

        K_materials_2 = np.array([
            [0.1, 0.7, 0.8],  # diffuse
            [0.1, 0.7, 0.8],  # specular
            [0.1, 0.7, 0.8]  # ambient
        ], dtype=np.float32)

        shininess = 100.0
        mode = 1

        GL.glUseProgram(self.shader.render_idx)
        self.uma.upload_uniform_matrix4fv(normalMat, 'normalMat', True)
        self.uma.upload_uniform_matrix4fv(projection, 'projection', True)
        self.uma.upload_uniform_matrix4fv(modelview, 'modelview', True)

        self.uma.upload_uniform_matrix3fv(I_light, 'I_light', False)
        self.uma.upload_uniform_vector3fv(light_pos, 'light_pos')

        self.uma.upload_uniform_matrix3fv(K_materials_1, 'K_materials_1', False)
        self.uma.upload_uniform_matrix3fv(K_materials_2, 'K_materials_2', False)
        self.uma.upload_uniform_scalar1f(shininess, 'shininess')
        self.uma.upload_uniform_scalar1i(mode, 'mode')

        return self

    def draw(self, projection, view, model):
        self.vao.activate()

        GL.glUseProgram(self.shader.render_idx)
        self.uma.upload_uniform_scalar1i(1, 'face')
        GL.glDrawElements(GL.GL_TRIANGLE_STRIP, 4, GL.GL_UNSIGNED_INT, None)

        GL.glUseProgram(self.shader.render_idx)
        self.uma.upload_uniform_scalar1i(2, 'face')
        offset = ctypes.c_void_p(2*4)  # None
        GL.glDrawElements(GL.GL_TRIANGLE_STRIP, 4, GL.GL_UNSIGNED_INT, offset)


