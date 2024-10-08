#include "imgui.h"
#include "imgui_impl_glfw.h"
#include "imgui_impl_opengl3.h"
#include <stdio.h>
#if defined(IMGUI_IMPL_OPENGL_ES2)
#include <GLES2/gl2.h>
#endif
#include <GLFW/glfw3.h> // Will drag system OpenGL headers

#include "yolov5.hpp"

//const std::string videoStreamAddress = "rtsp://192.168.108.11:554/user=admin&password=&channel=1&stream=1.sdp?";


//视频的处理，cv的Mat转成opengl要得格式
void Mat2Texture(cv::Mat &image, GLuint &imageTexture) {
	if (image.empty()) return;

	//generate texture using GL commands
	glBindTexture(GL_TEXTURE_2D, imageTexture);

	// Setup filtering parameters for display
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.cols, image.rows, 0, GL_RGB, GL_UNSIGNED_BYTE, image.data);
}


#if defined(_MSC_VER) && (_MSC_VER >= 1900) && !defined(IMGUI_DISABLE_WIN32_FUNCTIONS)
#pragma comment(lib, "legacy_stdio_definitions")
#endif

static void glfw_error_callback(int error, const char* description)
{
	fprintf(stderr, "Glfw Error %d: %s\n", error, description);
}




int main(int argc, char** argv)
{
	// Setup window
	glfwSetErrorCallback(glfw_error_callback);
	if (!glfwInit())
		return 1;

	// Decide GL+GLSL versions
#if defined(IMGUI_IMPL_OPENGL_ES2)
	// GL ES 2.0 + GLSL 100
	const char* glsl_version = "#version 100";
	glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 2);
	glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);
	glfwWindowHint(GLFW_CLIENT_API, GLFW_OPENGL_ES_API);
#elif defined(__APPLE__)
	// GL 3.2 + GLSL 150
	const char* glsl_version = "#version 150";
	glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
	glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 2);
	glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);  // 3.2+ only
	glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);            // Required on Mac
#else
	// GL 3.0 + GLSL 130
	const char* glsl_version = "#version 130";
	glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
	glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);
	//glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);  // 3.2+ only
	//glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);            // 3.0+ only
