@echo off
echo Starting Unitree Go2-W Development Environment...

docker run -it --rm --network host ^
  -v "C:\Development\Unitree_Go2_Development:/workspace/development" ^
  -v "%cd%:/workspace/current" ^
  -w /workspace/development ^
  --name unitree-robotics-dev ^
  unitree-robot bash

pause