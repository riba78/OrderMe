const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const svgBuffer = fs.readFileSync(path.join(__dirname, '../public/icon.svg'));

sharp(svgBuffer)
  .resize(1024, 1024)
  .png()
  .toFile(path.join(__dirname, '../public/icon.png'))
  .then(info => {
    console.log('Icon converted successfully:', info);
  })
  .catch(err => {
    console.error('Error converting icon:', err);
  }); 