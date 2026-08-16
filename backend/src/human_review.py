"""Human review system for AI diagnoses."""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.config import DATA_DIR
from src.models import DiagnosisResult, Case


REVIEW_LOG_FILE = DATA_DIR / "human_review_log.md"


class ReviewStatus:
    ACCEPTED = "Accepted"
    EDITED = "Edited"
    REJECTED = "Rejected"


class HumanReview:
    """Manages human review of AI diagnoses."""
    
    def __init__(self, log_file: Path = REVIEW_LOG_FILE):
        self.log_file = log_file
        self._ensure_log_exists()
    
    def _ensure_log_exists(self):
        """Create log file with header if it doesn't exist."""
        if not self.log_file.exists():
            header = f"""# Human Review Log - NetSage AI

**Project:** Cisco Network Troubleshooting AI  
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Purpose:** Track AI diagnoses that were corrected by human reviewers

---

## Review Guidelines

- **Accepted**: AI diagnosis is correct, no changes needed
- **Edited**: AI diagnosis partially correct, human made corrections
- **Rejected**: AI diagnosis incorrect, completely different root cause

Each entry documents the AI output, human decision, and reasoning.

---

"""
            self.log_file.write_text(header, encoding="utf-8")
    
    def log_review(self, case_id: int, case_title: str, 
                   ai_diagnosis: DiagnosisResult, 
                   human_decision: str,
                   human_notes: str = "",
                   corrected_fault: str = "",
                   corrected_confidence: float = 0.0,
                   corrected_reasoning: str = "",
                   corrected_fix: str = "",
                   corrected_commands: List[str] = None) -> None:
        """Log a human review decision."""
        
        if human_decision not in [ReviewStatus.ACCEPTED, ReviewStatus.EDITED, ReviewStatus.REJECTED]:
            raise ValueError(f"Invalid decision: {human_decision}")
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        entry = f"""## Case {case_id}: {case_title}

**Timestamp:** {timestamp}  
**Human Decision:** {human_decision}

### AI Diagnosis
- **Predicted Fault:** {ai_diagnosis.predicted_fault}
- **Confidence:** {ai_diagnosis.confidence:.2f}
- **Reasoning:** {ai_diagnosis.reasoning_summary}
- **Evidence Used:** {', '.join(ai_diagnosis.evidence_used) if ai_diagnosis.evidence_used else 'None'}
- **Recommended Fix:** {ai_diagnosis.recommended_fix}
- **Commands:** {', '.join(ai_diagnosis.commands) if ai_diagnosis.commands else 'None'}
- **Needs More Evidence:** {'Yes' if ai_diagnosis.needs_more_evidence else 'No'}

"""
        
        if human_decision == ReviewStatus.EDITED:
            entry += f"""### Human Correction
- **Corrected Fault:** {corrected_fault or 'N/A'}
- **Corrected Confidence:** {corrected_confidence:.2f if corrected_confidence else 'N/A'}
- **Corrected Reasoning:** {corrected_reasoning or 'N/A'}
- **Corrected Fix:** {corrected_fix or 'N/A'}
- **Corrected Commands:** {', '.join(corrected_commands) if corrected_commands else 'N/A'}

"""
        
        entry += f"""### Human Notes
{human_notes or 'No additional notes.'}

---

"""
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(entry)
        
        print(f"✓ Review logged: Case {case_id} - {human_decision}")
    
    def get_review_stats(self) -> Dict[str, int]:
        """Get statistics from review log."""
        content = self.log_file.read_text(encoding="utf-8")
        
        stats = {
            "total": 0,
            "accepted": 0,
            "edited": 0,
            "rejected": 0
        }
        
        for line in content.split('\n'):
            if '**Human Decision:**' in line:
                stats["total"] += 1
                if 'Accepted' in line:
                    stats["accepted"] += 1
                elif 'Edited' in line:
                    stats["edited"] += 1
                elif 'Rejected' in line:
                    stats["rejected"] += 1
        
        return stats
    
    def print_summary(self):
        """Print review statistics."""
        stats = self.get_review_stats()
        print("\n" + "=" * 50)
        print("HUMAN REVIEW SUMMARY")
        print("=" * 50)
        print(f"Total Reviews: {stats['total']}")
        print(f"  Accepted:  {stats['accepted']}")
        print(f"  Edited:    {stats['edited']}")
        print(f"  Rejected:  {stats['rejected']}")
        
        if stats['total'] > 0:
            agreement = (stats['accepted'] / stats['total']) * 100
            print(f"AI Agreement Rate: {agreement:.1f}%")
    
    def list_corrected_cases(self) -> List[Dict[str, Any]]:
        """List cases where AI was corrected (Edited or Rejected)."""
        content = self.log_file.read_text(encoding="utf-8")
        corrected = []
        
        sections = content.split('## Case ')
        for section in sections[1:]:  # Skip header
            lines = section.strip().split('\n')
            if not lines:
                continue
            
            # Parse case ID and title
            first_line = lines[0]
            if ':' in first_line:
                case_id_str = first_line.split(':')[0].strip()
                case_title = first_line.split(':', 1)[1].strip()
            else:
                continue
            
            decision = ""
            for line in lines:
                if '**Human Decision:**' in line:
                    decision = line.split('**Human Decision:**')[1].strip()
                    break
            
            if decision in [ReviewStatus.EDITED, ReviewStatus.REJECTED]:
                # Extract AI fault and corrected fault
                ai_fault = ""
                corrected_fault = ""
                for line in lines:
                    if '**Predicted Fault:**' in line:
                        ai_fault = line.split('**Predicted Fault:**')[1].strip()
                    if '**Corrected Fault:**' in line:
                        corrected_fault = line.split('**Corrected Fault:**')[1].strip()
                
                corrected.append({
                    "case_id": int(case_id_str),
                    "title": case_title,
                    "decision": decision,
                    "ai_fault": ai_fault,
                    "corrected_fault": corrected_fault
                })
        
        return corrected


