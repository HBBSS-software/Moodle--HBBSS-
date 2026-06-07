"""
云端同步客户端
负责与远程服务器同步账号信息
"""

import requests
import json
import time
import logging
from datetime import datetime
import os
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CloudSyncClient:
    """云端同步客户端"""
    
    def __init__(self, server_url: str, username: str, password: str):
        """
        初始化客户端
        
        Args:
            server_url: 服务器地址，如 http://124.222.116.32:5000
            username: 用户名
            password: 密码
        """
        self.server_url = server_url.rstrip('/')
        self.username = username
        self.password = password
        self.access_token = None
        self.login_time = None
    
    def login(self) -> bool:
        """
        登录到服务器
        
        Returns:
            bool: 登录是否成功
        """
        try:
            url = f"{self.server_url}/api/auth/login"
            data = {
                'username': self.username,
                'password': self.password
            }
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result.get('access_token')
                self.login_time = datetime.now()
                logger.info(f"成功登录: {self.username}")
                return True
            else:
                logger.error(f"登录失败: {response.status_code} - {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"登录异常: {str(e)}")
            return False
    
    def is_authenticated(self) -> bool:
        """检查是否已认证"""
        return self.access_token is not None
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {'Content-Type': 'application/json'}
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        return headers
    
    def register_user(self, username: str, password: str, email: str, 
                     full_name: str = '', department: str = '', phone: str = '') -> Optional[Dict]:
        """
        注册新用户
        
        Args:
            username: 用户名
            password: 密码
            email: 邮箱
            full_name: 全名
            department: 部门
            phone: 电话
        
        Returns:
            Dict: 用户信息，失败返回None
        """
        try:
            url = f"{self.server_url}/api/auth/register"
            data = {
                'username': username,
                'password': password,
                'email': email,
                'full_name': full_name,
                'department': department,
                'phone': phone
            }
            
            response = requests.post(url, json=data, 
                                   headers=self._get_headers(), timeout=10)
            
            if response.status_code == 201:
                result = response.json()
                logger.info(f"用户注册成功: {username}")
                return result.get('user')
            else:
                logger.error(f"用户注册失败: {response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"注册用户异常: {str(e)}")
            return None
    
    def update_user(self, user_id: int, **kwargs) -> Optional[Dict]:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            **kwargs: 要更新的字段（full_name, department, phone等）
        
        Returns:
            Dict: 更新后的用户信息，失败返回None
        """
        if not self.is_authenticated():
            logger.error("未认证，请先登录")
            return None
        
        try:
            url = f"{self.server_url}/api/users/{user_id}"
            
            response = requests.put(url, json=kwargs, 
                                  headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"用户更新成功: ID {user_id}")
                return result.get('user')
            else:
                logger.error(f"用户更新失败: {response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"更新用户异常: {str(e)}")
            return None
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """
        获取用户信息
        
        Args:
            user_id: 用户ID
        
        Returns:
            Dict: 用户信息，失败返回None
        """
        if not self.is_authenticated():
            logger.error("未认证，请先登录")
            return None
        
        try:
            url = f"{self.server_url}/api/users/{user_id}"
            
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"获取用户失败: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"获取用户异常: {str(e)}")
            return None
    
    def list_users(self) -> Optional[List[Dict]]:
        """
        获取所有用户列表（需要管理员权限）
        
        Returns:
            List[Dict]: 用户列表，失败返回None
        """
        if not self.is_authenticated():
            logger.error("未认证，请先登录")
            return None
        
        try:
            url = f"{self.server_url}/api/users"
            
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                logger.info(f"获取用户列表成功，共 {len(response.json())} 个用户")
                return response.json()
            else:
                logger.error(f"获取用户列表失败: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"获取用户列表异常: {str(e)}")
            return None
    
    def get_pending_syncs(self) -> Optional[Dict]:
        """
        获取待同步的数据
        
        Returns:
            Dict: 同步状态信息，失败返回None
        """
        if not self.is_authenticated():
            logger.error("未认证，请先登录")
            return None
        
        try:
            url = f"{self.server_url}/api/sync/status"
            
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"获取同步状态失败: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"获取同步状态异常: {str(e)}")
            return None
    
    def confirm_sync(self, sync_id: int) -> bool:
        """
        确认同步完成
        
        Args:
            sync_id: 同步记录ID
        
        Returns:
            bool: 是否成功
        """
        if not self.is_authenticated():
            logger.error("未认证，请先登录")
            return False
        
        try:
            url = f"{self.server_url}/api/sync/confirm"
            data = {'sync_id': sync_id}
            
            response = requests.post(url, json=data, 
                                   headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                logger.info(f"同步确认成功: ID {sync_id}")
                return True
            else:
                logger.error(f"同步确认失败: {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"确认同步异常: {str(e)}")
            return False
    
    def export_all_accounts(self) -> Optional[Dict]:
        """
        导出所有账号信息（需要管理员权限）
        
        Returns:
            Dict: 导出的账号数据，失败返回None
        """
        if not self.is_authenticated():
            logger.error("未认证，请先登录")
            return None
        
        try:
            url = f"{self.server_url}/api/sync/export"
            
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            
            if response.status_code == 200:
                logger.info("账号数据导出成功")
                return response.json()
            else:
                logger.error(f"导出失败: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"导出异常: {str(e)}")
            return None
    
    def get_stats(self) -> Optional[Dict]:
        """
        获取系统统计信息（需要管理员权限）
        
        Returns:
            Dict: 统计信息，失败返回None
        """
        if not self.is_authenticated():
            logger.error("未认证，请先登录")
            return None
        
        try:
            url = f"{self.server_url}/api/stats"
            
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"获取统计信息失败: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"获取统计信息异常: {str(e)}")
            return None


class SyncManager:
    """同步管理器，用于定期同步数据"""
    
    def __init__(self, client: CloudSyncClient, sync_interval: int = 300):
        """
        初始化同步管理器
        
        Args:
            client: CloudSyncClient实例
            sync_interval: 同步间隔（秒），默认300秒
        """
        self.client = client
        self.sync_interval = sync_interval
        self.running = False
    
    def sync_loop(self):
        """
        同步循环
        每隔sync_interval秒检查一次待同步的数据
        """
        logger.info(f"启动同步循环，间隔: {self.sync_interval} 秒")
        self.running = True
        
        while self.running:
            try:
                # 登录
                if not self.client.is_authenticated():
                    if not self.client.login():
                        logger.warning("登录失败，5秒后重试...")
                        time.sleep(5)
                        continue
                
                # 获取待同步的数据
                sync_status = self.client.get_pending_syncs()
                
                if sync_status and sync_status.get('pending_count', 0) > 0:
                    logger.info(f"发现 {sync_status['pending_count']} 条待同步记录")
                    
                    for sync in sync_status.get('syncs', []):
                        # 确认同步
                        self.client.confirm_sync(sync['id'])
                
                # 等待下一个周期
                time.sleep(self.sync_interval)
            
            except Exception as e:
                logger.error(f"同步循环异常: {str(e)}")
                time.sleep(self.sync_interval)
    
    def stop(self):
        """停止同步循环"""
        self.running = False
        logger.info("同步循环已停止")


if __name__ == '__main__':
    # 示例使用
    
    # 创建客户端
    client = CloudSyncClient(
        server_url='http://124.222.116.32:5000',
        username='admin',
        password='your-password'
    )
    
    # 登录
    if client.login():
        # 获取用户列表
        users = client.list_users()
        print(f"用户列表: {json.dumps(users, indent=2)}")
        
        # 获取统计信息
        stats = client.get_stats()
        print(f"统计信息: {json.dumps(stats, indent=2)}")
        
        # 获取待同步数据
        sync_status = client.get_pending_syncs()
        print(f"待同步数据: {json.dumps(sync_status, indent=2)}")
