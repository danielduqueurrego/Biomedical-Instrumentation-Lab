@echo off
setlocal

REM Beginner launcher for Windows students.
set "REPO_DIR=%~dp0"
set "PYTHON_DIR=%REPO_DIR%python"
set "TARGET_SCRIPT=%PYTHON_DIR%\run_student_acquisition_gui.py"

where conda >nul 2>nul
if errorlevel 1 (
  echo ERROR: Conda was not found on PATH.
  echo Install Miniconda or Anaconda, open a new Command Prompt, and try again.
  echo Setup steps:
  echo   1^) cd /d "%PYTHON_DIR%"
  echo   2^) conda env create -f environment.yml
  echo   3^) Re-run: launch_student_gui_windows.bat
  exit /b 1
)

for /f "delims=" %%i in ('conda info --base 2^>nul') do set "CONDA_BASE=%%i"
if "%CONDA_BASE%"=="" (
  echo ERROR: Could not determine your Conda base path.
  echo Setup steps:
  echo   1^) cd /d "%PYTHON_DIR%"
  echo   2^) conda env create -f environment.yml
  echo   3^) Re-run: launch_student_gui_windows.bat
  exit /b 1
)

if not exist "%CONDA_BASE%\condabin\conda.bat" (
  echo ERROR: Conda activation helper was not found:
  echo   "%CONDA_BASE%\condabin\conda.bat"
  echo Please verify your Conda installation, then try again.
  exit /b 1
)

call "%CONDA_BASE%\condabin\conda.bat" activate biomed-lab >nul 2>nul
if errorlevel 1 (
  echo ERROR: Conda environment "biomed-lab" is missing or failed to activate.
  echo Create it once, then run this launcher again:
  echo   1^) cd /d "%PYTHON_DIR%"
  echo   2^) conda env create -f environment.yml
  echo   3^) launch_student_gui_windows.bat
  exit /b 1
)

echo Launching Student Acquisition GUI...
python "%TARGET_SCRIPT%" %*
