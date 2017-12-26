@echo off
cls
:start
set Today=%date:~0,10%
@echo %Today%
@echo cd path : D:\movehouse_list\taobao
cd D:\movehouse_list\taobao
@echo python get_final_page_taobao.py
python get_final_page_taobao.py
goto start
