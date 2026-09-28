@echo off
REM SEB-XRIF launcher for Windows.
REM
REM Prerequisites (see README "Windows setup"):
REM   Git for Windows (includes Git Bash), uv, Node.js 20+, pnpm.
REM
REM Double-click or run:  scripts\run.cmd
REM This finds Git Bash and runs the POSIX run script inside it.

setlocal
set "ROOT=%~dp0.."

if not exist "%ROOT%\scripts\run.sh" (
  echo Could not find scripts\run.sh - run this from the repository.
  exit /b 1
)

set "BASH=%ProgramFiles%\Git\bin\bash.exe"
if not exist "%BASH%" set "BASH=%ProgramFiles(x86)%\Git\bin\bash.exe"
if not exist "%BASH%" set "BASH=%LocalAppData%\Programs\Git\bin\bash.exe"

if not exist "%BASH%" (
  echo Git Bash was not found. Install Git for Windows: https://git-scm.com/download/win
  exit /b 1
)

"%BASH%" -lc "cd \"$ROOT\" && ./scripts/run.sh %*"
endlocal
