// Initialize Lucide icons
lucide.createIcons();

// DOM Elements
const submissionView = document.getElementById('submissionView');
const scanningView = document.getElementById('scanningView');
const resultsView = document.getElementById('resultsView');
const analyzeBtn = document.getElementById('analyzeBtn');
const newAnalysisBtn = document.getElementById('newAnalysis');
const emailText = document.getElementById('emailText');
const charCount = document.getElementById('charCount');
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const removeFile = document.getElementById('removeFile');
const browseBtn = document.getElementById('browseBtn');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const riskArc = document.getElementById('riskArc');
const riskScore = document.getElementById('riskScore');
const severityBadge = document.getElementById('severityBadge');
const confidenceBar = document.getElementById('confidenceBar');
const confidenceText = document.getElementById('confidenceText');
const analysisTime = document.getElementById('analysisTime');

// State
let currentFile = null;
let scanningSteps = ['step1', 'step2', 'step3', 'step4', 'step5'];
let currentStep = 0;

// Character counter
emailText.addEventListener('input', () => {
    charCount.textContent = `${emailText.value.length} characters`;
    updateAnalyzeButton();
});

// File handling
dropZone.addEventListener('click', () => fileInput.click());
browseBtn.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('border-cyan-500');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('border-cyan-500');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('border-cyan-500');
    handleFileUpload(e.dataTransfer.files[0]);
});

fileInput.addEventListener('change', (e) => {
    handleFileUpload(e.target.files[0]);
});

removeFile.addEventListener('click', (e) => {
    e.stopPropagation();
    currentFile = null;
    fileInput.value = '';
    fileInfo.classList.add('hidden');
    dropZone.classList.remove('hidden');
    updateAnalyzeButton();
});

function handleFileUpload(file) {
    if (file && file.name.endsWith('.eml')) {
        currentFile = file;
        fileName.textContent = file.name;
        fileSize.textContent = `${(file.size / 1024).toFixed(2)} KB`;
        fileInfo.classList.remove('hidden');
        dropZone.classList.add('hidden');
        updateAnalyzeButton();
    } else {
        alert('Please upload a valid .eml file');
    }
}

function updateAnalyzeButton() {
    analyzeBtn.disabled = !(emailText.value.trim() || currentFile);
}

updateAnalyzeButton();

// ANALYZE BUTTON
analyzeBtn.addEventListener('click', async () => {

    submissionView.classList.add('hidden');
    scanningView.classList.remove('hidden');
    resultsView.classList.add('hidden');

    resetScanningState();

    try {
        let response;

        if (currentFile) {
            const formData = new FormData();
            formData.append("file", currentFile);

            response = await fetch("http://127.0.0.1:8000/analyze-file", {
                method: "POST",
                body: formData
            });

        } else {
            response = await fetch("http://127.0.0.1:8000/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ raw_email: emailText.value })
            });
        }

        if (!response.ok) throw new Error();

        const data = await response.json();
        startScanningAnimation(data);

    } catch {
        alert("Backend not running. Start FastAPI server.");
        submissionView.classList.remove('hidden');
        scanningView.classList.add('hidden');
    }
});

function resetScanningState() {
    currentStep = 0;
    scanningSteps.forEach(stepId => {
        const step = document.getElementById(stepId);
        step.classList.add('opacity-50');
        const circle = step.querySelector('.rounded-full');
        const dot = step.querySelector('.rounded-full div');
        circle.classList.remove('bg-cyan-900/50');
        circle.classList.add('bg-gray-900');
        dot.classList.remove('bg-cyan-400');
        dot.classList.add('bg-gray-600');
    });
}

