from libs.shader import *
from libs import transform as T
from libs.buffer import *
import ctypes
import glfw
import glm
import numpy as np

class mesh(object):
    def __init__(self, vert_shader, frag_shader, func):
        halfExtentX = 10.0
        halfExtentY = 10.0
        segmentsX = 30
        segmentsY = 30
        positions = []
        colors = []
        normals = []
        xStep = halfExtentX * 2 / segmentsX
        yStep = halfExtentY * 2 / segmentsY

        for i in range(0, segmentsX + 1):
            for j in range(0, segmentsY + 1):
                x0 = i * xStep - halfExtentX
                y0 = halfExtentY - j * yStep
                z0 = func(x0, y0)

                positions.append([x0, y0, z0])
                colors.append([0.0, 1.0, 0.0])

                x1 = (i+1)*xStep - halfExtentX
                y1 = y0
                z1 = func(x1, y1)

                x2 = x0
                y2 = halfExtentY - (j+1)*yStep
                z2 = func(x2, y2)

                x3 = (i-1)*xStep - halfExtentX
                y3 = y2
                z3 = func(x3, y3)

                x4 = (i-1) * xStep - halfExtentX
                y4 = y0
                z4 = func(x4, y4)

                x5 = x0
                y5 = halfExtentY - (j-1)*yStep
                z5 = func(x5, y5)

                x6 = (i+1)*xStep - halfExtentX
                y6 = y5
                z6 = func(x6, y6)

                vec01 = glm.vec3(x1-x0, y1-y0, z1-z0)
                vec02 = glm.vec3(x2-x0, y2-y0, z2-z0)
                vec03 = glm.vec3(x3-x0, y3-y0, z3-z0)
                vec04 = glm.vec3(x4-x0, y4-y0, z4-z0)
                vec05 = glm.vec3(x5-x0, y5-y0, z5-z0)
                vec06 = glm.vec3(x6-x0, y6-y0, z6-z0)

                norm1 = glm.normalize(glm.cross(vec01, vec06))
                norm2 = glm.normalize(glm.cross(vec02, vec01))
                norm3 = glm.normalize(glm.cross(vec03, vec02))
                norm4 = glm.normalize(glm.cross(vec04, vec03))
                norm5 = glm.normalize(glm.cross(vec05, vec04))
                norm6 = glm.normalize(glm.cross(vec06, vec05))

                normal = (norm1 + norm2 + norm3 + norm4 +norm5 + norm6) / 6
                normals.append(normal.to_list())

        self.vertices = np.array(positions,dtype=np.float32)
        idx = []
        self.idx_count = []
        for i in range(0, segmentsY):
            idx.append([])
            for j in range(0, segmentsX + 1):
                idx[i].append(j + i * (segmentsX + 1))
                idx[i].append(j + (i + 1) * (segmentsX + 1))
        indices = []
        for i in idx:
            indices = indices + i
        self.indices = np.array(indices)

        #normals = np.random.normal(0, 1, (self.vertices.shape[0], 3)).astype(np.float32)
        #normals[:, 2] = np.abs(normals[:, 2])  # (facing +z)
        self.normals = np.array(normals, dtype=np.float32)
        # self.normals = normals / np.linalg.norm(normals, axis=1, keepdims=True)
        # colors: RGB format
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
        self.materialDiffuse = glm.vec3(0.61424, 0.04136, 0.04136)
        self.materialAmbient = glm.vec3(0.1745, 0.01175, 0.01175)
        self.materialSpecular = glm.vec3(0.727811, 0.626959, 0.626959)

        self.shininess = 200.0
        self.mode = 2
    """
    Create object -> call setup -> call draw
    """
    def setup(self):
        # setup VAO for drawing cylinder's side
        self.vao.add_vbo(0, self.vertices, ncomponents=3, stride=0, offset=None)
        self.vao.add_vbo(1, self.colors, ncomponents=3, stride=0, offset=None)
        self.vao.add_vbo(2, self.normals, ncomponents=3, stride=0, offset=None)

        # setup EBO for drawing cylinder's side, bottom and top
        self.vao.add_ebo(self.indices)

        return self

    def draw(self, projection, view, model):
        segmentsx = 30
        segmentsY = 30
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

        self.uma.upload_uniform_vector3fv(self.materialAmbient, "material.ambient")
        self.uma.upload_uniform_vector3fv(self.materialDiffuse, "material.diffuse")
        self.uma.upload_uniform_vector3fv(self.materialSpecular, "material.specular")
        self.uma.upload_uniform_scalar1f(self.shininess, "material.shininess")

        self.uma.upload_uniform_scalar1i(1, "enabledDirectionalLight")
        self.vao.activate()
        for i in range(0, segmentsY):
            GL.glDrawElements(GL.GL_TRIANGLE_STRIP, (2 * (segmentsx + 1)), GL.GL_UNSIGNED_INT, ctypes.c_void_p(i * 8 * (segmentsx + 1)))


    def key_handler(self, key):

        if key == glfw.KEY_1:
            self.selected_texture = 1
        if key == glfw.KEY_2:
            self.selected_texture = 2

