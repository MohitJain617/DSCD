@echo off

SET dir_name=file_system

IF EXIST %dir_name% (
    rmdir /S /Q %dir_name%
)

mkdir %dir_name%