# HBBSS 账号管理系统部署指南

## 系统架构

本系统由以下核心组件组成：

1. **server.py** - 账号管理服务器（主要应用程序）
2. **cloud_sync_client.py** - 云端同步客户端
3. **database** - SQLite数据库（accounts.db）

## 服务器要求

- Ubuntu 20.04+ (或其他Linux发行版)
- Python 3.9+
- 开放端口 5000 (或自定义端口)

## 部署步骤

### 1. 连接到服务器

```bash
ssh ubuntu@124.222.116.32
# 输入密码: hbbssisthebest!666
```

### 2. 安装依赖

```bash
# 更新系统包
sudo apt-get update
sudo apt-get upgrade -y

# 安装Python和pip
sudo apt-get install -y python3 python3-pip python3-venv

# 创建项目目录
mkdir -p /home/ubuntu/hbbss-account-system
cd /home/ubuntu/hbbss-account-system

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements-server.txt
```

### 3. 配置环境

```bash
# 复制配置文件
cp .env.example .env

# 编辑.env文件，设置强密钥
nano .env
```

**重要的配置项：**
```
JWT_SECRET_KEY=生成一个强密钥（例如：openssl rand -hex 32）
ALLOWED_IPS=127.0.0.1,124.222.116.32
PORT=5000
```

### 4. 初始化数据库

```bash
python3 -c "from server import app, db; app.app_context().push(); db.create_all(); print('数据库初始化完成')"
```

### 5. 创建管理员账号

```bash
python3 << EOF
from server import app, db, User
from datetime import datetime

with app.app_context():
    # 检查管理员是否已存在
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@hbbss.com',
            full_name='系统管理员',
            is_admin=True,
            is_active=True
        )
        admin.set_password('admin-password')  # 请改为强密码
        db.session.add(admin)
        db.session.commit()
        print("管理员账号创建成功")
    else:
        print("管理员账号已存在")
EOF
```

### 6. 配置Nginx反向代理（推荐用于生产环境）

```bash
# 安装Nginx
sudo apt-get install -y nginx

# 创建Nginx配置
sudo nano /etc/nginx/sites-available/hbbss-account

# 在文件中添加以下内容：
```

```nginx
server {
    listen 80;
    server_name 124.222.116.32;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# 启用配置
sudo ln -s /etc/nginx/sites-available/hbbss-account /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

### 7. 配置Systemd服务（后台运行）

```bash
# 创建服务文件
sudo nano /etc/systemd/system/hbbss-account.service
```

```ini
[Unit]
Description=HBBSS Account Management Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/hbbss-account-system
Environment="PATH=/home/ubuntu/hbbss-account-system/venv/bin"
EnvironmentFile=/home/ubuntu/hbbss-account-system/.env
ExecStart=/home/ubuntu/hbbss-account-system/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 server:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 启用并启动服务
sudo systemctl daemon-reload
sudo systemctl enable hbbss-account
sudo systemctl start hbbss-account

# 查看状态
sudo systemctl status hbbss-account

# 查看日志
sudo journalctl -u hbbss-account -f
```

### 8. 安装SSL证书（可选但推荐）

```bash
# 安装certbot
sudo apt-get install -y certbot python3-certbot-nginx

# 获取证书（需要配置DNS或邮箱验证）
sudo certbot --nginx -d 124.222.116.32
```

## API使用说明

### 认证

**注册用户**
```bash
curl -X POST http://124.222.116.32:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "password123",
    "email": "john@example.com",
    "full_name": "John Doe",
    "department": "Engineering"
  }'
```

**用户登录**
```bash
curl -X POST http://124.222.116.32:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "password123"
  }'
```

### 用户管理

**获取用户信息**
```bash
curl -X GET http://124.222.116.32:5000/api/users/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**更新用户信息**
```bash
curl -X PUT http://124.222.116.32:5000/api/users/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Doe",
    "department": "Sales"
  }'
```

**获取所有用户（管理员）**
```bash
curl -X GET http://124.222.116.32:5000/api/users \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 云端同步

**获取待同步数据**
```bash
curl -X GET http://124.222.116.32:5000/api/sync/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**确认同步完成**
```bash
curl -X POST http://124.222.116.32:5000/api/sync/confirm \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sync_id": 1}'
```

**导出所有账号（管理员）**
```bash
curl -X GET http://124.222.116.32:5000/api/sync/export \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**获取统计信息（管理员）**
```bash
curl -X GET http://124.222.116.32:5000/api/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Python客户端使用

```python
from cloud_sync_client import CloudSyncClient, SyncManager

# 创建客户端
client = CloudSyncClient(
    server_url='http://124.222.116.32:5000',
    username='admin',
    password='admin-password'
)

# 登录
if client.login():
    # 注册新用户
    user = client.register_user(
        username='newuser',
        password='password123',
        email='user@example.com',
        full_name='New User'
    )
    
    # 获取用户列表
    users = client.list_users()
    
    # 更新用户
    client.update_user(1, department='New Department')
    
    # 导出所有账号
    export_data = client.export_all_accounts()
    
    # 获取统计信息
    stats = client.get_stats()
```

## 安全建议

1. **更改默认密码** - 立即更改管理员和所有默认账号的密码
2. **生成强JWT密钥** - 运行 `openssl rand -hex 32` 生成
3. **启用SSL/TLS** - 使用HTTPS而不是HTTP
4. **配置防火墙** - 只允许必要的IP地址访问
5. **定期备份** - 定期备份 `accounts.db` 数据库
6. **监控日志** - 定期检查访问日志和错误日志
7. **更新依赖** - 定期更新Python依赖包

## 备份和恢复

**备份数据库**
```bash
cp /home/ubuntu/hbbss-account-system/accounts.db /backup/accounts.db.$(date +%Y%m%d)
```

**恢复数据库**
```bash
cp /backup/accounts.db.20230101 /home/ubuntu/hbbss-account-system/accounts.db
sudo systemctl restart hbbss-account
```

## 故障排除

**检查服务状态**
```bash
sudo systemctl status hbbss-account
```

**查看详细日志**
```bash
sudo journalctl -u hbbss-account -n 100
```

**测试数据库连接**
```bash
cd /home/ubuntu/hbbss-account-system
source venv/bin/activate
python3 -c "from server import app, db; print('数据库连接成功')"
```

**测试API**
```bash
curl http://124.222.116.32:5000/api/health
```

## 性能优化

对于大规模部署，考虑以下优化：

1. 使用PostgreSQL替代SQLite
2. 使用Redis进行缓存和会话管理
3. 使用多个gunicorn workers
4. 启用数据库连接池
5. 定期清理旧的访问日志

## 监控和维护

建议定期检查以下内容：

- 数据库大小和性能
- API响应时间
- 错误率和异常
- 磁盘空间使用情况
- 内存使用情况
- 安全日志（未授权访问等）

## 支持和反馈

如有问题或建议，请联系系统管理员。
