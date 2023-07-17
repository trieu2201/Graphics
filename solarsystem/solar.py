import glm


def get_planet_transform(revolveAngle, rotateAngle, tiltingAngle, planetRadius, orbitX, orbitY, orbitOrientation=glm.vec3(0.0, 0.0, 1.0), orbitCenter=glm.vec3(0.0, 0.0, 0.0)):
    # Center
    transform = glm.translate(glm.mat4(1.0), orbitCenter)

    # Orientation
    if orbitOrientation != glm.vec3(0.0, 0.0, 1.0):
        orientingAxis = glm.normalize(glm.cross(glm.vec3(0.0, 0.0, 1.0), orbitOrientation))
        orientingAngle = glm.acos(glm.normalize(orbitOrientation).z)
        orientingQuat = glm.angleAxis(orientingAngle, orientingAxis)
        orientingMat = glm.mat4_cast(orientingQuat)
        transform = transform * orientingMat

    # Revolve
    revolveVec = glm.vec3(orbitX(revolveAngle), orbitY(revolveAngle), 0.0)
    transform = glm.translate(transform, revolveVec)

    # Tilt
    tiltingAxis = glm.vec3(0.0, 1.0, 0.0)
    tiltingQuat = glm.angleAxis(tiltingAngle, tiltingAxis)
    tiltingMat = glm.mat4_cast(tiltingQuat)
    transform = transform * tiltingMat

    # Rotate
    rotateAxis = glm.vec3(0.0, 0.0, 1.0)
    rotateQuat = glm.angleAxis(rotateAngle, rotateAxis)
    rotateMat = glm.mat4_cast(rotateQuat)
    transform = transform * rotateMat

    # Scale
    transform = glm.scale(transform, glm.vec3(planetRadius, planetRadius, planetRadius))

    return transform


def get_orbit_transform(orbitOrientation=glm.vec3(0.0, 0.0, 1.0), orbitCenter=glm.vec3(0.0, 0.0, 0.0)):
    # Center
    transform = glm.translate(glm.mat4(1.0), orbitCenter)

    # Orientation
    orientingAxis = glm.normalize(glm.cross(glm.vec3(0.0, 0.0, 1.0), orbitOrientation))
    orientingAngle = glm.acos(glm.normalize(orbitOrientation).z)
    orientingQuat = glm.angleAxis(orientingAngle, orientingAxis)
    orientingMat = glm.mat4_cast(orientingQuat)
    transform = transform * orientingMat

    return transform
