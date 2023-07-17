import glm
from glm import lookAt, perspective

class Camera:
    MIN_RADIUS = 1.0
    MAX_RADIUS = 500.0
    MIN_THETA = 1.0
    MAX_THETA = 179.0
    DEFAULT_FOV = 45.0
    DEFAULT_NEAR = 0.1
    DEFAULT_FAR = 100.0
    ZOOM_SENSITIVE = 1.0
    DRAG_SENSITIVE = 0.5

    def __init__(self):
        self._radius = 4.0  # radius of the looking sphere [MIN_RADIUS; MAX_RADIUS]
        self._phi = -90.0  # XY-plane rotation [0; 360]
        self._theta = 80.0  # Z-axis rotation [1; 179]
        self._projection = perspective(glm.radians(Camera.DEFAULT_FOV), 1.0, Camera.DEFAULT_NEAR, Camera.DEFAULT_FAR)

    def relative_drag(self, offset_x, offset_y):
        self._phi -= offset_x * Camera.DRAG_SENSITIVE
        self._theta -= offset_y * Camera.DRAG_SENSITIVE
        self._theta = glm.clamp(self._theta, Camera.MIN_THETA, Camera.MAX_THETA)

    def relative_zoom(self, amount):
        self._radius -= amount * Camera.ZOOM_SENSITIVE
        self._radius = glm.clamp(self._radius, Camera.MIN_RADIUS, Camera.MAX_RADIUS)

    def set_projection(self, fov, ratio, near, far):
        self._projection = perspective(glm.radians(fov), ratio, near, far)

    def set_orthographic_projection(self, left, right, bottom, top, z_near, z_far):
        self._projection = glm.ortho(left, right, bottom, top, z_near, z_far)

    def get_projection(self):
        return self._projection

    def get_view_matrix(self):
        pos = glm.vec3(
            self._radius * glm.sin(glm.radians(self._theta)) * glm.cos(glm.radians(self._phi)),
            self._radius * glm.sin(glm.radians(self._theta)) * glm.sin(glm.radians(self._phi)),
            self._radius * glm.cos(glm.radians(self._theta))
        )
        return lookAt(pos, glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0, 0.0, 1.0))

    def set_radius(self, radius):
        self._radius = radius

    def set_phi(self, phi):
        self._phi = phi

    def set_theta(self, theta):
        self._theta = theta
