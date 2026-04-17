const express = require('express');
const router = express.Router();
const { body } = require('express-validator');
const authController = require('../controllers/authController');

// GET /login
router.get('/login', authController.getLogin);

// POST /login
router.post('/login', [
  body('email').isEmail().withMessage('Please enter a valid email'),
  body('password').notEmpty().withMessage('Password is required'),
  body('role').isIn(['patient', 'doctor']).withMessage('Please select a role')
], authController.postLogin);

// GET /register
router.get('/register', authController.getRegister);

// POST /register
router.post('/register', [
  body('name').trim().notEmpty().withMessage('Name is required'),
  body('email').isEmail().withMessage('Please enter a valid email'),
  body('password').isLength({ min: 6 }).withMessage('Password must be at least 6 characters'),
  body('role').isIn(['patient', 'doctor']).withMessage('Please select a role')
], authController.postRegister);

// GET /logout
router.get('/logout', authController.getLogout);

module.exports = router;
