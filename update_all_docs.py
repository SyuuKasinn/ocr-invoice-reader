#!/usr/bin/env python3
"""
Batch update all documentation files to reflect Qwen Direct changes
"""
import re
from pathlib import Path

def update_file(filepath):
    """Update a single markdown file"""
    print(f"Updating {filepath}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    changes = []

    # 1. Update model naming: qwen2.5:Xb -> Xb
    patterns = [
        (r'qwen2\.5:14b', '14b', 'Model naming qwen2.5:14b -> 14b'),
        (r'qwen2\.5:7b', '7b', 'Model naming qwen2.5:7b -> 7b'),
        (r'qwen2\.5:3b', '3b', 'Model naming qwen2.5:3b -> 3b'),
        (r'qwen2\.5:0\.5b', '3b', 'Model naming qwen2.5:0.5b -> 3b'),
        (r'qwen2\.5:32b', '14b', 'Model naming qwen2.5:32b -> 14b (max available)'),
    ]

    for pattern, replacement, description in patterns:
        new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        if new_content != content:
            changes.append(description)
            content = new_content

    # 2. Remove --auto-setup-ollama flag
    pattern = r'--auto-setup-ollama\s*'
    new_content = re.sub(pattern, '', content)
    if new_content != content:
        changes.append('Removed --auto-setup-ollama flag')
        content = new_content

    # 3. Update version 2.3.1 -> 2.3.2
    pattern = r'\*\*Version\*\*:\s*2\.3\.1'
    new_content = re.sub(pattern, '**Version**: 2.3.2', content)
    if new_content != content:
        changes.append('Updated version 2.3.1 -> 2.3.2')
        content = new_content

    pattern = r'Version:\s*2\.3\.1'
    new_content = re.sub(pattern, 'Version: 2.3.2', content)
    if new_content != content:
        changes.append('Updated version 2.3.1 -> 2.3.2')
        content = new_content

    # 4. Update Python API imports
    pattern = r'from ocr_invoice_reader\.utils\.llm_processor import create_llm_processor'
    replacement = 'from ocr_invoice_reader.utils.qwen_direct_processor import create_qwen_processor'
    new_content = re.sub(pattern, replacement, content)
    if new_content != content:
        changes.append('Updated import to qwen_direct_processor')
        content = new_content

    # 5. Update create_llm_processor calls
    pattern = r"create_llm_processor\(['\"]qwen2\.5:(\d+)b['\"]\)"
    replacement = r"create_qwen_processor(model_size='\1b', use_gpu=True, quantization='int4')"
    new_content = re.sub(pattern, replacement, content)
    if new_content != content:
        changes.append('Updated create_llm_processor to create_qwen_processor')
        content = new_content

    # 6. Update Ollama references in descriptions
    pattern = r'requires? Ollama'
    replacement = 'uses Qwen Direct'
    new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    if new_content != content:
        changes.append('Updated Ollama references')
        content = new_content

    # 7. Update installation commands
    pattern = r'pip install -e \.\s*$'
    replacement = 'bash scripts/install.sh'
    # Don't replace all, just suggest in comments

    # Write back if changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  [OK] Updated {len(changes)} changes:")
        for change in changes:
            print(f"    - {change}")
        return True
    else:
        print(f"  [SKIP] No changes needed")
        return False

def main():
    """Main update function"""
    print("="*70)
    print("Updating all documentation files")
    print("="*70)
    print()

    # Get all markdown files
    docs_dir = Path('docs')
    guides_dir = Path('guides')

    files_to_update = []

    if docs_dir.exists():
        files_to_update.extend(docs_dir.glob('*.md'))

    if guides_dir.exists():
        files_to_update.extend(guides_dir.glob('*.md'))

    # Exclude OLLAMA_GPU_SETUP.md (already marked as deprecated)
    files_to_update = [f for f in files_to_update if 'OLLAMA' not in f.name]

    updated_count = 0
    total_count = len(files_to_update)

    for filepath in sorted(files_to_update):
        if update_file(filepath):
            updated_count += 1
        print()

    print("="*70)
    print(f"Summary: Updated {updated_count}/{total_count} files")
    print("="*70)
    print()
    print("Next steps:")
    print("  1. Review changes: git diff")
    print("  2. Commit: git add docs/ guides/ && git commit -m 'docs: Update all docs to Qwen Direct'")
    print("  3. Push: git push origin main")

if __name__ == '__main__':
    main()
