import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Tag, Modal, Form, Input, Select, Space, Switch, Tooltip, Dropdown, Menu, Avatar, Badge, Row, Col, Divider, List, Typography, Empty, Progress, Statistic, Tabs, Descriptions, Popconfirm, message } from 'antd';
import { 
  PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined, 
  MoreOutlined, SearchOutlined, FilterOutlined, DownloadOutlined,
  PlayOutlined, StopOutlined, PauseOutlined, ReloadOutlined,
  CopyOutlined, CodeOutlined, TerminalOutlined, RobotOutlined,
  CheckCircleOutlined, CloseCircleOutlined, ExclamationCircleOutlined,
  ClockCircleOutlined, FileTextOutlined, ArrowUpOutlined, ArrowDownOutlined,
  EnvironmentOutlined, DatabaseOutlined, UserOutlined, SettingOutlined,
  WarningOutlined, InfoCircleOutlined, SafetyOutlined, ExperimentOutlined,
  HistoryOutlined, LogoutOutlined, LinkOutlined, ShareAltOutlined,
  UploadOutlined, FolderOutlined, FileOutlined, SearchOutlined,
  UnlockOutlined, LockOutlined, KeyOutlined, ShieldOutlined,
  TeamOutlined, ProjectOutlined, GitBranchOutlined, ThunderboltOutlined
} from '@ant-design/icons';
import { api } from '../services/api';
import { format } from 'date-fns';

interface SettingsSection {
  key: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  component: React.ReactNode;
}

