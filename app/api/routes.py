"""
FastAPI route definitions.
"""

from __future__ import annotations

import hashlib
import logging
import time
import uuid

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse

from app.config import MAX_UPLOAD_SIZE_BYTES
from app.core.queue import enqueue_job
from app.models.schemas import (
    AuditJobResponse,
    AuditStatusResponse,
    HealthResponse,
    JobStatus,
)
from app.storage.store import get_job_store

logger = logging.getLogger(__name__)

router = APIRouter()

_start_time: float = time.time()


# ---------------------------------------------------------------------------
# Landing Page
# ---------------------------------------------------------------------------

LANDING_PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Lintora — Smart Contract Security Auditor</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    background: #fafbfc;
    min-height: 100vh;
    overflow-x: hidden;
}

/* Ballpit Container */
.ballpit-container {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}

#ballpit-canvas {
    width: 100%;
    height: 100%;
    display: block;
}

/* Background Pattern */
.bg-pattern {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: 
        radial-gradient(circle at 25% 25%, rgba(79, 70, 229, 0.02) 0%, transparent 50%),
        radial-gradient(circle at 75% 75%, rgba(16, 185, 129, 0.02) 0%, transparent 50%);
    pointer-events: none;
    z-index: 1;
}

.container {
    position: relative;
    z-index: 1;
    max-width: 900px;
    margin: 0 auto;
    padding: 4rem 2rem;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

/* Header */
.header {
    text-align: center;
    margin-bottom: 1rem;
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: #ecfdf5;
    color: #059669;
    padding: 0.4rem 1rem;
    border-radius: 100px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
}

.badge::before {
    content: '';
    width: 6px;
    height: 6px;
    background: #10b981;
    border-radius: 50%;
}

.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(2.5rem, 6vw, 4rem);
    font-weight: 700;
    color: #1a1a2e;
    line-height: 1.1;
    letter-spacing: -0.03em;
    margin-bottom: 1rem;
}

.hero-title .highlight {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-subtitle {
    font-size: 1.15rem;
    color: #6b7280;
    max-width: 500px;
    margin: 0 auto 3rem;
    line-height: 1.6;
}

/* Main Card */
.main-card {
    background: white;
    border-radius: 24px;
    box-shadow: 
        0 0 0 1px rgba(0,0,0,0.03),
        0 2px 4px rgba(0,0,0,0.02),
        0 12px 24px rgba(0,0,0,0.06);
    padding: 2rem;
    margin-bottom: 2rem;
}

/* Upload Area */
.upload-wrapper {
    position: relative;
}

.upload-area {
    border: 2px dashed #e5e7eb;
    border-radius: 16px;
    padding: 2.5rem 2rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    background: #fafbfc;
}

.upload-area:hover {
    border-color: #a5b4fc;
    background: #f5f3ff;
}

.upload-area.dragover {
    border-color: #4f46e5;
    background: #eef2ff;
    transform: scale(1.01);
}

.upload-area.has-file {
    border-color: #10b981;
    background: #ecfdf5;
    border-style: solid;
}

.upload-icon {
    width: 64px;
    height: 64px;
    margin: 0 auto 1rem;
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.75rem;
}

.upload-text {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1a1a2e;
    margin-bottom: 0.5rem;
}

.upload-hint {
    font-size: 0.9rem;
    color: #9ca3af;
}

.file-info {
    display: none;
    margin-top: 1rem;
    padding: 1rem;
    background: white;
    border-radius: 12px;
    border: 1px solid #d1fae5;
}

.file-info.show {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.file-icon {
    width: 40px;
    height: 40px;
    background: #ecfdf5;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
}

.file-details {
    flex: 1;
    text-align: left;
}

.file-name {
    font-weight: 600;
    color: #1a1a2e;
    font-size: 0.95rem;
}

.file-size {
    font-size: 0.8rem;
    color: #6b7280;
}

.file-remove {
    background: none;
    border: none;
    color: #9ca3af;
    cursor: pointer;
    font-size: 1.25rem;
    padding: 0.5rem;
    border-radius: 8px;
    transition: all 0.2s;
}

.file-remove:hover {
    background: #fee2e2;
    color: #ef4444;
}

#fileInput {
    display: none;
}

/* Search Bar Style Input */
.input-wrapper {
    margin-top: 1.5rem;
    position: relative;
}

.search-input {
    width: 100%;
    padding: 1rem 1.25rem;
    padding-right: 140px;
    font-size: 1rem;
    font-family: inherit;
    border: 2px solid #e5e7eb;
    border-radius: 14px;
    background: white;
    color: #1a1a2e;
    transition: all 0.2s;
}

.search-input:focus {
    outline: none;
    border-color: #4f46e5;
    box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1);
}

