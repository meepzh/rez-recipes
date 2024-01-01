cmake_minimum_required(VERSION 3.14)

include(FetchContent)
include(RezBuild)

message(NOTICE "Building from SHAPES download file at: ${SHAPES_DOWNLOAD}")

FetchContent_Declare(shapes URL ${SHAPES_DOWNLOAD})
FetchContent_MakeAvailable(shapes)

# Copy download to build directory to make it easier to compare
file(COPY "${shapes_SOURCE_DIR}/" DESTINATION ${shapes_BINARY_DIR})
file(RELATIVE_PATH build_subpath ${CMAKE_SOURCE_DIR} ${shapes_BINARY_DIR})

list(APPEND shapes_modules "rampWeights" "SHAPES" "SHAPESBrush" "weightDriver")

# Generate new .mod files with only the platform being targeted
if(WIN32)
  set(maya_module_platform "win64")
else()
  set(maya_module_platform $ENV{REZ_PLATFORM_VERSION})
endif()
foreach(module ${shapes_modules})
  file(
    WRITE "${shapes_BINARY_DIR}/modules/${module}.mod"
    "+ MAYAVERSION:$ENV{REZ_MAYA_MAJOR_VERSION} PLATFORM:${maya_module_platform} \
      ${module} $ENV{REZ_BUILD_PROJECT_VERSION} ./${module}")
endforeach()

# Prepare and install Python files
file(GLOB_RECURSE py_files "${shapes_BINARY_DIR}/modules/*.py")
# rez_install_python hardcodes the executable name, so use install_python
# directly
install_python(
  py
  FILES
  ${py_files}
  RELATIVE
  "${build_subpath}/modules"
  BIN
  $ENV{PYTHON_EXE}
  DESTINATION
  .)

# Install the platform-specific plug-ins
if(APPLE)
  set(plug_in_subdir "macOS")
elseif(LINUX)
  set(plug_in_subdir "linux64")
else()
  set(plug_in_subdir ${maya_module_platform})
endif()
foreach(module ${shapes_modules})
  set(plug_in_path
      "modules/${module}/plug-ins/${plug_in_subdir}/$ENV{REZ_MAYA_MAJOR_VERSION}"
  )
  file(GLOB plug_ins "${shapes_BINARY_DIR}/${plug_in_path}/*")
  rez_install_files(${plug_ins} RELATIVE "${build_subpath}/${plug_in_path}"
                    DESTINATION "${module}/plug-ins")
endforeach()

# Prepare and install other files
file(GLOB_RECURSE other_files "${shapes_BINARY_DIR}/modules/*")
list(FILTER other_files EXCLUDE REGEX "\.py$")
list(FILTER other_files EXCLUDE REGEX "plug-ins")
rez_install_files(${other_files} RELATIVE "${build_subpath}/modules"
                  DESTINATION .)
