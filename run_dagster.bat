@echo off
REM ============================================================
REM  Doble clic para levantar Dagster.
REM  Guarda el estado DENTRO del proyecto (carpeta dagster_home),
REM  asi las materializaciones y el on/off de sensores/schedules
REM  persisten entre reinicios.
REM ============================================================

REM Pararse en la carpeta del proyecto (donde esta este .bat)
cd /d "%~dp0"

REM Activar el entorno virtual si existe (venv o .venv)
if exist "venv\Scripts\activate.bat" call "venv\Scripts\activate.bat"
if exist ".venv\Scripts\activate.bat" call ".venv\Scripts\activate.bat"

REM Estado de Dagster dentro del proyecto
set "DAGSTER_HOME=%~dp0dagster_home"
if not exist "%DAGSTER_HOME%" mkdir "%DAGSTER_HOME%"

echo DAGSTER_HOME = %DAGSTER_HOME%
echo.
echo Abriendo Dagster en http://localhost:3000
echo (cerra esta ventana o apreta Ctrl+C para detenerlo)
echo.

dagster dev

echo.
echo Dagster se detuvo. Presiona una tecla para cerrar esta ventana.
pause >nul
