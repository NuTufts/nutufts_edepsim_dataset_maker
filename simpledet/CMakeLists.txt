cmake_minimum_required(VERSION 3.10)
project(simpledet VERSION 0.1)

set(CMAKE_BUILD_TYPE Debug)

#---Install location by default is in the build directory
if (CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
    set (CMAKE_INSTALL_PREFIX "${CMAKE_BINARY_DIR}" CACHE PATH "${CMAKE_BUILD_DIR}" FORCE )
endif()


set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")

## Dependencies

#---CERN ROOT (required)
find_package(ROOT REQUIRED)
# we set the compiler version based on the one used for ROOT
execute_process(
    COMMAND bash "-c" "root-config --features | awk '{print $1}'"
    OUTPUT_VARIABLE ROOT_CXX_STANDARD )
if (${ROOT_CXX_STANDARD} MATCHES "cxx17")
  message( STATUS "using cxx17")
  set(CMAKE_CXX_STANDARD 17)
elseif (${ROOT_CXX_STANDARD} MATCHES "cxx14")
  message(STATUS "using cxx14")
  set(CMAKE_CXX_STANDARD 14)
else ()
  message( STATUS "using cxx11")  
  set(CMAKE_CXX_STANDARD 11)
endif()
include(${ROOT_USE_FILE})

#--- EDEPSIM (required) ---
set(  EDEPSIM_DIR $ENV{EDEPSIM_DIR}/share/EDepSim )
find_package(EDepSim REQUIRED)

#--- Vectorclass headers --
set( VECTORCLASS_INCLUDE_DIR $ENV{VECTORCLASS_INCLUDE_DIR} )


#---Python
find_package( PythonInterp 3 REQUIRED )
find_package( PythonLibs 3 REQUIRED )
execute_process( COMMAND python3 -c "import numpy; print(numpy.get_include())" OUTPUT_VARIABLE NUMPY_INCLUDES OUTPUT_STRIP_TRAILING_WHITESPACE )    

#---Eigen
#find_package(Eigen3 REQUIRED)

#--- glog
#find_package(glog)

#-- OpenMP
find_package(OpenMP)
if (OPENMP_FOUND)
    set (CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
    set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
    set (CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${OpenMP_EXE_LINKER_FLAGS}")
endif()

## Setup


## Add Source

#---Add base of source
add_subdirectory(simpledet)

#---Configuration export
include(CMakePackageConfigHelpers)
set(SIMPLEDET_INCLUDE_DIR "${CMAKE_INSTALL_PREFIX}/include")
set(SIMPLEDET_LIBRARY_DIR "${CMAKE_INSTALL_PREFIX}/lib")
set(SIMPLEDET_BASE_DIR "${CMAKE_INSTALL_PREFIX}")
set(TARGETS_EXPORT_NAME "simpledetTargets")
configure_package_config_file("cmake/Config.cmake.in"
  "${CMAKE_BINARY_DIR}/cmake/simpledetConfig.cmake"
  INSTALL_DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/simpledet"
  PATH_VARS SIMPLEDET_INCLUDE_DIR SIMPLEDET_LIBRARY_DIR SIMPLEDET_BASE_DIR)
write_basic_package_version_file("${CMAKE_BINARY_DIR}/cmake/simpledetConfigVersion.cmake"
  COMPATIBILITY SameMajorVersion)


#---Create info to include simpledet in other cmake files
install(EXPORT simpledet
        FILE simpledetTargets.cmake 
        DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/simpledet")

#---Create info to include simpledet in other cmake files
install(FILES "${CMAKE_BINARY_DIR}/cmake/simpledetConfig.cmake"
  "${CMAKE_BINARY_DIR}/cmake/simpledetConfigVersion.cmake"
  DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/simpledet")







