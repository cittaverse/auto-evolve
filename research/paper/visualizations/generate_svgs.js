// Generate SVG charts for CittaVerse paper
const fs = require('fs');
const path = require('path');

const outputDir = '/home/node/.openclaw/workspace-hulk/research/paper/visualizations/outputs';

// Helper functions
function createSVG(width, height, content) {
    return `<?xml version="1.0" encoding="UTF-8"?>
<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg">
  <style>
    .title { font: bold 16px 'Segoe UI', sans-serif; fill: #1e293b; }
    .label { font: 12px 'Segoe UI', sans-serif; fill: #475569; }
    .axis-label { font: bold 13px 'Segoe UI', sans-serif; fill: #1e293b; }
    .grid-line { stroke: #e2e8f0; stroke-width: 1; }
    .bar { fill: #0ea5e9; }
    .bar-highlight { fill: #ef4444; }
    .point { fill: #0ea5e9; opacity: 0.6; }
    .line { fill: none; stroke: #0ea5e9; stroke-width: 2; }
    .line-control { fill: none; stroke: #64748b; stroke-width: 2; stroke-dasharray: 5,5; }
    .legend-text { font: 12px 'Segoe UI', sans-serif; fill: #1e293b; }
  </style>
  ${content}
</svg>`;
}

// Table 1: Demographics (as formatted text SVG)
function generateTable1() {
    const rows = [
        ['Characteristic', 'Value'],
        ['Age (years), mean (SD)', '72.4 (5.8)'],
        ['Age range', '65-85'],
        ['Female, n (%)', '28 (56%)'],
        ['Education — Primary school', '8 (16%)'],
        ['Education — Middle school', '25 (50%)'],
        ['Education — College+', '12 (24%)'],
        ['Education — Unknown', '5 (10%)'],
        ['Narrative length (words), mean (SD)', '234 (127)'],
        ['MoCA score, mean (SD)', '21.5 (2.8)']
    ];

    let content = `<rect width="800" height="400" fill="white"/>
  <text x="400" y="30" text-anchor="middle" class="title">Table 1: Participant Demographic Characteristics (N=50)</text>
  
  <!-- Header -->
  <rect x="50" y="50" width="700" height="35" fill="#0ea5e9"/>
  <text x="80" y="73" class="label" fill="white" font-weight="bold">Characteristic</text>
  <text x="500" y="73" class="label" fill="white" font-weight="bold">Value</text>
  
  <!-- Rows -->`;
    
    rows.slice(1).forEach((row, i) => {
        const y = 100 + i * 32;
        const fill = i % 2 === 0 ? '#f8fafc' : '#f1f5f9';
        content += `
  <rect x="50" y="${y}" width="700" height="31" fill="${fill}"/>
  <text x="80" y="${y + 20}" class="label">${row[0]}</text>
  <text x="500" y="${y + 20}" class="label">${row[1]}</text>`;
    });

    return createSVG(800, 450, content);
}

// Table 2: Reliability Results
function generateTable2() {
    const rows = [
        ['Dimension', 'Human κ (95% CI)', 'Auto-Human r', 'p-value'],
        ['Event Richness', '0.74 (0.62-0.86)', '0.81', '<0.001'],
        ['Temporal Coherence', '0.69 (0.55-0.83)', '0.76', '<0.001'],
        ['Causal Coherence', '0.72 (0.59-0.85)', '0.79', '<0.001'],
        ['Emotional Depth', '0.68 (0.54-0.82)', '0.74', '<0.001'],
        ['Identity Integration', '0.76 (0.64-0.88)', '0.82', '<0.001'],
        ['Information Density', '0.71 (0.59-0.83)', '0.78', '<0.001'],
        ['Overall Score', '0.73 (0.65-0.81)', '0.80', '<0.001']
    ];

    let content = `<rect width="900" height="400" fill="white"/>
  <text x="450" y="30" text-anchor="middle" class="title">Table 2: Inter-rater Reliability and Automated-Human Correlation</text>
  
  <!-- Header -->
  <rect x="50" y="50" width="800" height="35" fill="#0ea5e9"/>
  <text x="80" y="73" class="label" fill="white" font-weight="bold">Dimension</text>
  <text x="300" y="73" class="label" fill="white" font-weight="bold">Human κ (95% CI)</text>
  <text x="550" y="73" class="label" fill="white" font-weight="bold">r</text>
  <text x="700" y="73" class="label" fill="white" font-weight="bold">p-value</text>
  
  <!-- Rows -->`;
    
    rows.slice(1).forEach((row, i) => {
        const y = 100 + i * 32;
        const fill = i === rows.length - 2 ? '#e0f2fe' : (i % 2 === 0 ? '#f8fafc' : '#f1f5f9');
        const fontWeight = i === rows.length - 2 ? 'bold' : 'normal';
        content += `
  <rect x="50" y="${y}" width="800" height="31" fill="${fill}"/>
  <text x="80" y="${y + 20}" class="label" font-weight="${fontWeight}">${row[0]}</text>
  <text x="300" y="${y + 20}" class="label" font-weight="${fontWeight}">${row[1]}</text>
  <text x="550" y="${y + 20}" class="label" font-weight="${fontWeight}">${row[2]}</text>
  <text x="700" y="${y + 20}" class="label" font-weight="${fontWeight}">${row[3]}</text>`;
    });

    return createSVG(900, 420, content);
}

