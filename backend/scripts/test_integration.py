from src.evidence_parser import load_evidence
from src.diagnosis import diagnose, format_diagnosis
from src.rule_checker import run_rule_checker
from src.human_review import HumanReview
from src.dashboard import generate_dashboard

# Test case 1
evidence = load_evidence(1)
print('=== Rule Checker ===')
results = run_rule_checker(evidence)
for r in results:
    print(f"  [{r['severity']}] {r['check']}: {r['message']}")

print('\n=== AI Diagnosis ===')
result = diagnose(evidence, 1)
print(format_diagnosis(result))

print('\n=== Dashboard ===')
dashboard_file = generate_dashboard()
print(f'Generated: {dashboard_file}')