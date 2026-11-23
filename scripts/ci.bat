@echo off
rem CI build script for Windows.
rem Installs dependencies, builds, runs unit tests and produces the executable bin\hello.exe.
setlocal
cd /d "%~dp0\.."

echo == Environment
call node --version || exit /b 1
call npm --version || exit /b 1

echo == Install dependencies
call npm ci || exit /b 1

echo == Build
call npm run build || exit /b 1

echo == Unit tests
call npm test || exit /b 1

echo == Package executable
call npm run package || exit /b 1

echo == Run executable
bin\hello.exe || exit /b 1

echo == CI finished successfully
endlocal
