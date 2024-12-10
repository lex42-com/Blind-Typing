@echo off
REM Путь к папке, где находятся файлы .ui
set UI_FOLDER=C:\Users\User1\PerfectProject\PR\UI

REM Путь к директории, где находятся утилиты PyQt5 или PyQt6
set PYUIC_PATH=C:\Users\User1\PerfectProject\PR\.venv\Scripts\pyuic6.exe

REM Переключаемся в директорию с .ui файлами
cd %UI_FOLDER%

REM Проходим по всем .ui файлам в папке
for %%f in (*.ui) do (
    REM Преобразуем .ui в .py с использованием pyuic5 или pyuic6
    %PYUIC_PATH%\pyuic6 %%f -o %%~nf.py
)

echo Готово!
pause
