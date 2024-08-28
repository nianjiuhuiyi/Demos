#include <iostream>
#include <sstream>
// 语音库
#include <irrKlang.h>
using namespace irrklang;

#include "game.h"
#include "resource_manager.h"
#include "sprite_renderer.h"
#include "ball_object.h"
#include "particle_generator.h"
#include "post_processor.h"
#include "text_renderer.h"


// Game-related State data
SpriteRenderer  *Renderer;

// 玩家操控的挡板
GameObject      *Player;

// 球
BallObject      *Ball;

// 粒子  
ParticleGenerator *Particles;

// 三种不同的效果
PostProcessor    *Effects;
float ShakeTime = 0.0f;

// 语音
ISoundEngine     *SoundEigen = createIrrKlangDevice();
/*
bleep.mp3: 小球撞击非实心砖块时的音效
solid.wav：小球撞击实心砖块时的音效
powerup.wav: 获得道具时的音效
bleep.wav: 小球在挡板上反弹时的音效
*/

// 文本
TextRenderer     *Text;



Game::Game(GLuint width, GLuint height)
	: State(GAME_MENU), Keys(), KeysProcessed(), Width(width), Height(height), Level(0), Lives(3) {
	
}

Game::~Game() {
	delete Renderer;
	delete Player;
	delete Ball;
	delete Particles;
	delete Effects;
	SoundEigen->drop();
	delete Text;
}

void Game::Init() {
	// Load shaders
	std::string shaderDir = "./resources/shaders/";
	ResourceManager::LoadShader((shaderDir + "sprite.vs").c_str(), (shaderDir + "sprite.fs").c_str(), nullptr, "sprite");
	ResourceManager::LoadShader((shaderDir + "particle.vs").c_str(), (shaderDir + "particle.fs").c_str(), nullptr, "particle");
	ResourceManager::LoadShader((shaderDir + "post_processing.vs").c_str(), (shaderDir + "post_processing.fs").c_str(), nullptr, "post_processing");

	// Configure shaders
	glm::mat4 projection = glm::ortho(0.0f, static_cast<GLfloat>(this->Width), static_cast<GLfloat>(this->Height), 0.0f, -1.0f, 1.0f);
	ResourceManager::GetShader("sprite").Use().SetInteger("image", 0);
	ResourceManager::GetShader("sprite").SetMatrix4("projection", projection);
	ResourceManager::GetShader("particle").Use().SetInteger("sprite", 0);
	ResourceManager::GetShader("particle").SetMatrix4("projection", projection);

	// Load textures
	std::string PicDir = "./resources/textures/";
	ResourceManager::LoadTexture((PicDir + "background.jpg").c_str(), GL_FALSE, "background");
	ResourceManager::LoadTexture((PicDir + "awesomeface.png").c_str(), GL_TRUE, "face");
	ResourceManager::LoadTexture((PicDir + "block.png").c_str(), GL_FALSE, "block");
	ResourceManager::LoadTexture((PicDir + "block_solid.png").c_str(), GL_FALSE, "block_solid");
	ResourceManager::LoadTexture((PicDir + "paddle.png").c_str(), GL_TRUE, "paddle");  // 挡板
	ResourceManager::LoadTexture((PicDir + "particle.png").c_str(), GL_TRUE, "particle");  // 粒子
	// power_up
	ResourceManager::LoadTexture((PicDir + "powerup_speed.png").c_str(), true, "powerup_speed");
	ResourceManager::LoadTexture((PicDir + "powerup_sticky.png").c_str(), true, "powerup_sticky");
	ResourceManager::LoadTexture((PicDir + "powerup_increase.png").c_str(), true, "powerup_increase");
	ResourceManager::LoadTexture((PicDir + "powerup_confuse.png").c_str(), true, "powerup_confuse");
	ResourceManager::LoadTexture((PicDir + "powerup_chaos.png").c_str(), true, "powerup_chaos");
	ResourceManager::LoadTexture((PicDir + "powerup_passthrough.png").c_str(), true, "powerup_passthrough");


	// Set render-specific controls ( 所有加载的shader都来这里获取 )
	Shader shaderSP = ResourceManager::GetShader("sprite");
	Renderer = new SpriteRenderer(shaderSP);
	
	Particles = new ParticleGenerator(ResourceManager::GetShader("particle"), ResourceManager::GetTexture("particle"), 500);

	Effects = new PostProcessor(ResourceManager::GetShader("post_processing"), this->Width, this->Height);


	// 加载关卡
	std::string LvlDir = "./resources/levels/";
	GameLevel one; one.Load((LvlDir + "one.lvl").c_str(), this->Width, this->Height / 2);
	GameLevel two; two.Load((LvlDir + "two.lvl").c_str(), this->Width, this->Height / 2);
	GameLevel three; three.Load((LvlDir + "three.lvl").c_str(), this->Width, this->Height / 2);
	GameLevel four; four.Load((LvlDir + "four.lvl").c_str(), this->Width, this->Height / 2);
	this->Levels.push_back(one);
	this->Levels.push_back(two);
	this->Levels.push_back(three);
	this->Levels.push_back(four);
	this->Level = 0;   // 默认初始化在第一关

	// 设置玩家操控挡板的属性
	glm::vec2 playerPos = glm::vec2(this->Width / 2.0f - PLAYER_SIZE.x / 2.0f, this->Height - PLAYER_SIZE.y);
	Player = new GameObject(playerPos, PLAYER_SIZE, ResourceManager::GetTexture("paddle"));

	// 设置球的属性
	glm::vec2 ballPos = playerPos + glm::vec2(PLAYER_SIZE.x / 2 - BALL_RADIUS, -BALL_RADIUS * 2);
	Ball = new BallObject(ballPos, BALL_RADIUS, INITIAL_BALL_VELOCITY, ResourceManager::GetTexture("face"));

	// audio
	SoundEigen->play2D("./resources/audio/breakout.mp3", true);

	// 文本
	Text = new TextRenderer(this->Width, this->Height);
	Text->Load("./resources/fonts/OCRAEXT.TTF", 24);
}