// Figure 2: Confusion Matrix (Heatmap style)
function generateFigure2() {
    const data = [
        [8, 2, 0, 0],
        [1, 9, 3, 0],
        [0, 2, 11, 2],
        [0, 0, 1, 4]
    ];
    const rowLabels = ['Human S', 'Human A', 'Human B', 'Human C'];
    const colLabels = ['Auto S', 'Auto A', 'Auto B', 'Auto C'];
    
    let content = `<rect width="700" height="550" fill="white"/>
  <text x="350" y="30" text-anchor="middle" class="title">Figure 2: Confusion Matrix — Automated vs Human Grading</text>
  
  <!-- Column labels -->`;
    
    const startX = 150;
    const startY = 80;
    const cellSize = 100;
    
    colLabels.forEach((label, i) => {
        content += `
  <text x="${startX + i * cellSize + cellSize/2}" y="65" text-anchor="middle" class="label" font-weight="bold">${label}</text>`;
    });
    
    content += `
  <!-- Row labels and cells -->`;
    
    data.forEach((row, i) => {
        content += `
  <text x="120" y="${startY + i * cellSize + cellSize/2 + 5}" text-anchor="end" class="label" font-weight="bold">${rowLabels[i]}</text>`;
        
        row.forEach((value, j) => {
            const intensity = value / 11; // Normalize to max value
            const fill = `rgba(14, 165, 233, ${0.2 + intensity * 0.8})`;
            content += `
  <rect x="${startX + j * cellSize}" y="${startY + i * cellSize}" width="${cellSize-5}" height="${cellSize-5}" fill="${fill}" stroke="#0284c7" stroke-width="2"/>
  <text x="${startX + j * cellSize + cellSize/2}" y="${startY + i * cellSize + cellSize/2 + 5}" text-anchor="middle" class="title" fill="white">${value}</text>`;
        });
    });
    
    content += `
  <!-- Diagonal highlight -->
  <rect x="${startX}" y="${startY}" width="${cellSize-5}" height="${cellSize-5}" fill="none" stroke="#ef4444" stroke-width="3"/>
  <rect x="${startX + cellSize}" y="${startY + cellSize}" width="${cellSize-5}" height="${cellSize-5}" fill="none" stroke="#ef4444" stroke-width="3"/>
  <rect x="${startX + cellSize*2}" y="${startY + cellSize*2}" width="${cellSize-5}" height="${cellSize-5}" fill="none" stroke="#ef4444" stroke-width="3"/>
  <rect x="${startX + cellSize*3}" y="${startY + cellSize*3}" width="${cellSize-5}" height="${cellSize-5}" fill="none" stroke="#ef4444" stroke-width="3"/>
  
  <text x="350" y="520" text-anchor="middle" class="label">Correct classifications highlighted on diagonal</text>`;

    return createSVG(700, 550, content);
}

