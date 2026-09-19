"use client"
import { Card, CardHeader, CardBody, Grid, Badge, Button, Text } from '@/components/ui'

function DeepWikiPage() {
  return (
    <div className="space-y-6 p-6">
      <h1 className="text-3xl font-bold">📚 DeepWiki</h1>
      <Grid cols={3} gap={4}>
        <Card>
          <CardHeader title="🏗️ Architecture" subtitle="Auto Diagrams" />
          <CardBody><Text>Auto-generated architecture diagrams for your repository.</Text></CardBody>
        </Card>
        <Card>
          <CardHeader title="📦 Module Summaries" subtitle="Auto Index" />
          <CardBody><Text>Summarized descriptions of each module with related files.</Text></CardBody>
        </Card>
        <Card>
          <CardHeader title="🔗 Dependency Map" subtitle="Relationships" />
          <CardBody><Text>Cross-file dependency maps and wiki links.</Text></CardBody>
        </Card>
      </Grid>
      <Card>
        <CardHeader title="Features" subtitle="What DeepWiki Does" />
        <CardBody>
          <ul className="space-y-2">
            <li>✅ Index entire repository and generate wiki</li>
            <li>✅ Generate architecture diagrams</li>
            <li>✅ Module summaries with related files</li>
            <li>✅ Search and export wiki</li>
            <li>✅ Update index for changed files</li>
          </ul>
          <Button variant="primary" className="mt-4">Index Repository</Button>
        </CardBody>
      </Card>
    </div>
  )
}
export default DeepWikiPage
