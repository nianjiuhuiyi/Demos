cmake_minimum_required (VERSION 3.5)

project ("my_glfw_opengl3")

set(CMAKE_BUILD_TYPE Release)


# 添加glfwd的头文件及库路径
include_directories(./3rdparty/glfw/include/)
link_directories(./3rdparty/glfw/lib/lib-vc2017)

# 添加自己相关的头文件
include_directories(./include)


set(OpenCV_DIR D:/lib/opencv_4.5.3/build/x64/vc15/lib)
FIND_PACKAGE( OpenCV REQUIRED )


aux_source_directory(./src IMGUI_SRC)

add_executable( main ${IMGUI_SRC} )
target_link_libraries( main PRIVATE ${OpenCV_LIBS}  "glfw3.lib" "opengl32.lib")



# 若想在liunx上编译，也是需要glfw库的(linux的要自己去编译)，也会是需要opengl库的，
# 具体使用写法，可以参考这个项目：https://github.com/WerWolv/ImHex/blob/master/lib/external/imgui/CMakeLists.txt