void Game::Update(GLfloat dt) {
	// 通过move函数来更新球的位置
	Ball->Move(dt, this->Width);
	// 碰撞检测
	this->DoCollisions();

	// 更新粒子
	Particles->Update(dt, *Ball, 2, glm::vec2(Ball->Radius / 2));

	// 更新 PowerUps
	this->UpdatePowerUps(dt);

	// reduce shake time
	if (ShakeTime > 0.0F) {
		ShakeTime -= dt;
		if (ShakeTime <= 0.0f)
			Effects->Shake = false;
	}

	// check loss condition  // Did ball reach bottom edge?
	if (Ball->Position.y >= this->Height) {  
		--this->Lives;
		// 玩家是否已失去所有生命值? : 游戏结束
		if (this->Lives == 0) {
			this->ResetLevel();
			this->State = GAME_MENU;
		}
		this->Resetplayer();
	}

	// 检查赢的条件
	if (this->State == GAME_ACTIVE && this->Levels[this->Level].IsCompleted()) {
		this->ResetLevel();
		this->Resetplayer();
		Effects->Chaos = true;
		this->State = GAME_WIN;
	}
}


void Game::ProcessInput(GLfloat dt) {
	if (this->State == GAME_MENU) {
		if (this->Keys[GLFW_KEY_ENTER] && !this->KeysProcessed[GLFW_KEY_ENTER]) {
			this->State = GAME_ACTIVE;
			this->KeysProcessed[GLFW_KEY_ENTER] = true;
		}
		if (this->Keys[GLFW_KEY_W] && !this->KeysProcessed[GLFW_KEY_W]) {
			this->Level = (this->Level + 1) % 4;
			this->KeysProcessed[GLFW_KEY_W] = true;
		}
		if (this->Keys[GLFW_KEY_S] && !this->KeysProcessed[GLFW_KEY_S]) {
		/*	if (this->Level > 0)
				--this->Level;
			else
				this->Level = 3;*/
			this->Level = (this->Level - 1) % 4;   // 这是一直循环，上面的写法就到底就按不动了
			this->KeysProcessed[GLFW_KEY_S] = true;
		}
	}

	if (this->State == GAME_WIN) {
		if (this->Keys[GLFW_KEY_ENTER]) {
			this->KeysProcessed[GLFW_KEY_ENTER] = true;
			Effects->Chaos = false;
			this->State = GAME_MENU;
		}
	}

	if (this->State == GAME_ACTIVE) {
		// 按空格就会释放球
		if (this->Keys[GLFW_KEY_SPACE])
			Ball->Stuck = false;

		float velocity = PLAYER_VELOCITY * dt;
		// 移动挡板(按A或<-来移动)
		if (this->Keys[GLFW_KEY_A] || this->Keys[GLFW_KEY_LEFT]) {
			if (Player->Position.x >= 0) {
				Player->Position.x -= velocity;
				// 球没被困住就跟随挡板一起移动
				if (Ball->Stuck)
					Ball->Position.x -= velocity;
			}
		}
		if (this->Keys[GLFW_KEY_D] || this->Keys[GLFW_KEY_RIGHT]) {
			if (Player->Position.x <= this->Width - Player->Size.x) {
				Player->Position.x += velocity;
				if (Ball->Stuck)
					Ball->Position.x += velocity;
			}
		}
	}
}

