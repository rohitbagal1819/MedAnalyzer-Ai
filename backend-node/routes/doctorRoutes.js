const express = require('express');
const router = express.Router();
const { isAuthenticated, isDoctor } = require('../middleware/authMiddleware');
const doctorController = require('../controllers/doctorController');

// All doctor routes require authentication + doctor role
router.use(isAuthenticated, isDoctor);

// GET /doctor/dashboard
router.get('/dashboard', doctorController.getDashboard);

// GET /doctor/patient/:id
router.get('/patient/:id', doctorController.getPatientDetail);

// POST /doctor/notes/:id
router.post('/notes/:id', doctorController.addNote);

// GET /doctor/notes/:id
router.get('/notes/:id', doctorController.getNotes);

// POST /doctor/link/:id
router.post('/link', doctorController.linkPatient);

module.exports = router;
