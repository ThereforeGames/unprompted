@echo off
echo (NOTICE) Make a copy of this file and edit the call statements to match your environment!

call T:/code/python/automatic-stable-diffusion-webui/venv/Scripts/activate
if %ERRORLEVEL% neq 0 goto Error

python unprompted_dry.py

pause
exit /b 0

:Error
echo (ERROR) Failed to activate the Python environment. Did you set the path correctly?
pause
exit /b 1