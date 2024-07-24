@echo off
setlocal
chcp 65001

REM 检查winget是否安装
winget --version
if %errorlevel% neq 0 (
    echo winget 未安装，请安装winget后再试。
    pause
    exit /b 30
)

REM 安装Python运行环境
echo 正在安装Python运行环境
winget install --id Python.Python.3.11 -e --source winget

REM 等待安装完成
echo 等待安装完成...

set MAX_WAIT=60
set /a WAIT_TIME=0
:WAIT_LOOP
REM 检查Python是否成功安装
python --version
if %errorlevel% neq 0 (
    if %WAIT_TIME% geq %MAX_WAIT% (
        echo Python 安装失败，请检查winget输出以了解更多信息。
        pause
        exit /b 30
    )
    REM 每次等待5秒，然后重新检查
    timeout /T 5 /NOBREAK
    set /a WAIT_TIME+=5
    goto WAIT_LOOP
)

REM 确认pip已安装
python -m ensurepip

REM 等待pip安装完成
timeout /T 1 /NOBREAK

REM 检查pip是否成功安装
pip --version
if %errorlevel% neq 0 (
    echo pip 安装失败，请检查Python安装。
    pause
    exit /b 1
)


cd WeChatRobot-39.0.14.0

REM 安装第三方依赖库
echo 安装第三方依赖库
python -m pip install -U pip -i https://mirrors.ustc.edu.cn/pypi/web/simple
pip install -r requirements.txt -i https://mirrors.ustc.edu.cn/pypi/web/simple
if %errorlevel% neq 0 (
    echo 依赖库安装失败，请检查requirements.txt。
    pause
    exit /b 1
)
pip install -r coze2openai/requirements.txt -i https://mirrors.ustc.edu.cn/pypi/web/simple

if %errorlevel% neq 0 (
    echo 依赖库安装失败，请检查coze2openai/requirements.txt。
    pause
    exit /b 1
)

echo 调起微信客户端，请扫码登录！
python mainui5.py 

echo 全部完成
pause
