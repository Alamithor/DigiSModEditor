@echo off

call .venv\Scripts\Activate.bat

pyinstaller -w --add-data src\DigiSModEditor;.\DigiSModEditor src\DigiSModEditor.py
REM pyinstaller --onefile -w --add-data src\DigiSModEditor;.\DigiSModEditor src\DigiSModEditor.py
