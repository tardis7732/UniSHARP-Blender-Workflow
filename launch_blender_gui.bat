@echo off
call "C:\BuildTools\Common7\Tools\VsDevCmd.bat" -arch=x64 -host_arch=x64
set "CUDA_HOME=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8"
set "TORCH_CUDA_ARCH_LIST=12.0"
set "TORCH_EXTENSIONS_DIR=%~dp0build\torch_extensions"
set "PATH=C:\Users\AIRev\Desktop\RnD\miniforge3\envs\unisharp;C:\Users\AIRev\Desktop\RnD\miniforge3\envs\unisharp\Scripts;%CUDA_HOME%\bin;%PATH%"
"C:\Users\AIRev\Desktop\RnD\miniforge3\envs\unisharp\python.exe" "%~dp0scripts\blender_gui.py"
pause
