import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Tag, Modal, Form, Input, Select, Space, Dropdown, Menu, Message, Divider, Tooltip, Badge, Row, Col } from 'antd';
import { 
  PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined, 
  MoreOutlined, SearchOutlined, FilterOutlined, DownloadOutlined,
  TeamOutlined, SettingOutlined, DeleteOutlined, UserOutlined,
  CheckCircleOutlined, CloseCircleOutlined, ClockCircleOutlined
} from '@ant-design/icons';
import { api } from '../services/api';
import { format } from 'date-fns';

const { Option } = Select;

interface Organization {
  id: string;
  name: string;
  slug: string;
  description?: string;
  plan: string;
  is_active: boolean;
  created_at: string;
  member_count: number;
  project_count: number;
}

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

export function Organizations() {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingOrg, setEditingOrg] = useState<Organization | null>(null);
  const [searchText, setSearchText] = useState('');
  const [selectedOrg, setSelectedOrg] = useState<Organization | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectsLoading, setProjectsLoading] = useState(false);
  const [projectsModalVisible, setProjectsModalVisible] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });

  const fetchOrganizations = async () => {
    setLoading(true);
    try {
      const response = await api.get('/organizations', { params: { search: searchText } });
      setOrganizations(response.data);
    } catch (error) {
      console.error('Failed to fetch organizations:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchProjects = async (orgId: string) => {
    setProjectsLoading(true);
    try {
      const response = await api.get(`/organizations/${orgId}/projects`);
      setProjects(response.data);
      setProjectsModalVisible(true);
    } catch (error) {
      console.error('Failed to fetch projects:', error);
    } finally {
      setProjectsLoading(false);
    }
  };

  const handleCreateOrg = async (values: any) => {
    try {
      await api.post('/organizations', values);
      fetchOrganizations();
      Modal.close();
    } catch (error) {
      console.error('Failed to create organization:', error);
    }
  };

  const handleUpdateOrg = async (values: any) => {
    try {
      await api.put(`/organizations/${editingOrg?.id}`, values);
      fetchOrganizations();
      Modal.close();
    } catch (error) {
      console.error('Failed to update organization:', error);
    }
  };

  const handleDeleteOrg = async (id: string) => {
    try {
      await api.delete(`/organizations/${id}`);
      fetchOrganizations();
    } catch (error) {
      console.error('Failed to delete organization:', error);
    }
  };

  const handleToggleStatus = async (org: Organization) => {
    try {
      await api.patch(`/organizations/${org.id}`, { is_active: !org.is_active });
      fetchOrganizations();
    } catch (error) {
      console.error('Failed to update organization status:', error);
    }
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      render: (name: string, record: Organization) => (
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
      title: 'Plan',
      dataIndex: 'plan',
      key: 'plan',
      width: 100,
      render: (plan: string) => (
        <Tag color={plan === 'enterprise' ? 'gold' : plan === 'pro' ? 'blue' : 'default'}>
          {plan}
        </Tag>
      ),
    },
    {
      title: 'Members',
      dataIndex: 'member_count',
      key: 'member_count',
      width: 80,
      align: 'center',
    },
    {
      title: 'Projects',
      dataIndex: 'project_count',
      key: 'project_count',
      width: 80,
      align: 'center',
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      align: 'center',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'success' : 'default'}>
          {isActive ? 'Active' : 'Inactive'}
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
      render: (_: any, record: Organization) => (
        <Space>
          <Tooltip title="View Projects">
            <Button type="link" onClick={() => {
              setSelectedOrg(record);
              fetchProjects(record.id);
            }}>
              <EyeOutlined />
            </Button>
          </Tooltip>
          <Tooltip title="Edit">
            <Button type="link" onClick={() => {
              setEditingOrg(record);
              setModalVisible(true);
            }}>
              <EditOutlined />
            </Button>
          </Tooltip>
          <Tooltip title={record.is_active ? 'Deactivate' : 'Activate'}>
            <Button type="link" onClick={() => handleToggleStatus(record)}>
              {record.is_active ? <CheckCircleOutlined /> : <ClockCircleOutlined />}
            </Button>
          </Tooltip>
          <Dropdown
            menu={{
              items: [
                { label: 'View Members', key: 'members', icon: <TeamOutlined />, onClick: () => window.location.href = `/organizations/${record.id}/members` },
                { label: 'Settings', key: 'settings', icon: <SettingOutlined />, onClick: () => window.location.href = `/organizations/${record.id}/settings` },
                { type: 'divider' },
                { label: 'Delete', key: 'delete', icon: <DeleteOutlined />, danger: true, onClick: () => Modal.confirm({
                  title: 'Delete Organization',
                  content: `Are you sure you want to delete "${record.name}"? This action cannot be undone.`,
                  onOk: () => handleDeleteOrg(record.id),
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
    fetchOrganizations();
  }, []);

  return (
    <div className="organizations-page">
      <div className="page-header">
        <div>
          <h1>Organizations</h1>
          <p>Manage your organizations and their settings</p>
        </div>
        <Button type="primary" onClick={() => { setEditingOrg(null); setModalVisible(true); }}>
          <PlusOutlined /> Create Organization
        </Button>
      </div>

      <Card>
        <Form layout="inline" onFinish={() => fetchOrganizations()} style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col md={8}>
              <Form.Item name="search" label="Search">
                <Input.Search
                  placeholder="Search organizations..."
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  onPressEnter={() => fetchOrganizations()}
                  style={{ width: '100%' }}
                  allowClear
                />
              </Form.Item>
            </Col>
          </Row>
        </Form>
        
        <Table
          columns={columns}
          dataSource={organizations}
          loading={loading}
          rowKey="id"
          pagination={{ pageSize: 10, showTotal: (total) => `Total ${total} organizations` }}
          onChange={(pagination) => setPagination(pagination)}
        />

        {/* Create/Edit Organization Modal */}
        <Modal
          title={editingOrg ? 'Edit Organization' : 'Create Organization'}
          visible={modalVisible}
          onCancel={() => { setModalVisible(false); setEditingOrg(null); }}
          onOk={() => form.validateFields().then(handleCreateOrg).catch(() => {})}
          destroyOnClose
        >
          <Form layout="vertical">
            <Form.Item name="name" label="Name" rules={[{ required: true, message: 'Please input organization name' }]}>
              <Input placeholder="Enter organization name" />
            </Form.Item>
            <Form.Item name="slug" label="Slug" rules={[{ required: true, message: 'Please input slug' }]}>
              <Input placeholder="Enter slug (unique identifier)" />
            </Form.Item>
            <Form.Item name="description" label="Description">
              <Input.TextArea placeholder="Enter description" rows={3} />
            </Form.Item>
            <Form.Item name="plan" label="Plan" rules={[{ required: true }]}>
              <Select placeholder="Select plan" style={{ width: '100%' }}>
                <Option value="free">Free</Option>
                <Option value="pro">Pro</Option>
                <Option value="enterprise">Enterprise</Option>
              </Select>
            </Form.Item>
          </Form>
        </Modal>

        {/* Projects Modal */}
        <Modal
          title={`Projects in ${selectedOrg?.name}`}
          visible={projectsModalVisible}
          onCancel={() => setProjectsModalVisible(false)}
          width={800}
          footer={null}
        >
          <Table
            dataSource={projects}
            columns={[
              { title: 'Name', dataIndex: 'name', key: 'name' },
              { title: 'Description', dataIndex: 'description', key: 'description', ellipsis: true },
              { title: 'Visibility', dataIndex: 'visibility', key: 'visibility', render: (v: string) => <Tag color={v === 'public' ? 'green' : v === 'private' ? 'red' : 'blue'}>{v}</Tag> },
              { title: 'Created', dataIndex: 'created_at', key: 'created_at', render: (d: string) => format(new Date(d), 'PP') },
              { title: 'Actions', key: 'actions', render: (_: any, record: Project) => <Button type="link" onClick={() => window.location.href = `/projects/${record.id}`}>View</Button> },
            ]
            dataSource={projects}
            loading={projectsLoading}
            pagination={false}
          />
        </Modal>
      </Card>
    </div>
  );
}

export default Organizations;