void Game::Render() {  
	// 一开始的笑脸
	/*Texture2D texture = ResourceManager::GetTexture("face");
	Renderer->DrawSprite(texture, glm::vec2(200, 200), glm::vec2(300, 400), 45.0f, glm::vec3(0.0f, 1.0f, 0.0f));*/

	if (this->State == GAME_ACTIVE || this->State == GAME_MENU || this->State == GAME_WIN) {
		// begin rendering to postprocessing framebuffer
		Effects->BeginRender();
			// 1.绘制背景
			Texture2D texture = ResourceManager::GetTexture("background");
			Renderer->DrawSprite(texture, glm::vec2(0.0f, 0.0f), glm::vec2(this->Width, this->Height), 0.0f);
			// 2.绘制关卡
			this->Levels[this->Level].Draw(*Renderer);
			// 3.绘制玩家操作挡板
			Player->Draw(*Renderer);
			// draw PowerUps
			for (PowerUp &powerUp : this->PowerUps) {
				if (!powerUp.Destroyed)
					powerUp.Draw(*Renderer);
			}
			// 要渲染粒子
			Particles->Draw();
			// 4.绘制球
			Ball->Draw(*Renderer);

		// end rendering to postprocessing framebuffer
		Effects->EndRender();
		// render postprocessing quad
		Effects->Render(glfwGetTime());

		// render text，显示当前生命值 (don't include in postprocessing)
		std::stringstream ss; ss << this->Lives;   // 注意要头文件 #include <sstream>
		Text->RenderText("Lives: " + ss.str(), 5.0f, 5.0f, 1.0f);

		if (this->State == GAME_MENU) {
			Text->RenderText("Press ENTER to start", 250.f, Height / 2, 1.0f);
			Text->RenderText("Press W or S to select level", 245.0f, Height / 2 + 20.0f, 0.75f);
			// string 和 int 是不能直接相加的，要这样把int转成string
			std::stringstream level_name; level_name << this->Level + 1;
			Text->RenderText("Current Level: " + level_name.str(), 300.0f, Height / 2 + 40.0f, 0.6f);
			Text->RenderText("After start  Press space to loose ball", 250.0f, Height / 2 + 60.0f, 0.5f);
		}
		if (this->State == GAME_WIN) {
			Text->RenderText("You WON!!!", 320.F, this->Height / 2.0f - 20.f, 1.0f, glm::vec3(0.0f, 1.0f, 0.0f));
			Text->RenderText("Press ENTER to retry or ESC to quit", 130.0f, this->Height / 2.0f, 1.0f, glm::vec3(1.0f, 1.0f, 0.0f));
		}
	}
}


