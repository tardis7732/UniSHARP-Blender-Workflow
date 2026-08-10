# UniSHARP Blender - first-run guide

## First: install Blender 5.2 LTS

**Blender 5.2 LTS must be installed before running UniSHARP.** Install the Windows version from Blender's official LTS page, then return here and double-click `Run-UniSHARP.cmd`.

- [Blender LTS download](https://www.blender.org/download/lts/)

Run `Run-UniSHARP.cmd`. It creates a private Python environment in `.runtime`, then downloads the CUDA-enabled PyTorch package and the remaining Python libraries. It does not modify the system Python installation.

## Automatic NVIDIA / CUDA installer

- `Run-UniSHARP.cmd` is the only file you need to run. It checks Blender, the NVIDIA driver, Python, and PyTorch in order.
- If Blender 5.2 LTS or the NVIDIA driver/CUDA is missing, it asks for approval, downloads the official installer, and starts it automatically.
- After a CUDA/driver installation, restart Windows, then double-click `Run-UniSHARP.cmd` again.

## Required hardware

- Windows 10/11 64-bit
- NVIDIA GPU with a current NVIDIA driver
- Enough free disk space for the 4.7 GB checkpoint plus the Python/CUDA runtime (allow 15 GB free)
- Blender **5.2 LTS** installed. The launcher detects normal Blender installations automatically; set `BLENDER_EXE` if it is installed elsewhere.

## If the NVIDIA driver is missing

Install the current driver for the GPU, reboot, then run `Run-UniSHARP.cmd` again.

- [NVIDIA driver download](https://www.nvidia.com/Download/index.aspx)

## CUDA Toolkit and build tools

The downloaded PyTorch CUDA wheel already contains the CUDA runtime, so a separate CUDA Toolkit is normally unnecessary. If first run reports `nvcc` or a C++ compiler error while building a dependency, install both of the following and re-run the launcher.

- [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) - select **Desktop development with C++**

## Offline use

Complete the first run while connected to the internet. After `.runtime` has been created successfully, the package can run offline.