def interactive_review(case_id: int, case_title: str, 
                       ai_diagnosis: DiagnosisResult) -> None:
    """Interactive CLI for human review."""
    review = HumanReview()
    
    print("\n" + "=" * 60)
    print(f"HUMAN REVIEW - Case {case_id}: {case_title}")
    print("=" * 60)
    print(f"AI Predicted Fault: {ai_diagnosis.predicted_fault}")
    print(f"Confidence: {ai_diagnosis.confidence:.2f}")
    print(f"Reasoning: {ai_diagnosis.reasoning_summary}")
    print(f"Recommended Fix: {ai_diagnosis.recommended_fix}")
    print(f"Commands: {', '.join(ai_diagnosis.commands) if ai_diagnosis.commands else 'None'}")
    
    print("\nOptions:")
    print("  1. Accepted - AI diagnosis is correct")
    print("  2. Edited - AI partially correct, needs correction")
    print("  3. Rejected - AI diagnosis is wrong")
    
    while True:
        choice = input("\nDecision (1/2/3): ").strip()
        if choice in ['1', '2', '3']:
            break
        print("Invalid choice. Enter 1, 2, or 3.")
    
    decision_map = {'1': ReviewStatus.ACCEPTED, '2': ReviewStatus.EDITED, '3': ReviewStatus.REJECTED}
    decision = decision_map[choice]
    
    notes = input("Notes (optional): ").strip()
    
    corrected_fault = ""
    corrected_confidence = 0.0
    corrected_reasoning = ""
    corrected_fix = ""
    corrected_commands = []
    
    if decision == ReviewStatus.EDITED:
        print("\n--- Provide Corrections ---")
        corrected_fault = input("Corrected Fault: ").strip()
        corrected_confidence = float(input("Corrected Confidence (0-1): ").strip() or "0.9")
        corrected_reasoning = input("Corrected Reasoning: ").strip()
        corrected_fix = input("Corrected Fix: ").strip()
        cmd_input = input("Corrected Commands (comma-separated): ").strip()
        corrected_commands = [c.strip() for c in cmd_input.split(',') if c.strip()]
    elif decision == ReviewStatus.REJECTED:
        print("\n--- Provide Correct Diagnosis ---")
        corrected_fault = input("Correct Fault: ").strip()
        corrected_confidence = float(input("Confidence (0-1): ").strip() or "0.9")
        corrected_reasoning = input("Reasoning: ").strip()
        corrected_fix = input("Fix: ").strip()
        cmd_input = input("Commands (comma-separated): ").strip()
        corrected_commands = [c.strip() for c in cmd_input.split(',') if c.strip()]
    
    review.log_review(
        case_id=case_id,
        case_title=case_title,
        ai_diagnosis=ai_diagnosis,
        human_decision=decision,
        human_notes=notes,
        corrected_fault=corrected_fault,
        corrected_confidence=corrected_confidence,
        corrected_reasoning=corrected_reasoning,
        corrected_fix=corrected_fix,
        corrected_commands=corrected_commands
    )