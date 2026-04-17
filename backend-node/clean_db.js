const mongoose = require('mongoose');
require('dotenv').config();

mongoose.connect(process.env.MONGODB_URI).then(async () => {
  const Report = require('./models/Report');
  const Patient = require('./models/Patient');
  
  const count = await Report.countDocuments();
  await Report.deleteMany({});
  await Patient.updateMany({}, { reports: [], healthScore: 0 });
  
  console.log(`Deleted ${count} old reports. Database is clean now.`);
  process.exit(0);
});
