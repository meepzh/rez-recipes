install(CODE "execute_process(COMMAND $ENV{PYTHON_EXE} -m pip install pymel --prefix ${CMAKE_INSTALL_PREFIX})")
install(CODE "execute_process(COMMAND $ENV{PYTHON_EXE} -m compileall ${CMAKE_INSTALL_PREFIX})")
