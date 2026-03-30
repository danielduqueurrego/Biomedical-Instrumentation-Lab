@echo off
setlocal

REM Beginner doctor command for Windows students.
set "REPO_DIR=%~dp0"
set "PYTHON_DIR=%REPO_DIR%python"
set "TARGET_SCRIPT=%PYTHON_DIR%\run_student_doctor.py"

set "CONDA_EXE="
where conda >nul 2>nul
if not errorlevel 1 (
  for /f "delims=" %%i in ('where conda') do (
    set "CONDA_EXE=%%i"
    goto :conda_found
  )
)

for %%i in (
  "%USERPROFILE%\miniconda3\Scripts\conda.exe"
  "%USERPROFILE%\anaconda3\Scripts\conda.exe"
  "%USERPROFILE%\mambaforge\Scripts\conda.exe"
  "C:\ProgramData\miniconda3\Scripts\conda.exe"
  "C:\ProgramData\anaconda3\Scripts\conda.exe"
) do (
  if exist %%~i (
    set "CONDA_EXE=%%~i"
    goto :conda_found
  )
)

echo ERROR: Conda was not found on PATH or common install locations.
echo Install Miniconda or Anaconda, open a new Command Prompt, and try again.
echo Setup steps:
echo   1^) cd /d "%PYTHON_DIR%"
echo   2^) conda env create -f environment.yml
echo   3^) Re-run: launch_student_doctor_windows.bat
exit /b 1

:conda_found
for %%i in ("%CONDA_EXE%") do set "CONDA_SCRIPTS_DIR=%%~dpi"
set "CONDA_BAT=%CONDA_SCRIPTS_DIR%..\condabin\conda.bat"

if not exist "%CONDA_BAT%" (
  echo ERROR: Conda activation helper was not found:
  echo   "%CONDA_BAT%"
  echo Please verify your Conda installation, then try again.
  exit /b 1
)

call "%CONDA_BAT%" activate biomed-lab >nul 2>nul
if errorlevel 1 (
  echo ERROR: Conda environment "biomed-lab" is missing or failed to activate.
  echo Create it once, then run this launcher again:
  echo   1^) cd /d "%PYTHON_DIR%"
  echo   2^) conda env create -f environment.yml
  echo   3^) launch_student_doctor_windows.bat
  exit /b 1
)

echo Running student doctor checks...
python "%TARGET_SCRIPT%" %*
