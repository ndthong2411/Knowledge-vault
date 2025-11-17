#!/usr/bin/env python3
"""
Comprehensive Test Suite for Knowledge Vault v2.0
Tests code structure, syntax, and basic functionality without dependencies
"""
import sys
import ast
import re
from pathlib import Path
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class CodeAnalyzer:
    """Analyze Python code structure and quality"""

    def __init__(self):
        self.results = {
            'syntax_valid': [],
            'syntax_errors': [],
            'functions': defaultdict(list),
            'classes': defaultdict(list),
            'lines_of_code': {},
            'docstrings': {},
            'imports': defaultdict(list)
        }

    def analyze_file(self, filepath: Path):
        """Analyze a single Python file"""
        print(f"\n📄 Analyzing: {filepath.name}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()

            # Parse AST
            tree = ast.parse(code, filename=str(filepath))
            self.results['syntax_valid'].append(filepath.name)
            print(f"  ✅ Syntax: Valid")

            # Count lines
            lines = code.split('\n')
            loc = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
            self.results['lines_of_code'][filepath.name] = loc
            print(f"  📊 Lines of Code: {loc}")

            # Analyze structure
            functions = []
            classes = []
            has_docstring = False

            for node in ast.walk(tree):
                # Functions
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)

                # Classes
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)

                # Module docstring
                if isinstance(node, ast.Module) and ast.get_docstring(node):
                    has_docstring = True

            self.results['functions'][filepath.name] = functions
            self.results['classes'][filepath.name] = classes
            self.results['docstrings'][filepath.name] = has_docstring

            print(f"  🔧 Functions: {len(functions)}")
            print(f"  📦 Classes: {len(classes)}")
            print(f"  📝 Has Docstring: {'✅' if has_docstring else '❌'}")

            # Check for imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

            self.results['imports'][filepath.name] = imports
            print(f"  📥 Imports: {len(imports)} modules")

        except SyntaxError as e:
            self.results['syntax_errors'].append((filepath.name, str(e)))
            print(f"  ❌ Syntax Error: {e}")
        except Exception as e:
            print(f"  ⚠️  Analysis Error: {e}")

    def print_summary(self):
        """Print analysis summary"""
        print("\n" + "=" * 70)
        print("📊 CODE ANALYSIS SUMMARY")
        print("=" * 70)

        # Syntax
        print(f"\n✅ Valid Syntax: {len(self.results['syntax_valid'])} files")
        for file in self.results['syntax_valid']:
            print(f"   - {file}")

        if self.results['syntax_errors']:
            print(f"\n❌ Syntax Errors: {len(self.results['syntax_errors'])} files")
            for file, error in self.results['syntax_errors']:
                print(f"   - {file}: {error}")

        # Lines of Code
        total_loc = sum(self.results['lines_of_code'].values())
        print(f"\n📊 Total Lines of Code: {total_loc}")
        for file, loc in sorted(self.results['lines_of_code'].items(),
                               key=lambda x: x[1], reverse=True):
            print(f"   - {file}: {loc} lines")

        # Functions
        total_functions = sum(len(f) for f in self.results['functions'].values())
        print(f"\n🔧 Total Functions: {total_functions}")
        for file, funcs in self.results['functions'].items():
            if funcs:
                print(f"   - {file}: {len(funcs)} functions")

        # Classes
        total_classes = sum(len(c) for c in self.results['classes'].values())
        print(f"\n📦 Total Classes: {total_classes}")
        for file, classes in self.results['classes'].items():
            if classes:
                print(f"   - {file}: {', '.join(classes)}")

        # Documentation
        documented = sum(1 for has_doc in self.results['docstrings'].values() if has_doc)
        print(f"\n📝 Documentation: {documented}/{len(self.results['docstrings'])} files with docstrings")


