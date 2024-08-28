#ifndef GAME_H
#define GAME_H

#include <tuple>
#include <algorithm>

#include <glad/glad.h>
#include <GLFW/glfw3.h>

#include "game_level.h"
#include "power_up.h"

// Represents the current state of the game
enum GameState {
	GAME_ACTIVE,
	GAME_MENU,
	GAME_WIN
};


// Initial size of the player paddle
const glm::vec2 PLAYER_SIZE(100.0f, 20.0f);
const float PLAYER_VELOCITY(500.0f);     // 速度


// 初始化球的速度
const glm::vec2 INITIAL_BALL_VELOCITY(100.0F, -350.0F);
// 球半径
const float BALL_RADIUS = 12.5F;


// Represents the four possible (collision) directions
enum Direction {
	UP,
	RIGHT,
	DOWN,
	LEFT
};
// Defines a Collision typedef that represents collision data
typedef std::tuple<bool, Direction, glm::vec2> Collision;




// Game holds all game-related state and functionality.
// Combines all game-related data into a single class for
// easy access to each of the components and manageability.
class Game {
public:
	// Game state
	GameState              State;
	GLboolean              Keys[1024];
	bool                   KeysProcessed[1024];
	GLuint                 Width, Height;

	std::vector<GameLevel> Levels;
	GLuint                 Level;

	std::vector<PowerUp>   PowerUps;  // 道具

	GLuint                 Lives;  // 生命值

	// Constructor/Destructor
	Game(GLuint width, GLuint height);
	~Game();
	// Initialize game state (load all shaders/textures/levels)
	void Init();
	// GameLoop
	void ProcessInput(GLfloat dt);
	void Update(GLfloat dt);
	void Render();
	void DoCollisions();   // 碰撞检测

	// reset
	void ResetLevel();
	void Resetplayer();

	// power_up
	void SpawnPowerUps(GameObject &block);
	void UpdatePowerUps(float dt);
};

#endif