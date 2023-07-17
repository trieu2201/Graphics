#version 440 core

in vec4 fragColor;
in vec2 fragUV0;

out vec4 FragColor;

uniform sampler2D unlitTexture;
uniform bool enabledUnlitTexture;

void main() {
	if (enabledUnlitTexture) {
		FragColor = texture(unlitTexture, fragUV0);
	} else {
		FragColor = fragColor;
	}
}