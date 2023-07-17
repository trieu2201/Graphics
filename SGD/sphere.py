from numpy.random import normal

from libs.shader import *
from libs import transform as T
from libs.buffer import *
import ctypes
import glfw
import glm
import numpy as np

pi = np.pi



class Sphere(object):
    def __init__(self, vert_shader, frag_shader):
        latitudes = 20
        longitudes = 50
        radius = 2
        center = glm.vec3(0.0, 0.0, 0.0)
        positions = []
        colors = []
        normals = []
        textCoords = []

        # top vertex
        positions.append([0.0, 0.0, 1.0])
        colors.append([0.0, 1.0, 1.0])
        normals.append([0.0, 0.0, 1.0])
        textCoords.append([0.0, 0.0])

        # side vertices
        for i in range(1, latitudes):
            theta = i * pi/latitudes
            for j in range (0, longitudes + 1):
                phi = j * 2 * pi/longitudes
                diX = np.sin(theta) * np.cos(phi)
                diY = np.sin(theta) * np.sin(phi)
                diZ = np.cos(theta)

                dir = glm.normalize(glm.vec3(diX, diY, diZ))

                positions.append(dir.to_list())
                normals.append(dir.to_list())

                u = j / longitudes
                v = i / latitudes
                textCoords.append([u, v])

        # bottom vertices
        positions.append([0.0, 0.0, -1.0])
        normals.append([0.0, 0.0, -1.0])
        textCoords.append([0.0, 1.0])
        vertexCount = int(len(positions))

        stripIndices = []
        for i in range(0, latitudes-2):
            if i > 0 :
                stripIndices.append(i * (longitudes + 1) + 1)
            for j in range (0, longitudes + 1):
                stripIndices.append(i * (longitudes + 1) + j + 1)
                stripIndices.append((i + 1) * (longitudes + 1) + j + 1)
            if i < (latitudes - 3):
                stripIndices.append((i + 1) * (longitudes + 1) + 1)
        topIndices = []
        topIndices.append(0)
        for i in range (0, longitudes + 1):
            topIndices.append(i+1)
        botIndices = []
        botIndices.append(vertexCount - 1)
        for i in range(0, longitudes + 1):
            botIndices.append(vertexCount - 2 - i)

        self.vertices = np.array(positions, dtype=np.float32)
        self.indices = np.array(stripIndices + topIndices + botIndices)
        self.idx_count = len(stripIndices)
        self.top_count = len(topIndices)
        self.bot_count = len(botIndices)

        # normals = np.random.normal(0, 1, (self.vertices.shape[0], 3)).astype(np.float32)
        # normals[:, 2] = np.abs(normals[:, 2])  # (facing +z)
        # self.normals = normals / np.linalg.norm(normals, axis=1, keepdims=True)

        self.normals = np.array(normals, dtype=np.float32)
        self.textCoords = np.array(textCoords, dtype=np.float32)
        self.colors = np.array(colors, dtype=np.float32)

        self.vao = VAO()

        self.shader = Shader(vert_shader, frag_shader)
        self.uma = UManager(self.shader)

        # light
        self.lightDiffuse = glm.vec3(0.5, 0.5, 0.5)
        self.lightAmbient = glm.vec3(0.2, 0.2, 0.2)
        self.lightSpecular = glm.vec3(1.0, 1.0, 1.0)

        self.lightDir = glm.vec4(-1.0, -1.5, -0.5, 0.0)

        # material
        self.materialDiffuse = glm.vec3(1.0, 0.829, 0.829)
        self.materialAmbient = glm.vec3(0.25, 0.20725, 0.20725)
        self.materialSpecular = glm.vec3(0.296648, 0.296648, 0.296648)

        self.shininess = 0.088 * 128
        self.mode = 2
        #
     

    """
    Create object -> call setup -> call draw
    """
    def setup(self):
        # setup VAO for drawing cylinder's side
        self.vao.add_vbo(0, self.vertices, ncomponents=3, stride=0, offset=None)
        # self.vao.add_vbo(1, self.colors, ncomponents=3, stride=0, offset=None)
        self.vao.add_vbo(2, self.normals, ncomponents=3, stride=0, offset=None)
        self.vao.add_vbo(3, self.textCoords, ncomponents=2, stride=0, offset=None)

        # setup EBO for drawing cylinder's side, bottom and top
        self.vao.add_ebo(self.indices)

        self.uma.setup_texture("texturedMaterial.diffuse", "../textures/earth-diffuse.png")
        self.uma.setup_texture("texturedMaterial.specular", "../textures/earth-specular.png")

        return self

    def draw(self, projection, view, model):
        GL.glUseProgram(self.shader.render_idx)
        norMat = glm.transpose(glm.inverse(view * model))

        self.uma.upload_uniform_matrix4fv(glm.value_ptr(projection), 'projection', False)
        self.uma.upload_uniform_matrix4fv(glm.value_ptr(view), 'view', False)
        self.uma.upload_uniform_matrix4fv(glm.value_ptr(model), 'model', False)
        self.uma.upload_uniform_matrix4fv(glm.value_ptr(norMat), 'normalMat', False)

        lightNormalMat = glm.transpose(glm.inverse(view * glm.mat4(1.0)))
        direction = glm.normalize(glm.vec3(lightNormalMat * self.lightDir))
        self.uma.upload_uniform_vector3fv(direction, "directionalLight.direction")
        self.uma.upload_uniform_vector3fv(self.lightAmbient, "directionalLight.ambient")
        self.uma.upload_uniform_vector3fv(self.lightDiffuse, "directionalLight.diffuse")
        self.uma.upload_uniform_vector3fv(self.lightSpecular, "directionalLight.specular")

        self.uma.upload_uniform_scalar1f(self.shininess, "texturedMaterial.shininess")

        self.uma.upload_uniform_scalar1i(1, "enabledDirectionalLight")
        self.uma.upload_uniform_scalar1i(1, "enabledTexturedMaterial")

        self.vao.activate()
        # GL.glDrawElements(GL.GL_TRIANGLE_STRIP, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)
        GL.glDrawElements(GL.GL_TRIANGLE_STRIP, self.idx_count, GL.GL_UNSIGNED_INT, None)
        GL.glDrawElements(GL.GL_TRIANGLE_FAN, self.top_count, GL.GL_UNSIGNED_INT, ctypes.c_void_p(self.idx_count * 4))
        GL.glDrawElements(GL.GL_TRIANGLE_FAN, self.bot_count, GL.GL_UNSIGNED_INT, ctypes.c_void_p((self.idx_count + self.top_count) * 4))



    def key_handler(self, key):

        if key == glfw.KEY_1:
            self.selected_texture = 1
        if key == glfw.KEY_2:
            self.selected_texture = 2

