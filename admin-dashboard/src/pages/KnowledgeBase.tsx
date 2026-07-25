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
  UploadOutlined, FolderOutlined, FileOutlined, SearchOutlined
} from '@ant-design/icons';
import { api } from '../services/api';
import { format } from 'date-fns';

interface KnowledgeBase {
  id: string;
  name: string;
  description: string;
  type: string;
  embedding_model: string;
  embedding_dimension: number;
  chunk_size: number;
  chunk_overlap: number;
  settings: any;
  is_public: boolean;
  project_id: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  entry_count: number;
}

interface KnowledgeEntry {
  id: string;
  knowledge_base_id: string;
  title: string;
  content: string;
  source_url: string;
  source_type: string;
  language: string;
  tags: string[];
  metadata: any;
  token_count: number;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export function KnowledgeBase() {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingKb, setEditingKb] = useState<KnowledgeBase | null>(null);
  const [searchText, setSearchText] = useState('');
  const [selectedKb, setSelectedKb] = useState<KnowledgeBase | null>(null);
  const [entries, setEntries] = useState<KnowledgeEntry[]>([]);
  const [entriesLoading, setEntriesLoading] = useState(false);
  const [entriesModalVisible, setEntriesModalVisible] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
  const [activeTab, setActiveTab] = useState('bases');