def test_database_methods():
    """Test database.py has all required methods"""
    print("\n" + "=" * 70)
    print("🧪 TESTING DATABASE METHODS")
    print("=" * 70)

    db_file = project_root / 'src' / 'database.py'

    with open(db_file, 'r') as f:
        content = f.read()

    required_methods = {
        # Original methods
        'create_note': False,
        'get_note': False,
        'update_note': False,
        'delete_note': False,
        'full_text_search': False,
        'save_embedding': False,
        'get_note_tags': False,

        # V2.0 methods - Folders
        'create_folder': False,
        'get_all_folders': False,
        'move_note_to_folder': False,
        'get_notes_in_folder': False,
        'delete_folder': False,

        # V2.0 methods - Backlinks
        'add_note_link': False,
        'get_note_links': False,
        'remove_note_link': False,
        'get_graph_data': False,

        # V2.0 methods - Favorites
        'toggle_favorite': False,
        'get_favorite_notes': False,

        # V2.0 methods - Versions
        'save_version': False,
        'get_note_versions': False,
        'restore_version': False,

        # V2.0 methods - Templates
        'get_all_templates': False,
        'get_template': False,
        'create_template': False,
        'delete_template': False,

        # V2.0 methods - Daily Notes
        'get_or_create_daily_note': False,
        'get_all_daily_notes': False,
    }

    for method in required_methods:
        pattern = rf'def {method}\('
        if re.search(pattern, content):
            required_methods[method] = True
            print(f"  ✅ {method}")
        else:
            print(f"  ❌ {method} - NOT FOUND")

    implemented = sum(1 for v in required_methods.values() if v)
    total = len(required_methods)
    percentage = (implemented / total) * 100

    print(f"\n📊 Implementation: {implemented}/{total} methods ({percentage:.1f}%)")

    return all(required_methods.values())


def test_backlinks_features():
    """Test backlinks.py has required features"""
    print("\n" + "=" * 70)
    print("🧪 TESTING BACKLINKS FEATURES")
    print("=" * 70)

    backlinks_file = project_root / 'src' / 'backlinks.py'

    with open(backlinks_file, 'r') as f:
        content = f.read()

    required_features = {
        'parse_links': False,
        'process_note_links': False,
        'render_content_with_links': False,
        'get_orphan_notes': False,
        'get_most_linked_notes': False,
        'suggest_links': False,
        'get_broken_links': False,
        'bulk_update_links': False,
    }

    for feature in required_features:
        pattern = rf'def {feature}\('
        if re.search(pattern, content):
            required_features[feature] = True
            print(f"  ✅ {feature}")
        else:
            print(f"  ❌ {feature} - NOT FOUND")

    # Check for wiki link pattern
    if r'\[\[([^\]]+)\]\]' in content:
        print(f"  ✅ Wiki-style link pattern detected")
    else:
        print(f"  ❌ Wiki-style link pattern - NOT FOUND")

    implemented = sum(1 for v in required_features.values() if v)
    total = len(required_features)
    percentage = (implemented / total) * 100

    print(f"\n📊 Implementation: {implemented}/{total} features ({percentage:.1f}%)")

    return all(required_features.values())


def test_export_import_formats():
    """Test export_import.py supports all formats"""
    print("\n" + "=" * 70)
    print("🧪 TESTING EXPORT/IMPORT FORMATS")
    print("=" * 70)

    ei_file = project_root / 'src' / 'export_import.py'

    with open(ei_file, 'r') as f:
        content = f.read()

    required_methods = {
        'export_note_markdown': False,
        'export_note_json': False,
        'export_all_notes_zip': False,
        'export_to_obsidian_format': False,
        'import_note_markdown': False,
        'import_note_json': False,
        'import_from_zip': False,
        'import_from_obsidian_vault': False,
        'import_from_notion': False,
    }

    for method in required_methods:
        pattern = rf'def {method}\('
        if re.search(pattern, content):
            required_methods[method] = True
            print(f"  ✅ {method}")
        else:
            print(f"  ❌ {method} - NOT FOUND")

    implemented = sum(1 for v in required_methods.values() if v)
    total = len(required_methods)
    percentage = (implemented / total) * 100

    print(f"\n📊 Implementation: {implemented}/{total} methods ({percentage:.1f}%)")

    return all(required_methods.values())


