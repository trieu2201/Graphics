#version 440 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;
layout (location = 2) in vec4 color;
layout (location = 3) in vec2 uv0;
layout (location = 4) in vec2 uv1;

out vec4 fragColor;
out vec2 fragUV0;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
	gl_Position = projection * view * model * vec4(position, 1.0f);
    fragColor = color;
    fragUV0 = uv0;
}