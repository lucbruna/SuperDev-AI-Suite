"use client"

import { useState } from 'react'
import { Card, CardHeader, CardBody, Grid, Badge, Button, Text, Table } from '@/components/ui'

function AgenticMapReducePage() {
  const [phases, setPhases] = useState<{ name: string; status: string; findings: number }[]>([])
  const [isRunning, setIsRunning] = useState(false)

  const startScan = () => {
    setIsRunning(true)
    setPhases([
      { name: 'Plan', status: '✅ Complete', findings: 0 },
      { name: 'Shard', status: '✅ Complete', findings: 5 },
      { name: 'Map', status: '🔄 In Progress', findings: 23 },
      { name: 'Reduce', status: '⏳ Pending', findings: 0 },
    ])
    setTimeout(() => {
      setPhases([
        { name: 'Plan', status: '✅ Complete', findings: 0 },
        { name: 'Shard', status: '✅ Complete', findings: 5 },
        { name: 'Map', status: '✅ Complete', findings: 23 },
        { name: 'Reduce', status: '✅ Complete', findings: 15 },
      ])
      setIsRunning(false)
    }, 3000)
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">🔍 Agentic MapReduce Code Scans</h1>
        <Badge variant="primary">4 PHASES</Badge>
      </div>

      <Card>
        <CardHeader title="Scan Pipeline" subtitle="Plan → Shard → Map → Reduce" />
        <CardBody>
          <Grid cols={4} gap={4}>
            {phases.map((phase, i) => (
              <div key={i} className="p-4 rounded-lg border text-center">
                <h3 className="font-bold text-lg">Phase {i + 1}: {phase.name}</h3>
                <Badge variant={phase.status.includes('✅') ? 'success' : phase.status.includes('🔄') ? 'warning' : 'info'}>
                  {phase.status}
                </Badge>
                <Text size="sm" className="mt-2">Findings: {phase.findings}</Text>
              </div>
            ))}
          </Grid>
          <div className="flex justify-center mt-6">
            <Button variant="primary" size="lg" onClick={startScan} disabled={isRunning}>
              {isRunning ? '🔄 Scanning...' : '🚀 Start Code Scan'}
            </Button>
          </div>
        </CardBody>
      </Card>

      <Grid cols={2} gap={4}>
        <Card>
          <CardHeader title="Scan Types" subtitle="Available Scan Categories" />
          <CardBody>
            <div className="space-y-2">
              {['Performance', 'Database Queries', 'Test Coverage', 'Dead Code', 'Code Quality', 'Security', 'Accessibility', 'Compliance'].map(type => (
                <div key={type} className="flex items-center justify-between p-2 rounded border">
                  <Text>{type}</Text>
                  <Badge variant="info">Available</Badge>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Results Summary" subtitle="Latest Scan" />
          <CardBody>
            <Table>
              <tbody>
                <tr><td>Total Findings</td><td>15</td></tr>
                <tr><td>High Severity</td><td><Badge variant="danger">3</Badge></td></tr>
                <tr><td>Medium Severity</td><td><Badge variant="warning">5</Badge></td></tr>
                <tr><td>Low Severity</td><td><Badge variant="info">7</Badge></td></tr>
                <tr><td>PRs Generated</td><td>3</td></tr>
              </tbody>
            </Table>
          </CardBody>
        </Card>
      </Grid>
    </div>
  )
}

export default AgenticMapReducePage
