"use client"

import { useState } from 'react'
import { Card, CardHeader, CardBody, Grid, Badge, Button, Text, Table } from '@/components/ui'

function StackedPRsPage() {
  const [stacks, setStacks] = useState([
    { id: 'stack_1', task: 'Implement auth system', layers: 4, status: 'merged' },
    { id: 'stack_2', task: 'Add payment integration', layers: 3, status: 'review' },
    { id: 'stack_3', task: 'Refactor database layer', layers: 2, status: 'draft' },
  ])

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">📦 Stacked PR Manager</h1>
        <Badge variant="primary">3 STACKS</Badge>
      </div>

      <Card>
        <CardHeader title="PR Stacks" subtitle="Task → Layers → Merged" />
        <CardBody>
          <Table>
            <thead><tr><th>Task</th><th>Layers</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>
              {stacks.map(stack => (
                <tr key={stack.id}>
                  <td className="font-medium">{stack.task}</td>
                  <td>{stack.layers}</td>
                  <td><Badge variant={stack.status === 'merged' ? 'success' : stack.status === 'review' ? 'warning' : 'info'}>{stack.status}</Badge></td>
                  <td>
                    <Button variant="ghost" size="sm">Rebase</Button>
                    <Button variant="ghost" size="sm">Merge</Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
          <Button variant="primary" className="mt-4">Create New Stack</Button>
        </CardBody>
      </Card>

      <Grid cols={3} gap={4}>
        <Card>
          <CardHeader title="Stack Anatomy" subtitle="How It Works" />
          <CardBody>
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Badge variant="info">Layer 0</Badge>
                <Text size="sm">Base changes (must merge first)</Text>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="info">Layer 1</Badge>
                <Text size="sm">Depends on Layer 0</Text>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="info">Layer 2</Badge>
                <Text size="sm">Depends on Layer 1</Text>
              </div>
            </div>
            <Text size="sm" className="mt-3">Each layer depends on the previous one. Auto-rebase when feedback changes.</Text>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Features" subtitle="Stacked PR Capabilities" />
          <CardBody>
            <ul className="space-y-2">
              <li>✅ Decompose large tasks into ordered PRs</li>
              <li>✅ Automatic rebasing on feedback</li>
              <li>✅ Stack status overview (CI, reviews)</li>
              <li>✅ Merge all layers in order</li>
              <li>✅ Architectural seam detection</li>
            </ul>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Stack Stats" subtitle="Current Activity" />
          <CardBody>
            <Table>
              <tbody>
                <tr><td>Total Stacks</td><td>3</td></tr>
                <tr><td>Total Layers</td><td>9</td></tr>
                <tr><td>Merged</td><td>4</td></tr>
                <tr><td>In Review</td><td>3</td></tr>
                <tr><td>Draft</td><td>2</td></tr>
              </tbody>
            </Table>
          </CardBody>
        </Card>
      </Grid>
    </div>
  )
}

export default StackedPRsPage
