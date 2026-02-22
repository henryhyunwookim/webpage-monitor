@echo off
cd /d "%~dp0.."
rem src/main.py will default to config/config.yaml
call python src/main.py %*
