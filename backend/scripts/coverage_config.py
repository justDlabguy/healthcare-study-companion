#!/usr/bin/env python3
"""
Coverage configuration and reporting utilities.
"""
import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional


class CoverageConfig:
    """Coverage configuration and reporting utilities."""
    
    def __init__(self, backend_dir: Optional[str] = None):
        """Initialize coverage configuration.
        
        Args:
            backend_dir: Path to backend directory. Defaults to current directory.
        """
        self.backend_dir = Path(backend_dir or os.getcwd())
        self.coverage_file = self.backend_dir / ".coverage"
        self.coverage_xml = self.backend_dir / "coverage.xml"
        self.coverage_json = self.backend_dir / "coverage.json"
        self.htmlcov_dir = self.backend_dir / "htmlcov"
    
    def run_tests_with_coverage(self, 
                              test_path: Optional[str] = None,
                              min_coverage: int = 80,
                              verbose: bool = True) -> bool:
        """Run tests with coverage reporting.
        
        Args:
            test_path: Specific test path to run. Defaults to all tests.
            min_coverage: Minimum coverage threshold.
            verbose: Enable verbose output.
            
        Returns:
            True if tests pass and coverage meets threshold, False otherwise.
        """
        print("🧪 Running tests with coverage reporting...")
        
        # Build pytest command
        cmd = [
            "python", "-m", "pytest",
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=xml",
            "--cov-report=html",
            "--cov-report=json",
            "--cov-branch",
            f"--cov-fail-under={min_coverage}"
        ]
        
        if verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")
            
        if test_path:
            cmd.append(test_path)
        
        # Run tests
        try:
            result = subprocess.run(
                cmd,
                cwd=self.backend_dir,
                capture_output=False,
                text=True
            )
            
            success = result.returncode == 0
            
            if success:
                print("✅ Tests passed and coverage threshold met!")
            else:
                print("❌ Tests failed or coverage threshold not met")
                
            return success
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running tests: {e}")
            return False
    
    def generate_coverage_report(self, format_type: str = "term") -> bool:
        """Generate coverage report in specified format.
        
        Args:
            format_type: Report format ('term', 'html', 'xml', 'json').
            
        Returns:
            True if report generated successfully, False otherwise.
        """
        print(f"📊 Generating {format_type} coverage report...")
        
        format_map = {
            "term": ["coverage", "report", "--show-missing"],
            "html": ["coverage", "html"],
            "xml": ["coverage", "xml"],
            "json": ["coverage", "json"]
        }
        
        if format_type not in format_map:
            print(f"❌ Unsupported format: {format_type}")
            return False
        
        try:
            result = subprocess.run(
                format_map[format_type],
                cwd=self.backend_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ {format_type.upper()} report generated successfully")
                if format_type == "term":
                    print(result.stdout)
                return True
            else:
                print(f"❌ Error generating {format_type} report: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error generating {format_type} report: {e}")
            return False
    
    def get_coverage_summary(self) -> Optional[Dict[str, Any]]:
        """Get coverage summary from JSON report.
        
        Returns:
            Coverage summary dictionary or None if not available.
        """
        if not self.coverage_json.exists():
            print("❌ Coverage JSON report not found. Run tests with coverage first.")
            return None
        
        try:
            with open(self.coverage_json, 'r') as f:
                coverage_data = json.load(f)
            
            summary = coverage_data.get('totals', {})
            return {
                'covered_lines': summary.get('covered_lines', 0),
                'num_statements': summary.get('num_statements', 0),
                'percent_covered': summary.get('percent_covered', 0.0),
                'missing_lines': summary.get('missing_lines', 0),
                'excluded_lines': summary.get('excluded_lines', 0),
                'num_branches': summary.get('num_branches', 0),
                'num_partial_branches': summary.get('num_partial_branches', 0),
                'covered_branches': summary.get('covered_branches', 0),
                'percent_covered_display': summary.get('percent_covered_display', '0%')
            }
            
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"❌ Error reading coverage JSON: {e}")
            return None
    
    def check_coverage_threshold(self, min_coverage: int = 80) -> bool:
        """Check if coverage meets minimum threshold.
        
        Args:
            min_coverage: Minimum coverage percentage required.
            
        Returns:
            True if coverage meets threshold, False otherwise.
        """
        summary = self.get_coverage_summary()
        if not summary:
            return False
        
        current_coverage = summary['percent_covered']
        meets_threshold = current_coverage >= min_coverage
        
        print(f"📊 Current coverage: {current_coverage:.2f}%")
        print(f"📊 Required coverage: {min_coverage}%")
        
        if meets_threshold:
            print("✅ Coverage threshold met!")
        else:
            print("❌ Coverage below threshold")
            
        return meets_threshold
    
    def clean_coverage_files(self) -> None:
        """Clean up coverage files and directories."""
        print("🧹 Cleaning up coverage files...")
        
        files_to_clean = [
            self.coverage_file,
            self.coverage_xml,
            self.coverage_json
        ]
        
        dirs_to_clean = [
            self.htmlcov_dir
        ]
        
        # Remove files
        for file_path in files_to_clean:
            if file_path.exists():
                file_path.unlink()
                print(f"  Removed: {file_path.name}")
        
        # Remove directories
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                import shutil
                shutil.rmtree(dir_path)
                print(f"  Removed: {dir_path.name}/")
        
        print("✅ Coverage cleanup complete")


def main():
    """Main CLI interface for coverage utilities."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Coverage configuration and reporting utilities")
    parser.add_argument("command", choices=["test", "report", "summary", "check", "clean"],
                       help="Command to execute")
    parser.add_argument("--format", choices=["term", "html", "xml", "json"], default="term",
                       help="Report format (for report command)")
    parser.add_argument("--min-coverage", type=int, default=80,
                       help="Minimum coverage threshold")
    parser.add_argument("--test-path", help="Specific test path to run")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Change to backend directory if not already there
    if not Path("app").exists():
        backend_dir = Path(__file__).parent.parent
        os.chdir(backend_dir)
    
    coverage_config = CoverageConfig()
    
    if args.command == "test":
        success = coverage_config.run_tests_with_coverage(
            test_path=args.test_path,
            min_coverage=args.min_coverage,
            verbose=args.verbose
        )
        sys.exit(0 if success else 1)
        
    elif args.command == "report":
        success = coverage_config.generate_coverage_report(args.format)
        sys.exit(0 if success else 1)
        
    elif args.command == "summary":
        summary = coverage_config.get_coverage_summary()
        if summary:
            print("📊 Coverage Summary:")
            for key, value in summary.items():
                print(f"  {key}: {value}")
        else:
            sys.exit(1)
            
    elif args.command == "check":
        success = coverage_config.check_coverage_threshold(args.min_coverage)
        sys.exit(0 if success else 1)
        
    elif args.command == "clean":
        coverage_config.clean_coverage_files()


if __name__ == "__main__":
    main()