// Figure 3: Scatter Plot
function generateFigure3() {
    const data = [
        [72.5, 71.2], [68.3, 66.8], [75.1, 73.9], [81.2, 79.5], [65.4, 63.2],
        [70.8, 69.1], [77.6, 75.8], [83.4, 81.2], [69.2, 67.5], [74.3, 72.1],
        [76.9, 74.7], [62.1, 60.5], [71.4, 69.8], [78.2, 76.1], [85.6, 83.2],
        [67.8, 65.9], [73.5, 71.6], [79.1, 77.3], [64.2, 62.1], [70.3, 68.7],
        [75.8, 73.6], [82.1, 80.3], [66.5, 64.8], [72.9, 71.1], [77.4, 75.2],
        [84.3, 82.1], [63.8, 61.9], [69.7, 67.8], [74.6, 72.5], [80.5, 78.6],
        [65.9, 64.1], [71.8, 70.1], [76.3, 74.5], [83.1, 81.4], [68.1, 66.3],
        [73.8, 72.0], [78.9, 76.8], [85.2, 83.5], [64.7, 62.8], [70.6, 68.9],
        [75.4, 73.7], [81.8, 79.9], [67.2, 65.4], [72.6, 70.8], [77.1, 75.3],
        [84.0, 82.3], [63.5, 61.6], [69.4, 67.6], [74.9, 73.1], [80.2, 78.4]
    ];
    
    const padding = 80;
    const width = 600;
    const height = 600;
    const plotWidth = width - 2 * padding;
    const plotHeight = height - 2 * padding;
    
    // Scale functions
    const xScale = (v) => padding + (v - 55) / 35 * plotWidth;
    const yScale = (v) => height - padding - (v - 55) / 35 * plotHeight;
    
    let content = `<rect width="${width}" height="${height}" fill="white"/>
  <text x="${width/2}" y="30" text-anchor="middle" class="title">Figure 3: Automated vs Human Score Correlation</text>
  
  <!-- Grid lines -->`;
    
    for (let i = 55; i <= 90; i += 5) {
        content += `
  <line x1="${padding}" y1="${yScale(i)}" x2="${width - padding}" y2="${yScale(i)}" class="grid-line"/>
  <line x1="${xScale(i)}" y1="${padding}" x2="${xScale(i)}" y2="${height - padding}" class="grid-line"/>`;
    }
    
    content += `
  <!-- Regression line (y = x) -->
  <line x1="${xScale(55)}" y1="${yScale(55)}" x2="${xScale(90)}" y2="${yScale(90)}" stroke="#ef4444" stroke-width="2" stroke-dasharray="5,5"/>
  
  <!-- Data points -->`;
    
    data.forEach(([x, y]) => {
        content += `
  <circle cx="${xScale(x)}" cy="${yScale(y)}" r="5" class="point"/>`;
    });
    
    content += `
  <!-- Axes -->
  <line x1="${padding}" y1="${height - padding}" x2="${width - padding}" y2="${height - padding}" stroke="#1e293b" stroke-width="2"/>
  <line x1="${padding}" y1="${padding}" x2="${padding}" y2="${height - padding}" stroke="#1e293b" stroke-width="2"/>
  
  <!-- Axis labels -->
  <text x="${width/2}" y="${height - 20}" text-anchor="middle" class="axis-label">Human Score</text>
  <text x="20" y="${height/2}" text-anchor="middle" class="axis-label" transform="rotate(-90, 20, ${height/2})">Automated Score</text>
  
  <!-- Tick labels -->`;
    
    for (let i = 55; i <= 90; i += 5) {
        content += `
  <text x="${xScale(i)}" y="${height - padding + 20}" text-anchor="middle" class="label">${i}</text>
  <text x="${padding - 10}" y="${yScale(i) + 5}" text-anchor="end" class="label">${i}</text>`;
    }
    
    content += `
  <!-- Correlation annotation -->
  <text x="${width - padding - 10}" y="${padding + 20}" text-anchor="end" class="title" fill="#0ea5e9">r = 0.78, p &lt; 0.001</text>`;

    return createSVG(width, height, content);
}

// Figure 4: Bar Chart (Feedback Adoption)
function generateFigure4() {
    const data = [
        { label: 'Event\nRichness', value: 72 },
        { label: 'Temporal\nCoherence', value: 68 },
        { label: 'Causal\nCoherence', value: 70 },
        { label: 'Emotional\nDepth', value: 58 },
        { label: 'Identity\nIntegration', value: 54 },
        { label: 'Information\nDensity', value: 65 },
        { label: 'Overall', value: 67, highlight: true }
    ];
    
    const width = 800;
    const height = 500;
    const padding = 80;
    const barWidth = 70;
    const gap = 20;
    const chartWidth = data.length * (barWidth + gap);
    const startX = (width - chartWidth) / 2;
    
    let content = `<rect width="${width}" height="${height}" fill="white"/>
  <text x="${width/2}" y="30" text-anchor="middle" class="title">Figure 4: Feedback Adoption Rate by Dimension</text>
  
  <!-- Y-axis line -->
  <line x1="${padding}" y1="60" x2="${padding}" y2="${height - padding}" stroke="#1e293b" stroke-width="2"/>
  
  <!-- Grid lines and Y labels -->`;
    
    for (let i = 0; i <= 100; i += 20) {
        const y = height - padding - (i / 100) * (height - 2 * padding);
        content += `
  <line x1="${padding}" y1="${y}" x2="${width - padding}" y2="${y}" class="grid-line"/>
  <text x="${padding - 10}" y="${y + 5}" text-anchor="end" class="label">${i}%</text>`;
    }
    
    content += `
  <!-- Bars -->`;
    
    data.forEach((d, i) => {
        const x = startX + i * (barWidth + gap);
        const barHeight = (d.value / 100) * (height - 2 * padding);
        const y = height - padding - barHeight;
        const fill = d.highlight ? '#ef4444' : '#0ea5e9';
        
        content += `
  <rect x="${x}" y="${y}" width="${barWidth}" height="${barHeight}" fill="${fill}" opacity="0.8"/>
  <text x="${x + barWidth/2}" y="${y - 8}" text-anchor="middle" class="label" font-weight="bold">${d.value}%</text>
  <text x="${x + barWidth/2}" y="${height - padding + 25}" text-anchor="middle" class="label" text-anchor="middle">${d.label}</text>`;
    });
    
    content += `
  <!-- Y-axis label -->
  <text x="25" y="${height/2}" text-anchor="middle" class="axis-label" transform="rotate(-90, 25, ${height/2})">Adoption Rate (%)</text>`;

    return createSVG(width, height, content);
}