void Game::ResetLevel() {
	std::string LvlDir = "E:\\VS_project\\OpenGL2DGame\\OpenGL2DGame\\levels\\";
	if (this->Level == 0)
		this->Levels[0].Load((LvlDir + "one.lvl").c_str(), this->Width, this->Height / 2);
	else if (this->Level == 1)
		this->Levels[1].Load((LvlDir + "two.lvl").c_str(), this->Width, this->Height / 2);
	else if (this->Level == 2)
		this->Levels[2].Load((LvlDir + "three.lvl").c_str(), this->Width, this->Height / 2);
	else if (this->Level == 3) 
		this->Levels[3].Load((LvlDir + "four.lvl").c_str(), this->Width, this->Height / 2);

	this->Lives = 3;   // 重置生命值为3
}
void Game::Resetplayer() {
	// reset player/ball stats
	Player->Size = PLAYER_SIZE;
	Player->Position = glm::vec2(this->Width / 2.0f - PLAYER_SIZE.x / 2.0f, this->Height - PLAYER_SIZE.y);
	Ball->Reset(Player->Position + glm::vec2(PLAYER_SIZE.x / 2.0f - BALL_RADIUS, -(BALL_RADIUS * 2.0f)), INITIAL_BALL_VELOCITY);

	// also disable all activate powerups
	Effects->Chaos = Effects->Confuse = false;
	Ball->PassThrough = Ball->Sticky = false;
	Player->Color = glm::vec3(1.0f);
	Ball->Color = glm::vec3(1.0f);
}



// power_ups
bool ShouldSpawn(unsigned int chance) {
	unsigned int random = rand() % chance;
	return random == 0;
}
void Game::SpawnPowerUps(GameObject &block) {
	//  这里的数字来决定各种道具出现的概率
	if (ShouldSpawn(75))  // 1 in 75 chance
		this->PowerUps.push_back(PowerUp("speed", glm::vec3(0.5f, 0.5f, 1.0f), 0.0f, block.Position, ResourceManager::GetTexture("powerup_speed")));
	if (ShouldSpawn(75))
		this->PowerUps.push_back(PowerUp("sticky", glm::vec3(1.0f, 0.5f, 1.0f), 20.0f, block.Position, ResourceManager::GetTexture("powerup_sticky")));
	if (ShouldSpawn(35))
		this->PowerUps.push_back(PowerUp("pass-through", glm::vec3(0.5f, 1.0f, 0.5f), 10.0f, block.Position, ResourceManager::GetTexture("powerup_passthrough")));
	if (ShouldSpawn(75))
		this->PowerUps.push_back(PowerUp("pad-size-increase", glm::vec3(1.0f, 0.6f, 0.4), 0.0f, block.Position, ResourceManager::GetTexture("powerup_increase")));
	
	if (ShouldSpawn(100)) // Negative powerups 出现的概率小一点
		this->PowerUps.push_back(PowerUp("confuse", glm::vec3(1.0f, 0.3f, 0.3f), 15.0f, block.Position, ResourceManager::GetTexture("powerup_confuse")));
	if (ShouldSpawn(100))
		this->PowerUps.push_back(PowerUp("chaos", glm::vec3(0.9f, 0.25f, 0.25f), 15.0f, block.Position, ResourceManager::GetTexture("powerup_chaos")));
}

void ActivatePowerUp(PowerUp &powerUp) {
	if (powerUp.Type == "speed") {
		Ball->Velocity *= 1.2;
	}
	else if (powerUp.Type == "sticky") {
		Ball->Sticky = true;
		Player->Color = glm::vec3(1.0f, 0.5f, 1.0f);
	}
	else if (powerUp.Type == "pass-through") {
		Ball->PassThrough == true;
		Ball->Color == glm::vec3(1.0f, 0.5f, 0.5f);
	}
	else if (powerUp.Type == "pad-size-increase") {
		Player->Size.x += 50;
	}
	else if (powerUp.Type == "confuse") {
		if (!Effects->Chaos)
			Effects->Confuse = true;  // only activate if chaos wasn't already active
	}
	else if (powerUp.Type == "chaos") {
		if (!Effects->Confuse)
			Effects->Chaos = true;
	}
}


bool IsotherPowerUpActivate(std::vector<PowerUp> &powerUps, std::string type);