// SCANNING ANIMATION
function startScanningAnimation(data) {
    let progress = 0;

    const interval = setInterval(() => {
        progress++;
        progressBar.style.width = `${progress}%`;

        if (progress < 20) progressText.textContent = 'Parsing email structure...';
        else if (progress < 40) progressText.textContent = 'Analyzing authentication headers...';
        else if (progress < 60) progressText.textContent = 'Inspecting URLs and content...';
        else if (progress < 80) progressText.textContent = 'Correlating threat intelligence...';
        else progressText.textContent = 'Finalizing risk assessment...';

        if (progress > currentStep * 20 && currentStep < 5) {
            highlightStep(currentStep);
        }

        if (progress >= 100) {
            clearInterval(interval);
            setTimeout(() => showResults(data), 500);
        }
    }, 40);
}

function highlightStep(index) {
    const step = document.getElementById(scanningSteps[index]);
    step.classList.remove('opacity-50');
    const circle = step.querySelector('.rounded-full');
    const dot = step.querySelector('.rounded-full div');
    circle.classList.remove('bg-gray-900');
    circle.classList.add('bg-cyan-900/50');
    dot.classList.remove('bg-gray-600');
    dot.classList.add('bg-cyan-400');
    currentStep++;
}

// SHOW RESULTS
function showResults(data) {

    scanningView.classList.add('hidden');
    resultsView.classList.remove('hidden');

    analysisTime.textContent = new Date().toLocaleTimeString();

    const score = data.risk_score || 0;
    const confidence = data.confidence || 0;
    const offset = 283 - (283 * score / 100);

    riskArc.style.strokeDashoffset = 283;
    riskScore.textContent = 0;
    confidenceBar.style.width = "0%";
    confidenceText.textContent = "0%";

    setTimeout(() => {

        riskArc.style.strokeDashoffset = offset;

        let s = 0;
        const scoreInt = setInterval(() => {
            s++;
            riskScore.textContent = s;
            if (s >= score) clearInterval(scoreInt);
        }, 15);

        let c = 0;
        const confInt = setInterval(() => {
            c++;
            confidenceBar.style.width = `${c}%`;
            confidenceText.textContent = `${c}%`;
            if (c >= confidence) clearInterval(confInt);
        }, 10);

        updateSeverity(data.severity);

    }, 300);
}

function updateSeverity(severity) {

    if (severity === "Critical") {
        severityBadge.className = 'inline-flex items-center px-4 py-2 bg-red-900/30 text-red-400 rounded-lg font-semibold';
        severityBadge.innerHTML = `<div class="w-2 h-2 bg-red-400 rounded-full mr-2 animate-pulse"></div>Critical`;
    }
    else if (severity === "High") {
        severityBadge.className = 'inline-flex items-center px-4 py-2 bg-amber-900/30 text-amber-400 rounded-lg font-semibold';
        severityBadge.innerHTML = `<div class="w-2 h-2 bg-amber-400 rounded-full mr-2 animate-pulse"></div>High`;
    }
    else if (severity === "Medium") {
        severityBadge.className = 'inline-flex items-center px-4 py-2 bg-yellow-900/30 text-yellow-400 rounded-lg font-semibold';
        severityBadge.innerHTML = `<div class="w-2 h-2 bg-yellow-400 rounded-full mr-2 animate-pulse"></div>Medium`;
    }
    else {
        severityBadge.className = 'inline-flex items-center px-4 py-2 bg-green-900/30 text-green-400 rounded-lg font-semibold';
        severityBadge.innerHTML = `<div class="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></div>Low`;
    }
}
newAnalysisBtn.addEventListener('click', () => {

    resultsView.classList.add('hidden');
    scanningView.classList.add('hidden');
    submissionView.classList.remove('hidden');

    emailText.value = '';
    charCount.textContent = '0 characters';

    currentFile = null;
    fileInput.value = '';
    fileInfo.classList.add('hidden');
    dropZone.classList.remove('hidden');

    updateAnalyzeButton();
});
// Dropdown toggle for analysis sections
document.querySelectorAll('.analysis-header').forEach(header => {
    header.addEventListener('click', () => {
        const content = header.nextElementSibling;
        if (content) {
            content.classList.toggle('hidden');
        }
    });
});