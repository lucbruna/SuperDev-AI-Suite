import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Tag, Modal, Form, Input, Select, Space, Switch, Tooltip, Divider, Row, Col, Badge, Dropdown, Menu, Avatar, Tabs, Segmented, Progress, Statistic, List, Spin, Collapse, Descriptions, Typography, Alert, Empty } from 'antd';
import { 
  PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined, 
  MoreOutlined, SearchOutlined, FilterOutlined, DownloadOutlined,
  PlayOutlined, StopOutlined, PauseOutlined, ReloadOutlined,
  CopyOutlined, CodeOutlined, TerminalOutlined, RobotOutlined,
  CheckCircleOutlined, CloseCircleOutlined, ExclamationCircleOutlined,
  ClockCircleOutlined, FileTextOutlined, ArrowUpOutlined, ArrowDownOutlined,
  EnvironmentOutlined, DatabaseOutlined, UserOutlined, SettingOutlined,
  WarningOutlined, InfoCircleOutlined, SafetyOutlined, ExperimentOutlined,
  HistoryOutlined, LogoutOutlined, LinkOutlined, ShareAltOutlined
} from '@ant-design/icons';
import { api } from '../services/api';
import { format } from 'date-fns';

interface Workflow {
  id: string;
  name: string;
  description: string;
  definition: any;
  version: number;
  tags: string[];
  is_template: boolean;
  project_id: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

interface WorkflowRun {
  id: string;
  workflow_id: string;
  status: string;
  variables: any;
  result: any;
  error: string;
  started_at: string;
  completed_at: string;
  created_at: string;
}

export function Workflows() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingWorkflow, setEditingWorkflow] = useState<Workflow | null>(null);
  const [searchText, setSearchText] = useState('');
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [runs, setRuns] = useState<WorkflowRun[]>([]);
  const [runsLoading, setRunsLoading] = useState(false);
  const [runsModalVisible, setRunsModalVisible] = useState(false);
  const [selectedRun, setSelectedRun] = useState<WorkflowRun | null>(null);
  const [runLogs, setRunLogs] = useState<string[]>([]);
  const [logsModalVisible, setLogsModalVisible] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
  const [activeTab, setActiveTab] = useState('workflows');

  const fetchWorkflows = async () => {
    setLoading(true);
    try {
      const response = await api.get('/workflows', { params: { search: searchText } });
      setWorkflows(response.data);
    } catch (error) {
      console.error('Failed to fetch workflows:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRuns = async (workflowId: string) => {
    setRunsLoading(true);
    try {
      const response = await api.get(`/workflows/${workflowId}/runs`);
      setRuns(response.data);
      setRunsModalVisible(true);
    } catch (error) {
      console.error('Failed to fetch runs:', error);
    } finally {
      setRunsLoading(false);
    }
  };

  const fetchRunLogs = async (runId: string) => {
    try {
      const response = await api.get(`/workflow-runs/${runId}/logs`);
      setRunLogs(response.data.logs || []);
      setLogsModalVisible(true);
    } catch (error) {
      console.error('Failed to fetch run logs:', error);
    }
  };

  const handleCreateWorkflow = async (values: any) => {
    try {
      await api.post('/workflows', values);
      fetchWorkflows();
      Modal.close();
    } catch (error) {
      console.error('Failed to create workflow:', error);
    }
  };

  const handleUpdateWorkflow = async (values: any) => {
    try {
      await api.put(`/workflows/${editingWorkflow?.id}`, values);
      fetchWorkflows();
      Modal.close();
    } catch (error) {
      console.error('Failed to update workflow:', error);
    }
  };

  const handleDeleteWorkflow = async (id: string) => {
    try {
      await api.delete(`/workflows/${id}`);
      fetchWorkflows();
    } catch (error) {
      console.error('Failed to delete workflow:', error);
    }
  };

  const handleExecuteWorkflow = async (workflow: Workflow, variables?: any) => {
    try {
      const response = await api.post(`/workflows/${workflow.id}/execute`, { variables });
      fetchWorkflows();
      Message.success('Workflow execution started');
    } catch (error) {
      console.error('Failed to execute workflow:', error);
    }
  };

  const handleCancelRun = async (runId: string) => {
    try {
      await api.post(`/workflow-runs/${runId}/cancel`);
      if (selectedWorkflow) fetchRuns(selectedWorkflow.id);
    } catch (error) {
      console.error('Failed to cancel run:', error);
    }
  };

  const handleRetryRun = async (runId: string) => {
    try {
      await api.post(`/workflow-runs/${runId}/retry`);
      if (selectedWorkflow) fetchRuns(selectedWorkflow.id);
    } catch (error) {
      console.error('Failed to retry run:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'blue';
      case 'completed': return 'green';
      case 'failed': return 'red';
      case 'cancelled': return 'orange';
      case 'pending': return 'grey';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <ClockCircleOutlined style={{ color: '#1890ff' }} />;
      case 'completed': return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'failed': return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
      case 'cancelled': return <StopOutlined style={{ color: '#faad14' }} />;
      case 'pending': return <ClockCircleOutlined style={{ color: '#d9d9d9' }} />;
      default: return <ClockCircleOutlined style={{ color: '#d9d9d9' }} />;
    }
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      render: (name: string, record: Workflow) => (
        <div>
          <div style={{ fontWeight: 500 }}>{name}</div>
          <div style={{ color: '#999', fontSize: 12 }}>
            v{record.version} • {record.is_template ? 'Template' : 'Workflow'}
          </div>
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
      title: 'Project',
      dataIndex: 'project_id',
      key: 'project_id',
      width: 150,
      render: (projectId: string) => (
        <Tag color="blue">{projectId.substring(0, 8)}...</Tag>
      ),
    },
    {
      title: 'Version',
      dataIndex: 'version',
      key: 'version',
      width: 80,
      align: 'center',
    },
    {
      title: 'Status',
      dataIndex: 'is_template',
      key: 'is_template',
      width: 100,
      align: 'center',
      render: (isTemplate: boolean) => isTemplate ? (
        <Tag color="purple">Template</Tag>
      ) : (
        <Tag color="green">Active</Tag>
      ),
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (date: string) => format(new Date(date), 'PP'),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 200,
      fixed: 'right',
      render: (_: any, record: Workflow) => (
        <Space>
          <Tooltip title="View Runs">
            <Button type="link" onClick={() => {
              setSelectedWorkflow(record);
              fetchRuns(record.id);
            }}>
              <EyeOutlined />
            </Button>
          </Tooltip>
          <Tooltip title="Execute">
            <Button type="link" onClick={() => handleExecuteWorkflow(record)} danger={!selectedWorkflow}>
              <PlayOutlined />
            </Button>
          </Tooltip>
          <Tooltip title="Edit">
            <Button type="link" onClick={() => {
              setEditingWorkflow(record);
              setModalVisible(true);
            }}>
              <EditOutlined />
            </Button>
          </Tooltip>
          <Tooltip title="Duplicate">
            <Button type="link" onClick={() => {
              const copy = { ...record, name: `${record.name} (copy)`, version: 1, created_at: new Date().toISOString() };
              setEditingWorkflow(copy);
              setModalVisible(true);
            }}>
              <CopyOutlined />
            </Button>
          </Tooltip>
          <Dropdown
            menu={{
              items: [
                { label: 'Export', key: 'export', icon: <DownloadOutlined /> },
                { label: 'View Definition', key: 'view_def', icon: <CodeOutlined /> },
                { type: 'divider' },
                { label: 'Delete', key: 'delete', icon: <DeleteOutlined />, danger: true, onClick: () => Modal.confirm({
                  title: 'Delete Workflow',
                  content: `Are you sure you want to delete "${record.name}"? This action cannot be undone.`,
                  onOk: () => handleDeleteWorkflow(record.id),
                })},
              ]}
          >
            <Button type="link"><MoreOutlined /></Button>
          </Dropdown>
        </Space>
      ),
    },
  ];

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const statusColors = {
    running: 'blue',
    completed: 'green',
    failed: 'red',
    cancelled: 'orange',
    pending: 'default',
  };

  return (
    <div className="workflows-page">
      <div className="page-header">
        <div>
          <h1>Workflows</h1>
          <p>Create, manage, and execute automated workflows</p>
        </div>
        <Button type="primary" onClick={() => { setEditingWorkflow(null); setModalVisible(true); }}>
          <PlusOutlined /> Create Workflow
        </Button>
      </div>

      <Tabs activeKey={activeTab} onChange={setActiveTab} style={{ marginBottom: 24 }}>
        <Tabs.TabPane tab="Workflows" key="workflows" />
        <Tabs.TabPane tab="Templates" key="templates" />
      </Tabs>

      <Card>
        <Form layout="inline" onFinish={() => fetchWorkflows()} style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col md={8}>
              <Form.Item name="search" label="Search">
                <Input.Search
                  placeholder="Search workflows..."
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  onPressEnter={() => fetchWorkflows()}
                  style={{ width: '100%' }}
                  allowClear
                />
              </Form.Item>
            </Col>
          </Row>
        </Form>
        
        <Table
          columns={columns}
          dataSource={workflows}
          loading={loading}
          rowKey="id"
          pagination={{ pageSize: 10, showTotal: (total) => `Total ${total} workflows` }}
          onChange={(pagination) => setPagination(pagination)}
        />

        {/* Create/Edit Workflow Modal */}
        <Modal
          title={editingWorkflow ? 'Edit Workflow' : 'Create Workflow'}
          visible={modalVisible}
          onCancel={() => { setModalVisible(false); setEditingWorkflow(null); }}
          onOk={() => form.validateFields().then(editingWorkflow ? handleUpdateWorkflow : handleCreateWorkflow).catch(() => {})}
          destroyOnClose
        >
          <Form layout="vertical">
            <Form.Item name="name" label="Name" rules={[{ required: true, message: 'Please input workflow name' }]}>
              <Input placeholder="Enter workflow name" />
            </Form.Item>
            <Form.Item name="slug" label="Slug" rules={[{ required: true, message: 'Please input slug' }]}>
              <Input placeholder="Enter slug (unique identifier)" />
            </Form.Item>
            <Form.Item name="description" label="Description">
              <Input.TextArea placeholder="Enter description" rows={3} />
            </Form.Item>
            <Form.Item name="project_id" label="Project" rules={[{ required: true, message: 'Please select a project' }]}>
              <Select placeholder="Select project" style={{ width: '100%' }}>
                <Option value="proj-1">Default Project</Option>
              </Select>
            </Form.Item>
            <Form.Item name="definition" label="Workflow Definition" rules={[{ required: true, message: 'Please provide workflow definition' }]}>
              <Input.TextArea placeholder="Workflow definition (JSON)" rows={10} />
            </Form.Item>
            <Form.Item name="is_template" label="Is Template" valuePropName="checked">
              <Switch />
            </Form.Item>
            <Form.Item name="tags" label="Tags">
              <Input placeholder="Comma-separated tags" />
            </Form.Item>
          </Form>
        </Modal>

        {/* Runs Modal */}
        <Modal
          title={`Runs for ${selectedWorkflow?.name}`}
          visible={runsModalVisible}
          onCancel={() => setRunsModalVisible(false)}
          width={1000}
          footer={null}
        >
          <Table
            dataSource={runs}
            columns={[
              { title: 'Run ID', dataIndex: 'id', key: 'id', width: 150, render: (v: string) => <span>{v.substring(0, 8)}...</span> },
              { title: 'Status', dataIndex: 'status', key: 'status', width: 100, align: 'center', render: (v: string) => <Tag color={getStatusColor(v)}>{getStatusIcon(v)} {v}</Tag> },
              { title: 'Started', dataIndex: 'started_at', key: 'started_at', width: 150, render: (d: string) => format(new Date(d), 'PPp') },
              { title: 'Completed', dataIndex: 'completed_at', key: 'completed_at', width: 150, render: (d: string) => d ? format(new Date(d), 'PPp') : '—' },
              { title: 'Duration', dataIndex: 'duration_ms', key: 'duration_ms', width: 100, align: 'center', render: (v: number) => v ? `${(v / 1000).toFixed(1)}s` : '—' },
              { title: 'Actions', key: 'actions', width: 150, render: (_: any, record: WorkflowRun) => <Space>
                <Tooltip title="View Logs"><Button type="link" size="small" onClick={() => { setSelectedRun(record); fetchRunLogs(record.id); }}><FileTextOutlined /></Button></Tooltip>
                {record.status === 'running' && <Tooltip title="Cancel"><Button type="link" size="small" danger onClick={() => handleCancelRun(record.id)}><StopOutlined /></Button></Tooltip>}
                {record.status === 'failed' && <Tooltip title="Retry"><Button type="link" size="small" onClick={() => handleRetryRun(record.id)}><ReloadOutlined /></Button></Tooltip>}
              </Space> },
            ]
            dataSource={runs}
            loading={runsLoading}
            pagination={false}
          />
        </Modal>

        {/* Logs Modal */}
        <Modal
          title={`Logs for ${selectedRun?.id?.substring(0, 8)}`}
          visible={logsModalVisible}
          onCancel={() => setLogsModalVisible(false)}
          width={900}
          footer={null}
        >
          <div style={{ height: 500, overflow: 'auto', fontFamily: 'monospace', fontSize: 12, background: '#1e1e1e', color: '#d4d4d4', padding: 16, borderRadius: 4 }}>
            {runLogs.map((log: string, i: number) => (
              <div key={i} style={{ borderBottom: '1px solid #333', padding: '4px 0' }}>
                {log}
              </div>
            ))}
          </div>
        </Modal>

        {/* Create/Edit Modal */}
        <Modal
          title={editingWorkflow ? 'Edit Workflow' : 'Create Workflow'}
          visible={modalVisible}
          onCancel={() => { setModalVisible(false); setEditingWorkflow(null); }}
          onOk={() => form.validateFields().then(editingWorkflow ? handleUpdateWorkflow : handleCreateWorkflow).catch(() => {})}
          destroyOnClose
        >
          <Form layout="vertical">
            <Form.Item name="name" label="Name" rules={[{ required: true, message: 'Please input workflow name' }]}>
              <Input placeholder="Enter workflow name" />
            </Form.Item>
            <Form.Item name="slug" label="Slug" rules={[{ required: true, message: 'Please input slug' }]}>
              <Input placeholder="Enter slug (unique identifier)" />
            </Form.Item>
            <Form.Item name="description" label="Description">
              <Input.TextArea placeholder="Enter description" rows={3} />
            </Form.Item>
            <Form.Item name="project_id" label="Project" rules={[{ required: true, message: 'Please select a project' }]}>
              <Select placeholder="Select project" style={{ width: '100%' }}>
                <Option value="proj-1">Default Project</Option>
              </Select>
            </Form.Item>
            <Form.Item name="definition" label="Workflow Definition (JSON)" rules={[{ required: true, message: 'Please provide workflow definition' }]}>
              <Input.TextArea placeholder="Workflow definition (JSON)" rows={10} />
            </Form.Item>
            <Form.Item name="is_template" label="Is Template" valuePropName="checked">
              <Switch />
            </Form.Item>
            <Form.Item name="tags" label="Tags">
              <Input placeholder="Comma-separated tags" />
            </Form.Item>
          </Form>
        </Modal>
      </Card>
    </div>
  );
}

export default Workflows;