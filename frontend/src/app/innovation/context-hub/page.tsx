"use client"
import { Card, CardHeader, CardBody, Grid, Badge, Button, Text, Table } from '@/components/ui'

function ContextHubPage() {
  return (
    <div className="space-y-6 p-6">
      <h1 className="text-3xl font-bold">📋 Context Hub</h1>
      <Card>
        <CardHeader title="Agent Context Management" subtitle="Versioned, Tagged, Collaborative" />
        <CardBody>
          <Table>
            <thead><tr><th>Context</th><th>Version</th><th>Tags</th><th>Actions</th></tr></thead>
            <tbody>
              <tr><td>AGENTS.md</td><td>v3</td><td><Badge variant="info">project</Badge> <Badge variant="info">agents</Badge></td><td><Button variant="ghost" size="sm">Edit</Button></td></tr>
              <tr><td>Skills</td><td>v1</td><td><Badge variant="info">specialized</Badge></td><td><Button variant="ghost" size="sm">Edit</Button></td></tr>
              <tr><td>Policies</td><td>v2</td><td><Badge variant="danger">security</Badge></td><td><Button variant="ghost" size="sm">Edit</Button></td></tr>
              <tr><td>Examples</td><td>v1</td><td><Badge variant="info">project</Badge></td><td><Button variant="ghost" size="sm">Edit</Button></td></tr>
            </tbody>
          </Table>
          <Grid cols={3} gap={4} className="mt-4">
            <div className="p-4 rounded border"><h3 className="font-bold">📝 Versioning</h3><Text size="sm">Track all changes with version history</Text></div>
            <div className="p-4 rounded border"><h3 className="font-bold">🏷️ Tags</h3><Text size="sm">Tag versions as dev, staging, prod</Text></div>
            <div className="p-4 rounded border"><h3 className="font-bold">💬 Comments</h3><Text size="sm">Collaborative comments on context changes</Text></div>
          </Grid>
          <Button variant="primary" className="mt-4">Import AGENTS.md</Button>
        </CardBody>
      </Card>
    </div>
  )
}
export default ContextHubPage
