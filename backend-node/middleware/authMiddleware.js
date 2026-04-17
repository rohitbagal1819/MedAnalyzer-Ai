/**
 * Authentication & Authorization Middleware
 * Protects routes and enforces role-based access
 */

// Check if user is logged in
const isAuthenticated = (req, res, next) => {
  if (req.session && req.session.user) {
    return next();
  }
  req.session.returnTo = req.originalUrl;
  return res.redirect('/login');
};

// Check if user is a patient
const isPatient = (req, res, next) => {
  if (req.session && req.session.user && req.session.user.role === 'patient') {
    return next();
  }
  return res.status(403).render('error', {
    title: 'Access Denied',
    message: 'You do not have permission to access this page.',
    user: req.session.user || null
  });
};

// Check if user is a doctor
const isDoctor = (req, res, next) => {
  if (req.session && req.session.user && req.session.user.role === 'doctor') {
    return next();
  }
  return res.status(403).render('error', {
    title: 'Access Denied',
    message: 'You do not have permission to access this page.',
    user: req.session.user || null
  });
};

// Make user available in all EJS templates
const setLocals = (req, res, next) => {
  res.locals.user = req.session.user || null;
  res.locals.success = req.session.success || null;
  res.locals.error = req.session.error || null;
  // Clear flash messages after reading
  delete req.session.success;
  delete req.session.error;
  next();
};

module.exports = { isAuthenticated, isPatient, isDoctor, setLocals };
