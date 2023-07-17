from libs.shader import *
from libs import transform as T
from libs.buffer import *
import ctypes
import glfw
import glm
from color import *

class Cone(object):
    def __init__(self, vert_shader, frag_shader):
        _segments = 100
        positions = []
        colors = []
        normals = []
        texCoords = []

        baseCenter = glm.vec3(0.0, 0.0, -1.0)
        up = glm.vec3(0.0, 0.0, 1.0)

        top = baseCenter + up * 2
        for i in range(0, _segments):
            positions.append([top.x, top.y, top.z])
            colors.append(RED)
            normals.append([up.x, up.y, up.z])

            u = i / (_segments - 1)
            texCoords.append([u, 0.0])

        for i in range(0, 2):
            for j in range(0, _segments + 1):
                angle = j * 2.0 * np.pi / _segments
                direction = glm.normalize(glm.vec3(np.cos(angle), np.sin(angle), 0.0))
                point = baseCenter + direction * 1.0
                positions.append([point.x, point.y, point.z])
                colors.append(PURPLE)

                if i == 0:
                    tangent = glm.cross(up, direction)
                    norm = glm.normalize(glm.cross(tangent, top - point))
                    normals.append([norm.x, norm.y, norm.z])

                    u = j / _segments
                    texCoords.append([u, 1.0])
                else:
                    normals.append([-up.x, -up.y, -up.z])

                    u = 0.5 + 0.5 * np.cos(angle)
                    v = 0.5 + 0.5 * np.sin(angle)
                    texCoords.append([u, v])

        positions.append([baseCenter.x, baseCenter.y, baseCenter.z])
        colors.append(CYAN)
        normals.append([-up.x, -up.y, -up.z])
        texCoords.append([0.5, 0.5])

        vertexCount = len(positions)
        baseIndices = [vertexCount - 1]
        for i in range(0, _segments + 1):
            baseIndices.append(vertexCount - 2 - i)

        sideIndices = []
        for i in range(0, _segments):
            sideIndices.append(i)
            sideIndices.append(i + _segments)
            sideIndices.append(i + _segments + 1)

        self.vertices = np.array(positions, dtype=np.float32)
        self.normals = np.array(normals, dtype=np.float32)
        self.colors = np.array(colors, dtype=np.float32)
        self.texCoords = np.array(texCoords, dtype=np.float32)

        self.baseIndicesCount = len(baseIndices)
        self.sideIndicesCount = len(sideIndices)

        self.indices = np.array(baseIndices + sideIndices)
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
        GL.glDrawElements(GL.GL_TRIANGLE_FAN, self.baseIndicesCount, GL.GL_UNSIGNED_INT, None)
        GL.glDrawElements(GL.GL_TRIANGLES, self.sideIndicesCount, GL.GL_UNSIGNED_INT, ctypes.c_void_p(self.baseIndicesCount * 4))


    def key_handler(self, key):

        if key == glfw.KEY_1:
            self.selected_texture = 1
        if key == glfw.KEY_2:
            self.selected_texture = 2

