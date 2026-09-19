"use client"
import { Card, CardHeader, CardBody, Grid, Badge, Button, Text, Table } from '@/components/ui'

function AutoTriagePage() {
  return (
    <div className="space-y-6 p-6">
      <h1 className="text-3xl font-bold">🏷️ Auto-Triage System</h1>
      <Grid cols={3} gap={4}>
        <Card>
          <CardHeader title="P0 Critical" subtitle="Auto-Assigned" />
          <CardBody><Text>Emergency issues routed to critical agent.</Text><Badge variant="danger">AUTO</Badge></CardBody>
        </Card>
        <Card>
          <CardHeader title="P1 High" subtitle="Feature Agent" />
          <CardBody><Text>Important issues assigned to feature specialists.</Text><Badge variant="warning">AUTO</Badge></CardBody>
        </Card>
        <Card>
          <CardHeader title="P2 Medium" subtitle="General Queue" />
          <CardBody><Text>Standard issues in general agent queue.</Text><Badge variant="info">AUTO</Badge></CardBody>
        </Card>
      </Grid>
      <Card>
        <CardHeader title="Triage Statistics" subtitle="By Source" />
        <CardBody>
          <Table>
            <thead><tr><th>Source</th><th>Triaged</th><th>Auto-Started</th></tr></thead>
            <tbody>
              <tr><td>Slack</td><td>45</td><td>38</td></tr>
              <tr><td>Jira</td><td>32</td><td>29</td></tr>
              <tr><td>GitHub</td><td>67</td><td>61</td></tr>
              <tr><td>Linear</td><td>28</td><td>25</td></tr>
              <tr><td>Teams</td><td>15</td><td>12</td></tr>
            </tbody>
          </Table>
        </CardBody>
      </Card>
      <Card>
        <CardHeader title="Features" subtitle="Auto-Triage Capabilities" />
        <CardBody>
          <ul className="space-y-2">
            <li>✅ Automatically classify issues (bug, feature, security, etc.)</li>
            <li>✅ Assign priority levels (P0-P3)</li>
            <li>✅ Route to appropriate specialized agents</li>
            <li>✅ Track which surface spawned each session</li>
            <li>✅ Support for Slack, Jira, Linear, GitHub, Teams</li>
          </ul>
          <Button variant="primary" className="mt-4">Configure Auto-Triage</Button>
        </CardBody>
      </Card>
    </div>
  )
}
export default AutoTriagePage
