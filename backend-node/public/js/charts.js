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
 */
function initLabTrendChart(labData) {
  const ctx = document.getElementById('labTrendChart');
  if (!ctx || !labData || labData.length === 0) return;

  // Group lab values by test name
  const grouped = {};
  labData.forEach(item => {
    if (!grouped[item.testName]) {
      grouped[item.testName] = [];
    }
    grouped[item.testName].push({
      date: item.reportDate,
      value: parseFloat(item.value) || 0
    });
  });

  // Get unique test names (max 6 for readability)
  const testNames = Object.keys(grouped).slice(0, 6);

  // Color palette
  const colors = [
    { border: '#0d8fe0', bg: 'rgba(13, 143, 224, 0.1)' },
    { border: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.1)' },
    { border: '#10b981', bg: 'rgba(16, 185, 129, 0.1)' },
    { border: '#f59e0b', bg: 'rgba(245, 158, 11, 0.1)' },
    { border: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)' },
    { border: '#ec4899', bg: 'rgba(236, 72, 153, 0.1)' }
  ];

  // Build datasets
  const datasets = testNames.map((name, i) => {
    const colorPair = colors[i % colors.length];
    const dataPoints = grouped[name].sort((a, b) => new Date(a.date) - new Date(b.date));

    return {
      label: name,
      data: dataPoints.map(d => d.value),
      borderColor: colorPair.border,
      backgroundColor: colorPair.bg,
      borderWidth: 2,
      fill: true,
      tension: 0.4,
      pointBackgroundColor: colorPair.border,
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
      pointRadius: 4,
      pointHoverRadius: 6
    };
  });

  // Get all unique dates sorted
  const allDates = [...new Set(labData.map(d => d.reportDate))]
    .sort((a, b) => new Date(a) - new Date(b))
    .map(d => new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }));

  // Text color based on theme
  const textColor = getComputedStyle(document.documentElement)
    .getPropertyValue('--text-muted').trim() || '#94a3b8';
  const gridColor = getComputedStyle(document.documentElement)
    .getPropertyValue('--border-color').trim() || '#e2e8f0';

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: allDates.length > 0 ? allDates : ['Latest'],
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
          bodyFont: { family: "'Inter', sans-serif" }
        }
      },
      scales: {
        x: {
          grid: { color: gridColor, drawBorder: false },
          ticks: { color: textColor, font: { family: "'Inter', sans-serif", size: 11 } }
        },
        y: {
          grid: { color: gridColor, drawBorder: false },
          ticks: { color: textColor, font: { family: "'Inter', sans-serif", size: 11 } }
        }
      },
      animation: {
        duration: 1000,
        easing: 'easeOutQuart'
      }
    }
  });
}
