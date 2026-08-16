// NetSage AI - Main JavaScript

// Global utilities
window.NetSage = {
    // Toast notifications
    toast(message, type = 'success') {
        const container = this.getToastContainer();
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        container.appendChild(toast);
        new bootstrap.Toast(toast, { delay: 3000 }).show();
    },

    getToastContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            container.style.zIndex = '1080';
            document.body.appendChild(container);
        }
        return container;
    },

    // Loading state
    setLoading(element, loading = true) {
        if (loading) {
            element.classList.add('loading');
            element.disabled = true;
        } else {
            element.classList.remove('loading');
            element.disabled = false;
        }
    },

    // API helper
    async api(endpoint, options = {}) {
        const defaultOptions = {
            headers: { 'Content-Type': 'application/json' }
        };
        const response = await fetch(endpoint, { ...defaultOptions, ...options });
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }
        return response.json();
    },

    // Format helpers
    formatConfidence(confidence) {
        return (confidence * 100).toFixed(0) + '%';
    },

    confidenceClass(confidence) {
        if (confidence >= 0.8) return 'success';
        if (confidence >= 0.5) return 'warning';
        return 'danger';
    },

    severityBadge(severity) {
        const map = { High: 'danger', Medium: 'warning', Low: 'success' };
        return map[severity] || 'secondary';
    },

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    // Copy to clipboard
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.toast('Copied to clipboard');
        } catch (e) {
            this.toast('Failed to copy', 'error');
        }
    },

    // Download text file
    downloadText(text, filename = 'download.txt') {
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    },

    // Format diagnosis for display
    formatDiagnosis(diagnosis) {
        return `
Predicted Fault: ${diagnosis.predicted_fault}
Confidence: ${this.formatConfidence(diagnosis.confidence)}
Reasoning: ${diagnosis.reasoning_summary}
Evidence: ${diagnosis.evidence_used.join('; ')}
Fix: ${diagnosis.recommended_fix}
Commands: ${diagnosis.commands.join('\n')}
Needs More Evidence: ${diagnosis.needs_more_evidence ? 'Yes' : 'No'}
        `.trim();
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Add toast container if not exists
    if (!document.getElementById('toast-container')) {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '1080';
        document.body.appendChild(container);
    }

    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Enter to submit forms
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const activeForm = document.activeElement?.closest('form');
            if (activeForm) {
                const submitBtn = activeForm.querySelector('button[type="submit"]');
                if (submitBtn) submitBtn.click();
            }
        }
    });

    // Auto-hide alerts after 5 seconds
    document.querySelectorAll('.alert:not(.alert-permanent)').forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Add smooth scroll to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.NetSage;
}