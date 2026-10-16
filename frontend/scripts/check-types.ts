#!/usr/bin/env ts-node
/**
 * Check if generated TypeScript types are up to date with the OpenAPI schema.
 *
 * Usage:
 *   cd frontend && npm run check-types
 *
 * Exit codes:
 *   0 - types are up to date
 *   1 - types are stale or missing
 */
import { execSync } from "child_process";
import { existsSync, readFileSync, writeFileSync, mkdtempSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";
import { tmpdir } from "os";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const OPENAPI_PATH = join(__dirname, "../../openapi.json");
const GENERATED_PATH = join(__dirname, "../src/generated/api.ts");

function main() {
  // Check if OpenAPI schema exists
  if (!existsSync(OPENAPI_PATH)) {
    console.error("❌ OpenAPI schema not found at", OPENAPI_PATH);
    console.error("   Run: cd backend && python scripts/export-openapi.py ../openapi.json");
    process.exit(1);
  }

  // Check if generated types exist
  if (!existsSync(GENERATED_PATH)) {
    console.error("❌ Generated types not found at", GENERATED_PATH);
    console.error("   Run: cd frontend && npm run generate-types");
    process.exit(1);
  }

  // Generate fresh types to a temp file
  const tempDir = mkdtempSync(join(tmpdir(), "woosarr-types-"));
  const tempFile = join(tempDir, "api.ts");

  try {
    execSync(`npx openapi-typescript ${OPENAPI_PATH} -o ${tempFile}`, {
      stdio: "pipe",
    });

    // Compare generated types
    const existing = readFileSync(GENERATED_PATH, "utf-8");
    const fresh = readFileSync(tempFile, "utf-8");

    if (existing === fresh) {
      console.log("✅ Generated types are up to date");
      process.exit(0);
    } else {
      console.error("❌ Generated types are stale");
      console.error("   Run: cd frontend && npm run generate-types");
      process.exit(1);
    }
  } catch (error) {
    console.error("❌ Failed to generate types for comparison");
    process.exit(1);
  }
}

main();