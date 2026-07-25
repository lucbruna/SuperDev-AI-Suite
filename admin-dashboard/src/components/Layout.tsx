import React, { useState } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { Layout as AntLayout, Sider, Header, Content, Menu, Avatar, Dropdown, Menu as AntMenu, Space, Tooltip } from 'antd';
import { 
  MenuOutlined, DashboardOutlined, TeamOutlined, FolderOutlined, 
  GitBranchOutlined, RobotOutlined, DatabaseOutlined, 
  PluginOutlined, FlagOutlined, SettingOutlined, LogoutOutlined, 
  BellOutlined, UserOutlined, MenuUnfoldOutlined, MenuFoldOutlined, SearchOutlined,
  UserOutlined
} from '@ant-design/icons';
import { useAuth } from '../hooks/useAuth';
import { useFeatureFlags } from '../hooks/useFeatureFlags';
import './Layout.css';

const { SubMenu } = Menu;

const navItems = [
  { key: 'dashboard', label: 'Dashboard', icon: DashboardOutlined, path: '/dashboard' },
  { key: 'organizations', label: 'Organizations', icon: TeamOutlined, path: '/organizations' },
  { key: 'projects', label: 'Projects', icon: FolderOutlined, path: '/projects' },
  { key: 'workflows', label: 'Workflows', icon: GitBranchOutlined, path: '/workflows' },
  { key: 'agents', label: 'Agents', icon: RobotOutlined, path: '/agents' },
  { key: 'knowledgeBase', label: 'Knowledge Base', icon: DatabaseOutlined, path: '/knowledge-base', feature: 'knowledgeBase' },
  { key: 'plugins', label: 'Plugins', icon: PluginOutlined, path: '/plugins', feature: 'pluginMarketplace' },
  { key: 'featureFlags', label: 'Feature Flags', icon: FlagOutlined, path: '/feature-flags', feature: 'featureFlags' },
  { key: 'settings', label: 'Settings', icon: SettingOutlined, path: '/settings' },
];

export function LayoutComponent() {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();
  const { user, logout, org } = useAuth();
  const { flags } = useFeatureFlags();
  
  const filteredNavItems = navItems.filter(item => !item.feature || flags[item.feature]);

  const handleLogout = async () => {
    await logout();
  };

  const userMenuItems = [
    { label: 'Profile', key: 'profile', icon: <UserOutlined /> },
    { label: 'Settings', key: 'settings', icon: <SettingOutlined />, onClick: () => window.location.href = '/settings' },
    { type: 'divider' },
    { label: 'Logout', key: 'logout', icon: <LogoutOutlined />, danger: true, onClick: handleLogout },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        width={260}
        collapsedWidth={80}
        theme="light"
        className="sidebar"
      >
        <div className="logo">
          {!collapsed && (
            <div className="logo-content">
              <span className="logo-icon">SD</span>
              <span className="logo-text">SuperDev</span>
            </div>
          )}
          {collapsed && <div className="logo-icon">SD</div>}
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname.replace('/', '') || 'dashboard']}
          items={filteredNavItems.map(item => ({
            key: item.path.replace('/', '') || 'dashboard',
            label: item.label,
            icon: React.createElement(item.icon),
          }))}
          onClick={({ key }) => window.location.href = `/${key}`}
        />
      </Sider>
      <Layout className="main-layout">
        <Header className="header" style={{ padding: '0 24px', height: 64 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '100%' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              <button
                onClick={() => setCollapsed(!collapsed)}
                className="collapse-btn"
                aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
              >
                {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              </button>
              <div className="search-box">
                <SearchOutlined />
                <input 
                  type="text" 
                  placeholder="Search..." 
                  className="search-input"
                  placeholder="Search..."
                />
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <Tooltip title="Notifications">
                <div className="icon-btn" style={{ position: 'relative' }}>
                  <BellOutlined />
                  <span className="notification-badge">3</span>
                </div>
              </Tooltip>
              <Dropdown
                menu={{ items: userMenuItems }}
                trigger={['click']}
                placement="bottomRight"
              >
                <Space align="center" style={{ cursor: 'pointer' }}>
                  <Avatar size={32} src={user?.avatar_url} alt={user?.email}>
                    {user?.email?.charAt(0).toUpperCase()}
                  </Avatar>
                  <span className="username">{user?.email}</span>
                  <SettingOutlined />
                </Space>
              </Dropdown>
            </div>
          </div>
        </Header>
        <Content className="content" style={{ padding: 24, margin: 0 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}

export { LayoutComponent as Layout };