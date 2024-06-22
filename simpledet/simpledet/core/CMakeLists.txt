set( MODULE_NAME core )
set( LIBNAME simpledet_${MODULE_NAME} )

#message("IO LIBRARIES")

# Set the default verbosity of the compilation...
# set(CMAKE_VERBOSE_MAKEFILE TRUE)


# Define the source that should be used for the io part of edep-sim.
set(source
  PixelGrid.cxx
  Pixel2DReadout.cxx
  )

set(includes
  PixelGrid.h
  Pixel2DReadout.h
  )

# Compile the base library with private I/O fields.
#add_definitions(-DEDEPSIM_FORCE_PRIVATE_FIELDS)

# Make sure the current directories are available for the later
# compilation.  This is required to make ROOT_GENERATE_DICTIONARY
# work.
include_directories(
  "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>"
  )

# Build the dictionary for the i/o classes.
ROOT_GENERATE_DICTIONARY(G__${LIBNAME}
  PixelGrid.h
  Pixel2DReadout.h
  OPTIONS -inlineInputHeader
  LINKDEF ${LIBNAME}_LinkDef.h)

# Build the library.
add_library(${LIBNAME} SHARED ${source} G__${LIBNAME}.cxx)

target_include_directories(${LIBNAME} PUBLIC
  "$<INSTALL_INTERFACE:include/simpledet>")

target_link_libraries(${LIBNAME} PUBLIC ${ROOT_LIBRARIES})

# Install the library
install(TARGETS ${LIBNAME}
  EXPORT simpledet
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
  INCLUDES DESTINATION include/simpledet/${MODULE_NAME} )

# Install the header files.
install(FILES ${includes} DESTINATION include/simpledet/${MODULE_NAME})

# If this is ROOT6 or later, then install the rootmap and pcm files.
if(${ROOT_VERSION} VERSION_GREATER 6)
  install(FILES ${CMAKE_CURRENT_BINARY_DIR}/lib${LIBNAME}.rootmap
    DESTINATION lib)
  install(FILES ${CMAKE_CURRENT_BINARY_DIR}/lib${LIBNAME}_rdict.pcm
    DESTINATION lib)
endif(${ROOT_VERSION} VERSION_GREATER 6)

