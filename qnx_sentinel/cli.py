"""
QNX Sentinel - Unified Command Line Interface
Provides subcommands: audit, analyze, build-assist, build, test, diagnose, serve, full-pipeline.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from qnx_sentinel import __version__
from qnx_sentinel.audit.sdk_auditor import SDKAuditor
from qnx_sentinel.analyzer.project_analyzer import ProjectAnalyzer
from qnx_sentinel.analyzer.compatibility_engine import CompatibilityEngine
from qnx_sentinel.builder.config_assistant import ConfigAssistant
from qnx_sentinel.builder.build_runner import BuildRunner
from qnx_sentinel.tester.test_runner import TestRunner
from qnx_sentinel.diagnostics.error_explainer import ErrorExplainer
from qnx_sentinel.reporter.terminal_reporter import TerminalReporter, Colors
from qnx_sentinel.reporter.json_reporter import JSONReporter
from qnx_sentinel.reporter.markdown_reporter import MarkdownReporter
from qnx_sentinel.reporter.html_reporter import HTMLReporter
from qnx_sentinel.reporter.web_dashboard import start_server
from qnx_sentinel.core.models import AnalysisReport


def cmd_audit(args: argparse.Namespace) -> int:
    """Audits the host environment for QNX SDP 8.0 setup."""
    auditor = SDKAuditor()
    sdk = auditor.audit()

    print(f"\n{Colors.BOLD}{Colors.CYAN}=== QNX SDP 8.0 Host Environment Audit ==={Colors.RESET}\n")
    if sdk.is_qnx_sdp_detected:
        print(f"  {Colors.GREEN}[+] QNX SDP 8.0 Detected:{Colors.RESET} Active")
        print(f"      Version:         {sdk.sdp_version or '8.0.0'}")
        print(f"      QNX_HOST:        {sdk.qnx_host}")
        print(f"      QNX_TARGET:      {sdk.qnx_target}")
        print(f"      Compiler Driver: {sdk.qcc_path or 'Not in PATH'}")
        if sdk.supported_targets:
            print(f"      Target Sysroots: {', '.join(sdk.supported_targets)}")
    else:
        print(f"  {Colors.YELLOW}[!] QNX SDP 8.0 is not active in this shell session.{Colors.RESET}")
        print("      QNX Sentinel will run in Host-Static Analysis and Verification Mode.")
        if sdk.env_script_suggested:
            print(f"\n  {Colors.BOLD}To activate your QNX toolchain, run:{Colors.RESET}")
            print(f"      {Colors.CYAN}{sdk.env_script_suggested}{Colors.RESET}\n")

    print(f"  Target Emulation (QEMU):  {'DETECTED (' + sdk.qemu_binary + ')' if sdk.qemu_available else 'NOT DETECTED'}")
    print(f"  Target Utility (mkqnximage): {'DETECTED' if sdk.mkqnximage_available else 'NOT DETECTED'}\n")

    print(f"{Colors.BOLD}Diagnostic Notes:{Colors.RESET}")
    for n in sdk.diagnostic_notes:
        print(f"  - {n}")
    print("")
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    """Analyzes a project directory for QNX 8.0 compatibility and structure."""
    proj_path = Path(args.project_path).resolve()
    if not proj_path.is_dir():
        print(f"{Colors.RED}Error: Project directory not found: {proj_path}{Colors.RESET}", file=sys.stderr)
        return 1

    auditor = SDKAuditor()
    sdk = auditor.audit()

    # 1. Structure analysis
    p_analyzer = ProjectAnalyzer(proj_path)
    structure = p_analyzer.analyze()

    # 2. Compatibility rules inspection
    c_engine = CompatibilityEngine()
    files_to_scan = structure.source_files + structure.header_files + structure.build_files
    findings = c_engine.scan_files(files_to_scan, proj_path)
    recommendations = c_engine.generate_recommendations(findings)

    # 3. Assemble report
    report = AnalysisReport(
        project_name=structure.project_name,
        project_path=str(proj_path),
        sdk_status=sdk,
        project_structure=structure,
        findings=findings,
        recommendations=recommendations,
    )
    report.calculate_score()

    # 4. Render output
    fmt = getattr(args, "format", "terminal")
    output_dir = getattr(args, "output_dir", None)

    if fmt in ("terminal", "all"):
        print(TerminalReporter.render_report(report))

    if output_dir or fmt in ("json", "markdown", "html", "all"):
        out_base = Path(output_dir) if output_dir else proj_path / "qnx_sentinel_reports"
        out_base.mkdir(parents=True, exist_ok=True)

        if fmt in ("json", "all"):
            json_file = JSONReporter.save(report, out_base / "qnx_analysis_report.json")
            print(f"[+] Saved JSON Report: {json_file}")

        if fmt in ("markdown", "all"):
            md_file = MarkdownReporter.save(report, out_base / "qnx_analysis_report.md")
            print(f"[+] Saved Markdown Report: {md_file}")

        if fmt in ("html", "all"):
            html_file = HTMLReporter.save(report, out_base / "qnx_analysis_report.html")
            print(f"[+] Saved Standalone HTML Report: {html_file}")

    # Check fail-under threshold
    fail_under = getattr(args, "fail_under", None)
    if fail_under is not None and report.score < fail_under:
        print(f"\n{Colors.RED}[!] FAILED: QNX Readiness Score {report.score} is below threshold {fail_under}{Colors.RESET}\n", file=sys.stderr)
        return 2

    return 0


def cmd_build_assist(args: argparse.Namespace) -> int:
    """Inspects project build setup, explains QNX requirements, and proposes changes."""
    proj_path = Path(args.project_path).resolve()
    p_analyzer = ProjectAnalyzer(proj_path)
    structure = p_analyzer.analyze()

    assistant = ConfigAssistant(proj_path)
    plans = assistant.plan_changes(structure)

    print(f"\n{Colors.BOLD}{Colors.CYAN}=== QNX 8.0 Build Configuration Assistant ==={Colors.RESET}")
    print(f"Target Project: {proj_path}\n")

    if not plans:
        print(f"{Colors.GREEN}[+] All recommended QNX 8.0 build configurations are already in place!{Colors.RESET}\n")
        return 0

    print(f"Proposed {len(plans)} configuration updates:\n")
    for name, item in plans.items():
        print(f"  {Colors.BOLD}[{item['action']}]{Colors.RESET} {Colors.CYAN}{name}{Colors.RESET}")
        print(f"    Reason: {item['reason']}")
        print(f"{Colors.DIM}--- Diff Preview ---{Colors.RESET}")
        diff_lines = item["diff"].splitlines()
        for dl in diff_lines[:15]:
            if dl.startswith("+"):
                print(f"    {Colors.GREEN}{dl}{Colors.RESET}")
            elif dl.startswith("-"):
                print(f"    {Colors.RED}{dl}{Colors.RESET}")
            else:
                print(f"    {dl}")
        if len(diff_lines) > 15:
            print(f"    {Colors.DIM}... ({len(diff_lines) - 15} more lines) ...{Colors.RESET}")
        print("")

    if getattr(args, "apply", False):
        applied = assistant.apply_plan(plans, confirmed=True)
        print(f"{Colors.GREEN}[+] Successfully applied changes:{Colors.RESET}")
        for app in applied:
            print(f"  - {app}")
        print("")
    else:
        print(f"{Colors.YELLOW}[!] DRY RUN: No files were modified.{Colors.RESET}")
        print(f"    To apply these changes safely, re-run with: {Colors.BOLD}qnx-sentinel build-assist {args.project_path} --apply{Colors.RESET}\n")

    return 0


def cmd_build(args: argparse.Namespace) -> int:
    """Executes or simulates a QNX SDP 8.0 build."""
    proj_path = Path(args.project_path).resolve()
    arch = getattr(args, "arch", "aarch64le")
    btype = getattr(args, "type", "Debug")
    dry_run = getattr(args, "dry_run", False)

    print(f"\n{Colors.BOLD}{Colors.CYAN}=== QNX SDP 8.0 Build Runner ==={Colors.RESET}")
    print(f"Project:      {proj_path}")
    print(f"Architecture: {arch}")
    print(f"Build Type:   {btype}\n")

    runner = BuildRunner(proj_path)
    res = runner.build(target_arch=arch, build_type=btype, dry_run=dry_run)

    print(f"Execution Mode:   {Colors.BOLD}{res['execution_mode']}{Colors.RESET}")
    print(f"Simulated:        {'YES' if res['is_simulated'] else 'NO (Actual QNX SDP)'}")
    print(f"Duration:         {res['duration_seconds']}s")
    print(f"Status:           {Colors.GREEN + 'SUCCESS' if res['success'] else Colors.RED + 'FAILED'} (Exit code {res['exit_code']}){Colors.RESET}\n")

    if res["stdout"]:
        print(f"{Colors.DIM}--- Build Output ---{Colors.RESET}")
        print(res["stdout"])

    if res["stderr"]:
        print(f"\n{Colors.RED}--- Build Errors ---{Colors.RESET}")
        print(res["stderr"])

    return 0 if res["success"] else 1


def cmd_test(args: argparse.Namespace) -> int:
    """Executes test verification across available QNX targets or simulation harness."""
    proj_path = Path(args.project_path).resolve()
    t_filter = getattr(args, "filter", None)
    force_sim = getattr(args, "force_simulation", False)

    print(f"\n{Colors.BOLD}{Colors.CYAN}=== QNX SDP 8.0 Test Assistant ==={Colors.RESET}")
    print(f"Project: {proj_path}\n")

    runner = TestRunner(proj_path)
    report = runner.run_tests(test_filter=t_filter, force_simulation=force_sim)

    print(report.raw_output)
    print(f"Suite:          {report.suite_name}")
    print(f"Execution Mode: {Colors.BOLD}{report.execution_mode}{Colors.RESET}")
    print(f"Architecture:   {report.target_arch}")
    print(f"Duration:       {report.duration_seconds}s")
    print(f"Results:        {Colors.GREEN}PASSED: {report.passed}{Colors.RESET} | {Colors.RED}FAILED: {report.failed}{Colors.RESET} | TOTAL: {report.total_tests}\n")

    for item in report.tests:
        status_col = Colors.GREEN if item.status == "PASSED" else Colors.RED
        print(f"  [{status_col}{item.status}{Colors.RESET}] {item.name} ({item.duration_ms}ms)")
        if item.stdout:
            print(f"      {Colors.DIM}{item.stdout}{Colors.RESET}")
        if item.error_message:
            print(f"      {Colors.RED}Error: {item.error_message}{Colors.RESET}")

    print("")
    return 0 if report.failed == 0 else 1


def cmd_diagnose(args: argparse.Namespace) -> int:
    """Parses compiler/linker logs and explains errors in QNX 8.0 context."""
    source_arg = args.log_source
    explainer = ErrorExplainer()

    p = Path(source_arg)
    if p.is_file():
        explanations = explainer.explain_file(p)
    else:
        explanations = explainer.explain_log(source_arg)

    print(f"\n{Colors.BOLD}{Colors.CYAN}=== QNX Sentinel Diagnostic Intelligence ==={Colors.RESET}\n")
    if not explanations:
        print(f"{Colors.GREEN}[+] No known QNX SDP 8.0 failure signatures identified.{Colors.RESET}\n")
        return 0

    print(f"Identified {len(explanations)} failure cause(s):\n")
    for idx, exp in enumerate(explanations, start=1):
        print(f"{Colors.BOLD}#{idx} [{exp.category}] {Colors.RED}{exp.error_signature}{Colors.RESET}")
        print(f"    Explanation: {exp.explanation}")
        print("    Remediation Steps:")
        for step in exp.remediation_steps:
            print(f"      - {step}")
        if exp.suggested_diff:
            print(f"{Colors.DIM}    Suggested Patch:\n{exp.suggested_diff}{Colors.RESET}")
        if exp.official_doc_link:
            print(f"    Official QNX Reference: {Colors.CYAN}{exp.official_doc_link}{Colors.RESET}")
        print("")

    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    """Launches local interactive Web Dashboard."""
    proj_path = Path(args.project_path).resolve()
    port = getattr(args, "port", 8080)
    no_browser = getattr(args, "no_browser", False)

    # Run quick analysis to populate initial state
    auditor = SDKAuditor()
    sdk = auditor.audit()
    p_analyzer = ProjectAnalyzer(proj_path)
    structure = p_analyzer.analyze()
    c_engine = CompatibilityEngine()
    findings = c_engine.scan_files(structure.source_files + structure.header_files + structure.build_files, proj_path)
    recommendations = c_engine.generate_recommendations(findings)

    report = AnalysisReport(
        project_name=structure.project_name,
        project_path=str(proj_path),
        sdk_status=sdk,
        project_structure=structure,
        findings=findings,
        recommendations=recommendations,
    )
    report.calculate_score()

    start_server(report, proj_path, port=port, open_browser=not no_browser)
    return 0


def cmd_full_pipeline(args: argparse.Namespace) -> int:
    """Executes the full end-to-end QNX Sentinel workflow on a project."""
    proj_path = Path(args.project_path).resolve()

    print(f"\n{Colors.BOLD}{Colors.MAGENTA}" + "=" * 80)
    print("      RUNNING QNX SENTINEL END-TO-END VERIFICATION PIPELINE")
    print("=" * 80 + f"{Colors.RESET}\n")

    # Step 1: Audit
    print(f"{Colors.BOLD}>> STEP 1: QNX SDP 8.0 Environment Audit{Colors.RESET}")
    cmd_audit(args)

    # Step 2: Analyze
    print(f"{Colors.BOLD}>> STEP 2: Compatibility & Architecture Static Analysis{Colors.RESET}")
    args.format = "all"
    args.output_dir = str(proj_path / "sentinel_output")
    cmd_analyze(args)

    # Step 3: Build Assistant Check
    print(f"{Colors.BOLD}>> STEP 3: Build Configuration Inspection{Colors.RESET}")
    args.apply = False
    cmd_build_assist(args)

    # Step 4: Build Execution / Simulation
    print(f"{Colors.BOLD}>> STEP 4: Build Compilation Verification{Colors.RESET}")
    args.arch = "aarch64le"
    args.type = "Debug"
    args.dry_run = False
    cmd_build(args)

    # Step 5: Test Execution
    print(f"{Colors.BOLD}>> STEP 5: Target Test Execution{Colors.RESET}")
    args.filter = None
    args.force_simulation = False
    cmd_test(args)

    print(f"\n{Colors.BOLD}{Colors.GREEN}[+] Pipeline execution completed! Reports saved to: {args.output_dir}{Colors.RESET}\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qnx-sentinel",
        description="QNX Sentinel — Intelligent QNX 8.0 Build, Test & Compatibility Analyzer",
    )
    parser.add_argument("--version", action="version", version=f"qnx-sentinel {__version__}")
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # audit
    p_audit = subparsers.add_parser("audit", help="Audit host environment for QNX SDP 8.0 and QEMU")

    # analyze
    p_analyze = subparsers.add_parser("analyze", help="Analyze C/C++ project for QNX 8.0 compatibility")
    p_analyze.add_argument("project_path", nargs="?", default=".", help="Path to project directory")
    p_analyze.add_argument("--format", choices=["terminal", "json", "markdown", "html", "all"], default="terminal", help="Output format")
    p_analyze.add_argument("--output-dir", help="Directory to save generated reports")
    p_analyze.add_argument("--fail-under", type=float, help="Fail if readiness score is below threshold")

    # build-assist
    p_ba = subparsers.add_parser("build-assist", help="Generate or inspect QNX 8.0 build configurations")
    p_ba.add_argument("project_path", nargs="?", default=".", help="Path to project directory")
    p_ba.add_argument("--apply", action="store_true", help="Apply proposed changes to disk with confirmation")

    # build
    p_build = subparsers.add_parser("build", help="Run QNX 8.0 cross-compilation or simulated build")
    p_build.add_argument("project_path", nargs="?", default=".", help="Path to project directory")
    p_build.add_argument("--arch", choices=["aarch64le", "x86_64"], default="aarch64le", help="Target architecture")
    p_build.add_argument("--type", choices=["Debug", "Release"], default="Debug", help="Build type")
    p_build.add_argument("--dry-run", action="store_true", help="Force simulated build verification")

    # test
    p_test = subparsers.add_parser("test", help="Execute test suite against target or simulated runner")
    p_test.add_argument("project_path", nargs="?", default=".", help="Path to project directory")
    p_test.add_argument("--filter", help="Filter tests by name")
    p_test.add_argument("--force-simulation", action="store_true", help="Force host simulated test runner")

    # diagnose
    p_diag = subparsers.add_parser("diagnose", help="Explain compiler errors and suggest fixes")
    p_diag.add_argument("log_source", help="Raw error string or path to build log file")

    # serve
    p_serve = subparsers.add_parser("serve", help="Launch interactive local web dashboard")
    p_serve.add_argument("project_path", nargs="?", default=".", help="Path to project directory")
    p_serve.add_argument("--port", type=int, default=8080, help="HTTP server port")
    p_serve.add_argument("--no-browser", action="store_true", help="Do not automatically open browser")

    # full-pipeline
    p_pipe = subparsers.add_parser("pipeline", help="Run end-to-end verification pipeline")
    p_pipe.add_argument("project_path", nargs="?", default=".", help="Path to project directory")

    return parser


def main() -> int:
    parser = build_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        return 0

    args = parser.parse_args()
    if args.subcommand == "audit":
        return cmd_audit(args)
    elif args.subcommand == "analyze":
        return cmd_analyze(args)
    elif args.subcommand == "build-assist":
        return cmd_build_assist(args)
    elif args.subcommand == "build":
        return cmd_build(args)
    elif args.subcommand == "test":
        return cmd_test(args)
    elif args.subcommand == "diagnose":
        return cmd_diagnose(args)
    elif args.subcommand == "serve":
        return cmd_serve(args)
    elif args.subcommand == "pipeline":
        return cmd_full_pipeline(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
