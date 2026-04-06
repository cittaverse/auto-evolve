const { execSync } = require('child_process');
const path = require('path');

const scriptPath = path.join(__dirname, 'benchmark_eval.py');
const csvPath = path.join(__dirname, 'mock_samples_v2.csv');
const outputPath = path.join(__dirname, 'results_v3.json');

try {
    const result = execSync(`python3 "${scriptPath}" -b "${csvPath}" -o "${outputPath}"`, {
        encoding: 'utf-8',
        cwd: __dirname,
        timeout: 60000
    });
    console.log(result);
    console.log('Benchmark completed successfully!');
} catch (error) {
    console.error('Error running benchmark:');
    console.error(error.stdout || error.stderr || error.message);
    process.exit(1);
}
