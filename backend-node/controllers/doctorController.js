const Doctor = require('../models/Doctor');
const Patient = require('../models/Patient');
const Report = require('../models/Report');

/**
 * GET /doctor/dashboard — List of linked patients with health scores
 */
exports.getDashboard = async (req, res) => {
  try {
    const doctor = await Doctor.findById(req.session.user.id)
      .populate('linkedPatients');

    if (!doctor) {
      return res.redirect('/login');
    }

    // Get health data for each linked patient
    const patientsWithData = [];
    for (const patient of doctor.linkedPatients) {
      const reportCount = await Report.countDocuments({ patientId: patient._id });
      patientsWithData.push({
        ...patient.toObject(),
        reportCount,
        healthScore: patient.healthScore || 0
      });
    }

    res.render('doctor/dashboard', {
      title: 'Doctor Dashboard — MedAnalyzer AI',
      doctor,
      patients: patientsWithData
    });

  } catch (err) {
    console.error('Doctor dashboard error:', err);
    res.render('error', {
      title: 'Error',
      message: 'Unable to load doctor dashboard.',
      user: req.session.user
    });
  }
};

/**
 * GET /doctor/patient/:id — Full health view of one patient
 */
exports.getPatientDetail = async (req, res) => {
  try {
    const doctor = await Doctor.findById(req.session.user.id);
    const patient = await Patient.findById(req.params.id);

    if (!patient) {
      return res.render('error', {
        title: 'Not Found',
        message: 'Patient not found.',
        user: req.session.user
      });
    }

    // Check if doctor is linked to this patient
    const isLinked = doctor.linkedPatients.some(
      p => p.toString() === patient._id.toString()
    );
    if (!isLinked) {
      return res.render('error', {
        title: 'Access Denied',
        message: 'You are not linked to this patient.',
        user: req.session.user
      });
    }

    const reports = await Report.find({ patientId: patient._id })
      .sort({ uploadDate: -1 });

    // Get consultation notes for this patient
    const notes = doctor.consultationNotes.filter(
      n => n.patientId && n.patientId.toString() === patient._id.toString()
    );

    res.render('doctor/patientDetail', {
      title: `${patient.name} — MedAnalyzer AI`,
      patient,
      reports,
      notes,
      doctor
    });

  } catch (err) {
    console.error('Patient detail error:', err);
    res.render('error', {
      title: 'Error',
      message: 'Unable to load patient detail.',
      user: req.session.user
    });
  }
};

/**
 * POST /doctor/notes/:id — Add consultation note for a patient
 */
exports.addNote = async (req, res) => {
  try {
    const { note } = req.body;
    const patientId = req.params.id;

    await Doctor.findByIdAndUpdate(req.session.user.id, {
      $push: {
        consultationNotes: {
          patientId,
          note,
          date: new Date()
        }
      }
    });

    req.session.success = 'Consultation note added successfully.';
    res.redirect(`/doctor/patient/${patientId}`);

  } catch (err) {
    console.error('Add note error:', err);
    req.session.error = 'Unable to add note.';
    res.redirect(`/doctor/patient/${req.params.id}`);
  }
};

/**
 * POST /doctor/link/:id — Link doctor to a patient by health ID
 */
exports.linkPatient = async (req, res) => {
  try {
    const { healthId } = req.body;

    const patient = await Patient.findOne({ healthId });
    if (!patient) {
      req.session.error = 'No patient found with that Health ID.';
      return res.redirect('/doctor/dashboard');
    }

    // Check if already linked
    const doctor = await Doctor.findById(req.session.user.id);
    const alreadyLinked = doctor.linkedPatients.some(
      p => p.toString() === patient._id.toString()
    );

    if (alreadyLinked) {
      req.session.error = 'Patient is already linked to your account.';
      return res.redirect('/doctor/dashboard');
    }

    // Link both ways
    await Doctor.findByIdAndUpdate(req.session.user.id, {
      $push: { linkedPatients: patient._id }
    });
    await Patient.findByIdAndUpdate(patient._id, {
      $push: { linkedDoctors: req.session.user.id }
    });

    req.session.success = `Successfully linked to patient ${patient.name}.`;
    res.redirect('/doctor/dashboard');

  } catch (err) {
    console.error('Link patient error:', err);
    req.session.error = 'Unable to link patient.';
    res.redirect('/doctor/dashboard');
  }
};

/**
 * GET /doctor/notes/:id — View consultation notes page
 */
exports.getNotes = async (req, res) => {
  try {
    const doctor = await Doctor.findById(req.session.user.id);
    const patient = await Patient.findById(req.params.id);

    if (!patient) {
      return res.render('error', {
        title: 'Not Found',
        message: 'Patient not found.',
        user: req.session.user
      });
    }

    const notes = doctor.consultationNotes.filter(
      n => n.patientId && n.patientId.toString() === patient._id.toString()
    ).sort((a, b) => b.date - a.date);

    res.render('doctor/notes', {
      title: `Notes for ${patient.name} — MedAnalyzer AI`,
      patient,
      notes,
      doctor
    });

  } catch (err) {
    console.error('Notes error:', err);
    res.render('error', {
      title: 'Error',
      message: 'Unable to load notes.',
      user: req.session.user
    });
  }
};
