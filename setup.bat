@echo off
echo 此 bat 用于快速安装 LOJ-AC-Counter 需要的库，如已安装请忽略
echo 请将本文件放置在 pip 目录下或将 Python 添加到 Path 后运行
echo 任意键开始安装...
pause>nul
echo 安装 requests...
pip install requests
echo 安装 beautifulsoup4...
pip install beautifulsoup4
pause