const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function captureAndAnalyze() {
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
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
        
        // Capture just the symbol banks
        const symbolBanks = await page.$('.symbol-banks-container');
        if (symbolBanks) {
            await symbolBanks.screenshot({ path: 'symbol-banks.png' });
            console.log('Symbol banks screenshot saved as symbol-banks.png');
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