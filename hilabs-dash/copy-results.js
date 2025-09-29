const fs = require('fs');
const path = require('path');

// Function to copy directory recursively
function copyRecursiveSync(src, dest) {
  const exists = fs.existsSync(src);
  const stats = exists && fs.statSync(src);
  const isDirectory = exists && stats.isDirectory();
  
  if (isDirectory) {
    if (!fs.existsSync(dest)) {
      fs.mkdirSync(dest, { recursive: true });
    }
    fs.readdirSync(src).forEach(childItemName => {
      copyRecursiveSync(
        path.join(src, childItemName),
        path.join(dest, childItemName)
      );
    });
  } else {
    fs.copyFileSync(src, dest);
  }
}

// Source and destination paths
const backendResultsPath = path.join(__dirname, '..', 'Backend', 'results');
const publicBackendPath = path.join(__dirname, 'public', 'Backend', 'results');

// Create public/Backend directory if it doesn't exist
if (!fs.existsSync(path.join(__dirname, 'public', 'Backend'))) {
  fs.mkdirSync(path.join(__dirname, 'public', 'Backend'), { recursive: true });
}

// Copy results
console.log('Copying Backend results to public folder...');
try {
  copyRecursiveSync(backendResultsPath, publicBackendPath);
  console.log('✅ Successfully copied Backend results to public/Backend/results');
} catch (error) {
  console.error('❌ Error copying results:', error);
}
