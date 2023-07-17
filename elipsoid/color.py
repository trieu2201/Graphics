import glm

BLACK = [0.0, 0.0, 0.0]
RED = [1.0, 0.0, 0.0]
GREEN = [0.0, 1.0, 0.0]
BLUE = [0.0, 0.0, 1.0]
YELLOW = [1.0, 0.96863, 0.0]
CYAN = [0.0, 1.0, 1.0]
MAGENTA = [1.0, 0.0, 0.56471]
PURPLE = [0.43529, 0.05098, 0.54118]
BROWN = [0.54118, 0.20392, 0.04706]
WHITE = [1.0, 1.0, 1.0]

hot = glm.vec3(PURPLE[0], PURPLE[1], PURPLE[2])
warm = glm.vec3(YELLOW[0], YELLOW[1], YELLOW[2])
neutral = glm.vec3(GREEN[0], GREEN[1], GREEN[2])
cool = glm.vec3(CYAN[0], CYAN[1], CYAN[2])
cold = glm.vec3(BLUE[0], BLUE[1], BLUE[2])

def heatColorAt(height):
    factor = glm.clamp(height, -1.0, 1.0)
    color = glm.vec3()

    if factor < 0.0:
        if factor >= -0.5:
            color = glm.mix(neutral, cool, glm.abs(factor) * 2.0)
        else:
            color = glm.mix(neutral, cool, glm.abs(factor + 0.5) * 2.0)
    else:
        if factor < 0.5:
            color = glm.mix(neutral, warm, factor * 2)
        else:
            color = glm.mix(warm, hot, (factor - 0.5) * 2.0)

    return [color.r, color.g, color.b]
