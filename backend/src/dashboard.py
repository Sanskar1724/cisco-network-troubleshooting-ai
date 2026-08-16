"""HTML Dashboard for NetSage AI."""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from src.config import DATA_DIR
from src.models import Case, DiagnosisResult
from src.data_loader import load_cases
from src.human_review import HumanReview, REVIEW_LOG_FILE


DASHBOARD_FILE = DATA_DIR / "dashboard.html"


class Dashboard:
    """Generates HTML dashboard for the project."""
    
    def __init__(self, output_file: Path = DASHBOARD_FILE):
        self.output_file = output_file
        self.cases = load_cases()
        self.review = HumanReview(REVIEW_LOG_FILE)
    
    def generate(self, diagnosis_results: List[Dict[str, Any]] = None) -> str:
        """Generate HTML dashboard."""
        stats = self.review.get_review_stats()
        corrected_cases = self.review.list_corrected_cases()
        
        # Case type distribution
        concept_counts = {}
        severity_counts = {}
        for case in self.cases:
            concept_counts[case.concept] = concept_counts.get(case.concept, 0) + 1
            severity_counts[case.severity] = severity_counts.get(case.severity, 0) + 1
        
        # AI vs Human agreement
        agreement_rate = 0
        if stats['total'] > 0:
            agreement_rate = (stats['accepted'] / stats['total']) * 100
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NetSage AI - Dashboard</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               background: #f5f5f5; color: #333; line-height: 1.6; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        header {{ background: #1e3a5f; color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; }}
        header h1 {{ font-size: 2.5rem; margin-bottom: 10px; }}
        header p {{ opacity: 0.9; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: white; padding: 25px; border-radius: 8px; 
                     box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #1e3a5f; }}
        .stat-card h3 {{ font-size: 0.9rem; color: #666; margin-bottom: 8px; text-transform: uppercase; }}
        .stat-card .value {{ font-size: 2.5rem; font-weight: bold; color: #1e3a5f; }}
        .stat-card.accepted {{ border-left-color: #28a745; }}
        .stat-card.edited {{ border-left-color: #ffc107; }}
        .stat-card.rejected {{ border-left-color: #dc3545; }}
        .section {{ background: white; padding: 25px; border-radius: 8px; 
                   box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 30px; }}
        .section h2 {{ color: #1e3a5f; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #eee; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f8f9fa; font-weight: 600; color: #333; }}
        tr:hover {{ background: #f8f9fa; }}
        .badge {{ display: inline-block; padding: 4px 10px; border-radius: 12px; 
                  font-size: 0.8rem; font-weight: 500; }}
        .badge-high {{ background: #f8d7da; color: #721c24; }}
        .badge-medium {{ background: #fff3cd; color: #856404; }}
        .badge-low {{ background: #d4edda; color: #155724; }}
        .badge-accepted {{ background: #d4edda; color: #155724; }}
        .badge-edited {{ background: #fff3cd; color: #856404; }}
        .badge-rejected {{ background: #f8d7da; color: #721c24; }}
        .chart-container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        @media (max-width: 768px) {{ .chart-container {{ grid-template-columns: 1fr; }} }}
        .progress-bar {{ height: 8px; background: #e9ecef; border-radius: 4px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: #1e3a5f; border-radius: 4px; transition: width 0.5s; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>NetSage AI Dashboard</h1>
            <p>Cisco Network Troubleshooting Assistant - {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Cases</h3>
                <div class="value">{len(self.cases)}</div>
            </div>
            <div class="stat-card accepted">
                <h3>Accepted</h3>
                <div class="value">{stats['accepted']}</div>
            </div>
            <div class="stat-card edited">
                <h3>Edited</h3>
                <div class="value">{stats['edited']}</div>
            </div>
            <div class="stat-card rejected">
                <h3>Rejected</h3>
                <div class="value">{stats['rejected']}</div>
            </div>
            <div class="stat-card">
                <h3>AI Agreement Rate</h3>
                <div class="value">{agreement_rate:.1f}%</div>
            </div>
            <div class="stat-card">
                <h3>Total Reviews</h3>
                <div class="value">{stats['total']}</div>
            </div>
        </div>
        
        <div class="chart-container">
            <div class="section">
                <h2>Issue Types (by Concept)</h2>
                <table>
                    <thead><tr><th>Concept</th><th>Count</th><th>Distribution</th></tr></thead>
                    <tbody>
"""
        
        max_concept = max(concept_counts.values()) if concept_counts else 1
        for concept, count in sorted(concept_counts.items(), key=lambda x: -x[1]):
            pct = (count / max_concept) * 100
            html += f"""<tr><td>{concept}</td><td>{count}</td>
                <td><div class="progress-bar"><div class="progress-fill" style="width: {pct}%"></div></div></td></tr>"""
        
        html += """</tbody></table></div>
            <div class="section">
                <h2>Severity Distribution</h2>
                <table>
                    <thead><tr><th>Severity</th><th>Count</th><th>Distribution</th></tr></thead>
                    <tbody>
"""
        
        max_severity = max(severity_counts.values()) if severity_counts else 1
        severity_colors = {"High": "#dc3545", "Medium": "#ffc107", "Low": "#28a745"}
        for severity, count in sorted(severity_counts.items(), key=lambda x: -x[1]):
            pct = (count / max_severity) * 100
            color = severity_colors.get(severity, "#1e3a5f")
            html += f"""<tr><td><span class="badge badge-{severity.lower()}">{severity}</span></td>
                <td>{count}</td>
                <td><div class="progress-bar"><div class="progress-fill" style="width: {pct}%; background: {color}"></div></div></td></tr>"""
        
        html += f"""</tbody></table></div>
        </div>
        
        <div class="section">
            <h2>Human Review Log</h2>
"""
        
        if stats['total'] == 0:
            html += '<p style="color: #666; text-align: center; padding: 40px;">No reviews logged yet. Run diagnoses and use the review system to populate.</p>'
        else:
            html += """<table>
                    <thead><tr><th>Case ID</th><th>Title</th><th>Decision</th><th>AI Fault</th><th>Corrected Fault</th></tr></thead>
                    <tbody>
"""
            for case in corrected_cases:
                badge_class = "badge-accepted" if case['decision'] == "Accepted" else \
                              "badge-edited" if case['decision'] == "Edited" else "badge-rejected"
                html += f"""<tr>
                    <td>{case['case_id']}</td>
                    <td>{case['title']}</td>
                    <td><span class="badge {badge_class}">{case['decision']}</span></td>
                    <td>{case['ai_fault']}</td>
                    <td>{case['corrected_fault'] or '—'}</td>
                </tr>"""
            
            html += "</tbody></table>"
        
        html += """</div>
        
        <div class="section">
            <h2>All 30 Cases</h2>
            <table>
                <thead><tr><th>ID</th><th>Fault</th><th>Concept</th><th>Severity</th><th>OSI Layer</th></tr></thead>
                <tbody>
"""
        
        for case in self.cases:
            severity_class = f"badge-{case.severity.lower()}"
            html += f"""<tr>
                <td>{case.case_id}</td>
                <td>{case.title}</td>
                <td>{case.concept}</td>
                <td><span class="badge {severity_class}">{case.severity}</span></td>
                <td>{case.osi_layer}</td>
            </tr>"""
        
        html += f"""</tbody></table></div>
        
        <div class="footer">
            Generated by NetSage AI on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
            Cisco Network Troubleshooting Assistant
        </div>
    </div>
</body>
</html>"""
        
        self.output_file.write_text(html, encoding="utf-8")
        return str(self.output_file)
    
    def open_in_browser(self):
        """Open dashboard in default browser."""
        import webbrowser
        webbrowser.open(f"file://{self.output_file.absolute()}")


def generate_dashboard(diagnosis_results: List[Dict[str, Any]] = None) -> str:
    """Convenience function to generate dashboard."""
    dashboard = Dashboard()
    return dashboard.generate(diagnosis_results)