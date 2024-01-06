cmake_minimum_required(VERSION 3.14)

include(FetchContent)
include(RezBuild)

# Show download progress
set(FETCHCONTENT_QUIET OFF)

# Download and unpack the mGear release
FetchContent_Declare(mgear URL $ENV{FETCH_URL})
FetchContent_MakeAvailable(mgear)

# Copy download to build directory to make it easier to compare and avoid
# redownloading
file(COPY "${mgear_SOURCE_DIR}/release/" DESTINATION ${mgear_BINARY_DIR})
file(RELATIVE_PATH build_subpath ${CMAKE_SOURCE_DIR} ${mgear_BINARY_DIR})

# Generate a new .mod file with only the platform being targeted
if(WIN32)
  set(maya_module_platform "win64")
else()
  set(maya_module_platform $ENV{REZ_PLATFORM_VERSION})
endif()
file(
  WRITE "${mgear_BINARY_DIR}/mGear.mod"
  "+ MAYAVERSION:$ENV{REZ_MAYA_MAJOR_VERSION} PLATFORM:${maya_module_platform} \
    $ENV{REZ_BUILD_PROJECT_NAME} $ENV{REZ_BUILD_PROJECT_VERSION} .")

# Prepare and install Python files
file(GLOB_RECURSE py_files "${mgear_BINARY_DIR}/scripts/*.py")
foreach(py_file ${py_files})
  if(UNIX)
    execute_process(COMMAND dos2unix --keepdate --oldfile ${py_file})
    # Some files have not been made Python 3 compatible
    execute_process(COMMAND sed -i -E "s/^(\\s+)print (.+)/\\1print(\\2)/"
                            ${py_file})
  endif(UNIX)
endforeach()
# rez_install_python hardcodes the executable name, so use install_python
# directly
install_python(
  py
  FILES
  ${py_files}
  RELATIVE
  ${build_subpath}
  BIN
  $ENV{PYTHON_EXE}
  DESTINATION
  .)

# Prepare and install other script files next to the Python files
file(GLOB_RECURSE script_files "${mgear_BINARY_DIR}/scripts/*")
list(FILTER script_files EXCLUDE REGEX "\.py$")
rez_install_files(${script_files} RELATIVE ${build_subpath} DESTINATION .)

# Install icons
rez_install_dirs("${mgear_BINARY_DIR}/icons" DESTINATION .)

# Install the platform-specific plug-ins
rez_install_dirs(
  "${mgear_BINARY_DIR}/platforms/$ENV{REZ_MAYA_MAJOR_VERSION}/$ENV{REZ_PLATFORM_VERSION}/x64/"
  DESTINATION
  .)

# Install the custom .mod file
rez_install_files("${mgear_BINARY_DIR}/mGear.mod" RELATIVE ${build_subpath}
                  DESTINATION .)
