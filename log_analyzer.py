import argparse
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_LOG_FILE = Path("logs/system.log")
HIGH_LATENCY_MS = 1000
CRITICAL_500_THRESHOLD = 5
DATABASE_ERROR_THRESHOLD = 3
HIGH_LATENCY_THRESHOLD = 5

ENDPOINT_PATTERN = re.compile(r"/(?:login|api/users|payments)")
LATENCY_PATTERN = re.compile(r"latency=(\d+)ms")


@dataclass
class LogAnalysis:
    total_logs: int = 0
    requests_total: int = 0
    errors_total: int = 0
    warnings_total: int = 0
    high_latency_total: int = 0
    latency_sum: int = 0
    latency_count: int = 0
    error_messages: Counter = field(default_factory=Counter)
    status_codes: Counter = field(default_factory=Counter)
    endpoints: Counter = field(default_factory=Counter)

    @property
    def latency_avg(self) -> float:
        if self.latency_count == 0:
            return 0.0
        return self.latency_sum / self.latency_count

    @property
    def error_rate(self) -> float:
        if self.requests_total == 0:
            return 0.0
        return self.errors_total / self.requests_total


def parse_log_line(line: str) -> dict:
    parts = [part.strip() for part in line.strip().split("|")]
    record = {
        "timestamp": parts[0] if len(parts) > 0 else "",
        "level": parts[1] if len(parts) > 1 else "UNKNOWN",
        "message": parts[2] if len(parts) > 2 else "UNKNOWN",
        "endpoint": None,
        "status_code": None,
        "latency_ms": None,
    }

    for part in parts[3:]:
        endpoint_match = ENDPOINT_PATTERN.fullmatch(part)
        latency_match = LATENCY_PATTERN.fullmatch(part)

        if endpoint_match:
            record["endpoint"] = part
        elif part.isdigit():
            record["status_code"] = int(part)
        elif latency_match:
            record["latency_ms"] = int(latency_match.group(1))

    return record


def analyze_log_file(log_file: Path | str = DEFAULT_LOG_FILE) -> LogAnalysis:
    analysis = LogAnalysis()
    log_path = Path(log_file)

    if not log_path.exists():
        return analysis

    with log_path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            record = parse_log_line(line)
            level = record["level"]
            message = record["message"]
            endpoint = record["endpoint"]
            status_code = record["status_code"]
            latency_ms = record["latency_ms"]

            analysis.total_logs += 1

            if endpoint:
                analysis.requests_total += 1
                analysis.endpoints[endpoint] += 1

            if status_code is not None:
                analysis.status_codes[str(status_code)] += 1

            if latency_ms is not None:
                analysis.latency_sum += latency_ms
                analysis.latency_count += 1
                if latency_ms >= HIGH_LATENCY_MS:
                    analysis.high_latency_total += 1

            if level == "ERROR":
                analysis.errors_total += 1
                analysis.error_messages[message] += 1
            elif level == "WARNING":
                analysis.warnings_total += 1

    return analysis


def detect_root_cause(analysis: LogAnalysis) -> tuple[str, str]:
    database_errors = analysis.error_messages.get("Database connection failed", 0)
    backend_failures = analysis.status_codes.get("500", 0)

    if database_errors >= DATABASE_ERROR_THRESHOLD:
        return "DATABASE INSTABILITY", "CRITICAL"

    if backend_failures >= CRITICAL_500_THRESHOLD:
        return "BACKEND FAILURE", "CRITICAL"

    if analysis.high_latency_total >= HIGH_LATENCY_THRESHOLD or analysis.latency_avg >= HIGH_LATENCY_MS:
        return "PERFORMANCE ISSUE", "HIGH"

    if analysis.errors_total > 0:
        return "APPLICATION ERRORS DETECTED", "MEDIUM"

    return "NO MAJOR INCIDENT DETECTED", "LOW"


def print_counter(title: str, counter: Counter, suffix: str = "") -> None:
    print(f"\n{title}:")
    if not counter:
        print("- None")
        return

    for item, count in counter.most_common():
        print(f"- {item} -> {count}{suffix}")


def print_report(analysis: LogAnalysis) -> None:
    root_cause, severity = detect_root_cause(analysis)

    print("LOG ANALYSIS REPORT")
    print("===================")
    print(f"TOTAL LOGS: {analysis.total_logs}")
    print(f"REQUESTS: {analysis.requests_total}")
    print(f"ERRORS: {analysis.errors_total}")
    print(f"WARNINGS: {analysis.warnings_total}")
    print(f"AVERAGE LATENCY: {analysis.latency_avg:.2f}ms")
    print(f"ERROR RATE: {analysis.error_rate:.2%}")

    print_counter("ERRORS", analysis.error_messages)
    print_counter("HTTP STATUS", analysis.status_codes)
    print_counter("MOST USED ENDPOINTS", analysis.endpoints, " requests")

    print("\nSRE INFERENCE:")
    print(f"ROOT CAUSE: {root_cause}")
    print(f"SEVERITY: {severity}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze simulated application logs for SRE signals.")
    parser.add_argument("--log-file", default=str(DEFAULT_LOG_FILE), help="Path to the log file to analyze.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    analysis = analyze_log_file(args.log_file)
    print_report(analysis)


if __name__ == "__main__":
    main()
