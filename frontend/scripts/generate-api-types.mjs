import { execFileSync } from 'node:child_process'
import { mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { loadEnv } from 'vite'

const projectDirectory = process.cwd()
const environment = loadEnv('development', projectDirectory, '')
const apiBaseUrl =
  process.env.VITE_API_BASE_URL ??
  environment.VITE_API_BASE_URL ??
  'http://localhost:8000'
const openApiUrl = new URL('/openapi.json', apiBaseUrl)
const response = await fetch(openApiUrl)

if (!response.ok) {
  throw new Error(
    `Could not export OpenAPI from ${openApiUrl}: HTTP ${response.status}.`,
  )
}

const openApiDocument = await response.text()
const temporaryDirectory = await mkdtemp(join(tmpdir(), 'hisab-openapi-'))
const openApiPath = join(temporaryDirectory, 'openapi.json')
const outputPath = resolve(
  projectDirectory,
  'src',
  'lib',
  'api',
  'generated.ts',
)
const executable = join(
  projectDirectory,
  'node_modules',
  '.bin',
  process.platform === 'win32'
    ? 'openapi-typescript.cmd'
    : 'openapi-typescript',
)

try {
  await writeFile(openApiPath, openApiDocument, 'utf8')
  execFileSync(executable, [openApiPath, '-o', outputPath], {
    cwd: projectDirectory,
    shell: process.platform === 'win32',
    stdio: 'inherit',
  })
} finally {
  await rm(temporaryDirectory, { force: true, recursive: true })
}
