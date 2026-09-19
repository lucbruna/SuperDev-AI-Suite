"use client"
import { Card, CardHeader, CardBody, Grid, Badge, Button, Text, Table } from '@/components/ui'

function CursorRouterPage() {
  return (
    <div className="space-y-6 p-6">
      <h1 className="text-3xl font-bold">⚡ Cursor Router</h1>
      <Grid cols={3} gap={4}>
        <Card>
          <CardHeader title="🧠 Intelligence Mode" subtitle="Best Quality" />
          <CardBody><Text>Route to frontier models for best quality output.</Text></CardBody>
        </Card>
        <Card>
          <CardHeader title="⚖️ Balance Mode" subtitle="Quality/Cost Ratio" />
          <CardBody><Text>Optimal balance between quality and cost.</Text></CardBody>
        </Card>
        <Card>
          <CardHeader title="💰 Cost Mode" subtitle="Cheapest Viable" />
          <CardBody><Text>Route to cheapest models that still produce good results.</Text></CardBody>
        </Card>
      </Grid>
      <Card>
        <CardHeader title="Model Pool" subtitle="Available Models" />
        <CardBody>
          <Table>
            <thead><tr><th>Model</th><th>Provider</th><th>Cost/Token</th><th>Best For</th></tr></thead>
            <tbody>
              <tr><td>gpt-4o</td><td>OpenAI</td><td>$0.005</td><td>Complex, Reasoning</td></tr>
              <tr><td>gpt-4o-mini</td><td>OpenAI</td><td>$0.00015</td><td>Simple, UI</td></tr>
              <tr><td>claude-sonnet-4</td><td>Anthropic</td><td>$0.003</td><td>Complex, UI</td></tr>
              <tr><td>claude-haiku-4</td><td>Anthropic</td><td>$0.00025</td><td>Simple, UI</td></tr>
              <tr><td>deepseek-v3</td><td>DeepSeek</td><td>$0.00027</td><td>Complex, Reasoning</td></tr>
            </tbody>
          </Table>
        </CardBody>
      </Card>
    </div>
  )
}
export default CursorRouterPage
