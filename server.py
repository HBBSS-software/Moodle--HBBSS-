"""
HBBSS Account Management Server
负责管理用户账号信息、认证和云端同步
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta
import json
import logging
from functools import wraps
import sqlite3

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ==================== 配置 ====================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'hbbss-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

# 允许的IP地址（只有认识的人可以用）
ALLOWED_IPS = [
    '127.0.0.1',  # 本地
    '124.222.116.32',  # 自己的服务器
]

# ==================== 数据库初始化 ====================
db = SQLAlchemy(app)
jwt = JWTManager(app)


class User(db.Model):
    """用户账号模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(120))
    department = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    sync_status = db.Column(db.String(20), default='pending')  # pending, synced, failed
    cloud_sync_time = db.Column(db.DateTime)
    
    def set_password(self, password):
        """设置密码（加密存储）"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'department': self.department,
            'phone': self.phone,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'sync_status': self.sync_status,
        }


class CloudSync(db.Model):
    """云端同步记录"""
    __tablename__ = 'cloud_sync'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(20))  # create, update, delete
    status = db.Column(db.String(20), default='pending')  # pending, success, failed
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    synced_at = db.Column(db.DateTime)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'synced_at': self.synced_at.isoformat() if self.synced_at else None,
        }


class AccessLog(db.Model):
    """访问日志"""
    __tablename__ = 'access_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ip_address = db.Column(db.String(45))
    action = db.Column(db.String(100))
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ==================== 中间件和装饰器 ====================
def check_ip_whitelist(f):
    """检查IP地址是否在白名单中"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip not in ALLOWED_IPS:
            logger.warning(f"非白名单IP访问: {client_ip}")
            return jsonify({'error': 'Access denied: IP not whitelisted'}), 403
        return f(*args, **kwargs)
    return decorated_function


def log_access(action):
    """记录访问日志"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                user_id = None
                if request.headers.get('Authorization'):
                    from flask_jwt_extended import get_jwt_identity
                    try:
                        user_id = get_jwt_identity()
                    except:
                        pass
                
                log = AccessLog(
                    user_id=user_id,
                    ip_address=request.remote_addr,
                    action=action,
                    details=request.get_json() or {}
                )
                db.session.add(log)
                db.session.commit()
            except Exception as e:
                logger.error(f"日志记录失败: {str(e)}")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ==================== 认证API ====================
@app.route('/api/auth/register', methods=['POST'])
@check_ip_whitelist
@log_access('register')
def register():
    """注册新用户"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # 检查用户是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409
    
    # 创建新用户
    user = User(
        username=data['username'],
        email=data['email'],
        full_name=data.get('full_name', ''),
        department=data.get('department', ''),
        phone=data.get('phone', ''),
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # 触发云端同步
    sync = CloudSync(user_id=user.id, action='create', status='pending')
    db.session.add(sync)
    db.session.commit()
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict()
    }), 201


@app.route('/api/auth/login', methods=['POST'])
@check_ip_whitelist
@log_access('login')
def login():
    """用户登录"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        logger.warning(f"登录失败: {data.get('username')}")
        return jsonify({'error': 'Invalid username or password'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'User account is inactive'}), 403
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # 生成JWT token
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200


# ==================== 用户管理API ====================
@app.route('/api/users/<int:user_id>', methods=['GET'])
@check_ip_whitelist
@jwt_required()
@log_access('get_user')
def get_user(user_id):
    """获取用户信息"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200


@app.route('/api/users', methods=['GET'])
@check_ip_whitelist
@jwt_required()
@log_access('list_users')
def list_users():
    """获取所有用户列表"""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # 仅管理员可以查看所有用户
    if not current_user or not current_user.is_admin:
        return jsonify({'error': 'Permission denied'}), 403
    
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200