.search-input::placeholder {
    color: #9ca3af;
}

.submit-btn {
    position: absolute;
    right: 6px;
    top: 50%;
    transform: translateY(-50%);
    padding: 0.7rem 1.25rem;
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 0.95rem;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.submit-btn:hover:not(:disabled) {
    transform: translateY(-50%) scale(1.02);
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
}

.submit-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.submit-btn svg {
    width: 18px;
    height: 18px;
}

/* Features */
.features {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-top: 1.5rem;
}

.feature {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: #f9fafb;
    border-radius: 10px;
    font-size: 0.85rem;
    color: #4b5563;
}

.feature-icon {
    font-size: 1.1rem;
}

/* Loading State */
.loading-overlay {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255,255,255,0.95);
    z-index: 100;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.loading-overlay.show {
    display: flex;
}

.loading-spinner {
    width: 60px;
    height: 60px;
    border: 3px solid #e5e7eb;
    border-top-color: #4f46e5;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1.5rem;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.loading-text {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1a1a2e;
    margin-bottom: 0.5rem;
}

.loading-subtext {
    font-size: 0.9rem;
    color: #6b7280;
}

/* Result */
.result-card {
    display: none;
    background: white;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    border: 2px solid #d1fae5;
}

.result-card.show {
    display: block;
}

.result-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.result-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 0.5rem;
}

.result-text {
    color: #6b7280;
    margin-bottom: 1.5rem;
}

.result-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.85rem 1.5rem;
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: white;
    text-decoration: none;
    border-radius: 10px;
    font-weight: 600;
    transition: all 0.2s;
}

.result-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
}

/* Error */
.error-message {
    display: none;
    margin-top: 1rem;
    padding: 1rem;
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 10px;
    color: #dc2626;
    font-size: 0.9rem;
}

.error-message.show {
    display: block;
}

/* Footer */
.footer {
    margin-top: auto;
    padding-top: 2rem;
    text-align: center;
}

.footer-link {
    color: #6b7280;
    text-decoration: none;
    font-size: 0.9rem;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    transition: all 0.2s;
}

.footer-link:hover {
    background: #f3f4f6;
    color: #4f46e5;
}

/* Responsive */
@media (max-width: 640px) {
    .container {
        padding: 2rem 1rem;
    }
    
    .features {
        grid-template-columns: 1fr;
    }
    
    .search-input {
        padding-right: 1rem;
    }
    
    .submit-btn {
        position: static;
        width: 100%;
        margin-top: 1rem;
        transform: none;
        justify-content: center;
    }
    
    .submit-btn:hover:not(:disabled) {
        transform: none;
    }
}
</style>
</head>
<body>
<div class="ballpit-container">
    <canvas id="ballpit-canvas"></canvas>
</div>
<div class="bg-pattern"></div>

