#ifndef TEXT_RENDERER_H
#define TEXT_RENDERER_H

#include <map>

#include <glad/glad.h>
#include <glm/glm.hpp>

#include "texture.h"
#include "shader.h"

// Holds all state information relevant to a character as loaded using FreeType
struct Character {
	unsigned int TextureID;  // 字形纹理的ID
	glm::ivec2   Size;       // 字体大小
	glm::ivec2   Bearing;    // 从基准线到字形左部/顶部的偏移值
	unsigned int Advance;    // 原点距下一个字形原点的距离
};

// A renderer class for rendering text displayed by a font loaded using the 
// FreeType library. A single font is loaded, processed into a list of Character
// items for later rendering.

class TextRenderer {
public:
	// holds a list of pre-compiled Characters
	std::map<char, Character> Characters;
	// shader used for text rendering
	Shader TextShader;
	// 构造函数
	TextRenderer(unsigned int width, unsigned int height);
	// pre-compiles a list of characters from the given font
	void Load(std::string font, unsigned int fontSize);
	// renders a string of text using the precompiled list of characters
	void RenderText(std::string text, float x, float y, float scale, glm::vec3 color = glm::vec3(1.0f));
private:
	// render state
	unsigned int VAO, VBO;
};

#endif // !TEXT_RENDERER_H

