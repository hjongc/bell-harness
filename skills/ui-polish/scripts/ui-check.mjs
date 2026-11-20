#!/usr/bin/env node
// Prerequisite: Playwright resolvable from the project (npm i -D playwright, then npx playwright install chromium).
// Usage: node ui-check.mjs <url> [outDir] [widths, comma separated, default 1440,768,390]
import { mkdir } from "node:fs/promises";

let chromium;

try {
  ({ chromium } = await import("playwright"));
} catch {
  console.error("Playwright is required. Install it in the target project with: npm i -D playwright");
  process.exit(1);
}

const url = process.argv[2];
const outDir = process.argv[3] || "ui-check-artifacts";
const widths = (process.argv[4] || "1440,768,390").split(",").map(Number).filter(Boolean);

if (!url) {
  console.error("Usage: node ui-check.mjs <url> [outDir] [widths]");
  process.exit(1);
}

const viewports = widths.map((width) => ({ name: `w${width}`, width, height: width > 1000 ? 1000 : 900 }));

const browser = await chromium.launch();
const failures = [];

await mkdir(outDir, { recursive: true });

for (const viewport of viewports) {
  const page = await browser.newPage({ viewport });
  const consoleErrors = [];
  const failedRequests = [];

  page.on("console", (message) => {
    if (message.type() === "error") {
      consoleErrors.push(message.text());
    }
  });

  page.on("requestfailed", (request) => {
    failedRequests.push(`${request.method()} ${request.url()} ${request.failure()?.errorText || ""}`.trim());
  });

  await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
  await page.screenshot({
    path: `${outDir}/${viewport.name}.png`,
    fullPage: true,
  });

  if (consoleErrors.length) {
    failures.push(`${viewport.name}: console errors\n${consoleErrors.join("\n")}`);
  }

  if (failedRequests.length) {
    failures.push(`${viewport.name}: failed requests\n${failedRequests.join("\n")}`);
  }

  await page.close();
}

await browser.close();

if (failures.length) {
  console.error(failures.join("\n\n"));
  process.exit(1);
}

console.log(`Saved screenshots to ${outDir}`);
