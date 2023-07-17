#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 color;
layout (location = 2) in vec3 normal;
layout (location = 3) in vec2 uv0;
layout (location = 4) in vec2 uv1;

out vec3 fragPosition;
out vec3 fragNormal;
out vec4 fragColor;
out vec2 fragUV0;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform mat4 normalMat;

void main() {
	vec4 viewPos = view * model * vec4(position, 1.0f);
	fragPosition = vec3(viewPos) / viewPos.w;
	fragColor = vec4(color, 1.0f);
	fragNormal = vec3(normalMat * vec4(normal, 0.0));

	fragUV0 = uv0;

	gl_Position = projection * viewPos;
}