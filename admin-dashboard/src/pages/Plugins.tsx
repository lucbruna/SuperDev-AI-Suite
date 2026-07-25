import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Tag, Modal, Form, Input, Select, Space, Switch, Tooltip, Dropdown, Menu, Avatar, Badge, Row, Col, Divider, List, Empty, Progress, Statistic, Tabs, Typography, Descriptions, Popconfirm } from 'antd';
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
  TeamOutlined, ProjectOutlined, GitBranchOutlined, ThunderboltOutlined,
  GlobalOutlined, AuditOutlined, ScheduleOutlined, SyncOutlined
} from '@ant-design/icons';
import { api } from '../services/api';
import { format } from 'date-fns';

interface Plugin {
  name: string;
  slug: string;
  version: string;
  description: string;
  author: string;
  plugin_type: string;
  tags: string[];
  downloads: number;
  rating: number;
  is_official: boolean;
  is_installed: boolean;
  status: string;
}

interface InstalledPlugin {
  name: string;
  slug: string;
  version: string;
  status: string;
  config: any;
}

export function Plugins() {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [installedPlugins, setInstalledPlugins] = useState<InstalledPlugin[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingPlugin, setEditingPlugin] = useState<Plugin | null>(null);
  const [searchText, setSearchText] = useState('');
  const [selectedPlugin, setSelectedPlugin] = useState<Plugin | null>(null);
  const [pluginConfig, setPluginConfig] = useState<any>({});
  const [configModalVisible, setConfigModalVisible] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });

  const fetchPlugins = async () => {
    setLoading(true);
    try {
      const response = await api.get('/plugins/registry', { params: { search: searchText } });
      setPlugins(response.data);
    } catch (error) {
      console.error('Failed to fetch plugins:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchInstalledPlugins = async () => {
    try {
      const response = await api.get('/plugins/installed');
      setInstalledPlugins(response.data);
    } catch (error) {
      console.error('Failed to fetch installed plugins:', error);
    }
  };

  const installPlugin = async (slug: string) => {
    try {
      await api.post('/plugins/install', { slug });
      fetchPlugins();
      fetchInstalledPlugins();
      message.success('Plugin installed successfully');
    } catch (error) {
      console.error('Failed to install plugin:', error);
    }
  };

  const uninstallPlugin = async (slug: string) => {
    try {
      await api.delete(`/plugins/${slug}`);
      fetchInstalledPlugins();
      fetchPlugins();
      message.success('Plugin uninstalled successfully');
    } catch (error) {
      console.error('Failed to uninstall plugin:', error);
    }
  };

  const enablePlugin = async (slug: string) => {
    try {
      await api.post(`/plugins/${slug}/enable`);
      fetchInstalledPlugins();
    } catch (error) {
      console.error('Failed to enable plugin:', error);
    }
  };

  const disablePlugin = async (slug: string) => {
    try {
      await api.post(`/plugins/${slug}/disable`);
      fetchInstalledPlugins();
    } catch (error) {
      console.error('Failed to disable plugin:', error);
    }
  };

  const handleConfigPlugin = async (plugin: InstalledPlugin) => {
    setSelectedPlugin({ ...plugin } as any);
    setPluginConfig(plugin.config || {});
    setConfigModalVisible(true);
  };

  const handleConfigSubmit = async (values: any) => {
    try {
      await api.put(`/plugins/${selectedPlugin?.slug}/config`, values);
      fetchInstalledPlugins();
      Modal.close();
      message.success('Configuration saved');
    } catch (error) {
      console.error('Failed to save config:', error);
    }
  };

  const searchPlugins = async (query: string) => {
    setSearchText(query);
    setLoading(true);
    try {
      const response = await api.get('/plugins/registry', { params: { search: query } });
      setPlugins(response.data);
    } catch (error) {
      console.error('Failed to search plugins:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlugins();
    fetchInstalledPlugins();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'enabled': return 'green';
      case 'disabled': return 'red';
      case 'error': return 'orange';
      default: return 'default';
    }
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      render: (name: string, record: Plugin) => (
        <div>
          <div style={{ fontWeight: 500 }}>{name}</div>
          <div style={{ color: '#999', fontSize: 12 }}>{record.slug}</div>
        </div>
      ),
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      width: 200,
    },
    {
      title: 'Type',
      dataIndex: 'plugin_type',
      key: 'plugin_type',
      width: 100,
      align: 'center',
      render: (v: string) => <Tag color={v === 'provider' ? 'blue' : v === 'tool' ? 'green' : v === 'agent' ? 'purple' : 'default'}>{v}</Tag>,
    },
    {
      title: 'Version',
      dataIndex: 'version',
      key: 'version',
      width: 100,
      align: 'center',
    },
    {
      title: 'Author',
      dataIndex: 'author',
      key: 'author',
      width: 120,
    },
    {
      title: 'Downloads',
      dataIndex: 'downloads',
      key: 'downloads',
      width: 80,
      align: 'center',
    },
    {
      title: 'Rating',
      dataIndex: 'rating',
      key: 'rating',
      width: 80,
      align: 'center',
      render: (v: number) => <span>{v}/5</span>,
    },
    {
      title: 'Official',
      dataIndex: 'is_official',
      key: 'is_official',
      width: 80,
      align: 'center',
      render: (v: boolean) => v ? <Tag color="gold">Official</Tag> : <Tag>Community</Tag>,
    },
    {
      title: 'Installed',
      dataIndex: 'is_installed',
      key: 'is_installed',
      width: 80,
      align: 'center',
      render: (v: boolean) => v ? <CheckCircleOutlined style={{ color: '#52c41a' }} /> : <CloseCircleOutlined style={{ color: '#ff4d4f' }} />,
    },
    {
      title: 'Status',
      key: 'status',
      width: 100,
      align: 'center',
      render: (_, record: Plugin) => {
        const installed = installedPlugins.find(p => p.slug === record.slug);
        if (!installed) return <Tag color="default">Not Installed</Tag>;
        return <Tag color={getStatusColor(installed.status)}>{installed.status}</Tag>;
      },
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 200,
      fixed: 'right',
      render: (_, record: Plugin) => {
        const installed = installedPlugins.find(p => p.slug === record.slug);
        if (!installed) {
          return (
            <Button type="primary" size="small" onClick={() => installPlugin(record.slug)} loading={loading}>
              <DownloadOutlined /> Install
            </Button>
          );
        }
        return (
          <Space>
            <Tooltip title={installed.status === 'enabled' ? 'Disable' : 'Enable'}>
              <Button type="link" size="small" onClick={() => installed.status === 'enabled' ? disablePlugin(record.slug) : enablePlugin(record.slug)}>
                {installed.status === 'enabled' ? <StopOutlined /> : <PlayOutlined />}
              </Button>
            </Tooltip>
            <Tooltip title="Configure">
              <Button type="link" size="small" onClick={() => {
                const plugin = installedPlugins.find(p => p.slug === record.slug);
                if (plugin) {
                  setSelectedPlugin({ ...record, ...installed } as any);
                  setPluginConfig(installed.config || {});
                  setConfigModalVisible(true);
                }
              }}>
                <SettingOutlined />
              </Button>
            </Tooltip>
            <Popconfirm title="Uninstall Plugin" content={`Are you sure you want to uninstall ${record.name}?`} onConfirm={() => uninstallPlugin(record.slug)} okText="Yes" cancelText="No">
              <Button type="link" size="small" danger><DeleteOutlined /></Button>
            </Popconfirm>
          </Space>
        );
      },
    },
  ];

  useEffect(() => {
    fetchPlugins();
    fetchInstalledPlugins();
  }, []);

  return (
    <div className="plugins-page">
      <div className="page-header">
        <div>
          <h1>Plugin Marketplace</h1>
          <p>Browse, install, and manage plugins for your projects</p>
        </div>
        <Button type="primary" onClick={() => setConfigModalVisible(true)}>
          <PlusOutlined /> Configure Installed Plugin
        </Button>
      </div>

      <Tabs defaultActiveKey="marketplace">
        <Tabs.TabPane tab="Marketplace" key="marketplace">
          <Card>
            <Form layout="inline" onFinish={() => searchPlugins(searchText)} style={{ marginBottom: 16 }}>
              <Row gutter={16}>
                <Col md={8}>
                  <Form.Item name="search" label="Search">
                    <Input.Search
                      placeholder="Search plugins..."
                      value={searchText}
                      onChange={(e) => setSearchText(e.target.value)}
                      onPressEnter={() => searchPlugins(searchText)}
                      style={{ width: '100%' }}
                      allowClear
                    />
                  </Form.Item>
                </Col>
                <Col md={4}>
                  <Form.Item name="type" label="Type">
                    <Select placeholder="Filter by type" style={{ width: '100%' }}>
                      <Option value="provider">Provider</Option>
                      <Option value="tool">Tool</Option>
                      <Option value="agent">Agent</Option>
                      <Option value="integration">Integration</Option>
                      <Option value="ui">UI</Option>
                      <Option value="command">Command</Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>
            </Form>
            
            <Table
              columns={columns}
              dataSource={plugins}
              loading={loading}
              rowKey="slug"
              pagination={{ pageSize: 10, showTotal: (total) => `Total ${total} plugins` }}
              onChange={(pagination) => setPagination(pagination)}
            />

            {/* Config Modal */}
            <Modal
              title={`Configure ${selectedPlugin?.name}`}
              visible={configModalVisible}
              onCancel={() => setConfigModalVisible(false)}
              onOk={() => form.validateFields().then(handleConfigSubmit).catch(() => {})}
              destroyOnClose
            >
              <Form layout="vertical">
                {Object.entries(selectedPlugin?.config_schema?.properties || {}).map(([key, schema: any]) => (
                  <Form.Item key={key} name={key} label={schema.title || key} rules={schema.required ? [{ required: true }] : []}>
                    {schema.type === 'string' && schema.enum ? (
                      <Select placeholder={`Select ${schema.title || key}`} style={{ width: '100%' }}>
                        {schema.enum.map((opt: string) => <Option key={opt} value={opt}>{opt}</Option>)}
                      </Select>
                    ) : schema.type === 'boolean' ? (
                      <Switch />
                    ) : schema.type === 'number' ? (
                      <InputNumber placeholder={`Enter ${schema.title || key}`} />
                    ) : (
                      <Input placeholder={`Enter ${schema.title || key}`} />
                    )}
                  </Form.Item>
                ))}
              <Form.Item>
                <Button type="primary" htmlType="submit" loading={configModalVisible}>
                  Save Configuration
                </Button>
              </Form.Item>
            </Form>
            </Modal>
          </Card>
        </Tabs.TabPane>
        <Tabs.TabPane tab="Installed Plugins" key="installed">
          <Card>
            <Table
              dataSource={installedPlugins}
              columns={[
                { title: 'Name', dataIndex: 'name', key: 'name' },
                { title: 'Version', dataIndex: 'version', key: 'version' },
                { title: 'Status', dataIndex: 'status', key: 'status', render: (v: string) => <Tag color={getStatusColor(v)}>{v}</Tag> },
                { title: 'Actions', key: 'actions', render: (_, record: InstalledPlugin) => (
                  <Space>
                    <Tooltip title={record.status === 'enabled' ? 'Disable' : 'Enable'}>
                      <Button type="link" size="small" onClick={() => record.status === 'enabled' ? disablePlugin(record.slug) : enablePlugin(record.slug)}>
                        {record.status === 'enabled' ? <StopOutlined /> : <PlayOutlined />}
                      </Button>
                    </Tooltip>
                    <Tooltip title="Configure">
                      <Button type="link" size="small" onClick={() => {
                        const plugin = installedPlugins.find(p => p.slug === record.slug);
                        if (plugin) {
                          setSelectedPlugin({ ...record, ...plugin } as any);
                          setPluginConfig(plugin.config || {});
                          setConfigModalVisible(true);
                        }
                      }}>
                        <SettingOutlined />
                      </Button>
                    </Tooltip>
                    <Popconfirm title="Uninstall Plugin" content={`Are you sure you want to uninstall ${record.name}?`} onConfirm={() => uninstallPlugin(record.slug)} okText="Yes" cancelText="No">
                      <Button type="link" size="small" danger><DeleteOutlined /></Button>
                    </Popconfirm>
                  </Space>
                )} }
              ]
              dataSource={installedPlugins}
              loading={loading}
              pagination={false}
            />
          </Card>
        </Tabs.TabPane>
      </Tabs>
    </div>
  );
}

export default Plugins;