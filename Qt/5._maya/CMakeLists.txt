cmake_minimum_required(VERSION 3.14)

include(FetchContent)
include(RezBuild)

if(DEFINED ENV{QT_CMAKE_TAR_PATH})
  message(NOTICE "Installing CMake files from: $ENV{QT_CMAKE_TAR_PATH}")
  FetchContent_Declare(qt_cmake URL $ENV{QT_CMAKE_TAR_PATH})
  FetchContent_MakeAvailable(qt_cmake)

  file(GLOB_RECURSE files "${qt_cmake_SOURCE_DIR}/*")
  file(RELATIVE_PATH build_subpath ${CMAKE_SOURCE_DIR} ${qt_cmake_SOURCE_DIR})
  rez_install_files(${files} RELATIVE ${build_subpath} DESTINATION "cmake")
else()
  message(WARNING "No CMake files to install")
  install(DIRECTORY DESTINATION "cmake")
endif()
