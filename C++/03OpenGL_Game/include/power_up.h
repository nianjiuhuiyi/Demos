#ifndef POWER_UP_H
#define poWER_UP_H

#include <string>

#include <glad/glad.h>
#include <glm/glm.hpp>

#include "game_object.h"


// The size of a PowerUp block
const glm::vec2 POWERUP_SIZE(60.0f, 20.0f);
// Velocity a PowerUp block has when spawned
const glm::vec2 VELOCITY(0.0f, 150.0f);

class PowerUp : public GameObject {
public:
	// 道具状态
	std::string Type;
	float       Duration;
	bool        Activated;
	// 构造函数
	PowerUp(std::string type, glm::vec3 color, float duration, glm::vec2 position, Texture2D texture)
		: GameObject(position, POWERUP_SIZE, texture, color, VELOCITY), Type(type), Duration(duration), Activated() {}
};

#endif // !POWER_UP_H
