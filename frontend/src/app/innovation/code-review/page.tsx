"use client"
import { Card, CardHeader, CardBody, Grid, Badge, Button, Text, Table } from '@/components/ui'

function MultiAgentReviewPage() {
  return (
    <div className="space-y-6 p-6">
      <h1 className="text-3xl font-bold">👥 Multi-Agent Code Review</h1>
      <Grid cols={2} gap={4}>
        <Card>
          <CardHeader title="Review Statistics" subtitle="Performance Metrics" />
          <CardBody>
            <Table>
              <tbody>
                <tr><td>PRs Reviewed</td><td>89</td></tr>
                <tr><td>Substantive Reviews</td><td><Badge variant="danger">54%</Badge></td></tr>
                <tr><td>Before Multi-Agent</td><td>16%</td></tr>
                <tr><td>Avg Findings/PR</td><td>7.5 (large PRs)</td></tr>
                <tr><td>Agents Dispatched</td><td>142</td></tr>
              </tbody>
            </Table>
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="Severity Breakdown" subtitle="By Impact" />
          <CardBody>
            <Badge variant="danger">Blockers: 3</Badge>
            <Badge variant="warning">High: 12</Badge>
            <Badge variant="info">Medium: 28</Badge>
            <Badge variant="success">Low: 45</Badge>
            <Button variant="primary" className="mt-3">Review PR</Button>
          </CardBody>
        </Card>
      </Grid>
      <Card>
        <CardHeader title="How It Works" subtitle="Agent Teams per PR" />
        <CardBody>
          <Grid cols={3} gap={4}>
            <div className="p-4 rounded border"><h3 className="font-bold">1. Dispatch</h3><Text size="sm">Agent teams dispatched in parallel</Text></div>
            <div className="p-4 rounded border"><h3 className="font-bold">2. Find Bugs</h3><Text size="sm">Each agent searches for different issues</Text></div>
            <div className="p-4 rounded border"><h3 className="font-bold">3. Verify & Rank</h3><Text size="sm">False positives filtered, ranked by severity</Text></div>
          </Grid>
          <Text className="mt-3">Large PRs (&gt;1000 lines) get 8 agents. Small PRs (&lt;50 lines) get 1 agent.</Text>
        </CardBody>
      </Card>
    </div>
  )
}
export default MultiAgentReviewPage
