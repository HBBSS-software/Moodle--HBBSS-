#!/bin/bash

# HBBSS 账号管理系统 - 快速部署脚本

set -e

echo "=========================================="
echo "HBBSS 账号管理系统 - 快速部署"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Python版本
echo "[1] 检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "检测到Python版本: $python_version"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo -e "${RED}✗ Python版本需要3.9或更高${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python版本检查通过${NC}"
echo ""

# 创建虚拟环境
echo "[2] 创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ 虚拟环境已创建${NC}"
else
    echo -e "${YELLOW}✓ 虚拟环境已存在，跳过创建${NC}"
fi
echo ""

# 激活虚拟环境
source venv/bin/activate
echo "虚拟环境已激活"
echo ""

# 安装依赖
echo "[3] 安装依赖..."
pip install -q -r requirements-server.txt
echo -e "${GREEN}✓ 依赖安装完成${NC}"
echo ""

# 创建.env文件
echo "[4] 配置环境..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ".env文件已创建"
    
    # 生成JWT密钥
    jwt_key=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    
    # 更新.env文件
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$jwt_key/" .env
    else
        sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$jwt_key/" .env
    fi
    
    echo ".env文件已更新JWT密钥"
else
    echo -e "${YELLOW}✓ .env文件已存在，跳过创建${NC}"
fi
echo -e "${GREEN}✓ 环境配置完成${NC}"
echo ""

# 初始化数据库
echo "[5] 初始化数据库..."
python3 << EOF
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
EOF
echo -e "${GREEN}✓ 数据库初始化完成${NC}"
echo ""

# 显示配置信息
echo "=========================================="
echo -e "${GREEN}部署完成！${NC}"
echo "=========================================="
echo ""
echo "接下来的步骤:"
echo ""
echo "1. 编辑.env文件，更改重要配置:"
echo "   nano .env"
echo ""
echo "2. 启动开发服务器:"
echo "   python3 server.py"
echo ""
echo "3. 测试API (在另一个终端):"
echo "   python3 test_server.py"
echo ""
echo "4. 生产部署:"
echo "   参见 DEPLOYMENT.md 文件"
echo ""
echo "5. 使用Docker部署:"
echo "   docker-compose up -d"
echo ""
echo "=========================================="
echo ""
echo "默认管理员账户:"
echo "  用户名: admin"
echo "  密码: admin-password"
echo ""
echo -e "${YELLOW}⚠ 安全提示: 立即更改管理员密码!${NC}"
echo ""
