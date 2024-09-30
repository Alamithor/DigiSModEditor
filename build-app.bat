@echo off

call .venv\Scripts\Activate.bat

REM pyinstaller -w --add-data src\DigiSModEditor;.\DigiSModEditor src\DigiSModEditor.py
pyinstaller --onefile -w --add-data src\DigiSModEditor;.\DigiSModEditor src\DigiSModEditor.py
