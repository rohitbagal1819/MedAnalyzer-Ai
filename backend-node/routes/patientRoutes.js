const express = require('express');
const router = express.Router();
const { isAuthenticated, isPatient } = require('../middleware/authMiddleware');
const patientController = require('../controllers/patientController');

// All patient routes require authentication + patient role
router.use(isAuthenticated, isPatient);

// GET /dashboard
router.get('/dashboard', patientController.getDashboard);

// GET /upload
router.get('/upload', patientController.getUpload);

// GET /timeline
router.get('/timeline', patientController.getTimeline);

// GET /lab-results
router.get('/lab-results', patientController.getLabResults);

// GET /drug-interactions
router.get('/drug-interactions', patientController.getDrugInteractions);

// GET /summary
router.get('/summary', patientController.getSummary);

// GET /reports/:id
router.get('/reports/:id', patientController.getReportDetail);

module.exports = router;