void Game::UpdatePowerUps(float dt) {
	for (PowerUp &powerUp : this->PowerUps) {
		powerUp.Position += powerUp.Velocity * dt;
		if (powerUp.Activated) {
			powerUp.Duration -= dt;
			if (powerUp.Duration <= 0.0f) {
				// 之后会将这个道具移除
				powerUp.Activated = false;
				// 停用效果
				if (powerUp.Type == "sticky") {
					if (!IsotherPowerUpActivate(this->PowerUps, "sticky")) {
						// 仅当没有其他sticky效果处于激活状态时重置，以下同理
						Ball->Sticky = false;
						Player->Color = glm::vec3(1.0f);
					}
				}
				else if (powerUp.Type == "pass-through") {
					if (!IsotherPowerUpActivate(this->PowerUps, "pass-through")) {
						Ball->PassThrough = false;
						Ball->Color = glm::vec3(1.0f);
					}
				}
				else if (powerUp.Type == "confuse") {
					// only reset if no other PowerUp of type confuse is active
					if (!IsotherPowerUpActivate(this->PowerUps, "confuse")) {
						Effects->Confuse = false;
					}
				}
				else if (powerUp.Type == "chaos") {
					if (!IsotherPowerUpActivate(this->PowerUps, "chaos")) {
						Effects->Chaos == false;
					}
				}
			}
		}
	}
	// Remove all PowerUps from vector that are destroyed AND !activated (thus either off the map or finished)
	// Note we use a lambda expression to remove each PowerUp which is destroyed and not activated
	this->PowerUps.erase(
		std::remove_if(this->PowerUps.begin(), this->PowerUps.end(), 
			[](const PowerUp &mypoweUp) {return mypoweUp.Destroyed && !mypoweUp.Activated; }), 
		this->PowerUps.end()
	);
}

bool IsotherPowerUpActivate(std::vector<PowerUp> &powerUps, std::string type) {
	// Check if another PowerUp of the same type is still active
	// in which case we don't disable its effect (yet)
	for (const PowerUp &powerUp : powerUps) {
		if (powerUp.Activated) {
			if (powerUp.Type == type)
				return true;
		}
	}
	return false;
}


// collision detection
bool CheckCollision(GameObject &one, GameObject &two);    // AABB - AABB collision
Collision CheckCollision(BallObject &one, GameObject &two);  // AABB - Circle collision

// calculates which direction a vector is facing (N,E,S or W)
Direction VectorDirection(glm::vec2 closeset);  


void Game::DoCollisions() {
	for (GameObject &box : this->Levels[this->Level].Bricks) {
		if (!box.Destroyed) {
			Collision collision = CheckCollision(*Ball, box);
			if (std::get<0>(collision)) {  // if collision is true
				// destroy block if not solid
				if (!box.IsSolid) {
					box.Destroyed = GL_TRUE;
					this->SpawnPowerUps(box);
					SoundEigen->play2D("./resources/audio/bleep.mp3", false);
				}
				else {
					ShakeTime = 0.05f;
					Effects->Shake = true;
					SoundEigen->play2D("./resources/audio/bleep.mp3", false);
				}

				// 碰撞处理
				Direction dir = std::get<1>(collision);
				glm::vec2 diff_vector = std::get<2>(collision);
				// 当小球的PassThrough属性被设置为true时，我们不对非实心砖块做碰撞处理操作
				if (!(Ball->PassThrough && !box.IsSolid)) {
					if (dir == LEFT || dir == RIGHT) {   // 水平方向碰撞
						Ball->Velocity.x = -Ball->Velocity.x;   // 反转水平速度
						// 重定位
						GLfloat penetration = Ball->Radius - std::abs(diff_vector.x);
						if (dir == LEFT)
							Ball->Position.x += penetration;  // 将球右移
						else
							Ball->Position.x -= penetration;  // 将球左移
					}
					else {   // 垂直方向碰撞
						Ball->Velocity.y = -Ball->Velocity.y;  // 反转垂直速度
						GLfloat penetration = Ball->Radius - std::abs(diff_vector.y);
						if (dir == UP)
							Ball->Position.y -= penetration;  // 将球上移
						else
							Ball->Position.y += penetration;  // 将球下移
					}
				}
			}
		}
	}
	
	// also check collisions on PowerUps and if so, activate them
	for (PowerUp &powerUp : this->PowerUps) {
		if (!powerUp.Destroyed) {
			// first check if powerup passed bottom edge, if so: keep as inactive and destroy
			if (powerUp.Position.y >= this->Height)
				powerUp.Destroyed = true;

			if (CheckCollision(*Player, powerUp)) {
				// 道具与挡板接触，激活它！
				ActivatePowerUp(powerUp);
				powerUp.Destroyed = true;
				powerUp.Activated = true;
				SoundEigen->play2D("./resources/audio/powerup.wav", false);
			}
		}
	}

	//  check collisions for player pad (unless stuck)
	Collision result = CheckCollision(*Ball, *Player);
	if (!Ball->Stuck && std::get<0>(result)) {
		// 检查碰到了挡板的哪个位置，并根据碰到哪个位置来改变速度
		GLfloat centerBoard = Player->Position.x + Player->Size.x / 2;
		GLfloat distance = (Ball->Position.x + Ball->Radius) - centerBoard;
		GLfloat percentage = distance / (Player->Size.x / 2);

		// 依据结果移动
		GLfloat strength = 2.0f;
		glm::vec2 oldVelocity = Ball->Velocity;
		Ball->Velocity.x = INITIAL_BALL_VELOCITY.x * percentage * strength;
		Ball->Velocity.y = -Ball->Velocity.y;
		Ball->Velocity = glm::normalize(Ball->Velocity) * glm::length(oldVelocity);

		// fix sticky paddle
		Ball->Velocity.y = -1.0f * abs(Ball->Velocity.y);

		// if Sticky powerup is activated, also stick ball to paddle once new velocity vectors were calculated
		Ball->Stuck = Ball->Sticky;

		SoundEigen->play2D("./resources/audio/bleep.wav", false);
	}

}