def test_migration_script():
    """Test migration script structure"""
    print("\n" + "=" * 70)
    print("🧪 TESTING MIGRATION SCRIPT")
    print("=" * 70)

    migration_file = project_root / 'scripts' / 'migrate_db.py'

    with open(migration_file, 'r') as f:
        content = f.read()

    checks = {
        'has_folders_table': 'CREATE TABLE IF NOT EXISTS folders' in content,
        'has_note_links_table': 'CREATE TABLE IF NOT EXISTS note_links' in content,
        'has_note_versions_table': 'CREATE TABLE IF NOT EXISTS note_versions' in content,
        'has_templates_table': 'CREATE TABLE IF NOT EXISTS templates' in content,
        'has_is_favorite_column': 'is_favorite' in content,
        'has_is_daily_note_column': 'is_daily_note' in content,
        'has_folder_id_column': 'folder_id' in content,
        'has_default_templates': 'Meeting Notes' in content,
        'has_default_folders': 'Personal' in content or 'Work' in content,
    }

    for check, passed in checks.items():
        if passed:
            print(f"  ✅ {check}")
        else:
            print(f"  ❌ {check}")

    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    percentage = (passed / total) * 100

    print(f"\n📊 Migration Checks: {passed}/{total} ({percentage:.1f}%)")

    return all(checks.values())


def count_project_stats():
    """Count overall project statistics"""
    print("\n" + "=" * 70)
    print("📈 PROJECT STATISTICS")
    print("=" * 70)

    # Count files
    py_files = list(project_root.rglob('*.py'))
    py_files = [f for f in py_files if '__pycache__' not in str(f) and 'venv' not in str(f)]

    md_files = list(project_root.rglob('*.md'))
    sh_files = list(project_root.rglob('*.sh'))

    print(f"\n📁 File Counts:")
    print(f"   - Python files: {len(py_files)}")
    print(f"   - Markdown files: {len(md_files)}")
    print(f"   - Shell scripts: {len(sh_files)}")

    # Count lines in src/
    src_dir = project_root / 'src'
    src_files = list(src_dir.glob('*.py'))

    total_lines = 0
    for f in src_files:
        with open(f, 'r') as file:
            lines = file.readlines()
            loc = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
            total_lines += loc
            print(f"   - {f.name}: {loc} lines")

    print(f"\n📊 Total Production Code (src/): {total_lines} lines")

    # New files in v2.0
    new_files = ['backlinks.py', 'export_import.py']
    new_lines = 0
    for filename in new_files:
        filepath = src_dir / filename
        if filepath.exists():
            with open(filepath, 'r') as f:
                lines = f.readlines()
                loc = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
                new_lines += loc

    print(f"\n🆕 New Code in v2.0: {new_lines} lines")


def main():
    """Run all tests"""
    print("=" * 70)
    print("🚀 KNOWLEDGE VAULT v2.0 - COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    # 1. Code Analysis
    analyzer = CodeAnalyzer()

    src_files = [
        'config.py',
        'src/database.py',
        'src/storage.py',
        'src/search_engine.py',
        'src/tagging.py',
        'src/backlinks.py',
        'src/export_import.py',
        'src/utils.py',
    ]

    for filepath in src_files:
        full_path = project_root / filepath
        if full_path.exists():
            analyzer.analyze_file(full_path)

    analyzer.print_summary()

    # 2. Feature Tests
    db_ok = test_database_methods()
    backlinks_ok = test_backlinks_features()
    export_ok = test_export_import_formats()
    migration_ok = test_migration_script()

    # 3. Project Stats
    count_project_stats()

    # Final Summary
    print("\n" + "=" * 70)
    print("🎯 FINAL RESULTS")
    print("=" * 70)

    results = {
        'Database Methods': db_ok,
        'Backlinks Features': backlinks_ok,
        'Export/Import': export_ok,
        'Migration Script': migration_ok,
    }

    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test}: {status}")

    all_passed = all(results.values())

    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("=" * 70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
