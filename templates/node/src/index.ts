import express from 'express'
import cors from 'cors'
import dotenv from 'dotenv'
import { healthRouter } from './routes/health'

dotenv.config()

const app = express()
const PORT = process.env.PORT || 3000

app.use(cors())
app.use(express.json())

app.use('/api', healthRouter)

app.get('/', (_req, res) => {
  res.json({ message: '{{project_name}} API', version: '0.1.0' })
})

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`)
})