bool CheckCollision(GameObject & one, GameObject & two) {
	// x轴碰撞检测
	bool collisionX = (one.Position.x + one.Size.x >= two.Position.x) &&
		(two.Position.x + two.Size.x >= one.Position.x);
	// y轴碰撞检测
	bool collisionY = (one.Position.y + one.Size.y >= two.Position.y) &&
		(two.Position.y + two.Size.y >= one.Position.y);
	return collisionX && collisionY;
}

Collision CheckCollision(BallObject & one, GameObject & two) {
	// 获取圆的中心
	glm::vec2 center(one.Position + one.Radius);
	// 计算AABB的信息（中心、半边长）
	glm::vec2 aabb_half_extents(two.Size.x / 2.0f, two.Size.y / 2.0f);
	glm::vec2 aabb_center(two.Position.x + aabb_half_extents.x, two.Position.y + aabb_half_extents.y);
	// 获取两个中心的差矢量 (注意这是矢量的计算)
	glm::vec2 difference = center - aabb_center;
	glm::vec2 clamped = glm::clamp(difference, -aabb_half_extents, aabb_half_extents);
	// AABB_center加上clamped这样就得到了碰撞箱上距离圆最近的点closest
	glm::vec2 closest = aabb_center + clamped;
	// 获得圆心center和最近点closest的矢量并判断是否 length <= radius
	difference = closest - center;   // 注意这是矢量的计算
	if (glm::length(difference) < one.Radius)
		return std::make_tuple(true, VectorDirection(difference), difference);
	else
		return std::make_tuple(false, UP, glm::vec2(0.0f, 0.0f));
}

// calculates which direction a vector is facing (N,E,S or W)
Direction VectorDirection(glm::vec2 target) {
	glm::vec2 compass[] = {
		glm::vec2(0.0f, 1.0f),   // up
		glm::vec2(1.0f, 0.0f),   // right
		glm::vec2(0.0f, -1.0f),  // down
		glm::vec2(-1.0f, 0.0f)   // left
	};
	float max = 0.0f;
	unsigned int best_match = -1;
	for (unsigned int i = 0; i < 4; i++) {
		float dot_product = glm::dot(glm::normalize(target), compass[i]);
		if (dot_product > max) {
			max = dot_product;
			best_match = i;
		}
	}
	return static_cast<Direction>(best_match);
}

