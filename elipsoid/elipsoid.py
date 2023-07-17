import numpy as np

from libs.shader import *
from libs import transform as T
from libs.buffer import *
import ctypes
import glfw
import glm
from color import *

class Elipsoid(object):
    def __init__(self, vert_shader, frag_shader):
        latitudes = 20
        longitudes = 50
        positions =[]
        colors = []
        normals = []
        texCoords =[]

        for i in range(0, longitudes):
            positions.append([0.0, 0.0, 1.0])
            colors.append(RED)
            normals.append([0.0, 0.0, 1.0])
            u = i / (longitudes - 1)
            texCoords.append([u, 0.0])

        for i in range(1, latitudes):
            theta = i * np.pi / latitudes
            for j in range(0, longitudes + 1):
                phi = j * 2 * np.pi / longitudes
                diX = np.sin(theta) * np.cos(phi)
                diY = np.sin(theta) * np.sin(phi)
                diZ = np.cos(theta)

                dir = glm.normalize(glm.vec3(diX, diY, diZ))

                positions.append([dir.x, dir.y, dir.z])
                colors.append(heatColorAt(dir.z))
                normals.append([dir.x, dir.y, dir.z])

                u = j / longitudes
                v = i / latitudes

                texCoords.append([u, v])

        for i in range(0, longitudes):
            positions.append([0.0, 0.0, -1.0])
            colors.append(BLUE)
            normals.append([0.0, 0.0, -1.0])
            u = i / (longitudes - 1)
            texCoords.append([u, 1.0])

        vertexCount = len(positions)

        stripIndices =[]
        for i in range(0, latitudes - 2):
            if i > 0:
                stripIndices.append(i * (longitudes + 1) + longitudes)
            for j in range(0, longitudes + 1):
                stripIndices.append(i * (longitudes + 1) + j + longitudes)
                stripIndices.append((i + 1) * (longitudes + 1) + j + longitudes)
            if i < (latitudes - 3):
                stripIndices.append((i + 1) * (longitudes + 1) + longitudes + longitudes)

        topIndices = []
        for i in range(0, longitudes):
            topIndices.append(i)
            topIndices.append(i + longitudes)
            topIndices.append(i + longitudes + 1)

        botIndices = []
        for i in range(0, longitudes):
            botIndices.append(vertexCount - 1 - i)
            botIndices.append(vertexCount - 1 - i - longitudes)
            botIndices.append(vertexCount - 1 - i - longitudes - 1)

        self.vertices = np.array(positions, dtype=np.float32)
        self.normals = np.array(normals, dtype=np.float32)
        self.colors = np.array(colors, dtype=np.float32)
        self.texCoords = np.array(texCoords, dtype=np.float32)

        self.indices = np.array(topIndices + botIndices + stripIndices)
        self.topCount = len(topIndices)
        self.botCount = len(botIndices)
        self.stripCount = len(stripIndices)

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
        self.vao.add_vbo(3, self.texCoords, ncomponents=2, stride=0, offset=None)

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
        GL.glDrawElements(GL.GL_TRIANGLE_STRIP, self.stripCount, GL.GL_UNSIGNED_INT, ctypes.c_void_p(4 * (self.topCount + self.botCount)))
        GL.glDrawElements(GL.GL_TRIANGLES, self.topCount, GL.GL_UNSIGNED_INT, None)
        GL.glDrawElements(GL.GL_TRIANGLES, self.botCount, GL.GL_UNSIGNED_INT, ctypes.c_void_p(4 * self.topCount))


    def key_handler(self, key):

        if key == glfw.KEY_1:
            self.selected_texture = 1
        if key == glfw.KEY_2:
            self.selected_texture = 2

