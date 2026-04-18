const app = require('../app');
const connectDB = require('../config/db');

// Initialize database connection for the serverless function
// Mongoose will buffer queries until the connection is established.
connectDB();

// Export the Express app for Vercel to use as a serverless function
module.exports = app;
