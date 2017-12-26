@echo off
cls
:start
set Today=%date:~0,10%
@echo %Today%
@echo cd path : D:\cms\chinabidding
cd D:\cms\chinabidding
@echo python BaiduSaledCheck.py
python BaiduSaledCheck.py
goto start
