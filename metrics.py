import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from log_analyzer import DEFAULT_LOG_FILE, analyze_log_file

DEFAULT_PORT = 8001


def render_metrics(log_file: Path | str = DEFAULT_LOG_FILE) -> str:
    analysis = analyze_log_file(log_file)
    lines = [
        "# HELP logs_total Total number of logs processed",
        "# TYPE logs_total counter",
        f"logs_total {analysis.total_logs}",
        "# HELP errors_total Total number of error logs",
        "# TYPE errors_total counter",
        f"errors_total {analysis.errors_total}",
        "# HELP requests_total Total number of request logs",
        "# TYPE requests_total counter",
        f"requests_total {analysis.requests_total}",
        "# HELP latency_avg Average observed latency in milliseconds",
        "# TYPE latency_avg gauge",
        f"latency_avg {analysis.latency_avg:.2f}",
        "# HELP error_rate Ratio of errors to requests",
        "# TYPE error_rate gauge",
        f"error_rate {analysis.error_rate:.4f}",
    ]
    return "\n".join(lines) + "\n"


class MetricsHandler(BaseHTTPRequestHandler):
    log_file = DEFAULT_LOG_FILE

    def do_GET(self) -> None:
        if self.path != "/metrics":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found\n")
            return

        body = render_metrics(self.log_file).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        return


def run_metrics_server(port: int, log_file: Path) -> None:
    MetricsHandler.log_file = log_file
    server = HTTPServer(("0.0.0.0", port), MetricsHandler)
    print(f"Metrics server running on http://localhost:{port}/metrics")
    server.serve_forever()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Expose log analysis metrics in Prometheus text format.")
    parser.add_argument("--log-file", default=str(DEFAULT_LOG_FILE), help="Path to the log file used for metrics.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port where /metrics will be exposed.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_metrics_server(args.port, Path(args.log_file))


if __name__ == "__main__":
    main()
