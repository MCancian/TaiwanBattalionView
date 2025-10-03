const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function captureAndAnalyze() {
    const launchOptions = {
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    };

    // Prefer explicit executable path via env, else ask Puppeteer to use system Chrome
    if (process.env.PUPPETEER_EXECUTABLE_PATH) {
        launchOptions.executablePath = process.env.PUPPETEER_EXECUTABLE_PATH;
    } else {
        // Use Chrome channel (stable) if available on this system
        launchOptions.channel = 'chrome';
    }

    const browser = await puppeteer.launch(launchOptions);
    
    try {
        const page = await browser.newPage();
        await page.setViewport({ width: 1920, height: 1080 });
        
        // Load the HTML file
        const filePath = 'file:///' + path.resolve('taiwan-military-map-enhanced.html').replace(/\\/g, '/');
        console.log('Loading:', filePath);
        await page.goto(filePath, { waitUntil: 'networkidle0' });
        
        // Wait for map to load
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Take screenshots of different parts
        await page.screenshot({ path: 'full-map.png', fullPage: false });
        console.log('Full map screenshot saved as full-map.png');
        
        // Capture the symbols panel (tabs + banks)
        const symbolPanel = await page.$('.symbol-panel');
        if (symbolPanel) {
            await symbolPanel.screenshot({ path: 'symbol-panel.png' });
            console.log('Symbol panel screenshot saved as symbol-panel.png');
        }
        
        // Capture the legend
        const legend = await page.$('.legend');
        if (legend) {
            await legend.screenshot({ path: 'legend.png' });
            console.log('Legend screenshot saved as legend.png');
        }
        
    } catch (error) {
        console.error('Error:', error);
    } finally {
        await browser.close();
    }
}

captureAndAnalyze();