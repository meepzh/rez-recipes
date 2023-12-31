cmake_minimum_required(VERSION 3.14)

include(FetchContent)
include(RezBuild)

set(AUTODESK_PACKAGE_NAME "ngskintools2")

# Show download progress
set(FETCHCONTENT_QUIET OFF)

# Download and unpack the ngSkinTools release
FetchContent_Declare(ngskintools URL $ENV{FETCH_URL})
FetchContent_MakeAvailable(ngskintools)

# Copy download to build directory to make it easier to compare and avoid
# redownloading
file(COPY "${ngskintools_SOURCE_DIR}/" DESTINATION ${ngskintools_BINARY_DIR})
file(RELATIVE_PATH build_subpath ${CMAKE_SOURCE_DIR} ${ngskintools_BINARY_DIR})

# Reduce components in PackageContents.xml
if(APPLE)
  set(MAYA_PACKAGE_PLATFORM "macOS")
elseif(WIN32)
  set(MAYA_PACKAGE_PLATFORM "win64")
else()
  set(MAYA_PACKAGE_PLATFORM $ENV{REZ_PLATFORM_VERSION})
endif()
if(UNIX)
  execute_process(COMMAND sed -i "/\\/Components/q"
                          "${ngskintools_BINARY_DIR}/PackageContents.xml")
endif()
file(
  APPEND "${ngskintools_BINARY_DIR}/PackageContents.xml"
  "
\t<Components>
\t\t<RuntimeRequirements SupportPath=\"./Contents/docs/\" OS=\"${MAYA_PACKAGE_PLATFORM}\" Platform=\"Maya\" SeriesMin=\"$ENV{REZ_MAYA_MAJOR_VERSION}\" SeriesMax=\"$ENV{REZ_MAYA_MAJOR_VERSION}\" />
\t\t<ComponentEntry ModuleName=\"./Contents/plug-ins/ngSkinTools2.so\" />
\t</Components>
</ApplicationPackage>")

# Prepare and install Python files
file(GLOB_RECURSE py_files "${ngskintools_BINARY_DIR}/*.py")
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
  ${AUTODESK_PACKAGE_NAME})

# Install the version-specific plug-ins
install(
  DIRECTORY
    "${ngskintools_BINARY_DIR}/Contents/plug-ins/$ENV{REZ_MAYA_MAJOR_VERSION}/"
  DESTINATION "${AUTODESK_PACKAGE_NAME}/Contents/plug-ins")

# Prepare and install other files next to the Python files
file(GLOB_RECURSE other_files "${ngskintools_BINARY_DIR}/*")
list(FILTER other_files EXCLUDE REGEX "\.py$")
list(FILTER other_files EXCLUDE REGEX "plug-ins")
rez_install_files(${other_files} RELATIVE ${build_subpath} DESTINATION
                  ${AUTODESK_PACKAGE_NAME})
