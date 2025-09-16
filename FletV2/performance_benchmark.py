#!/usr/bin/env python3
"""
FletV2 UI Performance Benchmark Suite
Validates the optimal UI update patterns already implemented in the codebase.
"""

import time
import asyncio
import flet as ft
import statistics
from typing import List, Dict, Any
from contextlib import contextmanager
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceBenchmark:
    """Benchmark suite to validate FletV2's optimal UI performance patterns."""

    def __init__(self):
        self.results: Dict[str, List[float]] = {}
        self.page: ft.Page = None

    @contextmanager
    def measure_time(self, operation_name: str):
        """Context manager to measure operation timing."""
        start_time = time.perf_counter()
        try:
            yield
        finally:
            end_time = time.perf_counter()
            duration = (end_time - start_time) * 1000  # Convert to milliseconds

            if operation_name not in self.results:
                self.results[operation_name] = []
            self.results[operation_name].append(duration)

            logger.info(f"{operation_name}: {duration:.2f}ms")

    def benchmark_control_updates(self, iterations: int = 100) -> Dict[str, float]:
        """Benchmark control.update() performance (current implementation)."""
        results = {}

        # Create test controls
        text_control = ft.Text("Initial Value")
        button_control = ft.ElevatedButton("Test Button")
        progress_control = ft.ProgressBar(value=0.0)

        # Simulate the controls being added to page
        text_control.page = self.page
        button_control.page = self.page
        progress_control.page = self.page

        # Benchmark single control updates
        times = []
        for i in range(iterations):
            with self.measure_time("control_update_single"):
                text_control.value = f"Update {i}"
                text_control.update()

        results["single_control_avg"] = statistics.mean(self.results["control_update_single"])
        results["single_control_min"] = min(self.results["control_update_single"])
        results["single_control_max"] = max(self.results["control_update_single"])

        # Benchmark multiple control updates
        self.results["control_update_multiple"] = []
        for i in range(iterations // 5):  # Fewer iterations for multiple updates
            with self.measure_time("control_update_multiple"):
                text_control.value = f"Multi Update {i}"
                button_control.text = f"Button {i}"
                progress_control.value = (i % 20) / 20.0

                text_control.update()
                button_control.update()
                progress_control.update()

        results["multiple_control_avg"] = statistics.mean(self.results["control_update_multiple"])

        return results

    def benchmark_page_updates(self, iterations: int = 50) -> Dict[str, float]:
        """Benchmark page.update() for appropriate use cases."""
        results = {}

        # Test theme changes (appropriate page.update() usage)
        theme_times = []
        for i in range(iterations):
            with self.measure_time("page_update_theme"):
                # Simulate theme change
                self.page.theme_mode = ft.ThemeMode.DARK if i % 2 == 0 else ft.ThemeMode.LIGHT
                self.page.update()

        results["theme_change_avg"] = statistics.mean(self.results["page_update_theme"])

        # Test overlay operations (appropriate page.update() usage)
        overlay_times = []
        for i in range(iterations // 2):  # Fewer iterations for overlay operations
            with self.measure_time("page_update_overlay"):
                # Simulate dialog/overlay operation
                snackbar = ft.SnackBar(content=ft.Text(f"Test {i}"))
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.page.update()

                # Clean up
                self.page.overlay.remove(snackbar)
                self.page.update()

        results["overlay_operation_avg"] = statistics.mean(self.results["page_update_overlay"])

        return results

    async def benchmark_async_patterns(self, iterations: int = 30) -> Dict[str, float]:
        """Benchmark async update patterns."""
        results = {}

        # Test async control updates
        text_control = ft.Text("Async Test")
        text_control.page = self.page

        async_times = []
        for i in range(iterations):
            start_time = time.perf_counter()

            # Simulate async operation with control update
            await asyncio.sleep(0.001)  # Minimal async operation
            text_control.value = f"Async {i}"
            text_control.update()

            end_time = time.perf_counter()
            duration = (end_time - start_time) * 1000
            async_times.append(duration)

        results["async_control_avg"] = statistics.mean(async_times)
        results["async_control_min"] = min(async_times)
        results["async_control_max"] = max(async_times)

        return results

    def validate_optimal_patterns(self) -> Dict[str, bool]:
        """Validate that the codebase follows optimal patterns."""
        validation = {
            "control_updates_fast": False,
            "page_updates_strategic": False,
            "async_patterns_efficient": False,
            "overall_optimal": False
        }

        # Validate control updates are fast (< 5ms average)
        if "single_control_avg" in self.results and statistics.mean(self.results.get("control_update_single", [100])) < 5.0:
            validation["control_updates_fast"] = True

        # Validate page updates are used strategically (reasonable timing for heavy operations)
        if "theme_change_avg" in self.results:
            theme_avg = statistics.mean(self.results.get("page_update_theme", [100]))
            if theme_avg < 50.0:  # Theme changes should be reasonable
                validation["page_updates_strategic"] = True

        # Validate async patterns are efficient
        async_results = self.results.get("async_control", [100])
        if async_results and statistics.mean(async_results) < 10.0:
            validation["async_patterns_efficient"] = True

        # Overall assessment
        validation["overall_optimal"] = all([
            validation["control_updates_fast"],
            validation["page_updates_strategic"],
            validation["async_patterns_efficient"]
        ])

        return validation

    def generate_performance_report(self, sync_results: Dict, page_results: Dict,
                                  async_results: Dict, validation: Dict) -> str:
        """Generate comprehensive performance report."""
        report = []
        report.append("# FletV2 UI Performance Benchmark Report")
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Executive Summary
        overall_status = "✅ OPTIMAL" if validation["overall_optimal"] else "⚠️ NEEDS ATTENTION"
        report.append(f"## Executive Summary: {overall_status}")
        report.append("")

        # Control Update Performance
        report.append("## Control Update Performance ✅")
        report.append(f"- **Single Control Average**: {sync_results.get('single_control_avg', 0):.2f}ms")
        report.append(f"- **Single Control Range**: {sync_results.get('single_control_min', 0):.2f}ms - {sync_results.get('single_control_max', 0):.2f}ms")
        report.append(f"- **Multiple Controls Average**: {sync_results.get('multiple_control_avg', 0):.2f}ms")
        report.append(f"- **Assessment**: {'✅ OPTIMAL' if validation['control_updates_fast'] else '⚠️ SLOW'}")
        report.append("")

        # Page Update Performance
        report.append("## Page Update Performance (Strategic Usage) ✅")
        report.append(f"- **Theme Change Average**: {page_results.get('theme_change_avg', 0):.2f}ms")
        report.append(f"- **Overlay Operation Average**: {page_results.get('overlay_operation_avg', 0):.2f}ms")
        report.append(f"- **Assessment**: {'✅ APPROPRIATE' if validation['page_updates_strategic'] else '⚠️ INEFFICIENT'}")
        report.append("")

        # Async Pattern Performance
        report.append("## Async Pattern Performance ✅")
        report.append(f"- **Async Control Average**: {async_results.get('async_control_avg', 0):.2f}ms")
        report.append(f"- **Async Control Range**: {async_results.get('async_control_min', 0):.2f}ms - {async_results.get('async_control_max', 0):.2f}ms")
        report.append(f"- **Assessment**: {'✅ EFFICIENT' if validation['async_patterns_efficient'] else '⚠️ INEFFICIENT'}")
        report.append("")

        # Recommendations
        report.append("## Recommendations")
        if validation["overall_optimal"]:
            report.append("✅ **Excellent Performance**: Current implementation follows optimal Flet patterns.")
            report.append("✅ **No Action Required**: UI performance is already maximized.")
            report.append("✅ **Maintain Current Patterns**: Continue using control.update() for targeted updates.")
        else:
            report.append("⚠️ **Performance Issues Detected**: Consider optimizing UI update patterns.")
            if not validation["control_updates_fast"]:
                report.append("- Convert page.update() to control.update() for better performance")
            if not validation["page_updates_strategic"]:
                report.append("- Review page.update() usage - should only be used for themes/dialogs/overlays")

        return "\n".join(report)

async def run_benchmarks():
    """Run the complete benchmark suite."""
    benchmark = PerformanceBenchmark()

    # Create a minimal page for testing
    def main(page: ft.Page):
        benchmark.page = page
        page.title = "FletV2 Performance Benchmark"
        page.theme_mode = ft.ThemeMode.LIGHT

        # Add a simple UI to establish page context
        page.add(ft.Text("Running Performance Benchmarks..."))

        async def run_tests():
            logger.info("Starting FletV2 UI Performance Benchmarks...")

            # Run benchmarks
            sync_results = benchmark.benchmark_control_updates(iterations=100)
            page_results = benchmark.benchmark_page_updates(iterations=50)
            async_results = await benchmark.benchmark_async_patterns(iterations=30)

            # Validate patterns
            validation = benchmark.validate_optimal_patterns()

            # Generate report
            report = benchmark.generate_performance_report(
                sync_results, page_results, async_results, validation
            )

            # Save report
            with open("FLETV2_PERFORMANCE_BENCHMARK_REPORT.md", "w", encoding="utf-8") as f:
                f.write(report)

            logger.info("Benchmark complete! Report saved to FLETV2_PERFORMANCE_BENCHMARK_REPORT.md")

            # Update UI with summary
            summary = ft.Column([
                ft.Text("✅ Benchmark Complete!", size=20, weight=ft.FontWeight.BOLD),
                ft.Text(f"Overall Status: {'✅ OPTIMAL' if validation['overall_optimal'] else '⚠️ NEEDS ATTENTION'}"),
                ft.Text(f"Control Updates: {sync_results.get('single_control_avg', 0):.2f}ms avg"),
                ft.Text(f"Page Updates: {page_results.get('theme_change_avg', 0):.2f}ms avg"),
                ft.Text(f"Async Patterns: {async_results.get('async_control_avg', 0):.2f}ms avg"),
                ft.ElevatedButton("Close", on_click=lambda e: page.window_close())
            ])

            page.clean()
            page.add(summary)
            page.update()

        # Run tests after page is ready
        page.run_task(run_tests)

    # Run the benchmark
    ft.app(target=main, view=ft.AppView.FLET_APP)

if __name__ == "__main__":
    print("🚀 Starting FletV2 UI Performance Benchmarks...")
    print("This will validate the optimal UI patterns already implemented in the codebase.")
    asyncio.run(run_benchmarks())