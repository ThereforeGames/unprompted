@echo off
echo (NOTICE) Make a copy of this file and edit the call statements to match your environment!

call T:/programs/anaconda3/Scripts/activate.bat
call conda activate a1111_310

python unprompted_dry.py

pause