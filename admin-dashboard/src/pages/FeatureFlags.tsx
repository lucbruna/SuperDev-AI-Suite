import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Tag, Modal, Form, Input, Select, Space, Switch, Tooltip, Dropdown, Menu, Avatar, Badge, Row, Col, Tabs, Typography, List, Empty, Progress, Statistic, Popconfirm } from 'antd';
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
  LockOutlined, UnlockOutlined, TrophyOutlined, ThunderboltOutlined,
  GlobalOutlined, AuditOutlined, ScheduleOutlined, SyncOutlined
} from '@ant-design/icons';
import { api } from '../services/api';
import { format } from 'date-fns';

interface FeatureFlag {
  name: string;
  description: string;
  enabled: boolean;
  type: string;
  tags: string[];
  strategies: any[];
  created_at: string;
  updated_at: string;
}

export function FeatureFlags() {
  const [flags, setFlags] = useState<FeatureFlag[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingFlag, setEditingFlag] = useState<FeatureFlag | null>(null);
  const [searchText, setSearchText] = useState('');
  const [selectedFlag, setSelectedFlag] = useState<FeatureFlag | null>(null);
  const [flagDetails, setFlagDetails] = useState<any>(null);
  const [detailsModalVisible, setDetailsModalVisible] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });

  const fetchFlags = async () => {
    setLoading(true);
    try {
      const response = await api.get('/feature-flags', { params: { search: searchText } });
      setFlags(response.data);
    } catch (error) {
      console.error('Failed to fetch feature flags:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchFlagDetails = async (name: string) => {
    try {
      const response = await api.get(`/feature-flags/${name}`);
      setFlagDetails(response.data);
      setDetailsModalVisible(true);
    } catch (error) {
      console.error('Failed to fetch flag details:', error);
    }
  };

  const handleCreateFlag = async (values: any) => {
    try {
      await api.post('/feature-flags', values);
      fetchFlags();
      Modal.close();
    } catch (error) {
      console.error('Failed to create feature flag:', error);
    }
  };

  const handleUpdateFlag = async (values: any) => {
    try {
      await api.put(`/feature-flags/${editingFlag?.name}`, values);
      fetchFlags();
      Modal.close();
    } catch (error) {
      console.error('Failed to update feature flag:', error);
    }
  };

  const handleDeleteFlag = async (name: string) => {
    try {
      await api.delete(`/feature-flags/${name}`);
      fetchFlags();
    } catch (error) {
      console.error('Failed to delete feature flag:', error);
    }
  };

  const handleToggleFlag = async (flag: FeatureFlag) => {
    try {
      await api.put(`/feature-flags/${flag.name}`, { enabled: !flag.enabled });
      fetchFlags();
    } catch (error) {
      console.error('Failed to toggle feature flag:', error);
    }
  };

  const handleEvaluateFlag = async (name: string) => {
    try {
      const response = await api.post(`/feature-flags/${name}/evaluate`, { context: { user_id: 'current_user' } });
      Message.success(`Flag evaluation: ${response.data.enabled ? 'enabled' : 'disabled'}`);
    } catch (error) {
      console.error('Failed to evaluate flag:', error);
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'release': return 'green';
      case 'experiment': return 'blue';
      case 'kill_switch': return 'red';
      case 'permission': return 'purple';
      case 'ops': return 'orange';
      default: return 'default';
    }
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      render: (name: string, record: FeatureFlag) => (
        <div>
          <div style={{ fontWeight: 500 }}>{name}</div>
          <div style={{ color: '#999', fontSize: 12 }}>{record.description}</div>
        </div>
      ),
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      align: 'center',
      render: (v: string) => <Tag color={getTypeColor(v)}>{v}</Tag>,
    },
    {
      title: 'Status',
      dataIndex: 'enabled',
      key: 'enabled',
      width: 100,
      align: 'center',
      render: (enabled: boolean) => (
        <Switch checked={enabled} onChange={() => handleToggleFlag({ ...flag, enabled: !enabled })} />
      ),
    },
    {
      title: 'Type Badge',
      dataIndex: 'type',
      key: 'type_badge',
      width: 100,
      render: (v: string) => <Tag color={getTypeColor(v)}>{v}</Tag>,
    },
    {
      title: 'Tags',
      dataIndex: 'tags',
      key: 'tags',
      width: 150,
      render: (v: string[]) => (
        <Space wrap>
          {v.map((tag: string) => (
            <Tag key={tag} color="blue">{tag}</Tag>
          ))}
        </Space>
      ),
    },
    {
      title: 'Strategies',
      dataIndex: 'strategies',
      key: 'strategies',
      width: 100,
      render: (v: any[]) => v?.length ? `${v.length} strategies` : 'None',
    },
    {
      title: 'Updated',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 150,
      render: (date: string) => format(new Date(date), 'PP'),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 200,
      fixed: 'right',
      render: (_: any, record: FeatureFlag) => (
        <Space>
          <Tooltip title="Evaluate">
            <Button type="link" size="small" onClick={() => handleEvaluateFlag(record.name)}>
              <ExperimentOutlined />
            </Button>
          </Tooltip>
          <Tooltip title="View Details">
            <Button type="link" size="small" onClick={() => {
              setSelectedFlag(record);
              fetchFlagDetails(record.name);
            }}>
              <EyeOutlined />
            </Button>
          </Tooltip>
          <Tooltip title="Edit">
            <Button type="link" size="small" onClick={() => {
              setEditingFlag(record);
              setModalVisible(true);
            }}>
              <EditOutlined />
            </Button>
          </Tooltip>
          <Tooltip title={record.enabled ? 'Disable' : 'Enable'}>
            <Switch checked={record.enabled} size="small" onChange={() => handleToggleFlag(record)} />
          </Tooltip>
          <Dropdown
            menu={{
              items: [
                { label: 'Clone', key: 'clone', icon: <CopyOutlined />, onClick: () => {
                  const copy = { ...record, name: `${record.name}-copy`, enabled: false };
                  setEditingFlag(copy);
                  setModalVisible(true);
                }},
                { label: 'Export', key: 'export', icon: <DownloadOutlined /> },
                { type: 'divider' },
                { label: 'Delete', key: 'delete', icon: <DeleteOutlined />, danger: true, onClick: () => Modal.confirm({
                  title: 'Delete Feature Flag',
                  content: `Are you sure you want to delete "${record.name}"? This action cannot be undone.`,
                  onOk: () => handleDeleteFlag(record.name),
                })},
              ]}
          >
            <Button type="link" size="small"><MoreOutlined /></Button>
          </Dropdown>
        </Space>
      ),
    },
  ];

  useEffect(() => {
    fetchFlags();
  }, []);

  const statusColors = {
    release: 'green',
    experiment: 'blue',
    kill_switch: 'red',
    permission: 'purple',
    ops: 'orange',
  };

  return (
    <div className="feature-flags-page">
      <div className="page-header">
        <div>
          <h1>Feature Flags</h1>
          <p>Manage feature flags, experiments, and rollout strategies</p>
        </div>
        <Button type="primary" onClick={() => { setEditingFlag(null); setModalVisible(true); }}>
          <PlusOutlined /> Create Feature Flag
        </Button>
      </div>

      <Tabs defaultActiveKey="flags">
        <Tabs.TabPane tab="Feature Flags" key="flags" />
        <Tabs.TabPane tab="Experiments" key="experiments" />
        <Tabs.TabPane tab="Kill Switches" key="kill_switches" />
        <Tabs.TabPane tab="Audit Log" key="audit" />
      </Tabs>

      <Card>
        <Form layout="inline" onFinish={() => fetchFlags()} style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col md={8}>
              <Form.Item name="search" label="Search">
                <Input.Search
                  placeholder="Search feature flags..."
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  onPressEnter={() => fetchFlags()}
                  style={{ width: '100%' }}
                  allowClear
                />
              </Form.Item>
            </Col>
            <Col md={4}>
              <Form.Item name="type" label="Type">
                <Select placeholder="Filter by type" style={{ width: '100%' }}>
                  <Option value="release">Release</Option>
                  <Option value="experiment">Experiment</Option>
                  <Option value="kill_switch">Kill Switch</Option>
                  <Option value="permission">Permission</Option>
                  <Option value="ops">Ops</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
        </Form>
        
        <Table
          columns={columns}
          dataSource={flags}
          loading={loading}
          rowKey="name"
          pagination={{ pageSize: 10, showTotal: (total) => `Total ${total} feature flags` }}
          onChange={(pagination) => setPagination(pagination)}
        />

        {/* Create/Edit Flag Modal */}
        <Modal
          title={editingFlag ? 'Edit Feature Flag' : 'Create Feature Flag'}
          visible={modalVisible}
          onCancel={() => { setModalVisible(false); setEditingFlag(null); }}
          onOk={() => form.validateFields().then(editingFlag ? handleUpdateFlag : handleCreateFlag).catch(() => {})}
          destroyOnClose
        >
          <Form layout="vertical">
            <Form.Item name="name" label="Name" rules={[{ required: true, message: 'Please input flag name' }]}>
              <Input placeholder="Enter flag name (e.g., new-feature-enabled)" />
            </Form.Item>
            <Form.Item name="description" label="Description">
              <Input.TextArea placeholder="Enter description" rows={3} />
            </Form.Item>
            <Form.Item name="type" label="Type" rules={[{ required: true, message: 'Please select type' }]}>
              <Select placeholder="Select type" style={{ width: '100%' }}>
                <Option value="release">Release</Option>
                <Option value="experiment">Experiment</Option>
                <Option value="kill_switch">Kill Switch</Option>
                <Option value="permission">Permission</Option>
                <Option value="ops">Ops</Option>
              </Select>
            </Form.Item>
            <Form.Item name="enabled" label="Enabled" valuePropName="checked">
              <Switch />
            </Form.Item>
            <Form.Item name="tags" label="Tags">
              <Input placeholder="Comma-separated tags" />
            </Form.Item>
            <Form.Item name="strategies" label="Rollout Strategies">
              <Input.TextArea placeholder="JSON array of rollout strategies" rows={5} />
            </Form.Item>
          </Form>
        </Modal>

        {/* Details Modal */}
        <Modal
          title={`Flag Details: ${selectedFlag?.name}`}
          visible={detailsModalVisible}
          onCancel={() => setDetailsModalVisible(false)}
          width={800}
          footer={null}
        >
          <div style={{ padding: 16 }}>
            <Descriptions title={selectedFlag?.name} column={2}>
              <Descriptions.Item label="Name">{selectedFlag?.name}</Descriptions.Item>
              <Descriptions.Item label="Description">{selectedFlag?.description}</Descriptions.Item>
              <Descriptions.Item label="Type"><Tag color={getTypeColor(selectedFlag?.type || '')}>{selectedFlag?.type}</Tag></Descriptions.Item>
              <Descriptions.Item label="Enabled"><Tag color={selectedFlag?.enabled ? 'green' : 'red'}>{selectedFlag?.enabled ? 'Enabled' : 'Disabled'}</Tag></Descriptions.Item>
              <Descriptions.Item label="Tags">{selectedFlag?.tags?.join(', ')}</Descriptions.Item>
              <Descriptions.Item label="Created">{format(new Date(selectedFlag?.created_at || ''), 'PPpp')}</Descriptions.Item>
              <Descriptions.Item label="Updated">{format(new Date(selectedFlag?.updated_at || ''), 'PPpp')}</Descriptions.Item>
              <Descriptions.Item label="Strategies" span={2}>
                <pre style={{ fontSize: 12, background: '#f5f5f5', padding: 12, borderRadius: 4 }}>
                  {JSON.stringify(selectedFlag?.strategies, null, 2)}
                </pre>
              </Descriptions.Item>
            </Descriptions>
          </div>
        </Modal>
      </Card>
    </div>
  );
}

export default FeatureFlags;