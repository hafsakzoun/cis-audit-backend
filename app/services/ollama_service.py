# Script generation logic (incl. language detection)
import subprocess

def detect_language(audit_text):
    prompt = f"""
You are an AI assistant that classifies audit instructions into the most appropriate script or query language.

Respond with only one word: sql, bash, python, powershell, or other.

### AUDIT INSTRUCTIONS ###
{audit_text}
"""
    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.2"],
            input=prompt.encode(),
            capture_output=True,
        )
        return result.stdout.decode().strip().lower()
    except Exception as e:
        print(f"⚠️ Language detection failed: {e}")
        return "other"

def generate_audit_code(audit_text, default_value="", lang_hint="bash"):
    prompt = f"""
You are a cybersecurity automation assistant.

Based ONLY on the AUDIT INSTRUCTIONS below, and optionally the DEFAULT VALUE (if provided), generate a minimal, executable script that:
- Checks the condition described
- Prints whether the check passes or fails
- Uses the best-fit scripting/query language
- Is clean, short, and production-ready

Wrap the output in a fenced code block using the correct language label.

### AUDIT INSTRUCTIONS ###
{audit_text}

{f"### DEFAULT VALUE ###\n{default_value}" if default_value else ""}
"""
    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.2"],
            input=prompt.encode(),
            capture_output=True
        )
        code = result.stdout.decode().strip()

        # Ensure the code block starts with a language fence
        if not code.startswith("```"):
            code = f"```{lang_hint}\n{code.strip()}\n```"
        return code
    except Exception as e:
        return f"```{lang_hint}\n# Error generating audit code\n```"

def generate_script_from_controls(controls, category, editor_name, version):
    script_header = f"""# CIS Compliance Audit Script
# Generated from {editor_name} {category} Benchmark v{version}
# Contains checks for {len(controls)} controls

# Run each code block in its appropriate environment (e.g., Bash, SQL, PowerShell)
"""

    script_lines = [script_header]

    for hit in controls:
        src = hit["_source"]
        rule_id = src.get("Identifier", "UNKNOWN")
        rule = src.get("Rule", "").strip()
        audit = src.get("Audit", "").strip()
        default_value = src.get("Default Value", "").strip()

        if not audit:
            continue

        lang = detect_language(audit)
        lang = lang if lang in {"bash", "sql", "python", "powershell"} else "bash"

        script_lines.append(f"\n# === Rule {rule_id} ===")
        script_lines.append(f"# {rule}\n")

        code_block = generate_audit_code(audit, default_value, lang)
        script_lines.append(code_block)

    return "\n".join(script_lines)