#endif

	// Create window with graphics context
	GLFWwindow* window = glfwCreateWindow(1280, 720, "Dear ImGui GLFW+OpenGL3 example", NULL, NULL);
	if (window == NULL)
		return 1;
	glfwMakeContextCurrent(window);
	glfwSwapInterval(1); // Enable vsync

	// Setup Dear ImGui context
	IMGUI_CHECKVERSION();
	ImGui::CreateContext();
	ImGuiIO& io = ImGui::GetIO(); (void)io;
	//io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;     // Enable Keyboard Controls
	//io.ConfigFlags |= ImGuiConfigFlags_NavEnableGamepad;      // Enable Gamepad Controls

	// Setup Dear ImGui style
	//ImGui::StyleColorsDark();
	// ImGui::StyleColorsLight();
	ImGui::StyleColorsClassic();

	// Setup Platform/Renderer backends
	ImGui_ImplGlfw_InitForOpenGL(window, true);
	ImGui_ImplOpenGL3_Init(glsl_version);

	// Load Fonts  // 加载其它字体，其demo它文件里也有
	// 注意执行路径时，和这相对路径对不对应，可以添加几种字体，进到style中可以修改
	io.Fonts->AddFontFromFileTTF("JetBrainsMono-Bold.ttf", 16.0f);
	//io.Fonts->AddFontFromFileTTF("E:\\VS_project\\my_glfw_opengl3\\res\\JetBrainsMono-Bold.ttf", 16.0f);
	// 字体要支持汉字才行
	io.Fonts->AddFontFromFileTTF("c:/windows/fonts/simhei.ttf", 13.0f, NULL, io.Fonts->GetGlyphRangesChineseSimplifiedCommon());

	// Our state
	bool show_demo_window = false;
	bool show_videoCapture_window = true;  // my

	ImVec4 clear_color = ImVec4(0.45f, 0.55f, 0.60f, 1.00f);

	cv::VideoCapture cap;
	if (argc == 1) {
		cap.open(0);
	}
	else if (argc == 2) {
		// 一定要下面这么写。如果写成 cv::VideoCapture cap(rtsp地址或视频地址);这种，会读取失败
		cap.open(argv[1]);
	}
	else {
		printf("Usage: main.exe [video_path], \tdefalut 0 which means cream\n");
		return 1;
	}

	GLuint video_texture = 0;
	cv::Mat frame;

	cv::dnn::Net net;
	std::vector<std::string> class_list;
	loadModle("yolov5s.onnx", "coco.names", &net, &class_list);
	//loadModle("E:\\VS_project\\my_glfw_opengl3\\res\\coco.names", "E:\\VS_project\\my_glfw_opengl3\\res\\yolov5s.onnx", &net, &class_list);


	// Main loop
	while (!glfwWindowShouldClose(window)) {
		// 我把它的一些注释删了，，去它的demo里看就好
		glfwPollEvents();

		// Start the Dear ImGui frame
		ImGui_ImplOpenGL3_NewFrame();
		ImGui_ImplGlfw_NewFrame();
		ImGui::NewFrame();

		// 1. Show the big demo window (Most of the sample code is in ImGui::ShowDemoWindow()! You can browse its code to learn more about Dear ImGui!).
		if (show_demo_window)
			ImGui::ShowDemoWindow(&show_demo_window);

		// 2. Show a simple window that we create ourselves. We use a Begin/End pair to created a named window.
		{
			static float f = 0.0f;
			static int counter = 0;

			ImGui::Begin("Hello, world!");                          // Create a window called "Hello, world!" and append into it.

			ImGui::Text("This is some useful text.");               // Display some text (you can use a format strings too)
			ImGui::Checkbox("Demo Window", &show_demo_window);      // Edit bools storing our window open/close state

			// my function of videoCapture
			ImGui::Checkbox("VideoCapture Window", &show_videoCapture_window);

			ImGui::SliderFloat("float", &f, 0.0f, 1.0f);            // Edit 1 float using a slider from 0.0f to 1.0f
			ImGui::ColorEdit3("clear color", (float*)&clear_color); // Edit 3 floats representing a color

			if (ImGui::Button("Button"))                            // Buttons return true when clicked (most widgets return true when edited/activated)
				counter++;
			ImGui::SameLine();
			ImGui::Text("counter = %d", counter);

			ImGui::Text("Application average %.3f ms/frame (%.1f FPS)", 1000.0f / ImGui::GetIO().Framerate, ImGui::GetIO().Framerate);
			ImGui::End();
		}

		// my video and detect
		{
			if (show_videoCapture_window) {

				static bool if_detect = false;
				static bool show_style_editor = false;


				if (!cap.isOpened()) {
					printf("cream open failed!\n");
					break;
				}

				if (show_style_editor) {
					ImGui::Begin("Dear ImGui Style Editor", &show_style_editor);
					ImGui::ShowStyleEditor();
					ImGui::End();
				}

				cap >> frame;  //cap.read(frame);

				ImGui::Begin(u8"OpenGL Texture video，汉字可以嘛");  // 主要前面要有u8才能支持汉字
				ImGui::Text("size = %d x %d", frame.cols, frame.rows);

				// 检测目标 (这一句虽然简单，但还是一定要加大括号{},不然cmake那种来做的时候会报错，缺括号，只有很简单的语句才能不要大括号)
				if (if_detect) { frame = detect(net, class_list, frame); }
					  

				cv::cvtColor(frame, frame, cv::COLOR_BGR2RGB);
				Mat2Texture(frame, video_texture);
				ImGui::Image((void*)(intptr_t)video_texture, ImVec2(frame.cols, frame.rows));

				ImGui::Checkbox("Detect", &if_detect);
				ImGui::SameLine();  // 这个可以把两个button放在一行里
				ImGui::Checkbox("Style Editor", &show_style_editor);
				ImGui::End();
			}
		}

		// Rendering
		ImGui::Render();
		int display_w, display_h;
		glfwGetFramebufferSize(window, &display_w, &display_h);
		glViewport(0, 0, display_w, display_h);
		glClearColor(clear_color.x * clear_color.w, clear_color.y * clear_color.w, clear_color.z * clear_color.w, clear_color.w);
		glClear(GL_COLOR_BUFFER_BIT);
		ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());

		glfwSwapBuffers(window);
	}

	// Cleanup
	ImGui_ImplOpenGL3_Shutdown();
	ImGui_ImplGlfw_Shutdown();
	ImGui::DestroyContext();

	glfwDestroyWindow(window);
	glfwTerminate();

	cap.release();

	return 0;
}


/*
	不用opencv，可以直接加载图片，现在仅会图片

// 这是为了显示图像,这是加加载图片要用，如果用opencv，就可以不要这个了
#define STB_IMAGE_IMPLEMENTATION   // 下面这个头文件要用的
#include "stb_image.h"     // 这个头文件是到处通用的，用opengl来加载图像
// 直接OPENGL加载图片 （或许可以考虑opencv来处理吧）
bool LoadTextureFromFile(const char* filename, GLuint* out_texture, int* out_width, int* out_height)
{
	// Load from file
	int image_width = 0;
	int image_height = 0;
	unsigned char* image_data = stbi_load(filename, &image_width, &image_height, NULL, 4);
	if (image_data == NULL)
		return false;

	// Create a OpenGL texture identifier  //generate texture using GL commands
	GLuint image_texture;
	glGenTextures(1, &image_texture);
	glBindTexture(GL_TEXTURE_2D, image_texture);

	// Setup filtering parameters for display
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

	// Upload pixels into texture
#if defined(GL_UNPACK_ROW_LENGTH) && !defined(__EMSCRIPTEN__)
	glPixelStorei(GL_UNPACK_ROW_LENGTH, 0);
#endif
	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width, image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data);
	stbi_image_free(image_data);

	*out_texture = image_texture;
	*out_width = image_width;
	*out_height = image_height;

	return true;
}



	// 加载图像(tag:123)
	int my_image_width = 0;
	int my_image_height = 0;
	GLuint my_image_texture = 0;
	bool ret = LoadTextureFromFile("C:\\Users\\Administrator\\Pictures\\dog.jpg", &my_image_texture, &my_image_width, &my_image_height);
	IM_ASSERT(ret);



			//// 加载图像(tag:123)
		//ImGui::Begin("OpenGL Texture Text");
		//ImGui::Text("pointer = %p", my_image_texture);
		//ImGui::Text("size = %d x %d", my_image_width, my_image_height);
		//printf("地址：？%p", my_image_texture);
		//ImGui::Image((void*)(intptr_t)my_image_texture, ImVec2(my_image_width, my_image_height));
		//ImGui::End();
*/