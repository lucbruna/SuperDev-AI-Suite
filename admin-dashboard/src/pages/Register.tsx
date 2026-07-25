import React, { useState } from 'react';
import { Card, Form, Input, Button, Checkbox, Alert, Tabs, TabPane } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, UnlockOutlined } from '@ant-design/icons';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { message } from 'antd';
import './AuthPage.css';

const { Item } = Form;

interface RegisterData {
  email: string;
  password: string;
  confirmPassword: string;
  username: string;
  fullName: string;
  organizationName: string;
  organizationSlug: string;
}

export function Register() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'personal' | 'organization'>('personal');
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleFinish = async (values: any) => {
    setLoading(true);
    setError('');
    try {
      const data: RegisterData = {
        email: values.email,
        password: values.password,
        username: values.username,
        fullName: values.fullName,
        organizationName: values.organizationName,
        organizationSlug: values.organizationSlug,
      };
      await register(data);
      message.success('Registration successful!');
      navigate('/dashboard');
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <div className="logo">
            <span className="logo-icon">SD</span>
            <span className="logo-text">SuperDev</span>
          </div>
          <h1>Create Your Account</h1>
          <p>Start building with SuperDev AI Suite</p>
        </div>

        {error && <Alert message="Error" description={error} type="error" showIcon closable />}

        <Form layout="vertical" onFinish={handleFinish} className="auth-form">
          <Tabs activeKey={activeTab} onChange={setActiveTab} className="auth-tabs">
            <TabPane tab="Personal Info" key="personal">
              <Form.Item name="fullName" label="Full Name" rules={[{ required: true, message: 'Please input your full name' }]}>
                <Input prefix={<UserOutlined />} placeholder="Full Name" />
              </Form.Item>
              <Form.Item name="username" label="Username" rules={[{ required: true, message: 'Please input a username' }, { pattern: /^[a-zA-Z0-9_-]{3,20}$/, message: 'Username must be 3-20 characters (letters, numbers, _, -)' }]}>
                <Input prefix={<UserOutlined />} placeholder="Username" />
              </Form.Item>
              <Form.Item name="email" label="Email" rules={[{ required: true, message: 'Please input your email' }, { type: 'email', message: 'Invalid email format' }]}>
                <Input prefix={<MailOutlined />} placeholder="Email" />
              </Form.Item>
              <Form.Item name="password" label="Password" rules={[{ required: true, message: 'Please input your password' }, { min: 8, message: 'Password must be at least 8 characters' }]}>
                <Input.Password prefix={<LockOutlined />} placeholder="Password" />
              </Form.Item>
              <Form.Item name="confirmPassword" label="Confirm Password" rules={[{ required: true, message: 'Please confirm your password' }, ({ getFieldValue }) => ({ validator: (_, value) => value === getFieldValue('password') ? Promise.resolve() : Promise.reject(new Error('Passwords do not match')) })]}>
                <Input.Password prefix={<UnlockOutlined />} placeholder="Confirm Password" />
              </Form.Item>
            </TabPane>

            <TabPane tab="Organization" key="organization">
              <Form.Item name="organizationName" label="Organization Name" rules={[{ required: true, message: 'Please input organization name' }]}>
                <Input placeholder="Organization Name" />
              </Form.Item>
              <Form.Item name="organizationSlug" label="Organization Slug" rules={[{ required: true, message: 'Please input organization slug' }, { pattern: /^[a-z0-9-]+$/, message: 'Slug must be lowercase letters, numbers, and hyphens only' }]}>
                <Input placeholder="organization-slug" addonAfter=".superdev.ai" />
              </Form.Item>
              <Form.Item name="plan" label="Plan">
                <Select placeholder="Select plan" style={{ width: '100%' }}>
                  <Option value="free">Free</Option>
                  <Option value="pro">Pro</Option>
                  <Option value="enterprise">Enterprise</Option>
                </Select>
              </Form.Item>
            </TabPane>
          </Tabs>

          <Form.Item>
            <Button type="primary" htmlType="submit" block size="large" loading={loading}>
              Create Account
            </Button>
          </Form.Item>

          <div className="auth-footer">
            Already have an account? <Link to="/login">Sign in</Link>
          </div>
        </Form>

        <div className="auth-divider">
          <span>Or continue with</span>
        </div>

        <div className="social-buttons">
          <Button type="default" block icon={<GitHubOutlined />}>GitHub</Button>
          <Button type="default" block icon={<GoogleOutlined />}>Google</Button>
          <Button type="default" block icon={<GitlabOutlined />}>GitLab</Button>
        </div>
      </div>
    </div>
  );
}

export default Register;