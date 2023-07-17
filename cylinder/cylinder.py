import numpy as np

from libs.shader import *
from libs import transform as T
from libs.buffer import *
import ctypes
import glfw
import glm
from color import *

class Cylinder(object):
    def __init__(self, vert_shader, frag_shader):
        _segments = 100

        positions = []
        colors = []
        normals = []
        texCoords = []

        up = glm.vec3(0.0, 0.0, 1.0)

        # Top center vertex
        topCenter = glm.vec3(0.0, 0.0, 1.0)
        positions.append([topCenter.x, topCenter.y, topCenter.z])
        colors.append(YELLOW)

        normals.append([topCenter.x, topCenter.y, topCenter.z])
        texCoords.append([0.5, 0.5])

        for i in range(4):
            # The actual center, for transform reference only
            multiplier = int(i / 2)  # will be either 0 or 1
            center = topCenter - up * (2.0 * float(multiplier))

            # Circular vertices, repeated at the start and end for accurate texture mapping
            for j in range(_segments + 1):
                # The angle of rotation
                angle = 2.0 * np.pi * float(j) / float(_segments)
                # The direction to the point on circle
                dir = glm.normalize(glm.vec3(np.cos(angle), np.sin(angle), 0.0))
                # Translate to that point
                point = center + dir * 1.0
                positions.append([point.x, point.y, point.z])
                colors.append(BROWN)

                if i == 0 or i == 3:
                    if i == 0:
                        normals.append([up.x, up.y, up.z])
                    else:
                        normals.append([-up.x, -up.y, -up.z])
                    u = 0.5 + 0.5 * np.cos(angle)
                    v = 0.5 + 0.5 * np.sin(angle)
                    texCoords.append([u, v])
                else:
                    normals.append([dir.x, dir.y, dir.z])
                    u = float(j) / float(_segments)
                    v = float(multiplier)
                    texCoords.append([u, v])

        # Bottom center vertex
        botCenter = glm.vec3(0.0, 0.0, -1.0)
        positions.append([botCenter.x, botCenter.y, botCenter.z])
        colors.append(YELLOW)
        normals.append([-up.x, -up.y, -up.z])
        texCoords.append([0.5, 0.5])

        vertexCount = len(positions)

        topIndices = [0]
        for i in range(_segments + 1):
            topIndices.append(i + 1)

        botIndices = [vertexCount - 1]
        for i in range(_segments + 1):
            botIndices.append(vertexCount - i - 2)

        sideIndices = []
        for i in range(_segments + 1):
            sideIndices.append(i + 1 + (_segments + 1))
            sideIndices.append(i + 1 + 2 * (_segments + 1))

        self.vertices = np.array(positions, dtype=np.float32)
        self.normals = np.array(normals, dtype=np.float32)
        self.colors = np.array(colors, dtype=np.float32)
        self.texCoords = np.array(texCoords, dtype=np.float32)

        self.indices = np.array(topIndices + botIndices + sideIndices)
        self.segments = _segments

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
        GL.glDrawElements(GL.GL_TRIANGLE_FAN, self.segments + 2, GL.GL_UNSIGNED_INT, None)
        GL.glDrawElements(
            GL.GL_TRIANGLE_FAN, self.segments + 2, GL.GL_UNSIGNED_INT, ctypes.c_void_p(4 * (self.segments + 2))
        )
        GL.glDrawElements(
            GL.GL_TRIANGLE_STRIP, 2 * (self.segments + 1), GL.GL_UNSIGNED_INT, ctypes.c_void_p(8 * (self.segments + 2))
        )

    def key_handler(self, key):
        if key == glfw.KEY_1:
            self.selected_texture = 1
        if key == glfw.KEY_2:
            self.selected_texture = 2