<div class="container">
    <header class="header">
        <div class="badge">Powered by AI + Symbolic Execution</div>
        <h1 class="hero-title">
            Audit your <span class="highlight">Solidity</span><br>smart contracts
        </h1>
        <p class="hero-subtitle">
            Upload your contracts and get a comprehensive security audit powered by pattern matching, symbolic execution, and AI analysis.
        </p>
    </header>

    <div class="main-card">
        <form id="uploadForm">
            <div class="upload-wrapper">
                <div class="upload-area" id="uploadArea">
                    <div class="upload-icon">📦</div>
                    <div class="upload-text">Drop your ZIP file here</div>
                    <div class="upload-hint">or click to browse • Only .sol files will be analyzed</div>
                    <input type="file" id="fileInput" name="file" accept=".zip" required>
                </div>
                
                <div class="file-info" id="fileInfo">
                    <div class="file-icon">📄</div>
                    <div class="file-details">
                        <div class="file-name" id="fileName"></div>
                        <div class="file-size" id="fileSize"></div>
                    </div>
                    <button type="button" class="file-remove" id="fileRemove">×</button>
                </div>
            </div>

            <div class="error-message" id="errorMessage"></div>

            <div class="input-wrapper">
                <input 
                    type="text" 
                    class="search-input" 
                    id="projectName" 
                    name="project_name" 
                    placeholder="Audit this Solidity contract..."
                    value=""
                >
                <button type="submit" class="submit-btn" id="submitBtn">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M5 12h14M12 5l7 7-7 7"/>
                    </svg>
                    Audit
                </button>
            </div>
        </form>

        <div class="features">
            <div class="feature">
                <span class="feature-icon">🔍</span>
                <span>Pattern Detection</span>
            </div>
            <div class="feature">
                <span class="feature-icon">🤖</span>
                <span>AI Analysis</span>
            </div>
            <div class="feature">
                <span class="feature-icon">🔐</span>
                <span>Signed Reports</span>
            </div>
        </div>
    </div>

    <div class="result-card" id="resultCard">
        <div class="result-icon">✅</div>
        <h3 class="result-title">Audit Complete!</h3>
        <p class="result-text">Your security report is ready to view.</p>
        <a href="#" class="result-btn" id="reportLink" target="_blank">
            View Report
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                <polyline points="15 3 21 3 21 9"/>
                <line x1="10" y1="14" x2="21" y2="3"/>
            </svg>
        </a>
    </div>

    <footer class="footer">
        <a href="/docs" class="footer-link">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
            </svg>
            API Documentation
        </a>
    </footer>
</div>

<div class="loading-overlay" id="loadingOverlay">
    <div class="loading-spinner"></div>
    <div class="loading-text" id="loadingText">Analyzing your contracts...</div>
    <div class="loading-subtext">This may take a minute or two</div>
</div>

<script>
// Ballpit Animation Component
class Ballpit {
    constructor(canvas, options = {}) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.count = options.count || 100;
        this.gravity = options.gravity || 0.01;
        this.friction = options.friction || 0.9975;
        this.wallBounce = options.wallBounce || 0.95;
        this.followCursor = options.followCursor !== false;
        
        this.balls = [];
        this.mouse = { x: 0, y: 0 };
        this.animationId = null;
        
