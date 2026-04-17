const express = require('express');
const router = express.Router();
const { isAuthenticated, isPatient } = require('../middleware/authMiddleware');
const upload = require('../middleware/uploadMiddleware');
const reportController = require('../controllers/reportController');

// POST /reports/upload — Upload + analyze report
router.post('/upload', isAuthenticated, isPatient, upload.single('reportFile'), reportController.uploadReport);

// POST /reports/delete/:id — Delete a report
router.post('/delete/:id', isAuthenticated, isPatient, reportController.deleteReport);

// API Routes (JSON) — mounted at /api prefix via app.js
router.get('/reports', isAuthenticated, reportController.getReportsJSON);
router.get('/reports/:id', isAuthenticated, reportController.getReportJSON);
router.get('/health-score', isAuthenticated, reportController.getHealthScoreJSON);

module.exports = router;
