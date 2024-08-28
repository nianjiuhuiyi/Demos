#ifndef BALLOBJECT_H
#define BALLOBJECT_H

#include <glad/glad.h>
#include <glm/glm.hpp>

#include "game_object.h"
#include "texture.h"

class BallObject : public GameObject {
public:
	// 球的状态
	GLfloat    Radius;
	GLboolean  Stuck;
	GLboolean  Sticky, PassThrough;    // power_up所需要的属性

	BallObject();
	BallObject(glm::vec2 pos, GLfloat radius, glm::vec2 velocity, Texture2D sprite);

	// moves the ball, keeping it constrained within the window bounds (except bottom edge); returns new position
	glm::vec2 Move(float dt, unsigned int window_width);
	// resets the ball to original state with given position and velocity
	void Reset(glm::vec2 position, glm::vec2 velocity);
};



#endif // !BALLOBJECT_H