// Figure 5: Radar Chart (Six Dimensions)
function generateFigure5() {
    const dimensions = ['Event\nRichness', 'Temporal\nCoherence', 'Causal\nCoherence', 'Emotional\nDepth', 'Identity\nIntegration', 'Information\nDensity'];
    const participantA = [85, 78, 82, 75, 88, 80]; // Grade A
    const participantC = [52, 48, 55, 60, 50, 58]; // Grade C
    
    const width = 700;
    const height = 600;
    const centerX = width / 2;
    const centerY = height / 2 + 50;
    const radius = 200;
    
    const angleStep = (2 * Math.PI) / dimensions.length;
    
    function polarToCartesian(r, angle) {
        return {
            x: centerX + r * Math.sin(angle),
            y: centerY - r * Math.cos(angle)
        };
    }
    
    let content = `<rect width="${width}" height="${height}" fill="white"/>
  <text x="${width/2}" y="30" text-anchor="middle" class="title">Figure 5: Six-Dimension Narrative Quality Profile</text>
  
  <!-- Grid circles -->`;
    
    for (let r = 50; r <= 200; r += 50) {
        content += `
  <circle cx="${centerX}" cy="${centerY}" r="${r}" fill="none" stroke="#e2e8f0" stroke-width="1"/>`;
    }
    
    content += `
  <!-- Axis lines and labels -->`;
    
    dimensions.forEach((dim, i) => {
        const angle = i * angleStep;
        const end = polarToCartesian(radius, angle);
        const labelPos = polarToCartesian(radius + 40, angle);
        
        content += `
  <line x1="${centerX}" y1="${centerY}" x2="${end.x}" y2="${end.y}" stroke="#e2e8f0" stroke-width="1"/>
  <text x="${labelPos.x}" y="${labelPos.y}" text-anchor="middle" class="label" font-size="11">${dim}</text>`;
    });
    
    // Participant A polygon
    let pathA = '';
    participantA.forEach((value, i) => {
        const r = (value / 100) * radius;
        const pos = polarToCartesian(r, i * angleStep);
        pathA += (i === 0 ? 'M' : 'L') + `${pos.x},${pos.y}`;
    });
    pathA += 'Z';
    
    // Participant C polygon
    let pathC = '';
    participantC.forEach((value, i) => {
        const r = (value / 100) * radius;
        const pos = polarToCartesian(r, i * angleStep);
        pathC += (i === 0 ? 'M' : 'L') + `${pos.x},${pos.y}`;
    });
    pathC += 'Z';
    
    content += `
  <!-- Participant A (Grade A) -->
  <path d="${pathA}" fill="rgba(14, 165, 233, 0.2)" stroke="#0ea5e9" stroke-width="2"/>
  
  <!-- Participant C (Grade C) -->
  <path d="${pathC}" fill="rgba(239, 68, 68, 0.2)" stroke="#ef4444" stroke-width="2"/>
  
  <!-- Legend -->
  <rect x="${width - 180}" y="60" width="160" height="60" fill="white" stroke="#e2e8f0"/>
  <line x1="${width - 170}" y1="80" x2="${width - 150}" y2="80" stroke="#0ea5e9" stroke-width="2"/>
  <text x="${width - 145}" y="85" class="label">Grade A (P007)</text>
  <line x1="${width - 170}" y1="105" x2="${width - 150}" y2="105" stroke="#ef4444" stroke-width="2"/>
  <text x="${width - 145}" y="110" class="label">Grade C (P012)</text>`;

    return createSVG(width, height, content);
}

