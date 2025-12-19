@echo off
chcp 65001 >nul
echo Запуск Telegram-бота модератора...
echo.

docker-compose up --build

pause

