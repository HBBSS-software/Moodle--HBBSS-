import paramiko
import os
import logging
from cloud_sync_client import CloudSyncClient, SyncManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VMManager:
    """虚拟机管理器，用于与远程服务器交互"""
    
    def __init__(self, hostname, username, password, port=22):
        """
        初始化VM管理器
        
        Args:
            hostname: 服务器地址
            username: SSH用户名
            password: SSH密码
            port: SSH端口，默认22
        """
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.ssh_client = None
    
    def connect(self):
        """连接到VM"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                self.hostname,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10
            )
            logger.info(f"成功连接到VM: {self.hostname}")
            return True
        except Exception as e:
            logger.error(f"连接到VM失败: {str(e)}")
            return False
    
    def execute_command(self, command):
        """
        执行远程命令
        
        Args:
            command: 要执行的命令
        
        Returns:
            str: 命令输出
        """
        if not self.ssh_client:
            logger.error("未连接到VM")
            return None
        
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            
            if error:
                logger.error(f"命令执行错误: {error}")
                return None
            
            return output
        except Exception as e:
            logger.error(f"执行命令异常: {str(e)}")
            return None
    
    def disconnect(self):
        """断开连接"""
        if self.ssh_client:
            self.ssh_client.close()
            logger.info("已断开VM连接")
    
    def deploy_project(self, project_path):
        """部署项目到VM"""
        logger.info(f"开始部署项目: {project_path}")
        
        # 创建项目目录
        mkdir_cmd = "mkdir -p /home/ubuntu/hbbss-account-system"
        self.execute_command(mkdir_cmd)
        
        # 创建虚拟环境
        venv_cmd = "cd /home/ubuntu/hbbss-account-system && python3 -m venv venv"
        self.execute_command(venv_cmd)
        
        logger.info("项目部署初始化完成")


class HBBSSAccountManager:
    """HBBSS账号管理系统集成管理器"""
    
    def __init__(self, server_url, vm_hostname, vm_username, vm_password):
        """
        初始化HBBSS账号管理器
        
        Args:
            server_url: 账号管理服务器URL
            vm_hostname: VM主机名
            vm_username: VM用户名
            vm_password: VM密码
        """
        self.server_url = server_url
        self.vm_manager = VMManager(vm_hostname, vm_username, vm_password)
        self.sync_client = None
    
    def setup_account_system(self, admin_username, admin_password):
        """
        设置账号管理系统
        
        Args:
            admin_username: 管理员用户名
            admin_password: 管理员密码
        """
        logger.info("设置账号管理系统...")
        
        # 连接到VM
        if not self.vm_manager.connect():
            return False
        
        # 初始化同步客户端
        self.sync_client = CloudSyncClient(
            server_url=self.server_url,
            username=admin_username,
            password=admin_password
        )
        
        # 登录
        if not self.sync_client.login():
            logger.error("同步客户端登录失败")
            return False
        
        logger.info("账号管理系统设置完成")
        return True
    
    def get_server_stats(self):
        """获取服务器统计信息"""
        if not self.sync_client or not self.sync_client.is_authenticated():
            logger.error("同步客户端未认证")
            return None
        
        return self.sync_client.get_stats()
    
    def list_all_users(self):
        """列表所有用户"""
        if not self.sync_client or not self.sync_client.is_authenticated():
            logger.error("同步客户端未认证")
            return None
        
        return self.sync_client.list_users()
    
    def create_bulk_users(self, users_data):
        """
        批量创建用户
        
        Args:
            users_data: 用户数据列表
        """
        if not self.sync_client or not self.sync_client.is_authenticated():
            logger.error("同步客户端未认证")
            return []
        
        created_users = []
        for user_data in users_data:
            user = self.sync_client.register_user(**user_data)
            if user:
                created_users.append(user)
                logger.info(f"用户创建成功: {user['username']}")
            else:
                logger.error(f"用户创建失败: {user_data.get('username')}")
        
        return created_users
    
    def start_sync_daemon(self):
        """启动同步守护进程"""
        if not self.sync_client:
            logger.error("同步客户端未初始化")
            return
        
        logger.info("启动同步守护进程...")
        manager = SyncManager(self.sync_client, sync_interval=300)
        manager.sync_loop()
    
    def cleanup(self):
        """清理资源"""
        self.vm_manager.disconnect()
        logger.info("资源清理完成")


# 使用示例
if __name__ == '__main__':
    # 配置参数
    SERVER_URL = 'http://124.222.116.32:5000'  # 账号管理服务器地址
    VM_HOSTNAME = '124.222.116.32'
    VM_USERNAME = 'ubuntu'
    VM_PASSWORD = 'hbbssisthebest!666'
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin-password'
    
    # 创建管理器
    manager = HBBSSAccountManager(
        server_url=SERVER_URL,
        vm_hostname=VM_HOSTNAME,
        vm_username=VM_USERNAME,
        vm_password=VM_PASSWORD
    )
    
    try:
        # 设置系统
        if manager.setup_account_system(ADMIN_USERNAME, ADMIN_PASSWORD):
            # 获取统计信息
            stats = manager.get_server_stats()
            print(f"服务器统计: {stats}")
            
            # 列表所有用户
            users = manager.list_all_users()
            print(f"用户数量: {len(users) if users else 0}")
            
            # 批量创建用户（示例）
            new_users = [
                {
                    'username': 'user1',
                    'password': 'pass123',
                    'email': 'user1@hbbss.com',
                    'full_name': 'User One'
                },
                {
                    'username': 'user2',
                    'password': 'pass456',
                    'email': 'user2@hbbss.com',
                    'full_name': 'User Two'
                }
            ]
            # 创建用户（取消注释以使用）
            # created = manager.create_bulk_users(new_users)
            # print(f"创建了 {len(created)} 个用户")
    
    except Exception as e:
        logger.error(f"错误: {str(e)}")
    
    finally:
        manager.cleanup()
