const mongoose = require('mongoose');

const reportSchema = new mongoose.Schema({
  patientId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Patient',
    required: true
  },
  fileName: {
    type: String,
    required: true
  },
  fileType: {
    type: String,
    enum: ['pdf', 'image'],
    required: true
  },
  uploadDate: {
    type: Date,
    default: Date.now
  },
  reportDate: {
    type: Date
  },
  reportType: {
    type: String,
    enum: ['Blood Test', 'X-Ray', 'Prescription', 'Discharge Summary', 'Other'],
    default: 'Other'
  },
  extractedData: {
    rawText: { type: String, default: '' },
    labValues: [{
      testName: String,
      value: String,
      unit: String,
      normalRange: String,
      status: {
        type: String,
        enum: ['normal', 'high', 'low', 'critical']
      }
    }],
    medications: [{
      name: String,
      dosage: String,
      frequency: String
    }],
    diseases: [String],
    doctorName: { type: String, default: '' },
    hospitalName: { type: String, default: '' }
  },
  drugInteractions: [{
    drug1: String,
    drug2: String,
    severity: {
      type: String,
      enum: ['mild', 'moderate', 'severe']
    },
    description: String
  }],
  anomalies: [{
    parameter: String,
    value: String,
    severity: String,
    message: String
  }],
  healthScore: {
    type: Number,
    default: 0,
    min: 0,
    max: 100
  },
  processingStatus: {
    type: String,
    enum: ['pending', 'processing', 'done', 'failed'],
    default: 'pending'
  }
}, {
  timestamps: true
});

module.exports = mongoose.model('Report', reportSchema);
