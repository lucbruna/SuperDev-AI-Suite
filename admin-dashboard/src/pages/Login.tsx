import React, { useState } from 'react';
import { Card, Form, Input, Button, Checkbox, Alert, Tabs, TabPane } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, UnlockOutlined } from '@ant-design/icons';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import './AuthPage.css';

export function Login() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleFinish = async (values: any) => {
    setLoading(true);
    setError('');
    try {
      await login(values.email, values.password);
      navigate('/dashboard');
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Login failed');
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
          <h1>Welcome Back</h1>
          <p>Sign in to your SuperDev account</p>
        </div>

        {error && <Alert message="Error" description={error} type="error" showIcon closable />}

        <Form layout="vertical" onFinish={handleFinish} className="auth-form">
          <Form.Item name="email" rules={[{ required: true, message: 'Please input your email' }, { type: 'email', message: 'Invalid email format' }]}>
            <Input prefix={<MailOutlined />} placeholder="Email" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: 'Please input your password' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="Password" />
          </Form.Item>
          <Form.Item name="remember" valuePropName="checked">
            <Checkbox>Remember me</Checkbox>
          </Form.Item>
          <div className="auth-footer">
            <Link to="/forgot-password">Forgot password?</Link>
            <Link to="/register">Don't have an account? Sign up</Link>
          </div>
          <Form.Item>
            <Button type="primary" htmlType="submit" block loading={loading} size="large">
              Sign In
            </Button>
          </Form.Item>
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

export default Login;