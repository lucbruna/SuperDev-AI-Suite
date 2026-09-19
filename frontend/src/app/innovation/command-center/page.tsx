"use client"

import { useState } from 'react'
import { Card, CardHeader, CardBody, Grid, Badge, Button, Text, Table } from '@/components/ui'

function AgentCommandCenterPage() {
  const [agents, setAgents] = useState([
    { id: 'local_1', name: 'Local Agent 1', status: 'in_progress', type: 'local', task: 'Fix auth bug' },
    { id: 'cloud_1', name: 'Cloud Agent 1', status: 'blocked', type: 'cloud', task: 'Deploy staging' },
    { id: 'local_2', name: 'Local Agent 2', status: 'ready_for_review', type: 'local', task: 'Add tests' },
    { id: 'cloud_2', name: 'Cloud Agent 2', status: 'in_progress', type: 'cloud', task: 'Refactor API' },
  ])

  const spawnAgent = (type: string) => {
    const id = type === 'local' ? `local_${Date.now()}` : `cloud_${Date.now()}`
    setAgents([...agents, { id, name: `${type === 'local' ? 'Local' : 'Cloud'} Agent ${agents.length + 1}`, status: 'in_progress', type, task: 'New task' }])
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">🎯 Agent Command Center</h1>
        <Badge variant="primary">LIVE</Badge>
      </div>

      <Grid cols={3} gap={4}>
        <Card>
          <CardHeader title="📊 Kanban Overview" subtitle="Agent Status" />
          <CardBody>
            <Table>
              <thead><tr><th>Status</th><th>Count</th></tr></thead>
              <tbody>
                {['in_progress', 'blocked', 'ready_for_review', 'completed'].map(status => (
                  <tr key={status}>
                    <td>{status.replace('_', ' ')}</td>
                    <td>{agents.filter(a => a.status === status).length}</td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="⚡ Spawn Agent" subtitle="Create New Agent" />
          <CardBody>
            <Button variant="primary" className="mb-2" onClick={() => spawnAgent('local')}>
              🖥️ Spawn Local Agent
            </Button>
            <Button variant="secondary" onClick={() => spawnAgent('cloud')}>
              ☁️ Spawn Cloud Agent
            </Button>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="📈 Statistics" subtitle="Agent Activity" />
          <CardBody>
            <Text>Total Agents: {agents.length}</Text>
            <Text>Active: {agents.filter(a => a.status === 'in_progress').length}</Text>
          </CardBody>
        </Card>
      </Grid>

      <Card>
        <CardHeader title="📋 Agent Table" subtitle="All Registered Agents" />
        <CardBody>
          <Table>
            <thead>
              <tr><th>ID</th><th>Name</th><th>Status</th><th>Type</th><th>Task</th></tr>
            </thead>
            <tbody>
              {agents.map(agent => (
                <tr key={agent.id}>
                  <td>{agent.id}</td>
                  <td>{agent.name}</td>
                  <td><Badge variant={agent.status === 'in_progress' ? 'warning' : 'info'}>{agent.status.replace('_', ' ')}</Badge></td>
                  <td><Badge variant={agent.type === 'cloud' ? 'primary' : 'secondary'}>{agent.type}</Badge></td>
                  <td>{agent.task}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        </CardBody>
      </Card>
    </div>
  )
}

export default AgentCommandCenterPage
