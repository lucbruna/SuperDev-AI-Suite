import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Tag, Modal, Form, Input, Select, Space, Switch, Tooltip, Dropdown, Menu, Avatar, Badge, Segmented, Progress, Statistic, List, Spin, Collapse, Descriptions, Typography, Alert, Empty, Row, Col, Popconfirm, Message } from 'antd';
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

interface Agent {
  id: string;
  name: string;
  type: string;
  description: string;
  config: any;
  system_prompt: string;
  model_provider: string;
  model_name: string;
  tools: string[];
  is_active: boolean;
  project_id: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

interface AgentExecution {
  id: string;
  agent_id: string;
  task: string;
  context: any;
  status: string;
  result: any;
  error: string;
  tokens_used: number;
  cost_usd: number;
  started_at: string;
  completed_at: string;
  created_at: string;
}

export function Agents() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingAgent, setEditingAgent] = useState<Agent | null>(null);
  const [searchText, setSearchText] = useState('');
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [executions, setExecutions] = useState<AgentExecution[]>([]);
  const [executionsLoading, setExecutionsLoading] = useState(false);
  const [executionsModalVisible, setExecutionsModalVisible] = useState(false);
  const [selectedExecution, setSelectedExecution] = useState<AgentExecution | null>(null);
  const [executionLogs, setExecutionLogs] = useState<string[]>([]);
  const [logsModalVisible, setLogsModalVisible] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
  const [activeTab, setActiveTab] = useState('agents');

  const fetchAgents = async () => {
    setLoading(true);
    try {
      const response = await api.get('/agents', { params: { search: searchText } });
      setAgents(response.data);
    } catch (error) {
      console.error('Failed to fetch agents:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchExecutions = async (agentId: string) => {
    setExecutionsLoading(true);
    try {
      const response = await api.get(`/agents/${agentId}/executions`);
      setExecutions(response.data);
      setExecutionsModalVisible(true);
    } catch (error) {
      console.error('Failed to fetch executions:', error);
    } finally {
      setExecutionsLoading(false);
    }
  };

  const fetchExecutionLogs = async (executionId: string) => {
    try {
      const response = await api.get(`/agent-executions/${executionId}/logs`);
      setExecutionLogs(response.data.logs || []);
      setLogsModalVisible(true);
    } catch (error) {
      console.error('Failed to fetch execution logs:', error);
    }
  };

  const handleCreateAgent = async (values: any) => {
    try {
      await api.post('/agents', values);
      fetchAgents();
      Modal.close();
    } catch (error) {
      console.error('Failed to create agent:', error);
    }
  };

  const handleUpdateAgent = async (values: any) => {
    try {
      await api.put(`/agents/${editingAgent?.id}`, values);
      fetchAgents();
      Modal.close();
    } catch (error) {
      console.error('Failed to update agent:', error);
    }
  };

  const handleDeleteAgent = async (id: string) => {
    try {
      await api.delete(`/agents/${id}`);
      fetchAgents();
    } catch (error) {
      console.error('Failed to delete agent:', error);
    }
  };

  const handleExecuteAgent = async (agent: Agent, task?: string) => {
    try {
      const response = await api.post(`/agents/${agent.id}/execute`, { task: task || 'Execute default task' });
      fetchAgents();
      Message.success('Agent execution started');
    } catch (error) {
      console.error('Failed to execute agent:', error);
    }
  };

  const handleCancelExecution = async (executionId: string) => {
    try {
      await api.post(`/agent-executions/${executionId}/cancel`);
      if (selectedAgent) fetchExecutions(selectedAgent.id);
    } catch (error) {
      console.error('Failed to cancel execution:', error);
    }
  };

  const handleRetryExecution = async (executionId: string) => {
    try {
      await api.post(`/agent-executions/${executionId}/retry`);
      if (selectedAgent) fetchExecutions(selectedAgent.id);
    } catch (error) {
      console.error('Failed to retry execution:', error);
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
      render: (name: string, record: Agent) => (
        <div>
          <div style={{ fontWeight: 500 }}>{name}</div>
          <div style={{ color: '#999', fontSize: 12 }}>
            {record.type} • {record.model_provider}/{record.model_name}
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
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      align: 'center',
      render: (v: string) => (
        <Tag color={v === 'planner' ? 'blue' : v === 'executor' ? 'green' : v === 'reviewer' ? 'purple' : v === 'tester' ? 'orange' : v === 'architect' ? 'cyan' : v === 'researcher' ? 'gold' : 'default'}>
          {v}
        </Tag>
      ),
    },
    {
      title: 'Model',
      dataIndex: 'model_name',
      key: 'model_name',
      width: 150,
      render: (model: string, record: Agent) => (
        <div>
          <div style={{ fontWeight: 500 }}>{model}</div>
          <div style={{ color: '#999', fontSize: 12 }}>{record.model_provider}</div>
        </div>
      ),
    },
    {
      title: 'Tools',
      dataIndex: 'tools',
      key: 'tools',
      width: 150,
      render: (tools: string[]) => (
        <Space wrap>
          {tools.map((tool: string) => (
            <Tag key={tool} color="blue">{tool}</Tag>
          ))}
        </Space>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      align: 'center',
      render: (active: boolean) => (
        <Switch checked={active} disabled />
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
      render: (_: any, record: Agent) => (
        <Space>
          <Tooltip title="View Executions">
            <Button type="link" onClick={() => {
              setSelectedAgent(record);
              fetchExecutions(record.id);
            }}>
              <EyeOutlined />
            </Button>
          </Tooltip>
          <Tooltip title="Execute">
            <Button type="link" onClick={() => handleExecuteAgent(record)}>
              <PlayOutlined />
            </Button>
          </Tooltip>
          <Tooltip title="Edit">
            <Button type="link" onClick={() => {
              setEditingAgent(record);
              setModalVisible(true);
            }}>
              <EditOutlined />
            </Button>
          </Tooltip>
          <Tooltip title="Toggle Active">
            <Button type="link" onClick={() => handleToggleActive(record)} danger={record.is_active}>
              <Switch checked={record.is_active} size="small" />
            </Button>
          </Tooltip>
          <Dropdown
            menu={{
              items: [
                { label: 'Duplicate', key: 'duplicate', icon: <CopyOutlined />, onClick: () => {
                  const copy = { ...record, name: `${record.name} (copy)`, created_at: new Date().toISOString() };
                  setEditingAgent(copy);
                  setModalVisible(true);
                }},
                { label: 'Export', key: 'export', icon: <DownloadOutlined /> },
                { type: 'divider' },
                { label: 'Delete', key: 'delete', icon: <DeleteOutlined />, danger: true, onClick: () => Modal.confirm({
                  title: 'Delete Agent',
                  content: `Are you sure you want to delete "${record.name}"? This action cannot be undone.`,
                  onOk: () => handleDeleteAgent(record.id),
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
    fetchAgents();
  }, []);

  return (
    <div className="agents-page">
      <div className="page-header">
        <div>
          <h1>Agents</h1>
          <p>Create, manage, and execute AI agents</p>
        </div>
        <Button type="primary" onClick={() => { setEditingAgent(null); setModalVisible(true); }}>
          <PlusOutlined /> Create Agent
        </Button>
      </div>

      <Tabs activeKey={activeTab} onChange={setActiveTab} style={{ marginBottom: 24 }}>
        <Tabs.TabPane tab="Agents" key="agents" />
        <Tabs.TabPane tab="Executions" key="executions" />
      </Tabs>

      <Card>
        <Form layout="inline" onFinish={() => fetchAgents()} style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col md={8}>
              <Form.Item name="search" label="Search">
                <Input.Search
                  placeholder="Search agents..."
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  onPressEnter={() => fetchAgents()}
                  style={{ width: '100%' }}
                  allowClear
                />
              </Form.Item>
            </Col>
          </Row>
        </Form>
        
        <Table
          columns={columns}
          dataSource={agents}
          loading={loading}
          rowKey="id"
          pagination={{ pageSize: 10, showTotal: (total) => `Total ${total} agents` }}
          onChange={(pagination) => setPagination(pagination)}
        />

        {/* Create/Edit Agent Modal */}
        <Modal
          title={editingAgent ? 'Edit Agent' : 'Create Agent'}
          visible={modalVisible}
          onCancel={() => { setModalVisible(false); setEditingAgent(null); }}
          onOk={() => form.validateFields().then(editingAgent ? handleUpdateAgent : handleCreateAgent).catch(() => {})}
          destroyOnClose
        >
          <Form layout="vertical">
            <Form.Item name="name" label="Name" rules={[{ required: true, message: 'Please input agent name' }]}>
              <Input placeholder="Enter agent name" />
            </Form.Item>
            <Form.Item name="type" label="Type" rules={[{ required: true, message: 'Please select agent type' }]}>
              <Select placeholder="Select agent type" style={{ width: '100%' }}>
                <Option value="planner">Planner</Option>
                <Option value="executor">Executor</Option>
                <Option value="reviewer">Reviewer</Option>
                <Option value="tester">Tester</Option>
                <Option value="architect">Architect</Option>
                <Option value="researcher">Researcher</Option>
                <Option value="security">Security</Option>
                <Option value="deployment">Deployment</Option>
              </Select>
            </Form.Item>
            <Form.Item name="description" label="Description">
              <Input.TextArea placeholder="Enter description" rows={3} />
            </Form.Item>
            <Form.Item name="system_prompt" label="System Prompt" rules={[{ required: true, message: 'Please input system prompt' }]}>
              <Input.TextArea placeholder="Enter system prompt" rows={5} />
            </Form.Item>
            <Form.Item name="model_provider" label="Model Provider" rules={[{ required: true, message: 'Please select model provider' }]}>
              <Select placeholder="Select model provider" style={{ width: '100%' }}>
                <Option value="openai">OpenAI</Option>
                <Option value="anthropic">Anthropic</Option>
                <Option value="gemini">Google Gemini</Option>
                <Option value="ollama">Ollama (Local)</Option>
                <Option value="openrouter">OpenRouter</Option>
              </Select>
            </Form.Item>
            <Form.Item name="model_name" label="Model Name" rules={[{ required: true, message: 'Please input model name' }]}>
              <Input placeholder="e.g., gpt-4o, claude-3-5-sonnet-20241022" />
            </Form.Item>
            <Form.Item name="tools" label="Tools">
              <Input placeholder="Comma-separated tools (e.g., search,code_exec,file_ops)" />
            </Form.Item>
            <Form.Item name="is_active" label="Active" valuePropName="checked">
              <Switch />
            </Form.Item>
          </Form>
        </Modal>

        {/* Executions Modal */}
        <Modal
          title={`Executions for ${selectedAgent?.name}`}
          visible={executionsModalVisible}
          onCancel={() => setExecutionsModalVisible(false)}
          width={1000}
          footer={null}
        >
          <Table
            dataSource={executions}
            columns={[
              { title: 'Task', dataIndex: 'task', key: 'task', ellipsis: true },
              { title: 'Status', dataIndex: 'status', key: 'status', width: 100, align: 'center', render: (v: string) => <Tag color={getStatusColor(v)}>{getStatusIcon(v)} {v}</Tag> },
              { title: 'Tokens', dataIndex: 'tokens_used', key: 'tokens_used', width: 100, align: 'center', render: (v: number) => v ? v.toLocaleString() : '—' },
              { title: 'Cost', dataIndex: 'cost_usd', key: 'cost_usd', width: 100, align: 'center', render: (v: number) => v ? `$${v.toFixed(4)}` : '—' },
              { title: 'Started', dataIndex: 'started_at', key: 'started_at', width: 150, render: (d: string) => format(new Date(d), 'PPp') },
              { title: 'Completed', dataIndex: 'completed_at', key: 'completed_at', width: 150, render: (d: string) => d ? format(new Date(d), 'PPp') : '—' },
              { title: 'Actions', key: 'actions', render: (_: any, record: AgentExecution) => <Space>
                <Tooltip title="View Logs"><Button type="link" size="small" onClick={() => { setSelectedExecution(record); fetchExecutionLogs(record.id); }}><FileTextOutlined /></Button></Tooltip>
                {record.status === 'running' && <Tooltip title="Cancel"><Button type="link" size="small" danger onClick={() => handleCancelExecution(record.id)}><StopOutlined /></Button></Tooltip>}
                {record.status === 'failed' && <Tooltip title="Retry"><Button type="link" size="small" onClick={() => handleRetryExecution(record.id)}><ReloadOutlined /></Button></Tooltip>}
              </Space> },
            ]
            dataSource={executions}
            loading={executionsLoading}
            pagination={false}
          />
        </Modal>

        {/* Logs Modal */}
        <Modal
          title={`Logs for ${selectedExecution?.id?.substring(0, 8)}`}
          visible={logsModalVisible}
          onCancel={() => setLogsModalVisible(false)}
          width={900}
          footer={null}
        >
          <div style={{ height: 500, overflow: 'auto', fontFamily: 'monospace', fontSize: 12, background: '#1e1e1e', color: '#d4d4d4', padding: 16, borderRadius: 4 }}>
            {executionLogs.map((log: string, i: number) => (
              <div key={i} style={{ borderBottom: '1px solid #333', padding: '4px 0' }}>
                {log}
              </div>
            ))}
          </div>
        </Modal>
      </Card>
    </div>
  );
}

export default Agents;