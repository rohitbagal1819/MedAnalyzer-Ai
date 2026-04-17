const Patient = require('../models/Patient');
const Report = require('../models/Report');

/**
 * GET /dashboard — Patient dashboard with health score, alerts, recent reports
 */
exports.getDashboard = async (req, res) => {
  try {
    const patient = await Patient.findById(req.session.user.id)
      .populate({
        path: 'reports',
        options: { sort: { createdAt: -1 } }
      });

    if (!patient) {
      return res.redirect('/login');
    }

    const reports = patient.reports || [];
    const latestReport = reports[0] || null;

    // Collect all anomalies across reports
    const allAnomalies = [];
    reports.forEach(r => {
      if (r.anomalies && r.anomalies.length > 0) {
        r.anomalies.forEach(a => {
          allAnomalies.push({ ...a.toObject(), reportDate: r.uploadDate });
        });
      }
    });

    // Collect all drug interactions
    const allDrugInteractions = [];
    reports.forEach(r => {
      if (r.drugInteractions && r.drugInteractions.length > 0) {
        r.drugInteractions.forEach(d => {
          allDrugInteractions.push({ ...d.toObject(), reportDate: r.uploadDate });
        });
      }
    });

    res.render('patient/dashboard', {
      title: 'Dashboard — MedAnalyzer AI',
      patient,
      reports,
      latestReport,
      allAnomalies,
      allDrugInteractions,
      healthScore: patient.healthScore || 0
    });

  } catch (err) {
    console.error('Dashboard error:', err);
    res.render('error', {
      title: 'Error',
      message: 'Unable to load dashboard.',
      user: req.session.user
    });
  }
};

/**
 * GET /upload — Upload form page
 */
exports.getUpload = (req, res) => {
  res.render('patient/upload', {
    title: 'Upload Report — MedAnalyzer AI'
  });
};

/**
 * GET /timeline — All reports in chronological order
 */
exports.getTimeline = async (req, res) => {
  try {
    const reports = await Report.find({ patientId: req.session.user.id })
      .sort({ uploadDate: -1 });

    res.render('patient/timeline', {
      title: 'Health Timeline — MedAnalyzer AI',
      reports
    });
  } catch (err) {
    console.error('Timeline error:', err);
    res.render('error', {
      title: 'Error',
      message: 'Unable to load timeline.',
      user: req.session.user
    });
  }
};

/**
 * GET /lab-results — All extracted lab values across all reports
 */
exports.getLabResults = async (req, res) => {
  try {
    const reports = await Report.find({ patientId: req.session.user.id })
      .sort({ uploadDate: -1 });

    const allLabValues = [];
    reports.forEach(r => {
      if (r.extractedData && r.extractedData.labValues) {
        r.extractedData.labValues.forEach(lv => {
          allLabValues.push({
            ...lv.toObject(),
            reportDate: r.uploadDate,
            reportType: r.reportType,
            reportId: r._id
          });
        });
      }
    });

    res.render('patient/labResults', {
      title: 'Lab Results — MedAnalyzer AI',
      labValues: allLabValues,
      reports
    });
  } catch (err) {
    console.error('Lab results error:', err);
    res.render('error', {
      title: 'Error',
      message: 'Unable to load lab results.',
      user: req.session.user
    });
  }
};

/**
 * GET /drug-interactions — All detected medications + interaction warnings
 */
exports.getDrugInteractions = async (req, res) => {
  try {
    const reports = await Report.find({ patientId: req.session.user.id })
      .sort({ uploadDate: -1 });

    const allMedications = [];
    const allInteractions = [];

    reports.forEach(r => {
      if (r.extractedData && r.extractedData.medications) {
        r.extractedData.medications.forEach(med => {
          allMedications.push({
            ...med.toObject(),
            reportDate: r.uploadDate
          });
        });
      }
      if (r.drugInteractions) {
        r.drugInteractions.forEach(di => {
          allInteractions.push({
            ...di.toObject(),
            reportDate: r.uploadDate
          });
        });
      }
    });

    res.render('patient/drugInteractions', {
      title: 'Drug Interactions — MedAnalyzer AI',
      user: req.session.user,
      medications: allMedications,
      interactions: allInteractions
    });
  } catch (err) {
    console.error('Drug interactions error:', err);
    res.render('error', {
      title: 'Error',
      message: 'Unable to load drug interactions.',
      user: req.session.user
    });
  }
};

/**
 * GET /summary — One-page printable doctor summary
 */
exports.getSummary = async (req, res) => {
  try {
    const patient = await Patient.findById(req.session.user.id);
    const reports = await Report.find({ patientId: req.session.user.id })
      .sort({ uploadDate: -1 });

    const latestReport = reports[0] || null;

    res.render('patient/summary', {
      title: 'Doctor Summary — MedAnalyzer AI',
      patient,
      reports,
      latestReport
    });
  } catch (err) {
    console.error('Summary error:', err);
    res.render('error', {
      title: 'Error',
      message: 'Unable to load summary.',
      user: req.session.user
    });
  }
};

/**
 * GET /reports/:id — Single report detail view
 */
exports.getReportDetail = async (req, res) => {
  try {
    const report = await Report.findOne({
      _id: req.params.id,
      patientId: req.session.user.id
    });

    if (!report) {
      return res.render('error', {
        title: 'Not Found',
        message: 'Report not found.',
        user: req.session.user
      });
    }

    res.render('patient/dashboard', {
      title: `Report Detail — MedAnalyzer AI`,
      patient: await Patient.findById(req.session.user.id),
      reports: [report],
      latestReport: report,
      allAnomalies: report.anomalies || [],
      allDrugInteractions: report.drugInteractions || [],
      healthScore: report.healthScore || 0
    });
  } catch (err) {
    console.error('Report detail error:', err);
    res.render('error', {
      title: 'Error',
      message: 'Unable to load report.',
      user: req.session.user
    });
  }
};