  const fetchKnowledgeBases = async () => {
    setLoading(true);
    try {
      const response = await api.get('/knowledge-bases', { params: { search: searchText } });
      setKnowledgeBases(response.data);
    } catch (error) {
      console.error('Failed to fetch knowledge bases:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchEntries = async (kbId: string) => {
    setEntriesLoading(true);
    try {
      const response = await api.get(`/knowledge-bases/${kbId}/entries`);
      setEntries(response.data);
      setEntriesModalVisible(true);
    } catch (error) {
      console.error('Failed to fetch entries:', error);
    } finally {
      setEntriesLoading(false);
    }
  };

  const fetchSearch = async (query: string, kbId?: string) => {
    try {
      const response = await api.post('/knowledge-bases/search', { query, knowledge_base_id: kbId });
      return response.data;
    } catch (error) {
      console.error('Search failed:', error);
      return [];
    }
  };

  const handleCreateKb = async (values: any) => {
    try {
      await api.post('/knowledge-bases', values);
      fetchKnowledgeBases();
      Modal.close();
    } catch (error) {
      console.error('Failed to create knowledge base:', error);
    }
  };

  const handleUpdateKb = async (values: any) => {
    try {
      await api.put(`/knowledge-bases/${editingKb?.id}`, values);
      fetchKnowledgeBases();
      Modal.close();
    } catch (error) {
      console.error('Failed to update knowledge base:', error);
    }
  };

  const handleDeleteKb = async (id: string) => {
    try {
      await api.delete(`/knowledge-bases/${id}`);
      fetchKnowledgeBases();
    } catch (error) {
      console.error('Failed to delete knowledge base:', error);
    }
  };

  const handleIngestRepo = async (kbId: string, repoUrl: string) => {
    try {
      await api.post(`/knowledge-bases/${kbId}/ingest-repo`, { repo_url: repoUrl });
      Message.success('Repository ingestion started');
    } catch (error) {
      console.error('Failed to ingest repo:', error);
    }
  };

  const handleIngestFiles = async (kbId: string, files: File[]) => {
    try {
      const formData = new FormData();
      files.forEach(file => formData.append('files', file));
      await api.post(`/knowledge-bases/${kbId}/ingest-files`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
      Message.success('Files uploaded successfully');
    } catch (error) {
      console.error('Failed to upload files:', error);
    }
  };

  const handleSearch = async (query: string, kbId?: string) => {
    try {
      const response = await api.post('/knowledge-bases/search', { query, knowledge_base_id: kbId });
      return response.data;
    } catch (error) {
      console.error('Search failed:', error);
      return [];
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'documentation': return 'blue';
      case 'code': return 'green';
      case 'specification': return 'purple';
      case 'error_log': return 'red';
      case 'best_practice': return 'gold';
      case 'pattern': return 'cyan';
      case 'template': return 'magenta';
      case 'example': return 'orange';
      case 'research': return 'blue';
      default: return 'default';
    }
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      render: (name: string, record: KnowledgeBase) => (
        <div>
          <div style={{ fontWeight: 500 }}>{name}</div>
          <div style={{ color: '#999', fontSize: 12 }}>
            {record.type} • {record.entry_count} entries
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
      render: (v: string) => <Tag color={getTypeColor(v)}>{v}</Tag>,
    },
    {
      title: 'Embedding Model',
      dataIndex: 'embedding_model',
      key: 'embedding_model',
      width: 150,
    },
    {
      title: 'Chunk Size',
      dataIndex: 'chunk_size',
      key: 'chunk_size',
      width: 100,
      align: 'center',
    },
    {
      title: 'Entries',
      dataIndex: 'entry_count',
      key: 'entry_count',
      width: 80,
      align: 'center',
    },
    {
      title: 'Public',
      dataIndex: 'is_public',
      key: 'is_public',
      width: 80,
      align: 'center',
      render: (v: boolean) => v ? <CheckCircleOutlined style={{ color: '#52c41a' }} /> : <CloseCircleOutlined style={{ color: '#ff4d4f' }} />,
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
      render: (_: any, record: KnowledgeBase) => (
        <Space>
          <Tooltip title="View Entries">
            <Button type="link" onClick={() => {
              setSelectedKb(record);
              fetchEntries(record.id);
            }}>
              <EyeOutlined />
            </Button>
          </Tooltip>
          <Tooltip title="Search">
            <Button type="link" onClick={() => {
              const query = prompt('Enter search query:');
              if (query) {
                fetchSearch(query, record.id).then(results => {
                  if (results.length > 0) {
                    alert(`Found ${results.length} results`);
                  } else {
                    Message.info('No results found');
                  }
                });
              }
            }}>
              <SearchOutlined />
            </Button>
          </Tooltip>
          <Tooltip title="Ingest Repository">
            <Button type="link" onClick={() => {
              const url = prompt('Enter repository URL:');
              if (url) handleIngestRepo(record.id, url);
            }}>
              <DownloadOutlined />
            </Button>
          </Tooltip>
          <Tooltip title="Upload Files">
            <Button type="link" onClick={() => {
              const input = document.createElement('input');
              input.type = 'file';
              input.multiple = true;
              input.accept = '.py,.js,.ts,.md,.txt,.json,.yaml,.yml';
              input.onchange = (e) => {
                if (e.target.files) handleIngestFiles(record.id, Array.from(e.target.files));
              };
              input.click();
            }}>
              <UploadOutlined />
            </Button>
          </Tooltip>
          <Tooltip title="Edit">
            <Button type="link" onClick={() => {
              setEditingKb(record);
              setModalVisible(true);
            }}>
              <EditOutlined />
            </Button>
          </Tooltip>
          <Dropdown
            menu={{
              items: [
                { label: 'View Context', key: 'context', icon: <EnvironmentOutlined /> },
                { label: 'Export', key: 'export', icon: <DownloadOutlined /> },
                { type: 'divider' },
                { label: 'Delete', key: 'delete', icon: <DeleteOutlined />, danger: true, onClick: () => Modal.confirm({
                  title: 'Delete Knowledge Base',
                  content: `Are you sure you want to delete "${record.name}"? This action cannot be undone.`,
                  onOk: () => handleDeleteKb(record.id),
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
    fetchKnowledgeBases();
  }, []);

  return (
    <div className="knowledge-base-page">
      <div className="page-header">
        <div>
          <h1>Knowledge Base</h1>
          <p>Manage knowledge bases, documents, and semantic search</p>
        </div>
        <Button type="primary" onClick={() => { setEditingKb(null); setModalVisible(true); }}>
          <PlusOutlined /> Create Knowledge Base
        </Button>
      </div>

      <Tabs activeKey={activeTab} onChange={setActiveTab} style={{ marginBottom: 24 }}>
        <Tabs.TabPane tab="Knowledge Bases" key="bases" />
        <Tabs.TabPane tab="Semantic Search" key="search" />
      </Tabs>

      <Card>
        <Form layout="inline" onFinish={() => fetchKnowledgeBases()} style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col md={8}>
              <Form.Item name="search" label="Search">
                <Input.Search
                  placeholder="Search knowledge bases..."
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  onPressEnter={() => fetchKnowledgeBases()}
                  style={{ width: '100%' }}
                  allowClear
                />
              </Form.Item>
            </Col>
          </Row>
        </Form>
        
        <Table
          columns={columns}
          dataSource={knowledgeBases}
          loading={loading}
          rowKey="id"
          pagination={{ pageSize: 10, showTotal: (total) => `Total ${total} knowledge bases` }}
          onChange={(pagination) => setPagination(pagination)}
        />

        {/* Create/Edit KB Modal */}
        <Modal
          title={editingKb ? 'Edit Knowledge Base' : 'Create Knowledge Base'}
          visible={modalVisible}
          onCancel={() => { setModalVisible(false); setEditingKb(null); }}
          onOk={() => form.validateFields().then(editingKb ? handleUpdateKb : handleCreateKb).catch(() => {})}
          destroyOnClose
        >
          <Form layout="vertical">
            <Form.Item name="name" label="Name" rules={[{ required: true, message: 'Please input name' }]}>
              <Input placeholder="Enter knowledge base name" />
            </Form.Item>
            <Form.Item name="description" label="Description">
              <Input.TextArea placeholder="Enter description" rows={3} />
            </Form.Item>
            <Form.Item name="type" label="Type" rules={[{ required: true, message: 'Please select type' }]}>
              <Select placeholder="Select type" style={{ width: '100%' }}>
                <Option value="documentation">Documentation</Option>
                <Option value="code">Code</Option>
                <Option value="specification">Specification</Option>
                <Option value="error_log">Error Log</Option>
                <Option value="best_practice">Best Practice</Option>
                <Option value="pattern">Pattern</Option>
                <Option value="template">Template</Option>
                <Option value="example">Example</Option>
                <Option value="research">Research</Option>
              </Select>
            </Form.Item>
            <Form.Item name="embedding_model" label="Embedding Model" rules={[{ required: true }]}>
              <Select placeholder="Select embedding model" style={{ width: '100%' }}>
                <Option value="all-MiniLM-L6-v2">all-MiniLM-L6-v2 (384 dim)</Option>
                <Option value="all-mpnet-base-v2">all-mpnet-base-v2 (768 dim)</Option>
                <Option value="text-embedding-ada-002">OpenAI text-embedding-ada-002 (1536 dim)</Option>
                <Option value="text-embedding-3-small">OpenAI text-embedding-3-small (1536 dim)</Option>
                <Option value="text-embedding-3-large">OpenAI text-embedding-3-large (3072 dim)</Option>
              </Select>
            </Form.Item>
            <Form.Item name="embedding_dimension" label="Embedding Dimension" rules={[{ required: true }]}>
              <InputNumber placeholder="e.g., 384, 768, 1536" />
            </Form.Item>
            <Form.Item name="chunk_size" label="Chunk Size">
              <InputNumber placeholder="1000" />
            </Form.Item>
            <Form.Item name="chunk_overlap" label="Chunk Overlap">
              <InputNumber placeholder="200" />
            </Form.Item>
            <Form.Item name="is_public" label="Public" valuePropName="checked">
              <Switch />
            </Form.Item>
          </Form>
        </Modal>

        {/* Entries Modal */}
        <Modal
          title={`Entries in ${selectedKb?.name}`}
          visible={entriesModalVisible}
          onCancel={() => setEntriesModalVisible(false)}
          width={1000}
          footer={null}
        >
          <Table
            dataSource={entries}
            columns={[
              { title: 'Title', dataIndex: 'title', key: 'title', ellipsis: true },
              { title: 'Type', dataIndex: 'source_type', key: 'source_type', width: 100, render: (v: string) => <Tag>{v}</Tag> },
              { title: 'Language', dataIndex: 'language', key: 'language', width: 100 },
              { title: 'Tags', dataIndex: 'tags', key: 'tags', render: (v: string[]) => <Space wrap>{v.map(t => <Tag key={t}>{t}</Tag>)} },
              { title: 'Tokens', dataIndex: 'token_count', key: 'token_count', width: 80, align: 'center' },
              { title: 'Created', dataIndex: 'created_at', key: 'created_at', width: 150, render: (d: string) => format(new Date(d), 'PP') },
              { title: 'Actions', key: 'actions', render: (_: any, record: any) => <Space><Button type="link" size="small"><EyeOutlined /></Button><Button type="link" size="small"><CodeOutlined /></Button></Space> },
            ]
            dataSource={entries}
            loading={entriesLoading}
            pagination={false}
          />
        </Modal>
      </Card>
    </div>
  );
}

export default KnowledgeBase;