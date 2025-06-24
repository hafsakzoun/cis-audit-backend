def parse_notices(notices):
    results = []
    for msg in notices:
        if "Control" in msg and ("PASS" in msg or "FAIL" in msg):
            try:
                parts = msg.split(':', 2)
                rule = parts[1].strip() + ':'
                detail = parts[2].strip()

                status = 'PASS' if 'PASS' in detail else 'FAIL'
                explanation = detail.split('-', 1)[1].strip() if '-' in detail else ""
                current_value = explanation.split('expected')[0].strip().rstrip(',') if 'expected' in explanation else explanation
                expected_value = explanation.split('expected')[1].strip(': ').strip() if 'expected' in explanation else ""

                results.append([rule, status, current_value, expected_value])
            except:
                continue
    return results
