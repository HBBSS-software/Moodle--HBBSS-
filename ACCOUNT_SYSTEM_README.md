# HBBSS 账号管理系统

一个安全的、基于Flask的账号管理系统，用于存储和管理用户账号信息，支持云端同步。

## 功能特性

✅ **用户认证** - 支持注册、登录、密码管理
✅ **账号管理** - 创建、更新、删除用户账号
✅ **权限控制** - 管理员和普通用户的权限区分
✅ **云端同步** - 自动将账号信息同步到云端
✅ **IP白名单** - 只有认可的IP地址才能访问
✅ **数据备份** - 支持导出和备份所有账号信息
✅ **访问日志** - 记录所有API访问和操作
✅ **RESTful API** - 完整的API接口供集成使用

## 系统架构

```
┌─────────────────────────────────────────┐
│         客户端应用                         │
│  (web/mobile/desktop/命令行)              │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│   账号管理服务器 (server.py)             │
│  - Flask应用                             │
│  - JWT认证                               │
│  - IP白名单检查                          │
│  - 访问日志                              │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│      SQLite数据库                        │
│  (accounts.db)                           │
│  - 用户表                                │
│  - 同步记录表                            │
│  - 访问日志表                            │
└─────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│   云端同步客户端 (cloud_sync_client.py)  │
│  - 定期同步数据                          │
│  - 处理同步失败                          │
│  - 数据备份                              │
└─────────────────────────────────────────┘
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `server.py` | 主服务器应用程序 |
| `cloud_sync_client.py` | 云端同步客户端库 |
| `cvm.py` | VM管理器，整合所有功能 |
| `test_server.py` | API测试脚本 |
| `requirements-server.txt` | Python依赖 |
| `.env.example` | 环境配置模板 |
| `DEPLOYMENT.md` | 详细部署指南 |
| `accounts.db` | SQLite数据库（自动创建） |

## 运行说明

下面是最详细的运行说明，直接复制即可使用。

### 1. 系统要求

- Python 3.9 及以上
- pip 可用
- Windows / Linux / macOS 均可运行
- 如果在服务器上运行，建议使用 `124.222.116.32:5000` 作为默认地址

### 2. Windows 直接运行（推荐）

```powershell
# 1. 进入项目目录
cd D:\Moodle-HBBSS-\Moodle--HBBSS-

# 2. 运行自动化设置脚本
setup.bat

# 3. 启动程序
python server.py

# 4. 打开浏览器访问
http://localhost:5000/api/health
```

如果你想测试API，请打开另一个命令行窗口：

```powershell
cd D:\Moodle-HBBSS-\Moodle--HBBSS-
python test_server.py
```

### 3. Linux / macOS 直接运行（推荐）

```bash
cd /path/to/Moodle--HBBSS-
chmod +x setup.sh
./setup.sh
python3 server.py
```

访问服务：

```bash
http://localhost:5000/api/health
```

测试API：

```bash
cd /path/to/Moodle--HBBSS-
python3 test_server.py
```

### 4. 手动安装步骤（用于调试或自定义）

#### Windows 手动步骤

```powershell
cd D:\Moodle-HBBSS-\Moodle--HBBSS-
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements-server.txt
copy .env.example .env
python -c "from server import app, db; app.app_context().push(); db.create_all()"
```

创建管理员账号：

```powershell
python - <<'PY'
from server import app, db, User
with app.app_context():
    admin = User(username='admin', email='admin@hbbss.com', is_admin=True, is_active=True)
    admin.set_password('admin-password')
    db.session.add(admin)
    db.session.commit()
    print('管理员创建成功')
PY
```

启动服务：

```powershell
python server.py
```

#### Linux / macOS 手动步骤

```bash
cd /path/to/Moodle--HBBSS-
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-server.txt
cp .env.example .env
python3 -c "from server import app, db; app.app_context().push(); db.create_all()"
```

创建管理员账号：

```bash
python3 <<'EOF'
from server import app, db, User
with app.app_context():
    admin = User(username='admin', email='admin@hbbss.com', is_admin=True, is_active=True)
    admin.set_password('admin-password')
    db.session.add(admin)
    db.session.commit()
    print("管理员创建成功")
EOF
```

启动服务：

```bash
python3 server.py
```

### 5. Docker 运行

```bash
docker-compose up -d
```

访问服务：

```bash
http://localhost:5000
```

停止服务：

```bash
docker-compose down
```

### 6. 服务器运行（放到 124.222.116.32）

如果你已经把项目上传到服务器，可按下面步骤运行：

```bash
cd /home/ubuntu/hbbss-account-system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-server.txt
cp .env.example .env
python3 -c "from server import app, db; app.app_context().push(); db.create_all()"
python3 server.py
```

它将在服务器的 `5000` 端口启动，访问地址为：

```bash
http://124.222.116.32:5000
```

### 7. 运行后检查

- 健康检查：
  - `http://localhost:5000/api/health`
- 管理员登录：
  - POST `/api/auth/login`
- 如果是远程服务器，请将 `localhost` 替换为 `124.222.116.32`

### 8. 重要提示

- 默认管理员账号为 `admin`，密码 `admin-password`，请启动后立即修改
- `.env` 文件内可配置 `PORT`、`JWT_SECRET_KEY`、`ALLOWED_IPS`
- 本地访问建议使用 `http://localhost:5000`
- 服务器上访问建议使用 `http://124.222.116.32:5000`

### 9. 常见运行命令

```bash
# 启动服务
python server.py

# 启动服务并打印日志
python server.py

# 使用Gunicorn启动（生产部署）
gunicorn -w 4 -b 0.0.0.0:5000 server:app

# 运行测试脚本
python test_server.py
```

### 10. 运行环境变量

`.env` 示例中默认包含：