        this.init();
    }
    
    init() {
        this.resize();
        window.addEventListener('resize', () => this.resize());
        
        if (this.followCursor) {
            this.canvas.addEventListener('mousemove', (e) => {
                const rect = this.canvas.getBoundingClientRect();
                this.mouse.x = e.clientX - rect.left;
                this.mouse.y = e.clientY - rect.top;
            });
        }
        
        // Create balls
        for (let i = 0; i < this.count; i++) {
            this.balls.push(this.createBall());
        }
        
        this.animate();
    }
    
    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.width = this.canvas.width;
        this.height = this.canvas.height;
    }
    
    createBall() {
        const radius = Math.random() * 8 + 4;
        const colors = [
            'rgba(79, 70, 229, 0.4)',   // indigo
            'rgba(124, 58, 237, 0.4)',  // purple
            'rgba(16, 185, 129, 0.4)',   // emerald
            'rgba(59, 130, 246, 0.4)',  // blue
            'rgba(139, 92, 246, 0.4)',  // violet
        ];
        
        return {
            x: Math.random() * this.width,
            y: Math.random() * this.height,
            vx: (Math.random() - 0.5) * 2,
            vy: (Math.random() - 0.5) * 2,
            radius: radius,
            color: colors[Math.floor(Math.random() * colors.length)],
        };
    }
    
    update() {
        for (let ball of this.balls) {
            // Apply gravity
            ball.vy += this.gravity;
            
            // Apply friction
            ball.vx *= this.friction;
            ball.vy *= this.friction;
            
            // Update position
            ball.x += ball.vx;
            ball.y += ball.vy;
            
            // Wall collisions
            if (ball.x - ball.radius < 0) {
                ball.x = ball.radius;
                ball.vx *= -this.wallBounce;
            } else if (ball.x + ball.radius > this.width) {
                ball.x = this.width - ball.radius;
                ball.vx *= -this.wallBounce;
            }
            
            if (ball.y - ball.radius < 0) {
                ball.y = ball.radius;
                ball.vy *= -this.wallBounce;
            } else if (ball.y + ball.radius > this.height) {
                ball.y = this.height - ball.radius;
                ball.vy *= -this.wallBounce;
            }
            
            // Mouse interaction
            if (this.followCursor) {
                const dx = this.mouse.x - ball.x;
                const dy = this.mouse.y - ball.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                const maxDistance = 150;
                
                if (distance < maxDistance && distance > 0) {
                    const force = (maxDistance - distance) / maxDistance;
                    ball.vx += (dx / distance) * force * 0.1;
                    ball.vy += (dy / distance) * force * 0.1;
                }
            }
            
            // Ball-to-ball collisions
            for (let other of this.balls) {
                if (ball === other) continue;
                
                const dx = other.x - ball.x;
                const dy = other.y - ball.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                const minDistance = ball.radius + other.radius;
                
                if (distance < minDistance && distance > 0) {
                    const angle = Math.atan2(dy, dx);
                    const targetX = ball.x + Math.cos(angle) * minDistance;
                    const targetY = ball.y + Math.sin(angle) * minDistance;
                    const ax = (targetX - other.x) * 0.05;
                    const ay = (targetY - other.y) * 0.05;
                    
                    ball.vx -= ax;
                    ball.vy -= ay;
                    other.vx += ax;
                    other.vy += ay;
                }
            }
        }
    }
    
    draw() {
        this.ctx.clearRect(0, 0, this.width, this.height);
        
        for (let ball of this.balls) {
            this.ctx.beginPath();
            this.ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
            this.ctx.fillStyle = ball.color;
            this.ctx.fill();
            
            // Add subtle glow
            this.ctx.shadowBlur = 10;
            this.ctx.shadowColor = ball.color;
            this.ctx.fill();
            this.ctx.shadowBlur = 0;
        }
        
        // Draw connections between nearby balls
        for (let i = 0; i < this.balls.length; i++) {
            for (let j = i + 1; j < this.balls.length; j++) {
                const ball1 = this.balls[i];
                const ball2 = this.balls[j];
                const dx = ball2.x - ball1.x;
                const dy = ball2.y - ball1.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 100) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(ball1.x, ball1.y);
                    this.ctx.lineTo(ball2.x, ball2.y);
                    this.ctx.strokeStyle = `rgba(79, 70, 229, ${0.1 * (1 - distance / 100)})`;
                    this.ctx.lineWidth = 1;
                    this.ctx.stroke();
                }
            }
        }
    }
    
    animate() {
        this.update();
        this.draw();
        this.animationId = requestAnimationFrame(() => this.animate());
    }
    
    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
    }
}

// Initialize Ballpit when page loads
let ballpit;
window.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('ballpit-canvas');
    if (canvas) {
        ballpit = new Ballpit(canvas, {
            count: 100,
            gravity: 0.01,
            friction: 0.9975,
            wallBounce: 0.95,
            followCursor: false
        });
    }
});

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const fileRemove = document.getElementById('fileRemove');
const uploadForm = document.getElementById('uploadForm');
const submitBtn = document.getElementById('submitBtn');
const loadingOverlay = document.getElementById('loadingOverlay');
const loadingText = document.getElementById('loadingText');
const resultCard = document.getElementById('resultCard');
const reportLink = document.getElementById('reportLink');
const errorMessage = document.getElementById('errorMessage');
const projectName = document.getElementById('projectName');

// Click to upload
uploadArea.addEventListener('click', () => fileInput.click());

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].name.endsWith('.zip')) {
        fileInput.files = files;
        handleFileSelect();
    } else {
        showError('Please upload a ZIP file');
    }
});

fileInput.addEventListener('change', handleFileSelect);

fileRemove.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.value = '';
    fileInfo.classList.remove('show');
    uploadArea.classList.remove('has-file');
    errorMessage.classList.remove('show');
});