export function Settings() {
  const [activeTab, setActiveTab] = useState('general');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState<any>({});

  const tabs = [
    { key: 'general', tab: 'General', icon: <SettingOutlined /> },
    { key: 'auth', tab: 'Authentication', icon: <LockOutlined /> },
    { key: 'security', tab: 'Security', icon: <ShieldOutlined /> },
    { key: 'integrations', tab: 'Integrations', icon: <LinkOutlined /> },
    { key: 'notifications', tab: 'Notifications', icon: <BellOutlined /> },
    { key: 'api', tab: 'API Keys', icon: <KeyOutlined /> },
    { key: 'billing', tab: 'Billing', icon: <CreditCardOutlined /> },
    { key: 'advanced', tab: 'Advanced', icon: <SafetyOutlined /> },
  ];

  const fetchSettings = async () => {
    try {
      const response = await api.get('/settings');
      setSettings(response.data);
    } catch (error) {
      console.error('Failed to fetch settings:', error);
    }
  };

  const saveSettings = async (section: string, data: any) => {
    setSaving(true);
    try {
      await api.put(`/settings/${section}`, data);
      message.success(`${section} settings saved successfully`);
      fetchSettings();
    } catch (error) {
      console.error(`Failed to save ${section} settings:`, error);
      message.error(`Failed to save ${section} settings`);
    } finally {
      setSaving(false);
    }
  };

  const testConnection = async (integration: string) => {
    try {
      await api.post(`/integrations/${integration}/test`);
      message.success(`${integration} connection test successful`);
    } catch (error) {
      message.error(`${integration} connection test failed`);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const renderGeneralTab = () => (
    <Card>
      <Form layout="vertical" onFinish={(values) => saveSettings('general', values)}>
        <Form.Item name="app_name" label="Application Name" rules={[{ required: true }]}>
          <Input placeholder="SuperDev AI Suite" />
        </Form.Item>
        <Form.Item name="app_description" label="Description">
          <Input.TextArea rows={3} placeholder="Enter application description" />
        </Form.Item>
        <Form.Item name="timezone" label="Default Timezone">
          <Select placeholder="Select timezone" style={{ width: '100%' }}>
            <Option value="UTC">UTC</Option>
            <Option value="America/New_York">Eastern Time</Option>
            <Option value="America/Chicago">Central Time</Option>
            <Option value="America/Denver">Mountain Time</Option>
            <Option value="America/Los_Angeles">Pacific Time</Option>
            <Option value="Europe/London">London</Option>
            <Option value="Europe/Paris">Paris</Option>
            <Option value="Asia/Tokyo">Tokyo</Option>
            <Option value="Asia/Shanghai">Shanghai</Option>
          </Select>
        </Form.Item>
        <Form.Item name="date_format" label="Date Format">
          <Select placeholder="Select date format" style={{ width: '100%' }}>
            <Option value="YYYY-MM-DD">YYYY-MM-DD (2024-01-15)</Option>
            <Option value="MM/DD/YYYY">MM/DD/YYYY (01/15/2024)</Option>
            <Option value="DD/MM/YYYY">DD/MM/YYYY (15/01/2024)</Option>
            <Option value="MMM D, YYYY">MMM D, YYYY (Jan 15, 2024)</Option>
          </Select>
        </Form.Item>
        <Form.Item name="language" label="Default Language">
          <Select placeholder="Select language" style={{ width: '100%' }}>
            <Option value="en">English</Option>
            <Option value="es">Spanish</Option>
            <Option value="fr">French</Option>
            <Option value="de">German</Option>
            <Option value="ja">Japanese</Option>
            <Option value="zh">Chinese</Option>
          </Select>
        </Form.Item>
        <Form.Item name="maintenance_mode" label="Maintenance Mode" valuePropName="checked">
          <Switch />
        </Form.Item>
        <Form.Item name="maintenance_message" label="Maintenance Message">
          <Input.TextArea rows={2} placeholder="Message to display during maintenance" />
        </Form.Item>
        <Form.Item name="registration_enabled" label="Allow Registration" valuePropName="checked">
          <Switch />
        </Form.Item>
        <Form.Item name="email_verification_required" label="Require Email Verification" valuePropName="checked">
          <Switch />
        </Form.Item>
        <Divider />
        <Button type="primary" htmlType="submit" loading={saving}>
          <SaveOutlined /> Save General Settings
        </Button>
      </Form>
    </Card>
  );

  const renderAuthTab = () => (
    <Card>
      <Tabs defaultActiveKey="providers">
        <Tabs.TabPane tab="OAuth Providers" key="providers">
          <Card>
            <Form layout="vertical" onFinish={(values) => saveSettings('auth', values)}>
              <Form.Item name="jwt_secret" label="JWT Secret" rules={[{ required: true }]}>
                <Input.Password placeholder="Enter JWT secret key" />
              </Form.Item>
              <Form.Item name="jwt_algorithm" label="JWT Algorithm">
                <Select placeholder="Select algorithm" style={{ width: '100%' }}>
                  <Option value="HS256">HS256</Option>
                  <Option value="HS512">HS512</Option>
                  <Option value="RS256">RS256</Option>
                  <Option value="RS512">RS512</Option>
                </Select>
              </Form.Item>
              <Form.Item name="access_token_expire" label="Access Token Expiry (minutes)">
                <InputNumber min={5} max={1440} />
              </Form.Item>
              <Form.Item name="refresh_token_expire" label="Refresh Token Expiry (days)">
                <InputNumber min={1} max={30} />
              </Form.Item>
              <Divider />
              <Typography.Title level={4}>OAuth2/OIDC Providers</Typography.Title>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Form.Item name="oidc_enabled" label="Enable OIDC" valuePropName="checked">
                  <Switch />
                </Form.Item>
                <Form.Item name="oidc_issuer_url" label="OIDC Issuer URL">
                  <Input placeholder="https://auth.example.com" />
                </Form.Item>
                <Form.Item name="oidc_client_id" label="Client ID">
                  <Input />
                </Form.Item>
                <Form.Item name="oidc_client_secret" label="Client Secret">
                  <Input.Password />
                </Form.Item>
                <Form.Item name="oidc_redirect_uri" label="Redirect URI">
                  <Input placeholder="https://app.example.com/auth/callback" />
                </Form.Item>
                <Form.Item name="github_oauth_enabled" label="Enable GitHub OAuth" valuePropName="checked">
                  <Switch />
                </Form.Item>
                <Form.Item name="github_client_id" label="GitHub Client ID">
                  <Input />
                </Form.Item>
                <Form.Item name="github_client_secret" label="GitHub Client Secret">
                  <Input.Password />
                </Form.Item>
                <Form.Item name="google_oauth_enabled" label="Enable Google OAuth" valuePropName="checked">
                  <Switch />
                </Form.Item>
                <Form.Item name="google_client_id" label="Google Client ID">
                  <Input />
                </Form.Item>
                <Form.Item name="google_client_secret" label="Google Client Secret">
                  <Input.Password />
                </Form.Item>
              </Space>
            </Form>
          </Card>
        </Tabs.TabPane>
        <Tabs.TabPane tab="Session Management" key="session">
          <Card>
            <Form layout="vertical" onFinish={(values) => saveSettings('auth', values)}>
              <Form.Item name="session_ttl" label="Session TTL (seconds)">
                <InputNumber min={300} max={2592000} />
              </Form.Item>
              <Form.Item name="max_sessions_per_user" label="Max Sessions Per User">
                <InputNumber min={1} max={100} />
              </Form.Item>
              <Form.Item name="require_mfa_for_admin" label="Require MFA for Admins" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="password_min_length" label="Minimum Password Length">
                <InputNumber min={8} max={128} />
              </Form.Item>
              <Form.Item name="password_require_special" label="Require Special Characters" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="password_require_uppercase" label="Require Uppercase" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="password_require_number" label="Require Numbers" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Button type="primary" htmlType="submit" loading={saving}>
                <SaveOutlined /> Save Session Settings
              </Button>
            </Form>
          </Card>
        </Tabs.TabPane>
      </Tabs>
    </Card>
  );

  const renderSecurityTab = () => (
    <Card>
      <Tabs defaultActiveKey="policies">
        <Tabs.TabPane tab="Security Policies" key="policies">
          <Card>
            <Typography.Title level={4}>Password Policies</Typography.Title>
            <Form layout="vertical" onFinish={(values) => saveSettings('security', values)}>
              <Form.Item name="password_min_length" label="Minimum Password Length">
                <InputNumber min={8} max={128} />
              </Form.Item>
              <Form.Item name="password_require_uppercase" label="Require Uppercase" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="password_require_lowercase" label="Require Lowercase" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="password_require_number" label="Require Numbers" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="password_require_special" label="Require Special Characters" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="password_max_age" label="Password Max Age (days)">
                <InputNumber min={0} max={365} />
              </Form.Item>
              <Form.Item name="password_history" label="Password History Count">
                <InputNumber min={0} max={24} />
              </Form.Item>
              <Divider />
              <Typography.Title level={4}>Account Lockout</Typography.Title>
              <Form.Item name="lockout_threshold" label="Failed Attempts Before Lockout">
                <InputNumber min={1} max={20} />
              </Form.Item>
              <Form.Item name="lockout_duration" label="Lockout Duration (minutes)">
                <InputNumber min={1} max={1440} />
              </Form.Item>
              <Form.Item name="lockout_reset_after" label="Reset Lockout After (minutes)">
                <InputNumber min={1} max={1440} />
              </Form.Item>
              <Divider />
              <Typography.Title level={4}>MFA Settings</Typography.Title>
              <Form.Item name="mfa_enabled" label="Enable MFA" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="mfa_required_for_admin" label="Require MFA for Admins" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="mfa_issuer" label="MFA Issuer Name">
                <Input placeholder="SuperDev" />
              </Form.Item>
              <Divider />
              <Typography.Title level={4}>Session Security</Typography.Title>
              <Form.Item name="concurrent_sessions" label="Max Concurrent Sessions">
                <InputNumber min={1} max={50} />
              </Form.Item>
              <Form.Item name="idle_timeout" label="Idle Timeout (minutes)">
                <InputNumber min={5} max={1440} />
              </Form.Item>
              <Form.Item name="absolute_timeout" label="Absolute Session Timeout (minutes)">
                <InputNumber min={15} max={10080} />
              </Form.Item>
              <Button type="primary" htmlType="submit" loading={saving}>
                <SaveOutlined /> Save Security Settings
              </Button>
            </Form>
          </Card>
        </Tabs.TabPane>
        <Tabs.TabPane tab="IP Allowlist" key="ip_allowlist">
          <Card>
            <Form layout="vertical" onFinish={(values) => saveSettings('security', values)}>
              <Form.Item name="ip_allowlist_enabled" label="Enable IP Allowlist" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="ip_allowlist" label="Allowed IPs (CIDR)">
                <Input.TextArea rows={5} placeholder="192.168.1.0/24&#10;10.0.0.0/8" />
              </Form.Item>
              <Form.Item name="ip_denylist" label="Denied IPs (CIDR)">
                <Input.TextArea rows={5} placeholder="192.168.1.100/32&#10;10.0.0.0/8" />
              </Form.Item>
              <Button type="primary" htmlType="submit" loading={saving}>
                <SaveOutlined /> Save IP Rules
              </Button>
            </Form>
          </Card>
        </Tabs.TabPane>
      </Tabs>
    </Card>
  );

  const renderIntegrationsTab = () => (
    <Card>
      <Tabs defaultActiveKey="github">
        <Tabs.TabPane tab="GitHub" key="github">
          <Card>
            <Form layout="vertical" onFinish={(values) => saveSettings('integrations', values)}>
              <Form.Item name="github_enabled" label="Enable GitHub Integration" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="github_client_id" label="Client ID">
                <Input placeholder="GitHub OAuth App Client ID" />
              </Form.Item>
              <Form.Item name="github_client_secret" label="Client Secret">
                <Input.Password placeholder="GitHub OAuth App Client Secret" />
              </Form.Item>
              <Form.Item name="github_webhook_secret" label="Webhook Secret">
                <Input.Password placeholder="Webhook secret for verifying payloads" />
              </Form.Item>
              <Form.Item name="github_webhook_url" label="Webhook URL">
                <Input placeholder="https://your-domain.com/webhooks/github" />
              </Form.Item>
              <Divider />
              <Button type="primary" htmlType="submit" loading={saving} onClick={() => testConnection('github')}>
                <ReloadOutlined /> Test Connection
              </Button>
            </Form>
          </Card>
        </Tabs.TabPane>
        <Tabs.TabPane tab="Slack" key="slack">
          <Card>
            <Form layout="vertical" onFinish={(values) => saveSettings('integrations', values)}>
              <Form.Item name="slack_enabled" label="Enable Slack Integration" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="slack_client_id" label="Client ID">
                <Input placeholder="Slack App Client ID" />
              </Form.Item>
              <Form.Item name="slack_client_secret" label="Client Secret">
                <Input.Password placeholder="Slack App Client Secret" />
              </Form.Item>
              <Form.Item name="slack_signing_secret" label="Signing Secret">
                <Input.Password placeholder="Slack Signing Secret" />
              </Form.Item>
              <Form.Item name="slack_bot_token" label="Bot Token">
                <Input.Password placeholder="xoxb-..." />
              </Form.Item>
              <Divider />
              <Button type="primary" htmlType="submit" loading={saving} onClick={() => testConnection('slack')}>
                <ReloadOutlined /> Test Connection
              </Button>
            </Form>
          </Card>
        </Tabs.TabPane>
        <Tabs.TabPane tab="Jira" key="jira">
          <Card>
            <Form layout="vertical" onFinish={(values) => saveSettings('integrations', values)}>
              <Form.Item name="jira_enabled" label="Enable Jira Integration" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="jira_host" label="Jira Host">
                <Input placeholder="https://your-domain.atlassian.net" />
              </Form.Item>
              <Form.Item name="jira_email" label="Email">
                <Input placeholder="your-email@company.com" />
              </Form.Item>
              <Form.Item name="jira_api_token" label="API Token">
                <Input.Password placeholder="Jira API Token" />
              </Form.Item>
              <Form.Item name="jira_project_key" label="Default Project Key">
                <Input placeholder="PROJ" />
              </Form.Item>
              <Divider />
              <Button type="primary" htmlType="submit" loading={saving} onClick={() => testConnection('jira')}>
                <ReloadOutlined /> Test Connection
              </Button>
            </Form>
          </Card>
        </Tabs.TabPane>
        <Tabs.TabPane tab="Docker" key="docker">
          <Card>
            <Form layout="vertical" onFinish={(values) => saveSettings('integrations', values)}>
              <Form.Item name="docker_enabled" label="Enable Docker Integration" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="docker_host" label="Docker Host">
                <Input placeholder="unix:///var/run/docker.sock or tcp://host:2376" />
              </Form.Item>
              <Form.Item name="docker_tls_verify" label="TLS Verify" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="docker_cert_path" label="Certificate Path">
                <Input placeholder="/path/to/certs" />
              </Form.Item>
              <Divider />
              <Button type="primary" htmlType="submit" loading={saving} onClick={() => testConnection('docker')}>
                <ReloadOutlined /> Test Connection
              </Button>
            </Form>
          </Card>
        </Tabs.TabPane>
      </Tabs>
    </Card>
  );

  const renderNotificationsTab = () => (
    <Card>
      <Tabs defaultActiveKey="email">
        <Tabs.TabPane tab="Email" key="email">
          <Card>
            <Form layout="vertical" onFinish={(values) => saveSettings('notifications', values)}>
              <Form.Item name="email_enabled" label="Enable Email Notifications" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="smtp_host" label="SMTP Host">
                <Input placeholder="smtp.gmail.com" />
              </Form.Item>
              <Form.Item name="smtp_port" label="SMTP Port">
                <InputNumber min={1} max={65535} />
              </Form.Item>
              <Form.Item name="smtp_username" label="SMTP Username">
                <Input placeholder="your-email@gmail.com" />
              </Form.Item>
              <Form.Item name="smtp_password" label="SMTP Password">
                <Input.Password placeholder="App password or SMTP password" />
              </Form.Item>
              <Form.Item name="smtp_tls" label="Use TLS" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="smtp_from_email" label="From Email">
                <Input placeholder="noreply@yourdomain.com" />
              </Form.Item>
              <Form.Item name="smtp_from_name" label="From Name">
                <Input placeholder="SuperDev AI Suite" />
              </Form.Item>
              <Divider />
              <Typography.Title level={4}>Notification Preferences</Typography.Title>
              <Form.Item name="notify_on_workflow_complete" label="Workflow Complete" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="notify_on_workflow_failed" label="Workflow Failed" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="notify_on_agent_execution" label="Agent Execution Complete" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="notify_on_security_alert" label="Security Alerts" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="notify_on_billing" label="Billing Alerts" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Divider />
              <Button type="primary" htmlType="submit" loading={saving}>
                <SaveOutlined /> Save Email Settings
              </Button>
              <Button type="default" style={{ marginLeft: 8 }} onClick={() => testConnection('email')}>
                <ReloadOutlined /> Send Test Email
              </Button>
            </Form>
          </Card>
        </Tabs.TabPane>
        <Tabs.TabPane tab="Slack" key="slack">
          <Card>
            <Form layout="vertical" onFinish={(values) => saveSettings('notifications', values)}>
              <Form.Item name="slack_enabled" label="Enable Slack Notifications" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="slack_webhook_url" label="Webhook URL">
                <Input placeholder="https://hooks.slack.com/services/..." />
              </Form.Item>
              <Form.Item name="slack_channel" label="Default Channel">
                <Input placeholder="#general or #alerts" />
              </Form.Item>
              <Form.Item name="slack_bot_token" label="Bot Token">
                <Input.Password placeholder="xoxb-..." />
              </Form.Item>
              <Divider />
              <Button type="primary" htmlType="submit" loading={saving}>
                <SaveOutlined /> Save Slack Settings
              </Button>
              <Button type="default" style={{ marginLeft: 8 }} onClick={() => testConnection('slack')}>
                <ReloadOutlined /> Test Connection
              </Button>
            </Form>
          </Card>
        </Tabs.TabPane>
        <Tabs.TabPane tab="Webhooks" key="webhooks">
          <Card>
            <Table
              columns={[
                { title: 'Name', dataIndex: 'name', key: 'name' },
                { title: 'URL', dataIndex: 'url', key: 'url', ellipsis: true },
                { title: 'Events', dataIndex: 'events', key: 'events', render: (v: string[]) => <Space wrap>{v.map(e => <Tag key={e}>{e}</Tag>)}</Space> },
                { title: 'Status', dataIndex: 'active', key: 'active', render: (v: boolean) => v ? <Tag color="green">Active</Tag> : <Tag color="red">Inactive</Tag> },
                { title: 'Actions', key: 'actions', render: (_: any, record: any) => <Space><Button type="link" size="small"><EditOutlined /></Button><Popconfirm title="Delete this webhook?" onConfirm={() => handleDeleteWebhook(record.id)}><Button type="link" size="small" danger><DeleteOutlined /></Button></Popconfirm></Space> },
              ]
              dataSource={[]}
              pagination={false}
            />
            <Button type="dashed" style={{ marginTop: 16, width: '100%' }} onClick={() => setWebhookModalVisible(true)}>
              <PlusOutlined /> Add Webhook
            </Button>
          </Card>
        </Tabs.TabPane>
      </Tabs>
    </Card>
  );

  const renderApiKeysTab = () => (
    <Card>
      <Table
        columns={[
          { title: 'Name', dataIndex: 'name', key: 'name' },
          { title: 'Prefix', dataIndex: 'prefix', key: 'prefix', width: 100 },
          { title: 'Scopes', dataIndex: 'scopes', key: 'scopes', render: (v: string[]) => <Space wrap>{v.map(s => <Tag key={s}>{s}</Tag>)}</Space> },
          { title: 'Last Used', dataIndex: 'last_used', key: 'last_used', render: (v: string) => v ? format(new Date(v), 'PPp') : 'Never' },
          { title: 'Expires', dataIndex: 'expires_at', key: 'expires_at', render: (v: string) => v ? format(new Date(v), 'PP') : 'Never' },
          { title: 'Status', dataIndex: 'active', key: 'active', render: (v: boolean) => v ? <Tag color="green">Active</Tag> : <Tag color="red">Inactive</Tag> },
          { title: 'Actions', key: 'actions', render: (_: any, record: any) => <Space><Button type="link" size="small" onClick={() => handleCopyApiKey(record.key)}><CopyOutlined /></Button><Popconfirm title="Revoke this API key?" onConfirm={() => handleRevokeApiKey(record.id)}><Button type="link" size="small" danger><DeleteOutlined /></Button></Popconfirm></Space> },
        ]
        dataSource={[]}
        pagination={false}
      />
      <Button type="dashed" style={{ marginTop: 16, width: '100%' }} onClick={() => setApiKeyModalVisible(true)}>
        <PlusOutlined /> Create API Key
      </Button>
    </Card>
  );

  const renderBillingTab = () => (
    <Card>
      <Tabs defaultActiveKey="subscription">
        <Tabs.TabPane tab="Subscription" key="subscription">
          <Card>
            <Descriptions title="Current Plan" column={2}>
              <Descriptions.Item label="Plan">Professional</Descriptions.Item>
              <Descriptions.Item label="Status">Active</Descriptions.Item>
              <Descriptions.Item label="Billing Cycle">Monthly</Descriptions.Item>
              <Descriptions.Item label="Next Billing Date">{format(new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), 'PP')}</Descriptions.Item>
              <Descriptions.Item label="Price">$99/month</Descriptions.Item>
              <Descriptions.Item label="Usage This Month">$45.50</Descriptions.Item>
            </Descriptions>
            <Button type="primary" style={{ marginTop: 16 }}>Manage Subscription</Button>
          </Card>
        </Tabs.TabPane>
        <Tabs.TabPane tab="Usage" key="usage">
          <Card>
            <Table
              columns={[
                { title: 'Resource', dataIndex: 'resource', key: 'resource' },
                { title: 'Limit', dataIndex: 'limit', key: 'limit' },
                { title: 'Used', dataIndex: 'used', key: 'used' },
                { title: 'Percentage', dataIndex: 'percentage', key: 'percentage', render: (v: number) => <Progress percent={v} /> },
              ]
              dataSource={[
                { resource: 'API Calls', limit: 100000, used: 45230, percentage: 45 },
                { resource: 'AI Tokens', limit: 5000000, used: 2100000, percentage: 42 },
                { resource: 'Storage (GB)', limit: 100, used: 23.5, percentage: 23.5 },
                { resource: 'Workflow Runs', limit: 1000, used: 342, percentage: 34.2 },
                { resource: 'Agent Executions', limit: 5000, used: 1250, percentage: 25 },
              ]}
              pagination={false}
            />
          </Card>
        </Tabs.TabPane>
        <Tabs.TabPane tab="Invoices" key="invoices">
          <Card>
            <Table
              columns={[
                { title: 'Date', dataIndex: 'date', key: 'date', render: (v: string) => format(new Date(v), 'PP') },
                { title: 'Invoice', dataIndex: 'invoice_number', key: 'invoice_number' },
                { title: 'Amount', dataIndex: 'amount', key: 'amount', render: (v: number) => `$${v.toFixed(2)}` },
                { title: 'Status', dataIndex: 'status', key: 'status', render: (v: string) => <Tag color={v === 'paid' ? 'green' : v === 'pending' ? 'orange' : 'red'}>{v}</Tag> },
                { title: 'Actions', key: 'actions', render: (_, record: any) => <Space><Button type="link" size="small" onClick={() => window.open(record.pdf_url)}><DownloadOutlined /></Button><Button type="link" size="small"><EyeOutlined /></Button></Space> },
              ]
              dataSource={[]}
              pagination={false}
            />
          </Card>
        </Tabs.TabPane>
      </Tabs>
    </Card>
  );

  const renderAdvancedTab = () => (
    <Card>
      <Tabs defaultActiveKey="performance">
        <Tabs.TabPane tab="Performance" key="performance">
          <Card>
            <Form layout="vertical" onFinish={(values) => saveSettings('advanced', values)}>
              <Typography.Title level={4}>Rate Limiting</Typography.Title>
              <Form.Item name="rate_limit_enabled" label="Enable Rate Limiting" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="rate_limit_requests" label="Requests per Window">
                <InputNumber min={1} max={10000} />
              </Form.Item>
              <Form.Item name="rate_limit_window" label="Window (seconds)">
                <InputNumber min={1} max={3600} />
              </Form.Item>
              <Divider />
              <Typography.Title level={4}>Caching</Typography.Title>
              <Form.Item name="cache_enabled" label="Enable Caching" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="cache_ttl" label="Default TTL (seconds)">
                <InputNumber min={60} max={86400} />
              </Form.Item>
              <Divider />
              <Typography.Title level={4}>Feature Flags</Typography.Title>
              <Form.Item name="feature_flags_enabled" label="Enable Feature Flags" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="experiments_enabled" label="Enable Experiments" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Divider />
              <Typography.Title level={4}>Webhooks</Typography.Title>
              <Form.Item name="webhook_timeout" label="Webhook Timeout (seconds)">
                <InputNumber min={5} max={300} />
              </Form.Item>
              <Form.Item name="webhook_retries" label="Webhook Retries">
                <InputNumber min={0} max={10} />
              </Form.Item>
              <Form.Item name="webhook_retry_delay" label="Retry Delay (seconds)">
                <InputNumber min={1} max={300} />
              </Form.Item>
              <Divider />
              <Button type="primary" htmlType="submit" loading={saving}>
                <SaveOutlined /> Save Advanced Settings
              </Button>
            </Form>
          </Card>
        </Tabs.TabPane>
        <Tabs.TabPane tab="Logging" key="logging">
          <Card>
            <Form layout="vertical" onFinish={(values) => saveSettings('advanced', values)}>
              <Form.Item name="log_level" label="Log Level">
                <Select placeholder="Select log level" style={{ width: '100%' }}>
                  <Option value="debug">Debug</Option>
                  <Option value="info">Info</Option>
                  <Option value="warn">Warn</Option>
                  <Option value="error">Error</Option>
                </Select>
              </Form.Item>
              <Form.Item name="log_format" label="Log Format">
                <Select placeholder="Select format" style={{ width: '100%' }}>
                  <Option value="json">JSON</Option>
                  <Option value="text">Text</Option>
                </Select>
              </Form.Item>
              <Form.Item name="log_retention_days" label="Log Retention (days)">
                <InputNumber min={1} max={365} />
              </Form.Item>
              <Form.Item name="audit_log_enabled" label="Enable Audit Logging" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Divider />
              <Button type="primary" htmlType="submit" loading={saving}>
                <SaveOutlined /> Save Logging Settings
              </Button>
            </Form>
          </Card>
        </Tabs.TabPane>
      </Tabs>
    </Card>
  );

  return (
    <div className="settings-page">
      <div className="page-header">
        <div>
          <h1>Settings</h1>
          <p>Configure your SuperDev AI Suite instance</p>
        </div>
      </div>

      <Tabs defaultActiveKey="general" onChange={setActiveTab} style={{ marginBottom: 24 }}>
        {tabs.map(t => (
          <Tabs.TabPane tab={<Space><t.icon /> {t.title}</Space>} key={t.key} />
        ))}
      </Tabs>

      {activeTab === 'general' && renderGeneralTab()}
      {activeTab === 'auth' && renderAuthTab()}
      {activeTab === 'security' && renderSecurityTab()}
      {activeTab === 'integrations' && renderIntegrationsTab()}
      {activeTab === 'notifications' && renderNotificationsTab()}
      {activeTab === 'api' && renderApiKeysTab()}
      {activeTab === 'billing' && renderBillingTab()}
      {activeTab === 'advanced' && renderAdvancedTab()}
    </div>
  );
}

export default Settings;