
cmake_minimum_required(VERSION 3.13.4)

set(PYTHON_VERSION "3.6.7" CACHE STRING "The version of Python to build.")
set(PYTHON_DIR /opt/li-asterisk/tools/Python-${PYTHON_VERSION})

set(CMAKE_INSTALL_PREFIX "/opt/ali")


execute_process(COMMAND bash -c 
    "if [ -d 'build' ]; then
        rm -rf build

    fi"
)

execute_process (

    COMMAND bash -c "mkdir build"
)

execute_process (
    COMMAND bash -c "cp -p -R ${CMAKE_CURRENT_BINARY_DIR}/asterisk-li/ build/"
)


execute_process (
    COMMAND bash -c "mkdir -p ${CMAKE_CURRENT_BINARY_DIR}/build/asterisk-li/logs"
)

execute_process(COMMAND bash -c "${PYTHON_DIR}/bin/python3 -m compileall -b build/asterisk-li/")


execute_process(COMMAND bash -c "rm build/asterisk-li/*.py")
execute_process(COMMAND bash -c "rm build/asterisk-li/modules/*.py")
execute_process(COMMAND bash -c "rm build/asterisk-li/modules/adm_function/*.py")
execute_process(COMMAND bash -c "rm build/asterisk-li/modules/adm_function/user_interface/simple/*.py")
execute_process(COMMAND bash -c "rm build/asterisk-li/modules/asterisk/*.py")
execute_process(COMMAND bash -c "rm build/asterisk-li/modules/asterisk/cc/*.py")
execute_process(COMMAND bash -c "rm build/asterisk-li/modules/asterisk/iri/*.py")
execute_process(COMMAND bash -c "rm build/asterisk-li/modules/asterisk/events/*.py")
execute_process(COMMAND bash -c "rm build/asterisk-li/modules/asterisk/register/*.py")
execute_process(COMMAND bash -c "rm build/asterisk-li/modules/asterisk/server/*.py")
execute_process(COMMAND bash -c "rm build/asterisk-li/modules/asterisk/sniffer/*.py")
execute_process(COMMAND bash -c "rm build/asterisk-li/modules/mediation_function/*.py")
execute_process(COMMAND bash -c "rm build/asterisk-li/modules/mediation_function/cdr/*.py")
execute_process(COMMAND bash -c "rm build/asterisk-li/modules/mediation_function/evidences/*.py")


execute_process(COMMAND bash -c "chmod +x build/asterisk-li/init/*")

install(DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/build/asterisk-li/modules/adm_function/conf" DESTINATION ".")
install(DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/build/asterisk-li/modules/asterisk/conf" DESTINATION ".")

install(DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/build/asterisk-li/modules/mediation_function/conf" DESTINATION ".")

install(DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/build/asterisk-li/logs" DESTINATION ".")

install(DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/build/asterisk-li/library" DESTINATION ".")

install(DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/build/asterisk-li/modules" DESTINATION ".")

install(DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/build/asterisk-li/init" DESTINATION "." USE_SOURCE_PERMISSIONS)

install(FILES "${CMAKE_CURRENT_BINARY_DIR}/build/asterisk-li/module_adm.pyc" DESTINATION ${CMAKE_INSTALL_PREFIX})
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/build/asterisk-li/module_asterisk.pyc" DESTINATION ${CMAKE_INSTALL_PREFIX})

install(FILES "${CMAKE_CURRENT_BINARY_DIR}/build/asterisk-li/module_mediation.pyc" DESTINATION ${CMAKE_INSTALL_PREFIX})





