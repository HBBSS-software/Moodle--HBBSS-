# HBBSS 账号管理系统 - 快速参考指南

## 快速开始（5分钟）

### Windows用户
```bash
# 1. 运行设置脚本
setup.bat

# 2. 启动服务器
python server.py

# 3. 测试API
python test_server.py
```

### Linux/Mac用户
```bash
# 1. 运行设置脚本
chmod +x setup.sh
./setup.sh

# 2. 启动服务器
python3 server.py

# 3. 测试API
python3 test_server.py
```

## 默认凭证

```
用户名: admin
密码: admin-password
```

⚠️ **重要**：立即更改密码！

## 常用命令

### 开发模式
```bash
# 本地开发服务器
python3 server.py

# 开启调试模式
FLASK_ENV=development FLASK_DEBUG=1 python3 server.py
```

### 生产模式
```bash
# 使用Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 server:app

# 使用Docker
docker-compose up -d

# 查看日志
docker-compose logs -f hbbss-account
```

### 测试
```bash
# 运行测试脚本
python3 test_server.py

# 测试同步功能
python3 test_server.py --sync
```

## 数据库操作

### 查看数据库
```bash
# 使用SQLite CLI
sqlite3 accounts.db

# 查询用户
.schema
SELECT * FROM users;
```

### 备份数据库
```bash
# Linux/Mac
cp accounts.db accounts.db.backup.$(date +%Y%m%d)

# Windows
copy accounts.db accounts.db.backup.%date:~-4%.%date:~-10,2%.%date:~-7,2%
```

### 恢复数据库
```bash
# 如果服务器已停止
cp accounts.db.backup accounts.db
```

## API示例

### 注册用户
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123",
    "email": "test@example.com",
    "full_name": "Test User"
  }'
```

### 登录
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin-password"
  }'
```

### 获取用户列表
```bash
curl -X GET http://localhost:5000/api/users \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 获取统计信息
```bash
curl -X GET http://localhost:5000/api/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 常见问题

### Q: 如何更改管理员密码？
```python
from server import app, db, User

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        admin.set_password('new-password')
        db.session.commit()
        print("密码已更改")
```

### Q: 如何重置数据库？
```bash
# 删除数据库文件
rm accounts.db

# 重新初始化
python3 -c "from server import app, db; app.app_context().push(); db.create_all()"
```

### Q: 如何查看服务器日志？
```bash
# Docker
docker-compose logs -f hbbss-account

# Systemd
sudo journalctl -u hbbss-account -f

# 直接运行
# 日志输出到控制台
```

### Q: 如何添加新的IP到白名单？
编辑 `.env` 文件：
```
ALLOWED_IPS=127.0.0.1,124.222.116.32,新IP地址
```

### Q: 如何导出所有用户数据？
```bash
curl -X GET http://localhost:5000/api/sync/export \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  > users_export.json
```

### Q: 如何配置HTTPS？
参见 `DEPLOYMENT.md` 中的SSL配置部分

## 文件位置

| 文件 | 位置 | 说明 |
|------|------|------|
| 数据库 | `accounts.db` | SQLite数据库 |
| 配置 | `.env` | 环境配置 |
| 日志 | 控制台/`/var/log/hbbss-account/` | 运行日志 |
| 代码 | `server.py` | 主应用程序 |

## 安全清单

- [ ] 更改默认管理员密码
- [ ] 生成强JWT密钥
- [ ] 配置IP白名单
- [ ] 启用HTTPS/SSL
- [ ] 定期备份数据库
- [ ] 定期查看访问日志
- [ ] 更新Python依赖
- [ ] 配置防火墙规则
- [ ] 设置定期删除日志任务
- [ ] 文档记录系统访问规则

## 故障排除

### 症状：无法连接到服务器
**检查清单：**
1. 服务器是否在运行？ `curl http://localhost:5000/api/health`
2. 防火墙是否允许访问？
3. 端口是否正确？

### 症状：登录失败
**检查清单：**
1. 用户名和密码是否正确？
2. 用户是否被禁用？ `is_active` 字段
3. 查看服务器日志

### 症状：数据库错误
**检查清单：**
1. 磁盘空间是否充足？
2. 数据库文件是否损坏？
3. 权限是否正确？

## 获取帮助

1. 查看完整文档：`ACCOUNT_SYSTEM_README.md`
2. 查看部署指南：`DEPLOYMENT.md`
3. 查看API文档：本文件中的API示例部分
4. 检查日志输出
5. 运行测试脚本：`python3 test_server.py`

## 资源

- [Flask文档](https://flask.palletsprojects.com/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
- [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)
- [Gunicorn](https://gunicorn.org/)
- [Nginx](https://nginx.org/)

---

**最后更新**: 2024-01-01
**版本**: 1.0.0
