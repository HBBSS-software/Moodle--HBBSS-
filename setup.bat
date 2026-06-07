@echo off
REM HBBSS 账号管理系统 - 快速部署脚本（Windows版）

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo HBBSS 账号管理系统 - 快速部署
echo ==========================================
echo.

REM 检查Python版本
echo [1] 检查Python版本...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Python未安装或不在PATH中
    echo 请下载并安装Python 3.9+: https://www.python.org/
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo 检测到Python版本: %python_version%
echo ✓ Python版本检查通过
echo.

REM 创建虚拟环境
echo [2] 创建虚拟环境...
if exist venv (
    echo ✓ 虚拟环境已存在，跳过创建
) else (
    python -m venv venv
    echo ✓ 虚拟环境已创建
)
echo.

REM 激活虚拟环境
echo [3] 激活虚拟环境...
call venv\Scripts\activate.bat
echo ✓ 虚拟环境已激活
echo.

REM 安装依赖
echo [4] 安装依赖...
pip install -q -r requirements-server.txt
echo ✓ 依赖安装完成
echo.

REM 创建.env文件
echo [5] 配置环境...
if exist .env (
    echo ✓ .env文件已存在，跳过创建
) else (
    copy .env.example .env
    echo .env文件已创建
    
    REM 生成JWT密钥
    for /f "delims=" %%A in ('python -c "import secrets; print(secrets.token_hex(32))"') do (
        set jwt_key=%%A
    )
    
    REM 更新.env文件（使用PowerShell）
    powershell -Command "(Get-Content '.env') -replace 'JWT_SECRET_KEY=.*', 'JWT_SECRET_KEY=!jwt_key!' | Set-Content '.env'"
    echo .env文件已更新JWT密钥
)
echo ✓ 环境配置完成
echo.

REM 初始化数据库
echo [6] 初始化数据库...
python << PYTHON_EOF
from server import app, db, User
from datetime import datetime

with app.app_context():
    db.create_all()
    print("数据库已初始化")
    
    # 检查管理员用户
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@hbbss.com',
            full_name='System Administrator',
            is_admin=True,
            is_active=True
        )
        admin.set_password('admin-password')
        db.session.add(admin)
        db.session.commit()
        print("管理员账户已创建")
        print("用户名: admin")
        print("密码: admin-password (请立即更改!)")
    else:
        print("管理员账户已存在")
PYTHON_EOF
echo ✓ 数据库初始化完成
echo.

REM 显示完成信息
echo ==========================================
echo 部署完成！
echo ==========================================
echo.
echo 接下来的步骤:
echo.
echo 1. 编辑.env文件，更改重要配置:
echo    notepad .env
echo.
echo 2. 启动开发服务器:
echo    python server.py
echo.
echo 3. 测试API (在另一个终端):
echo    python test_server.py
echo.
echo 4. 生产部署:
echo    参见 DEPLOYMENT.md 文件
echo.
echo 5. 使用Docker部署:
echo    docker-compose up -d
echo.
echo ==========================================
echo.
echo 默认管理员账户:
echo   用户名: admin
echo   密码: admin-password
echo.
echo ⚠ 安全提示: 立即更改管理员密码!
echo.
