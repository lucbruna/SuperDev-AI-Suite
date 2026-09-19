"use client"
import { Card, CardHeader, CardBody, Grid, Badge, Button, Text, Table } from '@/components/ui'

function AgentEnginePage() {
  return (
    <div className="space-y-6 p-6">
      <h1 className="text-3xl font-bold">🔄 LangSmith Engine</h1>
      <Grid cols={3} gap={4}>
        <Card>
          <CardHeader title="🔴 Critical" subtitle="Needs Attention" />
          <CardBody><Text>2 issues requiring immediate action.</Text><Badge variant="danger">OPEN</Badge></CardBody>
        </Card>
        <Card>
          <CardHeader title="🟡 Monitoring" subtitle="In Progress" />
          <CardBody><Text>5 issues being investigated.</Text><Badge variant="warning">INVESTIGATING</Badge></CardBody>
        </Card>
        <Card>
          <CardHeader title="✅ Resolved" subtitle="Fixed" />
          <CardBody><Text>12 issues have been resolved.</Text><Badge variant="success">RESOLVED</Badge></CardBody>
        </Card>
      </Grid>
      <Card>
        <CardHeader title="Engine Pipeline" subtitle="Watch → Cluster → Diagnose → Fix" />
        <CardBody>
          <Grid cols={4} gap={4}>
            {['Watch Traces', 'Cluster Failures', 'Diagnose Root Cause', 'Propose Fixes'].map((step, i) => (
              <div key={i} className="p-4 rounded-lg border text-center">
                <Badge variant="primary">Step {i + 1}</Badge>
                <h3 className="font-bold mt-2">{step}</h3>
              </div>
            ))}
          </Grid>
          <Button variant="primary" className="mt-4">Run Autonomous Improvement</Button>
        </CardBody>
      </Card>
    </div>
  )
}
export default AgentEnginePage
