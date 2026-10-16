#!/usr/bin/env ts-node
/**
 * Generate TypeScript types from FastAPI OpenAPI schema.
 *
 * Usage:
 *   1. Export OpenAPI schema: cd backend && python scripts/export-openapi.py ../openapi.json
 *   2. Generate types: cd frontend && npm run generate-types
 */
import { execSync } from "child_process";
import { existsSync, writeFileSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const OPENAPI_PATH = join(__dirname, "../../openapi.json");
const OUTPUT_DIR = join(__dirname, "../src/generated");

function main() {
  // Check if OpenAPI schema exists
  if (!existsSync(OPENAPI_PATH)) {
    console.error(`OpenAPI schema not found at ${OPENAPI_PATH}`);
    console.error("Run: cd backend && python scripts/export-openapi.py ../openapi.json");
    process.exit(1);
  }

  console.log("Generating TypeScript types from OpenAPI schema...");

  // Use openapi-typescript CLI to generate types
  const output = execSync(
    `npx openapi-typescript ${OPENAPI_PATH} -o ${join(OUTPUT_DIR, "api.ts")}`,
    { stdio: "inherit" }
  );

  console.log("Generated types written to frontend/src/generated/api.ts");
}

main();