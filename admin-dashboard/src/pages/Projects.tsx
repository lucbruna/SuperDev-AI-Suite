import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Tag, Modal, Form, Input, Select, Space, Message, Divider, Row, Col, Badge, Switch, Tooltip } from 'antd';
import { 
  PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined, 
  MoreOutlined, SearchOutlined, FilterOutlined, DownloadOutlined,
  PlayOutlined, StopOutlined, PauseOutlined, ReloadOutlined,
  CopyOutlined, CodeOutlined, TerminalOutlined, RobotOutlined,
  CheckCircleOutlined, CloseCircleOutlined, ExclamationCircleOutlined
} from '@ant-design/icons';
import { api } from '../services/api';
import { format } from 'date-fns';

interface Project {
  id: string;
  name: string;
  slug: string;
  description?: string;
  visibility: string;
  organization_id: string;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

export function Projects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [searchText, setSearchText] = useState('');
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [workflows, setWorkflows] = useState([]);
  const [workflowsLoading, setWorkflowsLoading] = useState(false);
  const [workflowsModalVisible, setWorkflowsModalVisible] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const response = await api.get('/projects', { params: { search: searchText } });
      setProjects(response.data);
    } catch (error) {
      console.error('Failed to fetch projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchWorkflows = async (projectId: string) => {
    setWorkflowsLoading(true);
    try {
      const response = await api.get(`/projects/${projectId}/workflows`);
      setWorkflows(response.data);
      setWorkflowsModalVisible(true);
    } catch (error) {
      console.error('Failed to fetch workflows:', error);
    } finally {
      setWorkflowsLoading(false);
    }
  };

  const handleCreateProject = async (values: any) => {
    try {
      await api.post('/projects', values);
      fetchProjects();
      Modal.close();
    } catch (error) {
      console.error('Failed to create project:', error);
    }
  };

  const handleUpdateProject = async (values: any) => {
    try {
      await api.put(`/projects/${editingProject?.id}`, values);
      fetchProjects();
      Modal.close();
    } catch (error) {
      console.error('Failed to update project:', error);
    }
  };

  const handleDeleteProject = async (id: string) => {
    try {
      await api.delete(`/projects/${id}`);
      fetchProjects();
    } catch (error) {
      console.error('Failed to delete project:', error);
    }
  };

  const handleToggleVisibility = async (project: Project) => {
    try {
      await api.patch(`/projects/${project.id}`, { visibility: project.visibility === 'public' ? 'private' : 'public' });
      fetchProjects();
    } catch (error) {
      console.error('Failed to update project visibility:', error);
    }
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      render: (name: string, record: Project) => (
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
      title: 'Visibility',
      dataIndex: 'visibility',
      key: 'visibility',
      width: 100,
      align: 'center',
      render: (v: string) => (
        <Tag color={v === 'public' ? 'green' : v === 'private' ? 'red' : 'blue'}>
          {v}
        </Tag>
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
      width: 150,
      fixed: 'right',
      render: (_: any, record: Project) => (
        <Space>
          <Tooltip title="View Workflows">
            <Button type="link" onClick={() => {
              setSelectedProject(record);
              fetchWorkflows(record.id);
            }}>
              <EyeOutlined />
            </Button>
          </Tooltip>
          <Tooltip title="Edit">
            <Button type="link" onClick={() => {
              setEditingProject(record);
              setModalVisible(true);
            }}>
              <EditOutlined />
            </Button>
          </Tooltip>
          <Tooltip title={record.visibility === 'public' ? 'Make Private' : 'Make Public'}>
            <Button type="link" onClick={() => handleToggleVisibility(record)}>
              <Switch checked={record.visibility === 'public'} size="small" />
            </Button>
          </Tooltip>
          <Dropdown
            menu={{
              items: [
                { label: 'Duplicate', key: 'duplicate', icon: <CopyOutlined /> },
                { label: 'Export', key: 'export', icon: <DownloadOutlined /> },
                { type: 'divider' },
                { label: 'Delete', key: 'delete', icon: <DeleteOutlined />, danger: true, onClick: () => Modal.confirm({
                  title: 'Delete Project',
                  content: `Are you sure you want to delete "${record.name}"? This action cannot be undone.`,
                  onOk: () => handleDeleteProject(record.id),
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
    fetchProjects();
  }, []);

  return (
    <div className="projects-page">
      <div className="page-header">
        <div>
          <h1>Projects</h1>
          <p>Manage your projects and workflows</p>
        </div>
        <Button type="primary" onClick={() => { setEditingProject(null); setModalVisible(true); }}>
          <PlusOutlined /> Create Project
        </Button>
      </div>

      <Card>
        <Form layout="inline" onFinish={() => fetchProjects()} style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col md={8}>
              <Form.Item name="search" label="Search">
                <Input.Search
                  placeholder="Search projects..."
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  onPressEnter={() => fetchProjects()}
                  style={{ width: '100%' }}
                  allowClear
                />
              </Form.Item>
            </Col>
          </Row>
        </Form>
        
        <Table
          columns={columns}
          dataSource={projects}
          loading={loading}
          rowKey="id"
          pagination={{ pageSize: 10, showTotal: (total) => `Total ${total} projects` }}
          onChange={(pagination) => setPagination(pagination)}
        />

        {/* Create/Edit Project Modal */}
        <Modal
          title={editingProject ? 'Edit Project' : 'Create Project'}
          visible={modalVisible}
          onCancel={() => { setModalVisible(false); setEditingProject(null); }}
          onOk={() => form.validateFields().then(handleCreateProject).catch(() => {})}
          destroyOnClose
        >
          <Form layout="vertical">
            <Form.Item name="name" label="Name" rules={[{ required: true, message: 'Please input project name' }]}>
              <Input placeholder="Enter project name" />
            </Form.Item>
            <Form.Item name="slug" label="Slug" rules={[{ required: true, message: 'Please input slug' }]}>
              <Input placeholder="Enter slug (unique identifier)" />
            </Form.Item>
            <Form.Item name="description" label="Description">
              <Input.TextArea placeholder="Enter description" rows={3} />
            </Form.Item>
            <Form.Item name="visibility" label="Visibility" rules={[{ required: true }]}>
              <Select placeholder="Select visibility" style={{ width: '100%' }}>
                <Option value="private">Private</Option>
                <Option value="team">Team</Option>
                <Option value="public">Public</Option>
              </Select>
            </Form.Item>
          </Form>
        </Modal>

        {/* Workflows Modal */}
        <Modal
          title={`Workflows in ${selectedProject?.name}`}
          visible={workflowsModalVisible}
          onCancel={() => setWorkflowsModalVisible(false)}
          width={800}
          footer={null}
        >
          <Table
            dataSource={workflows}
            columns={[
              { title: 'Name', dataIndex: 'name', key: 'name' },
              { title: 'Description', dataIndex: 'description', key: 'description', ellipsis: true },
              { title: 'Version', dataIndex: 'version', key: 'version', width: 80 },
              { title: 'Runs', dataIndex: 'run_count', key: 'run_count', width: 80, align: 'center' },
              { title: 'Success Rate', dataIndex: 'success_rate', key: 'success_rate', width: 100, align: 'center', render: (v: number) => `${v}%` },
              { title: 'Actions', key: 'actions', render: (_: any, record: any) => <Space><Button type="link" onClick={() => window.location.href = `/workflows/${record.id}`}><EyeOutlined /></Button><Button type="link" onClick={() => window.location.href = `/workflows/${record.id}/execute`}><PlayOutlined /></Button></Space> },
            ]
            dataSource={workflows}
            loading={workflowsLoading}
            pagination={false}
          />
        </Modal>
      </Card>
    </div>
  );
}

export default Projects;