/**
 * AVALIA SENAI - Interactive Engine
 * Handles Chart.js visualization, real-time rating feedback, and anonymous token tools.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Rating Form Live Calculations
  const evaluationForm = document.querySelector('#evaluation-form');
  if (evaluationForm) {
    const radioInputs = evaluationForm.querySelectorAll('input[type="radio"]');
    const liveScoreBadge = document.querySelector('#live-average-score');
    const totalQuestions = document.querySelectorAll('.criterion-item').length;
    const progressFill = document.querySelector('#eval-progress-fill');
    const progressText = document.querySelector('#eval-progress-text');

    function updateFormMetrics() {
      const checkedInputs = evaluationForm.querySelectorAll('input[type="radio"]:checked');
      const answeredCount = checkedInputs.length;
      
      let sum = 0;
      checkedInputs.forEach(input => {
        sum += parseInt(input.value, 10);
      });

      if (answeredCount > 0 && liveScoreBadge) {
        const avg = (sum / answeredCount).toFixed(1);
        liveScoreBadge.textContent = avg;
      }

      if (progressFill && progressText && totalQuestions > 0) {
        const percent = Math.round((answeredCount / totalQuestions) * 100);
        progressFill.style.width = `${percent}%`;
        progressText.textContent = `${answeredCount} de ${totalQuestions} respondidas (${percent}%)`;
      }
    }

    radioInputs.forEach(radio => {
      radio.addEventListener('change', updateFormMetrics);
    });

    updateFormMetrics();
  }

  // 2. Initialize Charts if canvas elements exist
  initTeacherCharts();
  initCoordinationCharts();
});

/**
 * Renders Radar and Distribution Charts for Teacher Dashboard
 */
function initTeacherCharts() {
  const radarCanvas = document.getElementById('teacherRadarChart');
  const barCanvas = document.getElementById('teacherBarChart');

  if (radarCanvas && window.Chart) {
    const labels = JSON.parse(radarCanvas.dataset.labels || '[]');
    const scores = JSON.parse(radarCanvas.dataset.scores || '[]');

    new Chart(radarCanvas, {
      type: 'radar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Desempenho Pedagógico (Escala 1 a 5)',
          data: scores,
          backgroundColor: 'rgba(15, 23, 42, 0.15)',
          borderColor: '#0f172a',
          borderWidth: 2,
          pointBackgroundColor: '#dc2626',
          pointBorderColor: '#ffffff',
          pointHoverRadius: 6,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            min: 0,
            max: 5,
            ticks: { stepSize: 1, backdropColor: 'transparent' },
            grid: { color: '#e2e8f0' },
            pointLabels: {
              font: { family: 'Manrope', size: 12, weight: '600' },
              color: '#475569'
            }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }

  if (barCanvas && window.Chart) {
    const distribution = JSON.parse(barCanvas.dataset.distribution || '[0,0,0,0,0]');

    new Chart(barCanvas, {
      type: 'bar',
      data: {
        labels: ['1 Estrela', '2 Estrelas', '3 Estrelas', '4 Estrelas', '5 Estrelas'],
        datasets: [{
          label: 'Quantidade de Avaliações',
          data: distribution,
          backgroundColor: [
            '#ef4444',
            '#f97316',
            '#eab308',
            '#3b82f6',
            '#10b981'
          ],
          borderRadius: 6,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0 },
            grid: { color: '#f1f5f9' }
          },
          x: {
            grid: { display: false }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }
}

/**
 * Renders Comparative Charts for Coordination Dashboard
 */
function initCoordinationCharts() {
  const comparisonCanvas = document.getElementById('coordinationComparisonChart');
  if (comparisonCanvas && window.Chart) {
    const teachers = JSON.parse(comparisonCanvas.dataset.teachers || '[]');
    const averages = JSON.parse(comparisonCanvas.dataset.averages || '[]');

    new Chart(comparisonCanvas, {
      type: 'bar',
      data: {
        labels: teachers,
        datasets: [{
          label: 'Média Geral de Satisfação Docente',
          data: averages,
          backgroundColor: '#0f172a',
          borderRadius: 6,
          borderSkipped: false,
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            min: 0,
            max: 5,
            ticks: { stepSize: 1 },
            grid: { color: '#f1f5f9' }
          },
          y: {
            grid: { display: false },
            ticks: {
              font: { family: 'Manrope', weight: '600' }
            }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }
}

/**
 * Copies anonymous receipt hash or token PIN to clipboard
 */
function copyToClipboard(text, btnElement) {
  navigator.clipboard.writeText(text).then(() => {
    const originalText = btnElement.innerText;
    btnElement.innerText = 'Copiado!';
    btnElement.style.backgroundColor = '#16a34a';
    btnElement.style.color = '#ffffff';
    setTimeout(() => {
      btnElement.innerText = originalText;
      btnElement.removeAttribute('style');
    }, 2000);
  });
}
