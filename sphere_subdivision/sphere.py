import numpy as np

from libs.shader import *
from libs import transform as T
from libs.buffer import *
import ctypes
import glfw
import glm
from color import *

class Sphere(object):
    def getFaces(self):
        ratioPos = (1.0 + 1.0 / glm.sqrt(5.0)) / 2.0
        ratioNeg = (1.0 - 1.0 / glm.sqrt(5.0)) / 2.0

        v01 = glm.vec3(1.0, 0.0, 0.0)
        v02 = glm.vec3(-1.0, 0.0, 0.0)

        v03 = glm.vec3(1.0 / glm.sqrt(5.0), 2.0 / glm.sqrt(5.0), 0.0)
        v04 = glm.vec3(-1.0 / glm.sqrt(5.0), -2.0 / glm.sqrt(5.0), 0.0)

        v05 = glm.vec3(1.0 / glm.sqrt(5.0), ratioNeg, glm.sqrt(ratioPos))
        v06 = glm.vec3(1.0 / glm.sqrt(5.0), ratioNeg, -glm.sqrt(ratioPos))
        v07 = glm.vec3(-1.0 / glm.sqrt(5.0), -ratioNeg, -glm.sqrt(ratioPos))
        v08 = glm.vec3(-1.0 / glm.sqrt(5.0), -ratioNeg, glm.sqrt(ratioPos))

        v09 = glm.vec3(1.0 / glm.sqrt(5.0), -ratioPos, glm.sqrt(ratioNeg))
        v10 = glm.vec3(1.0 / glm.sqrt(5.0), -ratioPos, -glm.sqrt(ratioNeg))
        v11 = glm.vec3(-1.0 / glm.sqrt(5.0), ratioPos, -glm.sqrt(ratioNeg))
        v12 = glm.vec3(-1.0 / glm.sqrt(5.0), ratioPos, glm.sqrt(ratioNeg))

        faces = [
            v01, v09, v10,  # top set (5)
            v01, v10, v06,
            v01, v06, v03,
            v01, v03, v05,
            v01, v05, v09,
            v09, v04, v10,  # mid set (10)
            v10, v04, v07,
            v10, v07, v06,
            v06, v07, v11,
            v06, v11, v03,
            v03, v11, v12,
            v03, v12, v05,
            v05, v12, v08,
            v05, v08, v09,
            v09, v08, v04,
            v04, v08, v02,  # bot set (5)
            v07, v04, v02,
            v11, v07, v02,
            v12, v11, v02,
            v08, v12, v02,
        ]
        return faces

    def subdivide(self, p0, p1, p2, depth):
        if depth == 0:
            return [p0.to_list(), p1.to_list(), p2.to_list()]

        m0 = self.radius * glm.normalize((p1 + p2) / 2.0)
        m1 = self.radius * glm.normalize((p0 + p2) / 2.0)
        m2 = self.radius * glm.normalize((p0 + p1) / 2.0)

        vec0 = self.subdivide(p0, m2, m1, depth - 1)
        vec1 = self.subdivide(m2, p1, m0, depth - 1)
        vec2 = self.subdivide(m0, m1, m2, depth - 1)
        vec3 = self.subdivide(m1, m0, p2, depth - 1)

        vec0.extend(vec1)
        vec0.extend(vec2)
        vec0.extend(vec3)

        return vec0

    def __init__(self, vert_shader, frag_shader):
        self.radius = 1.0
        faces = self.getFaces()
        faceCount = int(len(faces) / 3)

        positions = []
        colors = []
        normals = []
        texCoords = []

        for i in range(0, faceCount):
            p0 = faces[i * 3 + 0]
            p1 = faces[i * 3 + 1]
            p2 = faces[i * 3 + 2]

            data = self.subdivide(p0, p1, p2, 4.0)
            positions.extend(data)
            normals.extend(data)

            count = len(data)
            color = hueAt(i)
            for j in range(count):
                colors.extend(color)

        vertexCount = len(positions)
        indices = []
        for i in range(vertexCount):
            indices.append(i)

        self.vertices = np.array(positions, dtype=np.float32)
        self.normals = np.array(normals, dtype=np.float32)
        self.colors = np.array(colors, dtype=np.float32)
        # self.texCoords = np.array(texCoords, dtype=np.float32)

        self.indicesCount = len(indices)
        self.indices = np.array(indices)

        self.vao = VAO()

        self.shader = Shader(vert_shader, frag_shader)
        self.uma = UManager(self.shader)

        # light
        self.lightDiffuse = glm.vec3(0.5, 0.5, 0.5)
        self.lightAmbient = glm.vec3(0.02, 0.02, 0.02)
        self.lightSpecular = glm.vec3(1.0, 1.0, 1.0)
        self.lightDir = glm.vec4(-1.0, -1.5, -0.5, 0.0)

        # material
        self.materialDiffuse = glm.vec3(1.0, 0.829, 0.829)
        self.materialAmbient = glm.vec3(0.25, 0.20725, 0.20725)
        self.materialSpecular = glm.vec3(0.296648, 0.296648, 0.296648)
        self.shininess = 80

    """
    Create object -> call setup -> call draw
    """
    def setup(self, enable_texture=0):
        # setup VAO for drawing cylinder's side
        self.vao.add_vbo(0, self.vertices, ncomponents=3, stride=0, offset=None)
        self.vao.add_vbo(1, self.colors, ncomponents=3, stride=0, offset=None)
        self.vao.add_vbo(2, self.normals, ncomponents=3, stride=0, offset=None)
        # self.vao.add_vbo(3, self.texCoords, ncomponents=2, stride=0, offset=None)

        # setup EBO for drawing cylinder's side, bottom and top
        self.vao.add_ebo(self.indices)

        self.uma.upload_uniform_vector3fv(self.materialAmbient, "material.ambient")
        self.uma.upload_uniform_vector3fv(self.materialDiffuse, "material.diffuse")
        self.uma.upload_uniform_vector3fv(self.materialSpecular, "material.specular")
        self.uma.upload_uniform_scalar1f(self.shininess, "material.shininess")

        self.uma.upload_uniform_scalar1i(1, "enabledDirectionalLight")
        self.uma.upload_uniform_scalar1i(enable_texture, "enabledTexturedMaterial")

        if enable_texture == 1:
            self.uma.setup_texture("texturedMaterial.diffuse", "./../textures/stone_diffuse.jpg")
            self.uma.setup_texture("texturedMaterial.specular", "./../textures/stone_specular.jpg")
            self.uma.upload_uniform_scalar1f(self.shininess, "texturedMaterial.shininess")

        return self

    def draw(self, projection, view, model):
        GL.glUseProgram(self.shader.render_idx)
        nor_mat = glm.transpose(glm.inverse(view * model))

        self.uma.upload_uniform_matrix4fv(glm.value_ptr(projection), 'projection', False)
        self.uma.upload_uniform_matrix4fv(glm.value_ptr(view), 'view', False)
        self.uma.upload_uniform_matrix4fv(glm.value_ptr(model), 'model', False)
        self.uma.upload_uniform_matrix4fv(glm.value_ptr(nor_mat), 'normalMat', False)

        light_nor_mat = glm.transpose(glm.inverse(view * glm.mat4(1.0)))
        direction = glm.normalize(glm.vec3(light_nor_mat * self.lightDir))
        self.uma.upload_uniform_vector3fv(direction, "directionalLight.direction")
        self.uma.upload_uniform_vector3fv(self.lightAmbient, "directionalLight.ambient")
        self.uma.upload_uniform_vector3fv(self.lightDiffuse, "directionalLight.diffuse")
        self.uma.upload_uniform_vector3fv(self.lightSpecular, "directionalLight.specular")

        self.vao.activate()
        GL.glDrawElements(GL.GL_TRIANGLES, self.indicesCount, GL.GL_UNSIGNED_INT, None)


    def key_handler(self, key):

        if key == glfw.KEY_1:
            self.selected_texture = 1
        if key == glfw.KEY_2:
            self.selected_texture = 2

