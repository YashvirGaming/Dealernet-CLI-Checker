@echo off
title Dealernet CLI Checker - Nuitka Builder
setlocal

set "SCRIPT=dealernet_checker.py"
set "OUT=Dealernet_CLI_Checker.exe"
set "ICON=icon.ico"

python -m pip install -U pip wheel setuptools

python -m nuitka ^
--standalone ^
--onefile ^
--windows-icon-from-ico=%ICON% ^
--jobs=12 ^
--output-filename="%OUT%" ^
"%SCRIPT%"

echo.
echo Build complete. Output: %OUT%
pause