```text
PORT=5000
HOST=0.0.0.0
JWT_SECRET_KEY=your-secret-key-here-change-this
DATABASE_URL=sqlite:///accounts.db
ALLOWED_IPS=127.0.0.1,124.222.116.32
```

### 11. 如果你要在服务器上长期挂载

建议使用 `gunicorn` 或 `docker-compose`，并配合 Nginx 反向代理。详见 [DEPLOYMENT.md](DEPLOYMENT.md)

### 12. 直接运行说明总结

1. 进入项目目录
2. 启动虚拟环境
3. 安装依赖
4. 初始化数据库
5. 创建管理员账号
6. 运行 `python server.py`
7. 访问 `http://localhost:5000/api/health`

### Docker 方式（推荐用于生产）

```bash
docker-compose up -d
```

### 生产部署

参见 [DEPLOYMENT.md](DEPLOYMENT.md)

## API文档

### 认证端点

#### 注册用户
```
POST /api/auth/register
Content-Type: application/json

{
  "username": "newuser",
  "password": "password123",
  "email": "user@example.com",
  "full_name": "Full Name",
  "department": "Department",
  "phone": "1234567890"
}

Response (201):
{
  "message": "User registered successfully",
  "user": { ... }
}
```

#### 用户登录
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "user",
  "password": "password"
}

Response (200):
{
  "message": "Login successful",
  "access_token": "jwt_token_here",
  "user": { ... }
}
```

### 用户管理端点

#### 获取用户信息
```
GET /api/users/{user_id}
Authorization: Bearer {access_token}

Response (200):
{ user_data }
```

#### 获取所有用户（仅管理员）
```
GET /api/users
Authorization: Bearer {access_token}

Response (200):
[ { user_data }, ... ]
```

#### 更新用户信息
```
PUT /api/users/{user_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "full_name": "Updated Name",
  "department": "New Department"
}

Response (200):
{ updated_user_data }
```

#### 删除用户（仅管理员）
```
DELETE /api/users/{user_id}
Authorization: Bearer {access_token}

Response (200):
{ "message": "User deleted successfully" }
```

### 云端同步端点

#### 获取待同步数据
```
GET /api/sync/status
Authorization: Bearer {access_token}

Response (200):
{
  "pending_count": 5,
  "syncs": [ ... ]
}
```

#### 确认同步完成
```
POST /api/sync/confirm
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "sync_id": 1
}

Response (200):
{ "message": "Sync confirmed successfully" }
```

#### 导出所有账号（仅管理员）
```
GET /api/sync/export
Authorization: Bearer {access_token}

Response (200):
{
  "exported_at": "2024-01-01T12:00:00",
  "total_users": 10,
  "users": [ ... ]
}
```

#### 获取统计信息（仅管理员）
```
GET /api/stats
Authorization: Bearer {access_token}

Response (200):
{
  "total_users": 10,
  "active_users": 9,
  "admin_count": 1,
  "pending_syncs": 0,
  "failed_syncs": 0,
  "total_access_logs": 150
}
```

### 系统端点

#### 健康检查
```
GET /api/health

Response (200):
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "database": "connected"
}
```

## Python客户端使用

```python
from cloud_sync_client import CloudSyncClient

# 创建客户端
client = CloudSyncClient(
    server_url='http://124.222.116.32:5000',
    username='admin',
    password='admin-password'
)

# 登录
if client.login():
    # 注册用户
    user = client.register_user(
        username='newuser',
        password='password123',
        email='user@example.com'
    )
    
    # 获取用户
    user = client.get_user(1)
    
    # 列表所有用户
    users = client.list_users()
    
    # 更新用户
    client.update_user(1, department='Sales')
    
    # 导出所有账号
    export = client.export_all_accounts()
    
    # 获取统计信息
    stats = client.get_stats()
```

## 数据库模型

### 用户表 (User)
```
- id (主键)
- username (唯一)
- email (唯一)
- password_hash
- full_name
- department
- phone
- is_active
- is_admin
- created_at
- updated_at
- last_login
- sync_status
- cloud_sync_time
```

### 同步记录表 (CloudSync)
```
- id (主键)
- user_id (外键)
- action (create/update/delete)
- status (pending/success/failed)
- error_message
- created_at
- synced_at
```

### 访问日志表 (AccessLog)
```
- id (主键)
- user_id (外键)
- ip_address
- action
- details
- created_at
```

## 安全特性

🔒 **密码加密** - 使用werkzeug的generate_password_hash进行密码加密存储
🔒 **JWT认证** - 使用Flask-JWT-Extended实现安全的令牌认证
🔒 **IP白名单** - 只允许特定IP地址访问API
🔒 **访问日志** - 记录所有API调用和操作
🔒 **权限控制** - 用户只能访问自己的信息，管理员可以管理所有用户

## 性能优化建议

1. 使用Gunicorn替代Flask内置服务器
2. 使用Nginx作为反向代理
3. 配置数据库连接池
4. 定期清理旧日志
5. 使用Redis进行会话缓存
6. 使用PostgreSQL替代SQLite（大规模部署）

## 故障排除

### 问题：无法连接到服务器
**解决方案：**
- 检查服务器是否正在运行
- 检查防火墙设置
- 检查IP是否在白名单中

### 问题：登录失败
**解决方案：**
- 检查用户名和密码是否正确
- 检查用户是否被禁用
- 检查服务器日志

### 问题：数据库错误
**解决方案：**
- 检查磁盘空间
- 重建数据库
- 检查文件权限

## 支持和反馈

如有问题或建议，请联系系统管理员。

## 许可证

内部使用 - 仅供HBBSS项目使用

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 基本账号管理功能
- 云端同步功能
- API文档完善

---

**创建时间**: 2024-01-01
**最后更新**: 2024-01-01
