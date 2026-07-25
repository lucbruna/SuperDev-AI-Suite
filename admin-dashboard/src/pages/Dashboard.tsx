import React, { useState, useEffect } from 'react';
import { Card, Statistic, Row, Col, Table, Tag, Button, Space, Modal, Form, Input, Select, DatePicker, Alert } from 'antd';
import { 
  UserOutlined, TeamOutlined, FolderOutlined, 
  GitBranchOutlined, RobotOutlined, DatabaseOutlined, 
  PluginOutlined, FlagOutlined, SettingOutlined,
  PlusOutlined, SearchOutlined, FilterOutlined,
  DownloadOutlined, EditOutlined, DeleteOutlined,
  EyeOutlined, MoreOutlined
} from '@ant-design/icons';
import { format, subDays } from 'date-fns';
import { api } from '../services/api';

const { Meta } = Statistic;
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

interface Workflow {
  id: string;
  name: string;
  description?: string;
  definition: any;
  version: number;
  tags: string[];
  is_template: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
  run_count: number;
  success_rate: number;
}

interface Agent {
  id: string;
  name: string;
  type: string;
  description?: string;
  config: any;
  system_prompt?: string;
  model_provider?: string;
  model_name?: string;
  tools: string[];
  is_active: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
  execution_count: number;
  success_rate: number;
}

interface KnowledgeBase {
  id: string;
  name: string;
  description?: string;
  type: string;
  embedding_model: string;
  embedding_dimension: number;
  chunk_size: number;
  chunk_overlap: number;
  settings: any;
  is_public: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
  entry_count: number;
}

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

interface FeatureFlag {
  name: string;
  description: string;
  enabled: boolean;
  type: string;
  tags: string[];
  strategies: any[];
}

export function Dashboard() {
  const [stats, setStats] = useState({
    organizations: 0,
    projects: 0,
    workflows: 0,
    agents: 0,
    knowledgeBases: 0,
    plugins: 0,
    executionsToday: 0,
    successRate: 0,
  });
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [orgs, projects, workflows, agents, kbs, plugins, executions] = await Promise.all([
        api.get('/organizations').then(r => r.data),
        api.get('/projects').then(r => r.data),
        api.get('/workflows').then(r => r.data),
        api.get('/agents').then(r => r.data),
        api.get('/knowledge-bases').then(r => r.data),
        api.get('/plugins/registry').then(r => r.data),
        api.get('/executions/stats/today').then(r => r.data).catch(() => ({ count: 0, success_rate: 0 })),
      ]);
      
      setStats({
        organizations: orgs.length,
        projects: projects.length,
        workflows: workflows.length,
        agents: agents.length,
        knowledgeBases: kbs.length,
        plugins: plugins.length,
        executionsToday: executions.count,
        successRate: executions.success_rate,
      });
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Welcome back! Here's what's happening with your projects.</p>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6} xl={4}>
          <Card>
            <Statistic
              title="Organizations"
              value={stats.organizations}
              prefix={<TeamOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6} xl={4}>
          <Card>
            <Statistic
              title="Projects"
              value={stats.projects}
              prefix={<FolderOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6} xl={4}>
          <Card>
            <Statistic
              title="Workflows"
              value={stats.workflows}
              prefix={<GitBranchOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6} xl={4}>
          <Card>
            <Statistic
              title="Agents"
              value={stats.agents}
              prefix={<RobotOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6} xl={4}>
          <Card>
            <Statistic
              title="Knowledge Bases"
              value={stats.knowledgeBases}
              prefix={<DatabaseOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6} xl={4}>
          <Card>
            <Statistic
              title="Plugins"
              value={stats.plugins}
              prefix={<PluginOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6} xl={4}>
          <Card>
            <Statistic
              title="Executions Today"
              value={stats.executionsToday}
              prefix={<GitBranchOutlined />}
              suffix="executions"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6} xl={4}>
          <Card>
            <Statistic
              title="Success Rate"
              value={`${stats.successRate}%`}
              prefix={<CheckCircleOutlined />}
              precision={1}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="Recent Activity" extra={<Button type="link">View All</Button>}>
            {recentActivity.length === 0 ? (
              <div className="empty-state">
                <p>No recent activity</p>
              </div>
            ) : (
              <div className="activity-list">
                {recentActivity.map((activity, index) => (
                  <div key={index} className="activity-item">
                    <div className="activity-icon">
                      {getActivityIcon(activity.type)}
                    </div>
                    <div className="activity-content">
                      <div className="activity-title">{activity.title}</div>
                      <div className="activity-meta">
                        <span>{activity.actor}</span>
                        <span>{format(new Date(activity.timestamp), 'PPpp')}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Quick Actions" extra={<Button type="link">More Actions</Button>}>
            <div className="quick-actions">
              <Button type="primary" block icon={<PlusOutlined />}>
                Create New Project
              </Button>
              <Button block icon={<PlusOutlined />}>
                Create Workflow
              </Button>
              <Button block icon={<RobotOutlined />}>
                Create Agent
              </Button>
              <Button block icon={<DatabaseOutlined />}>
                Create Knowledge Base
              </Button>
              <Button block icon={<PluginOutlined />}>
                Browse Plugins
              </Button>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

function getActivityIcon(type: string) {
  switch (type) {
    case 'workflow': return <GitBranchOutlined style={{ color: '#1890ff' }} />;
    case 'agent': return <RobotOutlined style={{ color: '#722ed1' }} />;
    case 'project': return <FolderOutlined style={{ color: '#faad14' }} />;
    case 'knowledge': return <DatabaseOutlined style={{ color: '#13c2c2' }} />;
    case 'plugin': return <PluginOutlined style={{ color: '#eb2f96' }} />;
    default: return <GitBranchOutlined />;
  }
}

export default Dashboard;