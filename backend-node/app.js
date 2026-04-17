require('dotenv').config();
const express = require('express');
const path = require('path');
const session = require('express-session');
const MongoStore = require('connect-mongo');
const { setLocals } = require('./middleware/authMiddleware');

const app = express();

// ─── View Engine ────────────────────────────────────────
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// ─── Body Parsers ───────────────────────────────────────
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// ─── Static Files ───────────────────────────────────────
app.use(express.static(path.join(__dirname, 'public')));
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// ─── Session ────────────────────────────────────────────
app.use(session({
  secret: process.env.SESSION_SECRET || 'fallback_secret_key',
  resave: false,
  saveUninitialized: false,
  store: MongoStore.create({
    mongoUrl: process.env.MONGODB_URI,
    collectionName: 'sessions',
    ttl: 24 * 60 * 60 // 1 day
  }),
  cookie: {
    maxAge: 24 * 60 * 60 * 1000, // 1 day
    httpOnly: true,
    secure: false // set to true in production with HTTPS
  }
}));

// ─── Template Locals ────────────────────────────────────
app.use(setLocals);

// ─── Routes ─────────────────────────────────────────────
const authRoutes = require('./routes/authRoutes');
const patientRoutes = require('./routes/patientRoutes');
const doctorRoutes = require('./routes/doctorRoutes');
const reportRoutes = require('./routes/reportRoutes');

// Landing page
app.get('/', (req, res) => {
  res.render('index', {
    title: 'MedAnalyzer AI — Medical Report Analyzer'
  });
});

// Auth routes (no prefix)
app.use('/', authRoutes);

// Doctor routes (prefixed with /doctor)
app.use('/doctor', doctorRoutes);

// Patient routes (no prefix, protected)
app.use('/', patientRoutes);

// Report routes
app.use('/reports', reportRoutes);
// API routes (JSON endpoints like /api/reports, /api/health-score)
app.use('/api', reportRoutes);

// ─── 404 Handler ────────────────────────────────────────
app.use((req, res) => {
  res.status(404).render('error', {
    title: 'Page Not Found',
    message: 'The page you are looking for does not exist.',
    user: req.session ? req.session.user : null
  });
});

// ─── Error Handler ──────────────────────────────────────
app.use((err, req, res, next) => {
  console.error('Server error:', err);
  res.status(500).render('error', {
    title: 'Server Error',
    message: 'Something went wrong on our end. Please try again.',
    user: req.session ? req.session.user : null
  });
});

module.exports = app;
