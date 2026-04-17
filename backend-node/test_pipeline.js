// Full end-to-end test: Send an uploaded image to Python AI and check response
const fs = require('fs');
const axios = require('axios');
const FormData = require('form-data');
const path = require('path');

async function test() {
  const uploadsDir = path.join(__dirname, 'uploads');
  const files = fs.readdirSync(uploadsDir);
  
  if (files.length === 0) {
    console.log('No files in uploads folder!');
    return;
  }
  
  const filePath = path.join(uploadsDir, files[files.length - 1]);
  console.log('Testing with file:', files[files.length - 1]);
  
  const form = new FormData();
  form.append('file', fs.createReadStream(filePath));
  form.append('report_id', 'test123');
  form.append('file_type', 'image');
  
  try {
    const res = await axios.post('http://localhost:5001/analyze', form, {
      headers: form.getHeaders(),
      timeout: 60000
    });
    
    const data = res.data;
    console.log('\n=== PYTHON AI RESPONSE ===');
    console.log('Success:', data.success);
    console.log('Report type:', data.report_type);
    console.log('Doctor:', data.doctor_name);
    console.log('Hospital:', data.hospital_name);
    console.log('Health score:', data.health_score);
    
    console.log('\n--- Lab Values (' + (data.lab_values || []).length + ') ---');
    (data.lab_values || []).forEach(lv => {
      console.log(`  ${lv.testName}: ${lv.value} ${lv.unit} [${lv.status}]`);
    });
    
    console.log('\n--- Medications (' + (data.medications || []).length + ') ---');
    (data.medications || []).forEach(m => {
      console.log(`  ${m.name} ${m.dosage} - ${m.frequency}`);
    });
    
    console.log('\n--- Drug Interactions (' + (data.drug_interactions || []).length + ') ---');
    (data.drug_interactions || []).forEach(di => {
      console.log(`  ${di.drug1} <-> ${di.drug2}: ${di.severity} - ${di.description}`);
    });
    
    console.log('\n--- Anomalies (' + (data.anomalies || []).length + ') ---');
    (data.anomalies || []).forEach(a => {
      console.log(`  ${a.parameter}: ${a.value} [${a.severity}] - ${a.message}`);
    });
    
    console.log('\n--- Diseases (' + (data.diseases || []).length + ') ---');
    (data.diseases || []).forEach(d => console.log(`  ${d}`));
    
    console.log('\n--- Raw Text (first 300 chars) ---');
    console.log((data.raw_text || '').substring(0, 300));
    
  } catch (err) {
    console.error('ERROR:', err.message);
    if (err.response) console.error('Response:', err.response.data);
  }
}

test();
