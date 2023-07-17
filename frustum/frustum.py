from libs.shader import *
from libs import transform as T
from libs.buffer import *
import ctypes
import glfw
import glm
from color import *

class Frustum(object):
    def __init__(self, vert_shader, frag_shader):
        self.vertices = np.array(
            [
                # Face +X
                [+0.5, -0.5, +1.0],
                [+1.0, -1.0, -1.0],
                [+0.5, +0.5, +1.0],
                [+1.0, +1.0, -1.0],
                # Face +Y
                [+0.5, +0.5, +1.0],
                [+1.0, +1.0, -1.0],
                [-0.5, +0.5, +1.0],
                [-1.0, +1.0, -1.0],
                # Face +Z
                [-0.5, +0.5, +1.0],
                [-0.5, -0.5, +1.0],
                [+0.5, +0.5, +1.0],
                [+0.5, -0.5, +1.0],
                # Face -X
                [-0.5, +0.5, +1.0],
                [-1.0, +1.0, -1.0],
                [-0.5, -0.5, +1.0],
                [-1.0, -1.0, -1.0],
                # Face -Y
                [-0.5, -0.5, +1.0],
                [-1.0, -1.0, -1.0],
                [+0.5, -0.5, +1.0],
                [+1.0, -1.0, -1.0],
                # Face -Z
                [+1.0, +1.0, -1.0],
                [+1.0, -1.0, -1.0],
                [-1.0, +1.0, -1.0],
                [-1.0, -1.0, -1.0],
            ]
            , dtype=np.float32)

        xpNorm = glm.normalize(glm.cross(glm.vec3(0.0, 1.0, 0.0), glm.vec3(-0.5, 0.0, 1.0)))
        xnNorm = glm.normalize(glm.cross(glm.vec3(0.0, -1.0, 0.0), glm.vec3(-0.5, 0.0, 1.0)))
        ypNorm = glm.normalize(glm.cross(glm.vec3(-1.0, 0.0, 0.0), glm.vec3(0.0, -0.5, 1.0)))
        ynNorm = glm.normalize(glm.cross(glm.vec3(1.0, 0.0, 0.0), glm.vec3(0.0, 0.5, 1.0)))
        self.normals = np.array(
            [
                # Face +X
                [xpNorm.x,  xpNorm.y,  xpNorm.z],
                [xpNorm.x,  xpNorm.y,  xpNorm.z],
                [xpNorm.x,  xpNorm.y,  xpNorm.z],
                [xpNorm.x,  xpNorm.y,  xpNorm.z],
                # Face +Y
                [ypNorm.x,  ypNorm.y,  ypNorm.z],
                [ypNorm.x,  ypNorm.y,  ypNorm.z],
                [ypNorm.x,  ypNorm.y,  ypNorm.z],
                [ypNorm.x,  ypNorm.y,  ypNorm.z],
                # Face +Z
                [0.0,  0.0,  1.0],
                [0.0,  0.0,  1.0],
                [0.0,  0.0,  1.0],
                [0.0,  0.0,  1.0],
                # Face -X
                [xnNorm.x, xnNorm.y, xnNorm.z],
                [xnNorm.x, xnNorm.y, xnNorm.z],
                [xnNorm.x, xnNorm.y, xnNorm.z],
                [xnNorm.x, xnNorm.y, xnNorm.z],
                # Face -Y
                [ynNorm.x, ynNorm.y, ynNorm.z],
                [ynNorm.x, ynNorm.y, ynNorm.z],
                [ynNorm.x, ynNorm.y, ynNorm.z],
                [ynNorm.x, ynNorm.y, ynNorm.z],
                # Face -Z
                [0.0,  0.0, -1.0],
                [0.0,  0.0, -1.0],
                [0.0,  0.0, -1.0],
                [0.0,  0.0, -1.0]
            ]
            , dtype=np.float32)

        self.texCoords = np.array(
            [
                # Face +X
                [0.0, 0.0],
                [0.0, 1.0],
                [1.0, 0.0],
                [1.0, 1.0],

                # Face +Y
                [0.0, 0.0],
                [0.0, 1.0],
                [1.0, 0.0],
                [1.0, 1.0],

                # Face +Z
                [0.0, 0.0],
                [0.0, 1.0],
                [1.0, 0.0],
                [1.0, 1.0],

                # Face -X
                [0.0, 0.0],
                [0.0, 1.0],
                [1.0, 0.0],
                [1.0, 1.0],

                # Face -Y
                [0.0, 0.0],
                [0.0, 1.0],
                [1.0, 0.0],
                [1.0, 1.0],

                # Face -Z
                [0.0, 0.0],
                [0.0, 1.0],
                [1.0, 0.0],
                [1.0, 1.0]
            ]
            , dtype=np.float32)

        # colors: RGB format
        self.colors = np.array(
            [
                # Face +X
                BLUE,
                BLACK,
                CYAN,
                GREEN,
                # Face +Y
                CYAN,
                GREEN,
                WHITE,
                YELLOW,
                # Face +Z
                WHITE,
                MAGENTA,
                CYAN,
                BLUE,
                # Face -X
                WHITE,
                YELLOW,
                MAGENTA,
                RED,
                # Face -Y
                MAGENTA,
                RED,
                BLUE,
                BLACK,
                # Face -Z
                GREEN,
                BLACK,
                YELLOW,
                RED
            ]
            , dtype=np.float32
        )

        indices = []
        for i in range(0, 6):
            it = i * 4
            indices.append(it)
            indices.append(it + 1)
            indices.append(it + 2)
            indices.append(it + 2)
            indices.append(it + 1)
            indices.append(it + 3)

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
        GL.glDrawElements(GL.GL_TRIANGLES, self.indices.shape[0], GL.GL_UNSIGNED_INT, None)


    def key_handler(self, key):

        if key == glfw.KEY_1:
            self.selected_texture = 1
        if key == glfw.KEY_2:
            self.selected_texture = 2

