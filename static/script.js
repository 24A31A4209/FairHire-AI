"use strict";

const state = {
    files: [],
    chart: null
};

const JD_EXAMPLES = {
    ml: "Looking for a Machine Learning Engineer with 2+ years of experience. Required: Python, TensorFlow, Scikit-learn, SQL.",
    de: "Data Engineer needed. Skills: Python, SQL, Apache Spark, Kafka, Airflow, AWS, Docker."
};

document.addEventListener("DOMContentLoaded", () => {
    initDropZone();
    initExampleButtons();
    
    const form = document.getElementById("uploadForm");
    if (form) form.addEventListener("submit", runAnalysis);

    const jdInput = document.getElementById("jobDescription");
    if (jdInput) jdInput.addEventListener("input", validateForm);

    // Initial render check
    if (document.getElementById('rankingChart')) {
        renderDashboardChart();
    }
});

/* --- File Management Logic --- */
function initDropZone() {
    const dropZone = document.getElementById("dropZone");
    const input = document.getElementById("resumeInput");
    if (!dropZone || !input) return;

    dropZone.addEventListener("click", () => input.click());

    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("border-[#00ffa3]");
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("border-[#00ffa3]");
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("border-[#00ffa3]");
        const droppedFiles = Array.from(e.dataTransfer.files).filter(f => f.name.endsWith(".pdf") || f.name.endsWith(".txt"));
        addFiles(droppedFiles);
    });

    input.addEventListener("change", () => {
        addFiles(Array.from(input.files));
        input.value = ""; 
    });
}

function addFiles(newFiles) {
    newFiles.forEach(file => {
        if (!state.files.find(f => f.name === file.name)) state.files.push(file);
    });
    renderFileList();
    validateForm();
}

function removeFile(name) {
    state.files = state.files.filter(f => f.name !== name);
    renderFileList();
    validateForm();
}
window.removeFile = removeFile;

function renderFileList() {
    const list = document.getElementById("fileList");
    if (!list) return;
    list.innerHTML = state.files.map(file => `
        <div class="flex items-center justify-between p-2 bg-white/5 border border-white/10 rounded font-mono text-[10px] animate-fade-in">
            <span class="truncate">📄 ${file.name}</span>
            <button type="button" onclick="removeFile('${file.name}')" class="text-[#00ffa3] hover:text-white transition-colors">✕</button>
        </div>
    `).join("");
}

function validateForm() {
    const btn = document.getElementById("analyzeBtn");
    const role = document.getElementById("roleInput")?.value.trim();
    const jd = document.getElementById("jobDescription")?.value.trim();
    if (btn) btn.disabled = !(state.files.length > 0 && jd?.length > 10 && role?.length > 2);
}

function initExampleButtons() {
    document.querySelectorAll(".example-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.getElementById("jobDescription").value = JD_EXAMPLES[btn.dataset.jd];
            validateForm();
        });
    });
}

/* --- Improved Analysis Flow --- */
async function runAnalysis(e) {
     if (e) e.preventDefault(); 
    const loading = document.getElementById("loadingState");
    if (loading) loading.classList.remove("hidden");

    const formData = new FormData();
    formData.append('role', document.getElementById("roleInput").value);
    formData.append('requirements', document.getElementById("jobDescription").value);
    state.files.forEach(file => formData.append('resumes', file));

    try {
        const response = await fetch('/', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const html = await response.text();
            
            // THE FIX: Completely replace the document content
            document.open();
            document.write(html);
            document.close();
            
            // Re-trigger the chart since the page just "reloaded"
            if (window.renderDashboardChart) {
                window.renderDashboardChart();
            }
        } else {
            const errorText = await response.text();
            alert("Analysis failed: " + errorText);
        }
    } catch (error) {
        console.error("Fetch Error:", error);
    } finally {
        if (loading) loading.classList.add("hidden");
    }
}


/* --- Dashboard Chart Engine --- */
function renderDashboardChart() {
    const chartElement = document.getElementById('rankingChart');
    if (!chartElement) return;

    const ctx = chartElement.getContext('2d');
    const labels = window.chartLabels || [];
    const scores = window.chartScores || [];

    if (state.chart) state.chart.destroy();

    // Create Gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, '#00ffa3');   // Neon Green
    gradient.addColorStop(1, 'rgba(0, 255, 163, 0.1)'); 

    state.chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Audit Match Score',
                data: scores,
                backgroundColor: gradient,
                borderColor: '#00ffa3',
                borderWidth: 2,
                borderRadius: 8,
                hoverBackgroundColor: '#bcfe2f', // Cyber Lime on hover
                barPercentage: 0.5,
                categoryPercentage: 0.8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 2000,
                easing: 'easeOutQuart'
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { 
                        color: 'rgba(255, 255, 255, 0.05)',
                        drawBorder: false 
                    },
                    ticks: { 
                        color: '#64748b',
                        font: { family: 'JetBrains Mono', size: 10 },
                        callback: value => value + '%'
                    }
                },
                x: {
                    grid: { display: false },
                    ticks: { 
                        color: '#f8fafc',
                        font: { family: 'JetBrains Mono', size: 9 }
                    }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#0a0a0f',
                    titleFont: { family: 'Syne', size: 13 },
                    bodyFont: { family: 'JetBrains Mono', size: 12 },
                    borderColor: 'rgba(0, 255, 163, 0.3)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: (context) => ` MERIT_SCORE: ${context.raw}%`
                    }
                }
            }
        }
    });
}

// Global exposure for the force-render call in HTML
window.renderDashboardChart = renderDashboardChart;