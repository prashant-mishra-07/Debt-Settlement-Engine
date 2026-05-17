# CMakeLists.txt for Debt Settlement Engine - Core Algorithmic Engine
# C++17, Graph-based Cash Flow Minimization Algorithm

cmake_minimum_required(VERSION 3.15)
project(DebtOptimizer VERSION 1.0.0 LANGUAGES CXX)

# Set C++ standard (C++14 for compatibility with older compilers)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Compiler flags
if(MSVC)
    # Windows/MSVC flags
    if(CMAKE_BUILD_TYPE STREQUAL "Release")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /O2")
    elseif(CMAKE_BUILD_TYPE STREQUAL "Debug")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /W4")
    endif()
else()
    # GCC/Clang flags
    if(CMAKE_BUILD_TYPE STREQUAL "Release")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native")
    elseif(CMAKE_BUILD_TYPE STREQUAL "Debug")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -Wall -Wextra")
    endif()
endif()

# Include directories
include_directories(${PROJECT_SOURCE_DIR}/include)

# Source files
set(SOURCES
    src/main.cpp
    src/optimizer.cpp
)

# Header files
set(HEADERS
    include/optimizer.hpp
)

# Create executable
add_executable(debt_optimizer ${SOURCES} ${HEADERS})

# Link libraries
# Add JSON library (nlohmann/json) - to be added in Phase 2
# target_link_libraries(debt_optimizer PRIVATE nlohmann_json::nlohmann_json)

# Installation rules
install(TARGETS debt_optimizer DESTINATION bin)

# Testing (optional - to be added in Phase 3)
# enable_testing()
# add_subdirectory(tests)