function handleFileSelect() {
    const file = fileInput.files[0];
    if (file) {
        if (!file.name.endsWith('.zip')) {
            showError('Please upload a ZIP file');
            fileInput.value = '';
            return;
        }
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        fileInfo.classList.add('show');
        uploadArea.classList.add('has-file');
        errorMessage.classList.remove('show');
        
        // Auto-fill project name from file name
        if (!projectName.value) {
            projectName.value = file.name.replace('.zip', '');
        }
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add('show');
}

// Form submission
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const file = fileInput.files[0];
    if (!file) {
        showError('Please select a ZIP file');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_name', projectName.value || file.name.replace('.zip', ''));

    // Show loading
    submitBtn.disabled = true;
    loadingOverlay.classList.add('show');
    resultCard.classList.remove('show');
    errorMessage.classList.remove('show');

    try {
        const response = await fetch('/audit', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        const data = await response.json();
        pollJobStatus(data.job_id);
    } catch (err) {
        loadingOverlay.classList.remove('show');
        submitBtn.disabled = false;
        showError(err.message || 'An error occurred');
    }
});

function pollJobStatus(jobId) {
    const messages = [
        'Extracting files...',
        'Scanning Solidity contracts...',
        'Running pattern analysis...',
        'AI analyzing code...',
        'Generating report...'
    ];
    let msgIndex = 0;

    const interval = setInterval(async () => {
        try {
            const response = await fetch(`/audit/${jobId}`);
            const data = await response.json();

            if (data.status === 'completed') {
                clearInterval(interval);
                loadingOverlay.classList.remove('show');
                reportLink.href = `/report/${jobId}`;
                resultCard.classList.add('show');
                submitBtn.disabled = false;
            } else if (data.status === 'failed') {
                clearInterval(interval);
                loadingOverlay.classList.remove('show');
                submitBtn.disabled = false;
                showError(data.error || 'Analysis failed');
            } else {
                // Update loading message
                loadingText.textContent = messages[msgIndex % messages.length];
                msgIndex++;
            }
        } catch (err) {
            clearInterval(interval);
            loadingOverlay.classList.remove('show');
            submitBtn.disabled = false;
            showError('Failed to check status');
        }
    }, 2000);
}
</script>
</body>
</html>"""


@router.get("/", response_class=HTMLResponse)
async def landing_page() -> HTMLResponse:
    """User-friendly landing page."""
    return HTMLResponse(content=LANDING_PAGE_HTML)


# ---------------------------------------------------------------------------
# POST /audit
# ---------------------------------------------------------------------------

@router.post("/audit", response_model=AuditJobResponse, status_code=202)
async def create_audit(
    file: UploadFile = File(..., description="ZIP archive of Solidity contracts"),
    project_name: str = Form("unnamed_project"),
) -> AuditJobResponse:
    """Accept a ZIP upload and enqueue a security audit job."""
    data = await file.read()

    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(data) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({len(data)} bytes). Max: {MAX_UPLOAD_SIZE_BYTES} bytes.",
        )

    if data[:4] not in (b"PK\\x03\\x04", b"PK\\x05\\x06", b"PK\\x07\\x08"):
        # More lenient check
        if not data[:2] == b"PK":
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid ZIP archive.")

    job_id = uuid.uuid4().hex
    code_hash = hashlib.sha256(data).hexdigest()

    store = get_job_store()
    store.create(job_id=job_id, project_name=project_name, code_hash=code_hash)

    enqueue_job(job_id, data, project_name, store)

    logger.info("Job %s created for project '%s' (%d bytes)", job_id, project_name, len(data))

    return AuditJobResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="Audit job accepted. Poll GET /audit/{job_id} for results.",
    )


# ---------------------------------------------------------------------------
# GET /audit/{job_id}
# ---------------------------------------------------------------------------

@router.get("/audit/{job_id}", response_model=AuditStatusResponse)
async def get_audit_status(job_id: str) -> AuditStatusResponse:
    """Return the current status and report for a job."""
    store = get_job_store()
    record = store.get(job_id)

    if record is None:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    html_url = f"/report/{job_id}" if record.status == JobStatus.COMPLETED else None

    return AuditStatusResponse(
        job_id=job_id,
        status=record.status,
        report=record.report,
        error=record.error,
        html_report_url=html_url,
    )


# ---------------------------------------------------------------------------
# GET /report/{job_id}
# ---------------------------------------------------------------------------

@router.get("/report/{job_id}", response_class=HTMLResponse)
async def get_html_report(job_id: str) -> HTMLResponse:
    """Serve the rendered HTML audit report."""
    store = get_job_store()
    path = store.get_html_report_path(job_id)

    if path is None:
        raise HTTPException(
            status_code=404,
            detail=f"HTML report for job '{job_id}' not found or not yet ready.",
        )

    return HTMLResponse(content=path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Liveness probe."""
    from app import __version__

    return HealthResponse(
        status="healthy",
        version=__version__,
        uptime_seconds=round(time.time() - _start_time, 2),
    )
