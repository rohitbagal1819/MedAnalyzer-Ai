/**
 * MedAnalyzer AI — Chart.js Initialization
 * Health Score Donut Chart + Lab Value Trend Charts
 */

/**
 * Initialize Health Score Donut Chart
 */
function initHealthScoreChart(score) {
  const ctx = document.getElementById('healthScoreChart');
  if (!ctx) return;

  // Determine color based on score
  let color1, color2;
  if (score >= 70) {
    color1 = '#10b981';
    color2 = '#34d399';
  } else if (score >= 40) {
    color1 = '#f59e0b';
    color2 = '#fbbf24';
  } else {
    color1 = '#ef4444';
    color2 = '#f87171';
  }

  // Get CSS variable for background
  const bgColor = getComputedStyle(document.documentElement)
    .getPropertyValue('--border-color').trim() || '#e2e8f0';

  new Chart(ctx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [score, 100 - score],
        backgroundColor: [
          createGradient(ctx, color1, color2),
          bgColor
        ],
        borderWidth: 0,
        borderRadius: 8,
        spacing: 2
      }]
    },
    options: {
      cutout: '78%',
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false }
      },
      animation: {
        animateRotate: true,
        duration: 1500,
        easing: 'easeOutQuart'
      }
    }
  });
}

/**
 * Create a linear gradient for Chart.js
 */
function createGradient(ctx, color1, color2) {
  const canvas = ctx.getContext ? ctx : ctx.canvas;
  const context = canvas.getContext('2d');
  const gradient = context.createLinearGradient(0, 0, 0, canvas.height || 200);
  gradient.addColorStop(0, color1);
  gradient.addColorStop(1, color2);
  return gradient;
}

/**
 * Initialize Lab Value Trend Chart
 * Fixed: Properly aligns data points with global x-axis date labels
 */
function initLabTrendChart(labData) {
  const ctx = document.getElementById('labTrendChart');
  if (!ctx || !labData || labData.length === 0) return;

  // Group lab values by test name
  const grouped = {};
  labData.forEach(item => {
    const val = parseFloat(item.value);
    if (isNaN(val)) return; // skip non-numeric values

    if (!grouped[item.testName]) {
      grouped[item.testName] = {};
    }
    // Use the date string as key for alignment
    const dateKey = item.reportDate || 'Unknown';
    // If same test has multiple values on same date, keep the latest
    grouped[item.testName][dateKey] = val;
  });

  // Get unique test names (max 6 for readability)
  const testNames = Object.keys(grouped).slice(0, 6);

  if (testNames.length === 0) return; // No valid numeric data

  // Get all unique dates sorted chronologically
  const allDateKeys = [...new Set(labData.map(d => d.reportDate || 'Unknown'))]
    .sort((a, b) => {
      if (a === 'Unknown') return -1;
      if (b === 'Unknown') return 1;
      return new Date(a) - new Date(b);
    });

  // Format date labels for display
  const dateLabels = allDateKeys.map(d => {
    if (d === 'Unknown') return 'Latest';
    try {
      return new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: '2-digit' });
    } catch {
      return d;
    }
  });

  // Color palette
  const colors = [
    { border: '#0d8fe0', bg: 'rgba(13, 143, 224, 0.1)' },
    { border: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.1)' },
    { border: '#10b981', bg: 'rgba(16, 185, 129, 0.1)' },
    { border: '#f59e0b', bg: 'rgba(245, 158, 11, 0.1)' },
    { border: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)' },
    { border: '#ec4899', bg: 'rgba(236, 72, 153, 0.1)' }
  ];

  // Build datasets — each test's data is aligned to the global date labels
  const datasets = testNames.map((name, i) => {
    const colorPair = colors[i % colors.length];
    const testData = grouped[name]; // { dateKey: value }

    // Build data array aligned to allDateKeys, using null for missing dates
    const dataPoints = allDateKeys.map(dateKey => {
      return testData[dateKey] !== undefined ? testData[dateKey] : null;
    });

    return {
      label: name,
      data: dataPoints,
      borderColor: colorPair.border,
      backgroundColor: colorPair.bg,
      borderWidth: 2,
      fill: true,
      tension: 0.4,
      pointBackgroundColor: colorPair.border,
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
      pointRadius: allDateKeys.length === 1 ? 6 : 4, // Bigger dots for single point
      pointHoverRadius: 7,
      spanGaps: true // Connect lines across null gaps
    };
  });

  // Text color based on theme
  const textColor = getComputedStyle(document.documentElement)
    .getPropertyValue('--text-muted').trim() || '#94a3b8';
  const gridColor = getComputedStyle(document.documentElement)
    .getPropertyValue('--border-color').trim() || '#e2e8f0';

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: dateLabels.length > 0 ? dateLabels : ['Latest'],
      datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: textColor,
            font: { family: "'Inter', sans-serif", size: 12 },
            usePointStyle: true,
            pointStyle: 'circle',
            padding: 16
          }
        },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.9)',
          titleColor: '#fff',
          bodyColor: '#cbd5e1',
          borderColor: 'rgba(255,255,255,0.1)',
          borderWidth: 1,
          cornerRadius: 8,
          padding: 12,
          titleFont: { family: "'Inter', sans-serif", weight: 600 },
          bodyFont: { family: "'Inter', sans-serif" },
          callbacks: {
            label: function(context) {
              if (context.parsed.y === null) return null;
              return context.dataset.label + ': ' + context.parsed.y;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: gridColor, drawBorder: false },
          ticks: { color: textColor, font: { family: "'Inter', sans-serif", size: 11 } }
        },
        y: {
          grid: { color: gridColor, drawBorder: false },
          ticks: { color: textColor, font: { family: "'Inter', sans-serif", size: 11 } },
          beginAtZero: false
        }
      },
      animation: {
        duration: 1000,
        easing: 'easeOutQuart'
      }
    }
  });
}
