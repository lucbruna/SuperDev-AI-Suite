"use client"
import { Card, CardHeader, CardBody, Grid, Badge, Button, Text } from '@/components/ui'

function SkillsPage() {
  return (
    <div className="space-y-6 p-6">
      <h1 className="text-3xl font-bold">🎯 Skills System</h1>
      <Grid cols={3} gap={4}>
        <Card>
          <CardHeader title="🏗️ Architecture" />
          <CardBody><Text>System design skills for complex projects.</Text><Badge variant="info">ACTIVE</Badge></CardBody>
        </Card>
        <Card>
          <CardHeader title="🔒 Security" />
          <CardBody><Text>Security audit and vulnerability skills.</Text><Badge variant="danger">ACTIVE</Badge></CardBody>
        </Card>
        <Card>
          <CardHeader title="🧪 Testing" />
          <CardBody><Text>Test-driven development skills.</Text><Badge variant="success">ACTIVE</Badge></CardBody>
        </Card>
        <Card>
          <CardHeader title="📖 Documentation" />
          <CardBody><Text>Auto-generate documentation skills.</Text><Badge variant="info">ACTIVE</Badge></CardBody>
        </Card>
        <Card>
          <CardHeader title="⚡ Performance" />
          <CardBody><Text>Performance optimization skills.</Text><Badge variant="warning">ACTIVE</Badge></CardBody>
        </Card>
        <Card>
          <CardHeader title="🔄 CI/CD" />
          <CardBody><Text>Pipeline and deployment skills.</Text><Badge variant="info">ACTIVE</Badge></CardBody>
        </Card>
      </Grid>
      <Card>
        <CardHeader title="How Skills Work" subtitle="Progressive Disclosure" />
        <CardBody>
          <Text>Skills are markdown files + scripts that improve agent performance.</Text>
          <ul className="mt-4 space-y-2">
            <li>✅ Dynamically loaded based on task description</li>
            <li>✅ Only relevant skills loaded (progressive disclosure)</li>
            <li>✅ Portable and shareable across teams</li>
            <li>✅ Versioned and tracked</li>
          </ul>
          <Button variant="primary" className="mt-4">Create New Skill</Button>
        </CardBody>
      </Card>
    </div>
  )
}
export default SkillsPage