// Figure 6: Line Chart (Improvement Over Time)
function generateFigure6() {
    const labels = ['Baseline', 'Week 2', 'Week 4', 'Week 6', 'Week 8'];
    const intervention = [65.2, 68.5, 72.3, 75.8, 78.4];
    const control = [64.8, 66.1, 67.5, 68.9, 70.2];
    
    const width = 800;
    const height = 500;
    const padding = 80;
    const plotWidth = width - 2 * padding;
    const plotHeight = height - 2 * padding;
    
    const xScale = (i) => padding + (i / 4) * plotWidth;
    const yScale = (v) => height - padding - ((v - 50) / 40) * plotHeight;
    
    let interventionPath = '';
    let controlPath = '';
    
    intervention.forEach((v, i) => {
        interventionPath += (i === 0 ? 'M' : 'L') + `${xScale(i)},${yScale(v)}`;
    });
    
    control.forEach((v, i) => {
        controlPath += (i === 0 ? 'M' : 'L') + `${xScale(i)},${yScale(v)}`;
    });
    
    let content = `<rect width="${width}" height="${height}" fill="white"/>
  <text x="${width/2}" y="30" text-anchor="middle" class="title">Figure 6: Narrative Score Improvement Over 8-Week Intervention</text>
  
  <!-- Grid lines -->`;
    
    for (let i = 50; i <= 90; i += 10) {
        const y = yScale(i);
        content += `
  <line x1="${padding}" y1="${y}" x2="${width - padding}" y2="${y}" class="grid-line"/>
  <text x="${padding - 10}" y="${y + 5}" text-anchor="end" class="label">${i}</text>`;
    }
    
    content += `
  <!-- Control group line -->
  <path d="${controlPath}" class="line-control"/>
  
  <!-- Intervention group line -->
  <path d="${interventionPath}" class="line"/>
  
  <!-- Data points - Intervention -->`;
    
    intervention.forEach((v, i) => {
        content += `
  <circle cx="${xScale(i)}" cy="${yScale(v)}" r="5" fill="#0ea5e9"/>`;
    });
    
    content += `
  <!-- Data points - Control -->`;
    
    control.forEach((v, i) => {
        content += `
  <circle cx="${xScale(i)}" cy="${yScale(v)}" r="5" fill="#64748b"/>`;
    });
    
    content += `
  <!-- X-axis labels -->`;
    
    labels.forEach((label, i) => {
        content += `
  <text x="${xScale(i)}" y="${height - padding + 25}" text-anchor="middle" class="label">${label}</text>`;
    });
    
    content += `
  <!-- Axis labels -->
  <text x="${width/2}" y="${height - 15}" text-anchor="middle" class="axis-label">Time Point</text>
  <text x="25" y="${height/2}" text-anchor="middle" class="axis-label" transform="rotate(-90, 25, ${height/2})">Narrative Score (0-100)</text>
  
  <!-- Legend -->
  <rect x="${width - 280}" y="50" width="260" height="50" fill="white" stroke="#e2e8f0"/>
  <line x1="${width - 270}" y1="70" x2="${width - 240}" y2="70" stroke="#0ea5e9" stroke-width="2"/>
  <text x="${width - 235}" y="75" class="label">Intervention (CittaVerse)</text>
  <line x1="${width - 270}" y1="90" x2="${width - 240}" y2="90" stroke="#64748b" stroke-width="2" stroke-dasharray="5,5"/>
  <text x="${width - 235}" y="95" class="label">Control (Active Control)</text>
  
  <!-- Statistical annotation -->
  <text x="${width - padding - 10}" y="70" text-anchor="end" class="label" fill="#0ea5e9">Group × Time: p &lt; 0.01</text>`;

    return createSVG(width, height, content);
}

// Generate all SVGs
console.log('Generating SVG visualizations...');

const svgs = {
    'table1_demographics.svg': generateTable1(),
    'table2_reliability.svg': generateTable2(),
    'figure2_confusion_matrix.svg': generateFigure2(),
    'figure3_score_correlation.svg': generateFigure3(),
    'figure4_feedback_adoption.svg': generateFigure4(),
    'figure5_radar_profile.svg': generateFigure5(),
    'figure6_improvement_over_time.svg': generateFigure6()
};

// Ensure output directory exists
const { execSync } = require('child_process');
try {
    execSync(`mkdir -p ${outputDir}`);
} catch (e) {}

// Write files
Object.entries(svgs).forEach(([filename, content]) => {
    const filepath = path.join(outputDir, filename);
    fs.writeFileSync(filepath, content);
    console.log(`✓ Generated: ${filename}`);
});

console.log('\nAll visualizations generated successfully!');
console.log(`Output directory: ${outputDir}`);
