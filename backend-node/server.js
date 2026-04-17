const app = require('./app');
const connectDB = require('./config/db');
const fs = require('fs');
const path = require('path');

// Ensure uploads directory exists
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

const PORT = process.env.PORT || 3000;

// Connect to MongoDB and start server
connectDB().then(() => {
  app.listen(PORT, () => {
    console.log('\n' +
      '==================================================\n' +
      '  MedAnalyzer AI - Node.js Backend\n' +
      '  Server running on http://localhost:' + PORT + '\n' +
      '  MongoDB connected\n' +
      '==================================================\n'
    );
  });
}).catch(err => {
  console.error('Failed to start server:', err);
  process.exit(1);
});
