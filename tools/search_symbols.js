#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const INDEX_PATH = path.join(ROOT, 'symbols-index.json');
const PREVIEW_DIR = path.join(ROOT, 'symbols');

function usage() {
  console.log('Usage: node tools/search_symbols.js <keyword1> [keyword2] ...');
  console.log(' - Case-insensitive substring match against labels');
  process.exit(1);
}

const terms = process.argv.slice(2).map(s => s.toLowerCase());
if (terms.length === 0) usage();

if (!fs.existsSync(INDEX_PATH)) {
  console.error('symbols-index.json not found. Run: npm run index:symbols');
  process.exit(2);
}

const idx = JSON.parse(fs.readFileSync(INDEX_PATH, 'utf8'));
const matches = idx.symbols.filter(s => {
  const label = (s.label || '').toLowerCase();
  return terms.every(t => label.includes(t));
});

if (matches.length === 0) {
  console.log('No matches.');
  process.exit(0);
}

matches.forEach((m, i) => {
  const file = path.join(PREVIEW_DIR, `${m.slug}.svg`);
  console.log(`${i+1}. ${m.label}`);
  console.log(`   slug: ${m.slug}`);
  console.log(`   preview: ${file}`);
  console.log(`   panel@ (${m.panel.x}, ${m.panel.y}) size ${m.panel.width}x${m.panel.height}`);
});
