#include "game_level.h"

#include <iostream>
#include <fstream>
#include <sstream>


GameLevel::GameLevel() {
}


void GameLevel::Load(const char * file, unsigned int levelWidth, unsigned levelHeight) {
	// clear old data
	this->Bricks.clear();
	// load from file
	unsigned int tileCode;
	GameLevel level;
	std::string line;
	std::ifstream fstream(file);
	std::vector<std::vector<unsigned int>> tileData;
	if (fstream) {
		while (std::getline(fstream, line)) {
			std::istringstream sstream(line);
			std::vector<unsigned int> row;
			while (sstream >> tileCode) {
				row.push_back(tileCode);
			}
			tileData.push_back(row);
		}

		if (tileData.size() > 0) {
			this->init(tileData, levelWidth, levelHeight);
		}
	}
	else {
		std::cout << "Can not find file: " << file << std::endl;
	}
	
}

void GameLevel::Draw(SpriteRenderer &renderer) {
	for (GameObject &tile : this->Bricks) {
		if (!tile.Destroyed)
			tile.Draw(renderer);
	}
}

bool GameLevel::IsCompleted() {
	for (GameObject &tile : this->Bricks) {
		if (!tile.IsSolid && !tile.Destroyed)
			return false;
	}
	return true;
}

void GameLevel::init(std::vector<std::vector<unsigned int>> tileData, unsigned int levelWidth, unsigned int levelHeight) {
	// calculate dimensions
	unsigned int height = tileData.size();
	unsigned int width = tileData.at(0).size();
	float unit_width = levelWidth / static_cast<float>(width);
	float unit_height = levelHeight / static_cast<float>(height);
	// initialize level tiles based on tileData		
	for (unsigned int y = 0; y < height; ++y) {
		for (unsigned int x = 0; x < width; ++x) {
			glm::vec2 pos(unit_width * x, unit_height * y);
			glm::vec2 size(unit_width, unit_height);
			// 检查砖块类型
			unsigned int BrickType = tileData[y][x];
			if (BrickType == 1) {  // solid
				GameObject obj(pos, size, ResourceManager::GetTexture("block_solid"), glm::vec3(0.8f, 0.8f, 0.7f));
				obj.IsSolid = true;     //  这种类型就代表不可摧毁，其它的碰撞了就可以摧毁
				this->Bricks.push_back(obj);
			}
			else if (BrickType > 1) {
				glm::vec3 color = glm::vec3(1.0f);  // 默认白色
				if (BrickType == 2)
					color = glm::vec3(0.2f, 0.6f, 1.0f);
				else if (BrickType == 3)
					color = glm::vec3(0.0f, 0.7f, 0.0f);
				else if (BrickType == 4)
					color = glm::vec3(0.8f, 0.8f, 0.4f);
				else if (BrickType == 5)
					color = glm::vec3(1.0f, 0.5f, 0.0f);
				
				this->Bricks.push_back(GameObject(pos, size, ResourceManager::GetTexture("block"), color));
			}
		}
	}

}
