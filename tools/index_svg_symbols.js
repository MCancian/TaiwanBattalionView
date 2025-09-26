/*
 Index labeled symbol panels from Military_Symbology_Guide.svg.
 - Scans for <g transform="translate(x,y)"> groups that contain a 600x400 panel
   (identified by the border path d="M 5,5 H 595 V 395 H 5 Z").
 - Extracts the English label (from the group's <switch> with text[systemLanguage="en"],
   or falls back to the default text in the switch).
 - Writes symbols-index.json with slug, label, bbox (x,y,width,height), and section hints.
 - Optionally exports a preview SVG for each symbol into symbols/ (excluding the label text).
*/

const fs = require('fs');
const path = require('path');
const cheerio = require('cheerio');

const ROOT = path.resolve(__dirname, '..');
const SVG_PATH = path.join(ROOT, 'Military_Symbology_Guide.svg');
const OUT_DIR = ROOT;
const PREVIEW_DIR = path.join(ROOT, 'symbols');
const INDEX_PATH = path.join(ROOT, 'symbols-index.json');

function slugify(label) {
  return label
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .substring(0, 80);
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function readSvg() {
  if (!fs.existsSync(SVG_PATH)) {
    console.error(`SVG not found at ${SVG_PATH}`);
    process.exit(1);
  }
  const xml = fs.readFileSync(SVG_PATH, 'utf8');
  return cheerio.load(xml, { xmlMode: true, decodeEntities: false });
}

function extractEnglishLabel($, $switch) {
  if (!$switch || $switch.length === 0) return null;
  // Prefer explicit English text
  let $en = $switch.find('text[systemLanguage="en"]').first();
  if ($en.length === 0) {
    // Fall back to the last text in the switch (often default)
    const $texts = $switch.find('text');
    if ($texts.length > 0) {
      $en = $texts.last();
    }
  }
  if ($en && $en.length > 0) {
    const tspans = [];
    $en.find('tspan').each((i, el) => {
      const t = $(el).text().trim();
      if (t) tspans.push(t);
    });
    const line = tspans.join(' ').replace(/\s+/g, ' ').trim();
    return line || null;
  }
  return null;
}

function parseTranslate(transform) {
  // Example: translate(200,200)
  const m = /translate\(([-0-9.]+),\s*([-0-9.]+)\)/.exec(transform || '');
  if (!m) return { x: 0, y: 0 };
  return { x: parseFloat(m[1]), y: parseFloat(m[2]) };
}

function groupHasPanelBorder($, $g) {
  // Identify by the exact panel path d
  const has = $g.find('path[d="M 5,5 H 595 V 395 H 5 Z"]').length > 0;
  return has;
}

function cloneGroupContentWithoutLabels($, $g) {
  // Clone children except the labeling <switch> (which contains description text below the panel)
  const children = [];
  $g.children().each((i, el) => {
  const $el = $(el);
    if ($el[0].tagName === 'switch') return; // skip labels
    // Skip <text> elements (defensive)
    if ($el[0].tagName === 'text') return;
    children.push($.html($el));
  });
  return children.join('\n');
}

function main() {
  const $ = readSvg();
  ensureDir(PREVIEW_DIR);

  const results = [];

  // Walk all groups, collect those that look like symbol panels
  $('g[transform]').each((i, el) => {
    const $g = $(el);
    if (!groupHasPanelBorder($, $g)) return;

    const transform = $g.attr('transform');
    const { x, y } = parseTranslate(transform);

    // Extract label from the nearest <switch> child in the panel group
    const $switch = $g.children('switch').first();
  const label = extractEnglishLabel($, $switch) || 'unlabeled';
    const slug = slugify(label);

    const entry = {
      slug,
      label,
      transform: { x, y },
      bbox: { x: x + 5, y: y + 5, width: 590, height: 390 }, // inner area borders
      panel: { x, y, width: 600, height: 400 },
    };
    results.push(entry);

    // Export preview SVG (panel content without label text)
    const inner = cloneGroupContentWithoutLabels($, $g);
    const svg = `<?xml version="1.0" encoding="UTF-8"?>\n` +
      `<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">\n` +
      `${inner}\n` +
      `</svg>\n`;
    const outPath = path.join(PREVIEW_DIR, `${slug || 'symbol_' + i}.svg`);
    fs.writeFileSync(outPath, svg, 'utf8');
  });

  // Write index
  fs.writeFileSync(INDEX_PATH, JSON.stringify({
    source: path.basename(SVG_PATH),
    total: results.length,
    generatedAt: new Date().toISOString(),
    symbols: results
  }, null, 2));

  console.log(`Indexed ${results.length} symbol panels.`);
  console.log(`- Index: ${INDEX_PATH}`);
  console.log(`- Previews: ${PREVIEW_DIR}/*.svg`);
}

main();
