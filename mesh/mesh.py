from libs.shader import *
from libs import transform as T
from libs.buffer import *
import ctypes
import glfw
import glm
from color import *

class Mesh(object):
    def __init__(self, vert_shader, frag_shader, func):
        halfExtentX = 1.0
        halfExtentY = 1.0
        segmentsX = 40
        segmentsY = 40
        positions = []
        colors = []
        normals = []
        texCoords = []

        xStep = halfExtentX * 2 / segmentsX
        yStep = halfExtentY * 2 / segmentsY

        for i in range(0, segmentsX + 1):
            for j in range(0, segmentsY + 1):
                x0 = i * xStep - halfExtentX
                y0 = halfExtentY - j * yStep

                z0 = func(x0, y0)

                positions.append([x0, y0, z0])

                x1 = (i + 1) * yStep - halfExtentX
                y1 = y0
                z1 = func(x1, y1)

                x2 = x0
                y2 = halfExtentY - (j + 1) * yStep
                z2 = func(x2, y2)

                x3 = (i - 1) * xStep - halfExtentX
                y3 = y2
                z3 = func(x3, y3)

                x4 = (i - 1) * xStep - halfExtentX
                y4 = y0
                z4 = func(x4, y4)

                x5 = x0
                y5 = halfExtentY - (j - 1) * yStep
                z5 = func(x5, y5)

                x6 = (i + 1) * xStep - halfExtentX
                y6 = y5
                z6 = func(x6, y6)

                vec01 = glm.vec3(x1 - x0, y1 - y0, z1 - z0)
                vec02 = glm.vec3(x2 - x0, y2 - y0, z2 - z0)
                vec03 = glm.vec3(x3 - x0, y3 - y0, z3 - z0)
                vec04 = glm.vec3(x4 - x0, y4 - y0, z4 - z0)
                vec05 = glm.vec3(x5 - x0, y5 - y0, z5 - z0)
                vec06 = glm.vec3(x6 - x0, y6 - y0, z6 - z0)

                norm1 = glm.normalize(glm.cross(vec01, vec06))
                norm2 = glm.normalize(glm.cross(vec02, vec01))
                norm3 = glm.normalize(glm.cross(vec03, vec02))
                norm4 = glm.normalize(glm.cross(vec04, vec03))
                norm5 = glm.normalize(glm.cross(vec05, vec04))
                norm6 = glm.normalize(glm.cross(vec01, vec06))

                normal = (norm1 + norm2 + norm3 + norm4 + norm5 + norm6) / 6.0
                normals.append([normal.x, normal.y, normal.z])

                colors.append(heatColorAt(z0))

                u = i / segmentsX
                v = j / segmentsY
                texCoords.append([u, v])

        self.vertices = np.array(positions, dtype=np.float32)
        self.normals = np.array(normals, dtype=np.float32)
        self.colors = np.array(colors, dtype=np.float32)
        self.texCoords = np.array(texCoords, dtype=np.float32)

        self.indices = []
        for i in range(0, segmentsY):
            indices = []
            for j in range(0, segmentsX + 1):
                indices.append(j + i * (segmentsX + 1))
                indices.append(j + (i + 1) * (segmentsX + 1))
            self.indices = self.indices + indices

        self.idxCountY = segmentsY
        self.idxCountX = segmentsX + 1

        self.indices = np.array(self.indices)
        self.vao = VAO()

        self.shader = Shader(vert_shader, frag_shader)
        self.uma = UManager(self.shader)

        # light
        self.lightDiffuse = glm.vec3(0.5, 0.5, 0.5)
        self.lightAmbient = glm.vec3(0.02, 0.02, 0.02)
        self.lightSpecular = glm.vec3(1.0, 1.0, 1.0)
        self.lightDir = glm.vec4(0.0, 0.0, -1.0, 0.0)

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
        for i in range(0, self.idxCountY):
            GL.glDrawElements(GL.GL_TRIANGLE_STRIP, self.idxCountX * 2, GL.GL_UNSIGNED_INT, ctypes.c_void_p(4 * (i * self.idxCountX * 2)))


    def key_handler(self, key):

        if key == glfw.KEY_1:
            self.selected_texture = 1
        if key == glfw.KEY_2:
            self.selected_texture = 2

