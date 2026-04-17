const bcrypt = require('bcryptjs');
const { validationResult } = require('express-validator');
const Patient = require('../models/Patient');
const Doctor = require('../models/Doctor');

/**
 * GET /login — Render login page
 */
exports.getLogin = (req, res) => {
  res.render('auth/login', {
    title: 'Login — MedAnalyzer AI',
    errors: [],
    formData: {}
  });
};

/**
 * POST /login — Authenticate user
 */
exports.postLogin = async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.render('auth/login', {
      title: 'Login — MedAnalyzer AI',
      errors: errors.array(),
      formData: req.body
    });
  }

  const { email, password, role } = req.body;

  try {
    let user;
    if (role === 'doctor') {
      user = await Doctor.findOne({ email });
    } else {
      user = await Patient.findOne({ email });
    }

    if (!user) {
      return res.render('auth/login', {
        title: 'Login — MedAnalyzer AI',
        errors: [{ msg: 'Invalid email or password' }],
        formData: req.body
      });
    }

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.render('auth/login', {
        title: 'Login — MedAnalyzer AI',
        errors: [{ msg: 'Invalid email or password' }],
        formData: req.body
      });
    }

    // Set session
    req.session.user = {
      id: user._id,
      name: user.name,
      email: user.email,
      role: user.role || role
    };

    // Redirect by role
    if (role === 'doctor') {
      return res.redirect('/doctor/dashboard');
    }
    return res.redirect('/dashboard');

  } catch (err) {
    console.error('Login error:', err);
    return res.render('auth/login', {
      title: 'Login — MedAnalyzer AI',
      errors: [{ msg: 'Server error. Please try again.' }],
      formData: req.body
    });
  }
};

/**
 * GET /register — Render register page
 */
exports.getRegister = (req, res) => {
  res.render('auth/register', {
    title: 'Register — MedAnalyzer AI',
    errors: [],
    formData: {}
  });
};

/**
 * POST /register — Create new user
 */
exports.postRegister = async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.render('auth/register', {
      title: 'Register — MedAnalyzer AI',
      errors: errors.array(),
      formData: req.body
    });
  }

  const { name, email, password, role, specialization, licenseNumber, age, gender, bloodGroup, healthId } = req.body;

  try {
    // Check if user already exists
    const existingPatient = await Patient.findOne({ email });
    const existingDoctor = await Doctor.findOne({ email });
    if (existingPatient || existingDoctor) {
      return res.render('auth/register', {
        title: 'Register — MedAnalyzer AI',
        errors: [{ msg: 'An account with this email already exists' }],
        formData: req.body
      });
    }

    // Hash password
    const salt = await bcrypt.genSalt(12);
    const hashedPassword = await bcrypt.hash(password, salt);

    if (role === 'doctor') {
      await Doctor.create({
        name,
        email,
        password: hashedPassword,
        role: 'doctor',
        specialization: specialization || '',
        licenseNumber: licenseNumber || ''
      });
    } else {
      await Patient.create({
        name,
        email,
        password: hashedPassword,
        role: 'patient',
        age: age || undefined,
        gender: gender || '',
        bloodGroup: bloodGroup || '',
        healthId: healthId || ''
      });
    }

    req.session.success = 'Registration successful! Please log in.';
    return res.redirect('/login');

  } catch (err) {
    console.error('Register error:', err);
    return res.render('auth/register', {
      title: 'Register — MedAnalyzer AI',
      errors: [{ msg: 'Server error. Please try again.' }],
      formData: req.body
    });
  }
};

/**
 * GET /logout — Destroy session
 */
exports.getLogout = (req, res) => {
  req.session.destroy((err) => {
    if (err) console.error('Logout error:', err);
    res.redirect('/login');
  });
};
