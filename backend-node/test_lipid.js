const fs = require('fs');
const axios = require('axios');
const FormData = require('form-data');
const path = require('path');

async function test() {
  // Test with the first file (the lipid profile one)
  const filePath = path.join(__dirname, 'uploads', 'report-1776444704491-802827094.png');
  console.log('Testing with lipid profile image...');
  
  const form = new FormData();
  form.append('file', fs.createReadStream(filePath));
  form.append('report_id', 'test_lipid');
  form.append('file_type', 'image');
  
  try {
    const res = await axios.post('http://localhost:5001/analyze', form, {
      headers: form.getHeaders(),
      timeout: 60000
    });
    
    const data = res.data;
    console.log('Success:', data.success);
    console.log('Lab Values:', (data.lab_values || []).length);
    data.lab_values.forEach(lv => console.log(`  ${lv.testName}: ${lv.value} ${lv.unit} [${lv.status}]`));
    console.log('Medications:', (data.medications || []).length);
    data.medications.forEach(m => console.log(`  ${m.name} ${m.dosage}`));
    console.log('Drug Interactions:', (data.drug_interactions || []).length);
    data.drug_interactions.forEach(di => console.log(`  ${di.drug1} <-> ${di.drug2}: ${di.severity}`));
    console.log('Anomalies:', (data.anomalies || []).length);
    data.anomalies.forEach(a => console.log(`  ${a.parameter}: ${a.severity}`));
  } catch (err) {
    console.error('ERROR:', err.message);
  }
}
test();
