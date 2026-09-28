@echo off
REM SEB-XRIF bootstrap for Windows (installs deps). See README "Windows setup".

setlocal
set "ROOT=%~dp0.."

set "BASH=%ProgramFiles%\Git\bin\bash.exe"
if not exist "%BASH%" set "BASH=%ProgramFiles(x86)%\Git\bin\bash.exe"
if not exist "%BASH%" set "BASH=%LocalAppData%\Programs\Git\bin\bash.exe"

if not exist "%BASH%" (
  echo Git Bash was not found. Install Git for Windows: https://git-scm.com/download/win
  exit /b 1
)

"%BASH%" -lc "cd \"$ROOT\" && ./scripts/bootstrap.sh"
endlocal