@app.route('/api/users/<int:user_id>', methods=['PUT'])
@check_ip_whitelist
@jwt_required()
@log_access('update_user')
def update_user(user_id):
    """更新用户信息"""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    
    # 用户只能更新自己的信息，或者管理员可以更新任何用户
    current_user = User.query.get(current_user_id)
    if current_user_id != user_id and (not current_user or not current_user.is_admin):
        return jsonify({'error': 'Permission denied'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # 更新允许的字段
    allowed_fields = ['full_name', 'department', 'phone', 'email']
    for field in allowed_fields:
        if field in data:
            setattr(user, field, data[field])
    
    # 仅管理员可以更改密码或激活状态
    if current_user and current_user.is_admin:
        if 'password' in data:
            user.set_password(data['password'])
        if 'is_active' in data:
            user.is_active = data['is_active']
    
    db.session.commit()
    
    # 触发云端同步
    sync = CloudSync(user_id=user.id, action='update', status='pending')
    db.session.add(sync)
    db.session.commit()
    
    return jsonify({
        'message': 'User updated successfully',
        'user': user.to_dict()
    }), 200


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@check_ip_whitelist
@jwt_required()
@log_access('delete_user')
def delete_user(user_id):
    """删除用户"""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # 仅管理员可以删除用户
    if not current_user or not current_user.is_admin:
        return jsonify({'error': 'Permission denied'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # 触发云端同步
    sync = CloudSync(user_id=user.id, action='delete', status='pending')
    db.session.add(sync)
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'}), 200


# ==================== 云端同步API ====================
@app.route('/api/sync/status', methods=['GET'])
@check_ip_whitelist
@jwt_required()
def get_sync_status():
    """获取待同步的数据"""
    pending_syncs = CloudSync.query.filter_by(status='pending').all()
    
    return jsonify({
        'pending_count': len(pending_syncs),
        'syncs': [sync.to_dict() for sync in pending_syncs]
    }), 200


@app.route('/api/sync/confirm', methods=['POST'])
@check_ip_whitelist
@jwt_required()
@log_access('confirm_sync')
def confirm_sync():
    """确认云端同步完成"""
    data = request.get_json()
    sync_id = data.get('sync_id')
    
    if not sync_id:
        return jsonify({'error': 'Missing sync_id'}), 400
    
    sync = CloudSync.query.get(sync_id)
    if not sync:
        return jsonify({'error': 'Sync record not found'}), 404
    
    sync.status = 'success'
    sync.synced_at = datetime.utcnow()
    
    user = User.query.get(sync.user_id)
    if user:
        user.sync_status = 'synced'
        user.cloud_sync_time = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': 'Sync confirmed successfully'}), 200


@app.route('/api/sync/export', methods=['GET'])
@check_ip_whitelist
@jwt_required()
def export_all_accounts():
    """导出所有账号信息（用于云端备份）"""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # 仅管理员可以导出所有数据
    if not current_user or not current_user.is_admin:
        return jsonify({'error': 'Permission denied'}), 403
    
    users = User.query.all()
    export_data = {
        'exported_at': datetime.utcnow().isoformat(),
        'total_users': len(users),
        'users': [user.to_dict() for user in users]
    }
    
    return jsonify(export_data), 200


# ==================== 健康检查和管理 ====================
@app.route('/api/health', methods=['GET'])
@check_ip_whitelist
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'connected'
    }), 200


@app.route('/api/stats', methods=['GET'])
@check_ip_whitelist
@jwt_required()
@log_access('view_stats')
def get_stats():
    """获取系统统计信息"""
    from flask_jwt_extended import get_jwt_identity
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or not current_user.is_admin:
        return jsonify({'error': 'Permission denied'}), 403
    
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'admin_count': User.query.filter_by(is_admin=True).count(),
        'pending_syncs': CloudSync.query.filter_by(status='pending').count(),
        'failed_syncs': CloudSync.query.filter_by(status='failed').count(),
        'total_access_logs': AccessLog.query.count(),
    }
    
    return jsonify(stats), 200


# ==================== 错误处理 ====================
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


# ==================== 主程序 ====================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        logger.info("数据库已初始化")
    
    # 生产环境中应该使用gunicorn或其他WSGI服务器
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"启动账号管理服务器，端口: {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
