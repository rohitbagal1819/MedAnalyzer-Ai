const mongoose = require('mongoose');
const uri = 'mongodb+srv://rohitbagal1819_db_user:1W7Cc5XKOCyK3wTG@cluster0.zytbij1.mongodb.net/medanalyzer?retryWrites=true&w=majority';

mongoose.connect(uri)
  .then(() => {
    console.log('Successfully connected to MongoDB Atlas');
    process.exit(0);
  })
  .catch(err => {
    console.error('Failed to connect:', err.message);
    if (err.code) console.error('Code:', err.code);
    process.exit(1);
  });
