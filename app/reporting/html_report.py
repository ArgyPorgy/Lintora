"""
Beautiful HTML report generator.
"""

from __future__ import annotations

from app.models.schemas import AuditReport, Severity, FindingSource


def generate_html_report(report: AuditReport) -> str:
    """Generate a beautiful, modern HTML audit report."""
    
    severity_colors = {
        "critical": "#ef4444",
        "high": "#f97316",
        "medium": "#eab308",
        "low": "#3b82f6",
        "info": "#6b7280",
    }
    
    source_colors = {
        "ai": "#10b981",
        "openclaw_ai": "#10b981",
    }
    
    source_labels = {
        "ai": "Agent",
        "openclaw_ai": "Agent",
    }

    risk_colors = {
        "CRITICAL": "#ef4444",
        "HIGH": "#f97316",
        "MEDIUM": "#eab308",
        "LOW": "#22c55e",
    }

    findings_html = ""
    for f in report.findings:
        sev_color = severity_colors.get(f.severity.value, "#6b7280")
        src_color = source_colors.get(f.source.value, "#6b7280")
        src_label = source_labels.get(f.source.value, f.source.value)
        
        findings_html += f"""
        <div class="finding-card" style="border-left-color: {sev_color};">
            <div class="finding-header">
                <div class="finding-badges">
                    <span class="severity-badge" style="background: {sev_color};">{f.severity.value.upper()}</span>
                    <span class="source-badge" style="background: {src_color};">{src_label}</span>
                    {f'<span class="swc-badge">{f.swc_id}</span>' if f.swc_id else ''}
                </div>
                <span class="finding-location">{f.file_path}{f':{f.line_number}' if f.line_number else ''}</span>
            </div>
            <h3 class="finding-title">{f.title}</h3>
            <p class="finding-description">{f.description}</p>
            {f'<div class="finding-recommendation"><strong>Recommendation:</strong> {f.recommendation}</div>' if f.recommendation else ''}
        </div>
        """

    if not report.findings:
        findings_html = """
        <div class="no-findings">
            <div class="no-findings-icon">✓</div>
            <h3>No Vulnerabilities Found</h3>
            <p>The analysis did not detect any security issues in your smart contracts.</p>
        </div>
        """

    analyzers_html = " ".join([
        f'<span class="analyzer-badge" style="background: {source_colors.get(a, "#6b7280")};">{source_labels.get(a, a)}</span>'
        for a in report.summary.analyzers_used
    ])

    risk_color = risk_colors.get(report.risk_level, "#22c55e")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Security Audit Report — {report.project_name}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    background: #fafbfc;
    color: #1a1a2e;
    line-height: 1.6;
    min-height: 100vh;
}}

.container {{
    max-width: 1000px;
    margin: 0 auto;
    padding: 3rem 2rem;
}}

/* Header */
.header {{
    text-align: center;
    margin-bottom: 3rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid #e5e7eb;
}}

.logo {{
    font-size: 1.5rem;
    font-weight: 700;
    color: #4f46e5;
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
}}

.header h1 {{
    font-size: 2rem;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
}}

.header .subtitle {{
    color: #6b7280;
    font-size: 1rem;
}}

/* Summary Grid */
.summary-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}}

.summary-card {{
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    border: 1px solid #e5e7eb;
}}

.summary-card .label {{
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #6b7280;
    margin-bottom: 0.5rem;
}}

.summary-card .value {{
    font-size: 1.75rem;
    font-weight: 700;
    color: #1a1a2e;
}}

.summary-card .value.risk {{
    color: {risk_color};
}}

/* Severity Breakdown */
.severity-breakdown {{
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 2rem;
}}

.severity-item {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: white;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
}}

.severity-dot {{
    width: 12px;
    height: 12px;
    border-radius: 50%;
}}

.severity-count {{
    font-weight: 600;
    font-size: 1.1rem;
}}

.severity-label {{
    color: #6b7280;
    font-size: 0.9rem;
}}

