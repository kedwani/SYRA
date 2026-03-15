#!/usr/bin/env python3
"""
SYRA Code Review Automation Script
Scans Django codebase for common issues, security concerns, and performance problems.
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple


class CodeReviewScanner:
    """Automated code review scanner for Django projects."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues = defaultdict(list)
        self.stats = {
            "files_scanned": 0,
            "total_lines": 0,
            "python_files": 0,
            "template_files": 0,
        }

    def scan_all(self):
        """Run all scanning checks."""
        print("🔍 Starting SYRA Code Review Scan...")
        print(f"📁 Project root: {self.project_root}\n")

        self.scan_python_files()
        self.scan_templates()
        self.scan_settings()
        self.generate_report()

    def scan_python_files(self):
        """Scan all Python files for common issues."""
        print("🐍 Scanning Python files...")

        for py_file in self.project_root.rglob("*.py"):
            # Skip migrations and pycache
            if "migrations" in str(py_file) or "__pycache__" in str(py_file):
                continue

            self.stats["python_files"] += 1
            self.stats["files_scanned"] += 1

            with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")
                self.stats["total_lines"] += len(lines)

                # Check for security issues
                self._check_security(py_file, content, lines)

                # Check for performance issues
                self._check_performance(py_file, content, lines)

                # Check for code quality
                self._check_code_quality(py_file, content, lines)

    def _check_security(self, filepath: Path, content: str, lines: List[str]):
        """Check for security vulnerabilities."""
        relative_path = filepath.relative_to(self.project_root)

        # Check for hardcoded secrets
        secret_patterns = [
            (
                r'SECRET_KEY\s*=\s*[\'"](?!<|{{)[^\'"]+[\'"]',
                "Hardcoded SECRET_KEY detected",
            ),
            (r'PASSWORD\s*=\s*[\'"][^\'"]+[\'"]', "Hardcoded password detected"),
            (r'API_KEY\s*=\s*[\'"][^\'"]+[\'"]', "Hardcoded API key detected"),
        ]

        for pattern, message in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                self.issues["security"].append(
                    {
                        "severity": "critical",
                        "file": str(relative_path),
                        "message": message,
                        "category": "hardcoded_secrets",
                    }
                )

        # Check for SQL injection risks
        if "raw(" in content or "extra(" in content:
            for i, line in enumerate(lines, 1):
                if "raw(" in line or "extra(" in line:
                    self.issues["security"].append(
                        {
                            "severity": "high",
                            "file": str(relative_path),
                            "line": i,
                            "message": "Potential SQL injection: raw SQL query detected",
                            "category": "sql_injection",
                        }
                    )

        # Check for missing permission classes
        if "ViewSet" in content or "APIView" in content:
            if "permission_classes" not in content:
                self.issues["security"].append(
                    {
                        "severity": "high",
                        "file": str(relative_path),
                        "message": "ViewSet/APIView without permission_classes",
                        "category": "missing_permissions",
                    }
                )

        # Check for AllowAny usage
        if "AllowAny" in content:
            for i, line in enumerate(lines, 1):
                if "AllowAny" in line:
                    self.issues["security"].append(
                        {
                            "severity": "medium",
                            "file": str(relative_path),
                            "line": i,
                            "message": "AllowAny permission detected - verify this is intentional",
                            "category": "permissive_access",
                        }
                    )

    def _check_performance(self, filepath: Path, content: str, lines: List[str]):
        """Check for performance issues."""
        relative_path = filepath.relative_to(self.project_root)

        # Check for N+1 queries
        if "for " in content and ".objects" in content:
            # Look for loops that access related objects
            loop_pattern = r"for\s+\w+\s+in\s+.*\.all\(\)"
            if re.search(loop_pattern, content):
                for i, line in enumerate(lines, 1):
                    if re.search(loop_pattern, line):
                        # Check if select_related or prefetch_related is used
                        context = "\n".join(
                            lines[max(0, i - 5) : min(len(lines), i + 5)]
                        )
                        if (
                            "select_related" not in context
                            and "prefetch_related" not in context
                        ):
                            self.issues["performance"].append(
                                {
                                    "severity": "high",
                                    "file": str(relative_path),
                                    "line": i,
                                    "message": "Potential N+1 query - consider using select_related/prefetch_related",
                                    "category": "n_plus_1",
                                }
                            )

        # Check for missing database indexes
        if "models.py" in str(filepath):
            if "class Meta:" in content:
                # Check if frequently queried fields have indexes
                if "index_together" not in content and "indexes" not in content:
                    self.issues["performance"].append(
                        {
                            "severity": "medium",
                            "file": str(relative_path),
                            "message": "Consider adding database indexes for frequently queried fields",
                            "category": "missing_indexes",
                        }
                    )

    def _check_code_quality(self, filepath: Path, content: str, lines: List[str]):
        """Check for code quality issues."""
        relative_path = filepath.relative_to(self.project_root)

        # Check for long functions
        function_pattern = r"^\s*def\s+(\w+)\("
        current_function = None
        function_start = 0

        for i, line in enumerate(lines, 1):
            match = re.match(function_pattern, line)
            if match:
                if current_function and (i - function_start) > 50:
                    self.issues["code_quality"].append(
                        {
                            "severity": "low",
                            "file": str(relative_path),
                            "line": function_start,
                            "message": f"Long function detected: {current_function} ({i - function_start} lines)",
                            "category": "long_function",
                        }
                    )
                current_function = match.group(1)
                function_start = i

        # Check for commented code
        commented_lines = [
            i
            for i, line in enumerate(lines, 1)
            if line.strip().startswith("#") and len(line.strip()) > 20
        ]
        if len(commented_lines) > 10:
            self.issues["code_quality"].append(
                {
                    "severity": "low",
                    "file": str(relative_path),
                    "message": f"High number of commented lines ({len(commented_lines)}) - consider cleanup",
                    "category": "commented_code",
                }
            )

        # Check for TODO/FIXME comments
        for i, line in enumerate(lines, 1):
            if "TODO" in line or "FIXME" in line:
                self.issues["code_quality"].append(
                    {
                        "severity": "low",
                        "file": str(relative_path),
                        "line": i,
                        "message": f"Unresolved TODO/FIXME: {line.strip()}",
                        "category": "todo_fixme",
                    }
                )

    def scan_templates(self):
        """Scan HTML templates for issues."""
        print("📄 Scanning templates...")

        for html_file in self.project_root.rglob("*.html"):
            self.stats["template_files"] += 1
            self.stats["files_scanned"] += 1

            with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")
                relative_path = html_file.relative_to(self.project_root)

                # Check for missing CSRF tokens in forms
                if "<form" in content.lower():
                    if (
                        "{% csrf_token %}" not in content
                        and "csrf_token" not in content
                    ):
                        self.issues["security"].append(
                            {
                                "severity": "critical",
                                "file": str(relative_path),
                                "message": "Form without CSRF token detected",
                                "category": "missing_csrf",
                            }
                        )

                # Check for inline JavaScript (XSS risk)
                if "<script>" in content and "{{" in content:
                    self.issues["security"].append(
                        {
                            "severity": "medium",
                            "file": str(relative_path),
                            "message": "Template variable in inline script - potential XSS risk",
                            "category": "xss_risk",
                        }
                    )

                # Check for accessibility issues
                if "<img" in content:
                    img_pattern = r"<img[^>]*>"
                    for match in re.finditer(img_pattern, content):
                        if "alt=" not in match.group():
                            self.issues["accessibility"].append(
                                {
                                    "severity": "medium",
                                    "file": str(relative_path),
                                    "message": "Image without alt attribute",
                                    "category": "missing_alt",
                                }
                            )

                # Check for deprecated HTML
                deprecated = ["<center>", "<font>", "<marquee>"]
                for tag in deprecated:
                    if tag in content.lower():
                        self.issues["code_quality"].append(
                            {
                                "severity": "low",
                                "file": str(relative_path),
                                "message": f"Deprecated HTML tag: {tag}",
                                "category": "deprecated_html",
                            }
                        )

    def scan_settings(self):
        """Scan Django settings for security issues."""
        print("⚙️  Scanning settings...")

        settings_file = self.project_root / "syra" / "settings.py"
        if not settings_file.exists():
            return

        with open(settings_file, "r", encoding="utf-8") as f:
            content = f.read()

            # Check DEBUG setting
            if re.search(r"DEBUG\s*=\s*True", content):
                self.issues["security"].append(
                    {
                        "severity": "critical",
                        "file": "syra/settings.py",
                        "message": "DEBUG=True in production - this must be False in production",
                        "category": "debug_mode",
                    }
                )

            # Check for security middleware
            required_middleware = [
                "SecurityMiddleware",
                "SessionMiddleware",
                "CsrfViewMiddleware",
                "AuthenticationMiddleware",
            ]

            for middleware in required_middleware:
                if middleware not in content:
                    self.issues["security"].append(
                        {
                            "severity": "high",
                            "file": "syra/settings.py",
                            "message": f"Missing security middleware: {middleware}",
                            "category": "missing_middleware",
                        }
                    )

            # Check for HTTPS settings
            https_settings = [
                "SECURE_SSL_REDIRECT",
                "SESSION_COOKIE_SECURE",
                "CSRF_COOKIE_SECURE",
            ]

            for setting in https_settings:
                if setting not in content:
                    self.issues["security"].append(
                        {
                            "severity": "medium",
                            "file": "syra/settings.py",
                            "message": f"Missing HTTPS security setting: {setting}",
                            "category": "https_config",
                        }
                    )

    def generate_report(self):
        """Generate and display the code review report."""
        print("\n" + "=" * 80)
        print("📊 SYRA CODE REVIEW REPORT")
        print("=" * 80)

        # Summary stats
        print(f"\n📈 Scan Statistics:")
        print(f"  • Files scanned: {self.stats['files_scanned']}")
        print(f"  • Python files: {self.stats['python_files']}")
        print(f"  • Template files: {self.stats['template_files']}")
        print(f"  • Total lines: {self.stats['total_lines']:,}")

        # Issues by severity
        severity_counts = defaultdict(int)
        for category_issues in self.issues.values():
            for issue in category_issues:
                severity_counts[issue["severity"]] += 1

        print(f"\n🚨 Issues Found:")
        print(f"  • Critical: {severity_counts['critical']}")
        print(f"  • High: {severity_counts['high']}")
        print(f"  • Medium: {severity_counts['medium']}")
        print(f"  • Low: {severity_counts['low']}")

        # Detailed issues by category
        print("\n" + "=" * 80)
        print("📋 DETAILED ISSUES")
        print("=" * 80)

        for category, category_issues in sorted(self.issues.items()):
            if not category_issues:
                continue

            print(f"\n🔍 {category.upper()} ({len(category_issues)} issues)")
            print("-" * 80)

            # Group by severity
            by_severity = defaultdict(list)
            for issue in category_issues:
                by_severity[issue["severity"]].append(issue)

            for severity in ["critical", "high", "medium", "low"]:
                issues = by_severity.get(severity, [])
                if not issues:
                    continue

                severity_icon = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🟢",
                }[severity]

                print(f"\n  {severity_icon} {severity.upper()}")
                for issue in issues[:10]:  # Limit to 10 per severity
                    line_info = f":{issue['line']}" if "line" in issue else ""
                    print(f"    • {issue['file']}{line_info}")
                    print(f"      {issue['message']}")

                if len(issues) > 10:
                    print(f"    ... and {len(issues) - 10} more")

        # Recommendations
        print("\n" + "=" * 80)
        print("💡 PRIORITY RECOMMENDATIONS")
        print("=" * 80)

        recommendations = []

        if severity_counts["critical"] > 0:
            recommendations.append(
                "1. Fix all CRITICAL issues immediately - these are security vulnerabilities"
            )

        if any(
            "n_plus_1" in issue["category"]
            for issues in self.issues.values()
            for issue in issues
        ):
            recommendations.append(
                "2. Optimize database queries - add select_related/prefetch_related"
            )

        if any(
            "missing_csrf" in issue["category"]
            for issues in self.issues.values()
            for issue in issues
        ):
            recommendations.append("3. Add CSRF tokens to all forms")

        if any(
            "missing_permissions" in issue["category"]
            for issues in self.issues.values()
            for issue in issues
        ):
            recommendations.append("4. Add permission classes to all API endpoints")

        if any(
            "missing_alt" in issue["category"]
            for issues in self.issues.values()
            for issue in issues
        ):
            recommendations.append("5. Improve accessibility - add alt text to images")

        for i, rec in enumerate(recommendations[:5], 1):
            print(f"\n{rec}")

        # Save JSON report
        report = {
            "stats": self.stats,
            "severity_counts": dict(severity_counts),
            "issues": {k: v for k, v in self.issues.items()},
        }

        report_file = self.project_root / "code_review_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n\n💾 Full report saved to: {report_file}")
        print("=" * 80)


if __name__ == "__main__":
    import sys

    # Get project root from command line or use current directory
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."

    scanner = CodeReviewScanner(project_root)
    scanner.scan_all()
