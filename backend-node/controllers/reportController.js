const axios = require('axios');
const fs = require('fs');
const os = require('os');
const path = require('path');
const FormData = require('form-data');
const Report = require('../models/Report');
const Patient = require('../models/Patient');

/**
 * POST /reports/upload — Upload report, send to Python AI, save results
 */
exports.uploadReport = async (req, res) => {
  try {
    if (!req.file) {
      req.session.error = 'No file uploaded. Please select a PDF or image file.';
      return res.redirect('/upload');
    }

    const filePath = req.file.path;
    const fileExt = path.extname(req.file.originalname).toLowerCase();
    const fileType = fileExt === '.pdf' ? 'pdf' : 'image';

    // Create report record in MongoDB with pending status
    const report = await Report.create({
      patientId: req.session.user.id,
      fileName: req.file.filename,
      fileType,
      uploadDate: new Date(),
      processingStatus: 'processing'
    });

    // Add report to patient's reports array
    await Patient.findByIdAndUpdate(req.session.user.id, {
      $push: { reports: report._id }
    });

    // Send file to Python AI microservice
    try {
      const formData = new FormData();
      formData.append('file', fs.createReadStream(filePath));
      formData.append('report_id', report._id.toString());
      formData.append('file_type', fileType);

      const aiResponse = await axios.post(
        `${process.env.PYTHON_AI_URL}/analyze`,
        formData,
        {
          headers: {
            ...formData.getHeaders()
          },
          timeout: 120000, // 2 min timeout for AI processing
          maxContentLength: Infinity,
          maxBodyLength: Infinity
        }
      );

      const result = aiResponse.data;

      // Update report with AI results
      await Report.findByIdAndUpdate(report._id, {
        reportDate: result.report_date ? new Date(result.report_date) : new Date(),
        reportType: result.report_type || 'Other',
        extractedData: {
          rawText: result.raw_text || '',
          labValues: result.lab_values || [],
          medications: result.medications || [],
          diseases: result.diseases || [],
          doctorName: result.doctor_name || '',
          hospitalName: result.hospital_name || ''
        },
        drugInteractions: result.drug_interactions || [],
        anomalies: result.anomalies || [],
        healthScore: result.health_score || 0,
        processingStatus: 'done'
      });

      // Update patient health score
      await Patient.findByIdAndUpdate(req.session.user.id, {
        healthScore: result.health_score || 0
      });

      req.session.success = 'Report uploaded and analyzed successfully!';
      return res.redirect('/dashboard');

    } catch (aiError) {
      console.error('AI Service error:', aiError.message);

      // If AI service fails, still mark report but with failed status
      await Report.findByIdAndUpdate(report._id, {
        processingStatus: 'failed',
        extractedData: {
          rawText: 'AI service unavailable. Please try again later.'
        }
      });

      req.session.error = 'Report uploaded but AI analysis failed. The AI service may be offline.';
      return res.redirect('/dashboard');
    }

  } catch (err) {
    console.error('Upload error:', err);
    req.session.error = 'Unable to upload report. Please try again.';
    return res.redirect('/upload');
  }
};

/**
 * POST /reports/delete/:id — Delete a report and its associated file
 */
exports.deleteReport = async (req, res) => {
  try {
    const report = await Report.findOne({ _id: req.params.id, patientId: req.session.user.id });
    if (!report) {
      req.session.error = 'Report not found or not authorized to delete.';
      return res.redirect('/dashboard');
    }

    // Remove file from filesystem if it exists
    if (report.fileName) {
      const filePath = path.join(os.tmpdir(), report.fileName);
      if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
      }
    }

    // Remove report reference from patient
    await Patient.findByIdAndUpdate(req.session.user.id, {
      $pull: { reports: report._id }
    });

    // Delete the report record
    await Report.findByIdAndDelete(report._id);

    req.session.success = 'Report deleted successfully.';
    res.redirect('/dashboard');
  } catch (err) {
    console.error('Delete report error:', err);
    req.session.error = 'Unable to delete report.';
    res.redirect('/dashboard');
  }
};

/**
 * GET /api/reports — Returns all reports for logged-in patient (JSON)
 */
exports.getReportsJSON = async (req, res) => {
  try {
    const reports = await Report.find({ patientId: req.session.user.id })
      .sort({ uploadDate: -1 });
    res.json({ success: true, reports });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
};

/**
 * GET /api/reports/:id — Returns single report data (JSON)
 */
exports.getReportJSON = async (req, res) => {
  try {
    const report = await Report.findOne({
      _id: req.params.id,
      patientId: req.session.user.id
    });
    if (!report) {
      return res.status(404).json({ success: false, error: 'Report not found' });
    }
    res.json({ success: true, report });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
};

/**
 * GET /api/health-score — Returns latest health score (JSON)
 */
exports.getHealthScoreJSON = async (req, res) => {
  try {
    const patient = await Patient.findById(req.session.user.id);
    res.json({
      success: true,
      healthScore: patient ? patient.healthScore : 0
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
};