/* Analyzers */
.analyzers {{
    margin-bottom: 2rem;
}}

.analyzers-label {{
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #6b7280;
    margin-bottom: 0.75rem;
}}

.analyzer-badge {{
    display: inline-block;
    padding: 0.35rem 0.75rem;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
    color: white;
    margin-right: 0.5rem;
}}

/* Findings */
.findings-section {{
    margin-top: 2rem;
}}

.findings-header {{
    font-size: 1.25rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
    color: #1a1a2e;
}}

.finding-card {{
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    border: 1px solid #e5e7eb;
    border-left: 4px solid;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}}

.finding-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.75rem;
    flex-wrap: wrap;
    gap: 0.5rem;
}}

.finding-badges {{
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}}

.severity-badge, .source-badge, .swc-badge {{
    padding: 0.25rem 0.6rem;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}}

.severity-badge {{
    color: white;
}}

.source-badge {{
    color: white;
}}

.swc-badge {{
    background: #f3f4f6;
    color: #4b5563;
}}

.finding-location {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #6b7280;
    background: #f3f4f6;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
}}

.finding-title {{
    font-size: 1.1rem;
    font-weight: 600;
    color: #1a1a2e;
    margin-bottom: 0.5rem;
}}

.finding-description {{
    color: #4b5563;
    font-size: 0.95rem;
    margin-bottom: 0.75rem;
}}

.finding-recommendation {{
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.9rem;
    color: #166534;
}}

/* No Findings */
.no-findings {{
    text-align: center;
    padding: 4rem 2rem;
    background: white;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
}}

.no-findings-icon {{
    font-size: 3rem;
    color: #22c55e;
    margin-bottom: 1rem;
}}

.no-findings h3 {{
    font-size: 1.25rem;
    color: #1a1a2e;
    margin-bottom: 0.5rem;
}}

.no-findings p {{
    color: #6b7280;
}}

/* Footer */
.footer {{
    margin-top: 3rem;
    padding-top: 2rem;
    border-top: 1px solid #e5e7eb;
    text-align: center;
}}

.footer .hash {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #9ca3af;
    word-break: break-all;
    margin-bottom: 0.5rem;
}}

.footer .timestamp {{
    font-size: 0.85rem;
    color: #6b7280;
}}

.footer .signature-info {{
    font-size: 0.75rem;
    color: #9ca3af;
    margin-top: 0.5rem;
}}

/* Verification Section */
.verification-section {{
    margin-top: 3rem;
    margin-bottom: 2rem;
}}

.verification-card {{
    background: white;
    border-radius: 12px;
    padding: 2rem;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}}

.verification-item {{
    margin-bottom: 2rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid #e5e7eb;
}}

.verification-item:last-child {{
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
}}

.verification-label {{
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #6b7280;
    margin-bottom: 0.75rem;
}}

.verification-value {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    color: #1a1a2e;
    background: #f3f4f6;
    padding: 1rem;
    border-radius: 8px;
    word-break: break-all;
    margin-bottom: 0.5rem;
    border: 1px solid #e5e7eb;
}}

.verification-desc {{
    font-size: 0.85rem;
    color: #6b7280;
    font-style: italic;
}}

