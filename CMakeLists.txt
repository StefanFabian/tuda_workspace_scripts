cmake_minimum_required(VERSION 3.5)
project(tuda_workspace_scripts)

find_package(ament_cmake REQUIRED)

if (WIN32)
  message(FATAL_ERROR "Windows is currently not supported! Feel free to add support :)")
else()
  ament_environment_hooks(env_hooks/setup.dsv.in)
  ament_environment_hooks(env_hooks/command.bash.in)
endif()

install(DIRECTORY scripts DESTINATION share/${PROJECT_NAME} USE_SOURCE_PERMISSIONS)

ament_package()
