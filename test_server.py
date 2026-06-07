#!/usr/bin/env python3
"""
HBBSS账号管理系统 - 测试脚本
演示如何使用API和客户端库
"""

import sys
import time
import json
from cloud_sync_client import CloudSyncClient


def test_basic_flow():
    """测试基本工作流"""
    
    print("=" * 60)
    print("HBBSS 账号管理系统 - 测试脚本")
    print("=" * 60)
    print()
    
    # 配置
    SERVER_URL = 'http://127.0.0.1:5000'  # 本地测试，生产环境改为 http://124.222.116.32:5000
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin-password'
    
    print("[1] 创建客户端...")
    client = CloudSyncClient(
        server_url=SERVER_URL,
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD
    )
    
    print("[2] 登录...")
    if not client.login():
        print("ERROR: 登录失败！")
        print("请确保:")
        print("  1. 服务器正在运行")
        print("  2. 数据库已初始化")
        print("  3. 管理员账号已创建")
        return
    
    print("✓ 登录成功")
    print()
    
    # 测试1: 注册新用户
    print("[3] 注册新用户...")
    new_user = client.register_user(
        username='testuser',
        password='testpass123',
        email='test@example.com',
        full_name='Test User',
        department='Testing',
        phone='1234567890'
    )
    
    if new_user:
        print(f"✓ 用户注册成功: {new_user['username']}")
        test_user_id = new_user['id']
    else:
        print("✗ 用户注册失败")
        return
    
    print()
    
    # 测试2: 获取用户信息
    print("[4] 获取用户信息...")
    user = client.get_user(test_user_id)
    if user:
        print(f"✓ 获取成功:")
        print(f"  用户名: {user['username']}")
        print(f"  邮箱: {user['email']}")
        print(f"  部门: {user['department']}")
    else:
        print("✗ 获取失败")
    
    print()
    
    # 测试3: 更新用户信息
    print("[5] 更新用户信息...")
    updated_user = client.update_user(
        test_user_id,
        full_name='Updated Test User',
        department='Updated Department',
        phone='9876543210'
    )
    
    if updated_user:
        print(f"✓ 用户更新成功:")
        print(f"  全名: {updated_user['full_name']}")
        print(f"  部门: {updated_user['department']}")
        print(f"  电话: {updated_user['phone']}")
    else:
        print("✗ 用户更新失败")
    
    print()
    
    # 测试4: 列表所有用户
    print("[6] 获取所有用户列表...")
    users = client.list_users()
    if users:
        print(f"✓ 成功获取 {len(users)} 个用户:")
        for user in users[:5]:  # 显示前5个
            print(f"  - {user['username']} ({user['email']})")
        if len(users) > 5:
            print(f"  ... 还有 {len(users) - 5} 个用户")
    else:
        print("✗ 获取用户列表失败")
    
    print()
    
    # 测试5: 获取统计信息
    print("[7] 获取系统统计信息...")
    stats = client.get_stats()
    if stats:
        print("✓ 统计信息:")
        print(f"  总用户数: {stats['total_users']}")
        print(f"  活跃用户: {stats['active_users']}")
        print(f"  管理员数: {stats['admin_count']}")
        print(f"  待同步: {stats['pending_syncs']}")
        print(f"  同步失败: {stats['failed_syncs']}")
        print(f"  访问日志数: {stats['total_access_logs']}")
    else:
        print("✗ 获取统计信息失败")
    
    print()
    
    # 测试6: 获取同步状态
    print("[8] 获取待同步数据...")
    sync_status = client.get_pending_syncs()
    if sync_status is not None:
        print(f"✓ 待同步记录: {sync_status['pending_count']}")
        for sync in sync_status.get('syncs', [])[:3]:
            print(f"  - ID {sync['id']}: {sync['action']} (用户 {sync['user_id']})")
    else:
        print("✗ 获取同步状态失败")
    
    print()
    
    # 测试7: 导出账号
    print("[9] 导出所有账号信息...")
    export_data = client.export_all_accounts()
    if export_data:
        print(f"✓ 导出成功:")
        print(f"  导出时间: {export_data['exported_at']}")
        print(f"  用户总数: {export_data['total_users']}")
    else:
        print("✗ 导出失败")
    
    print()
    
    print("=" * 60)
    print("测试完成！")
    print("=" * 60)
    print()
    print("下一步:")
    print("1. 修改.env文件中的配置")
    print("2. 启动生产环境服务: gunicorn -w 4 -b 0.0.0.0:5000 server:app")
    print("3. 配置Nginx反向代理（参见DEPLOYMENT.md）")
    print("4. 配置系统服务（参见DEPLOYMENT.md）")
    print("5. 定期备份数据库")


def test_sync_client():
    """测试同步客户端"""
    
    print("=" * 60)
    print("同步客户端测试")
    print("=" * 60)
    print()
    
    from cloud_sync_client import SyncManager
    
    SERVER_URL = 'http://127.0.0.1:5000'
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin-password'
    
    print("[1] 创建同步管理器...")
    client = CloudSyncClient(
        server_url=SERVER_URL,
        username=ADMIN_USERNAME,
        password=ADMIN_PASSWORD
    )
    
    manager = SyncManager(client, sync_interval=10)
    
    print("[2] 同步管理器将每10秒检查一次待同步数据")
    print("按 Ctrl+C 停止")
    
    try:
        # 这里只演示，不实际运行
        # manager.sync_loop()
        print("（演示模式，未实际启动同步循环）")
    except KeyboardInterrupt:
        print("\n已停止")
    
    print()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--sync':
        test_sync_client()
    else:
        test_basic_flow()