/* Responsive */
@media (max-width: 640px) {{
    .container {{
        padding: 1.5rem 1rem;
    }}
    
    .summary-grid {{
        grid-template-columns: 1fr 1fr;
    }}
    
    .finding-header {{
        flex-direction: column;
    }}
}}
</style>
</head>
<body>
<div class="container">
    <header class="header">
        <div class="logo">🔒 Private Security Agent</div>
        <h1>{report.project_name}</h1>
        <p class="subtitle">Smart Contract Security Audit Report</p>
    </header>

    <div class="summary-grid">
        <div class="summary-card">
            <div class="label">Risk Level</div>
            <div class="value risk">{report.risk_level}</div>
        </div>
        <div class="summary-card">
            <div class="label">Total Findings</div>
            <div class="value">{report.summary.total_findings}</div>
        </div>
        <div class="summary-card">
            <div class="label">Solidity Files</div>
            <div class="value">{report.summary.solidity_files}</div>
        </div>
        <div class="summary-card">
            <div class="label">Files Scanned</div>
            <div class="value">{report.summary.files_scanned}</div>
        </div>
    </div>

    <div class="severity-breakdown">
        <div class="severity-item">
            <div class="severity-dot" style="background: #ef4444;"></div>
            <span class="severity-count">{report.summary.critical}</span>
            <span class="severity-label">Critical</span>
        </div>
        <div class="severity-item">
            <div class="severity-dot" style="background: #f97316;"></div>
            <span class="severity-count">{report.summary.high}</span>
            <span class="severity-label">High</span>
        </div>
        <div class="severity-item">
            <div class="severity-dot" style="background: #eab308;"></div>
            <span class="severity-count">{report.summary.medium}</span>
            <span class="severity-label">Medium</span>
        </div>
        <div class="severity-item">
            <div class="severity-dot" style="background: #3b82f6;"></div>
            <span class="severity-count">{report.summary.low}</span>
            <span class="severity-label">Low</span>
        </div>
    </div>

    <div class="analyzers">
        <div class="analyzers-label">Analysis Engines Used</div>
        {analyzers_html}
    </div>

    <!-- Archive & Verification Info -->
    <div class="summary-grid" style="margin-top: 1.5rem;">
        <div class="summary-card">
            <div class="label">Archive Hash (SHA-256)</div>
            <div class="value" style="font-size: 0.85rem; font-family: 'JetBrains Mono', monospace; word-break: break-all; line-height: 1.4;">{report.code_hash}</div>
        </div>
        <div class="summary-card">
            <div class="label">Generated</div>
            <div class="value" style="font-size: 0.9rem;">{report.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</div>
        </div>
        {f'''
        <div class="summary-card">
            <div class="label">Signature Status</div>
            <div class="value" style="font-size: 0.9rem; color: #22c55e;">✓ Signed</div>
        </div>
        <div class="summary-card">
            <div class="label">Public Key</div>
            <div class="value" style="font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; word-break: break-all; line-height: 1.3;">{report.public_key}</div>
        </div>
        ''' if report.signature and report.public_key else ''}
    </div>

    <section class="findings-section">
        <h2 class="findings-header">Security Findings</h2>
        {findings_html}
    </section>

    <!-- Cryptographic Verification Section -->
    <section class="verification-section">
        <h2 class="findings-header">Cryptographic Verification</h2>
        <div class="verification-card">
            <div class="verification-item">
                <div class="verification-label">Archive Hash (SHA-256)</div>
                <div class="verification-value">{report.code_hash}</div>
                <div class="verification-desc">Hash of the uploaded ZIP archive</div>
            </div>
            {f'''
            <div class="verification-item">
                <div class="verification-label">Report Signature</div>
                <div class="verification-value">{report.signature}</div>
                <div class="verification-desc">Ed25519 signature of this report (signed hash of JSON report)</div>
            </div>
            <div class="verification-item">
                <div class="verification-label">Public Key</div>
                <div class="verification-value">{report.public_key}</div>
                <div class="verification-desc">Ed25519 public key for signature verification</div>
            </div>
            ''' if report.signature and report.public_key else '<div class="verification-item"><div class="verification-desc" style="color: #ef4444;">⚠ Report not cryptographically signed</div></div>'}
        </div>
    </section>

    <footer class="footer">
        <div class="hash">SHA-256: {report.code_hash}</div>
        <div class="timestamp">Generated: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</div>
        {f'<div class="signature-info">✓ Cryptographically signed with Ed25519 • Public Key: {report.public_key[:32]}...' if report.signature and report.public_key else ''}
    </footer>
</div>
</body>
</html>"""

    return html
