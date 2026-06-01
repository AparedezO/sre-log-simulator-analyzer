import argparse
import random
import time
from datetime import datetime
from pathlib import Path

DEFAULT_LOG_FILE = Path("logs/system.log")
ENDPOINTS = ["/login", "/api/users", "/payments"]
HTTP_CODES = [200, 200, 200, 200, 404, 500]
ERROR_MESSAGES = [
    "Database connection failed",
    "Timeout error",
    "Internal service failure",
]


def current_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def generate_latency(status_code: int) -> int:
    if status_code == 500:
        return random.randint(800, 2500)
    if status_code == 404:
        return random.randint(80, 700)
    return random.randint(40, 1500)


def generate_log_line() -> str:
    endpoint = random.choice(ENDPOINTS)
    status_code = random.choice(HTTP_CODES)
    latency_ms = generate_latency(status_code)
    timestamp = current_timestamp()

    if status_code == 500:
        message = random.choice(ERROR_MESSAGES)
        return f"{timestamp} | ERROR | {message} | {endpoint} | {status_code} | latency={latency_ms}ms"

    if latency_ms >= 1000:
        return f"{timestamp} | WARNING | High response time | {endpoint} | {status_code} | latency={latency_ms}ms"

    return f"{timestamp} | INFO | Request completed | {endpoint} | {status_code} | latency={latency_ms}ms"


def write_log(log_file: Path, line: str) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8") as file:
        file.write(line + "\n")
    print(line)


def run_generator(log_file: Path, count: int, interval: float, loop: bool) -> None:
    generated = 0

    try:
        while loop or generated < count:
            line = generate_log_line()
            write_log(log_file, line)
            generated += 1
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Log generation stopped by user.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate simulated application logs for SRE practice.")
    parser.add_argument("--log-file", default=str(DEFAULT_LOG_FILE), help="Path where logs will be written.")
    parser.add_argument("--count", type=int, default=50, help="Number of logs to generate when not using --loop.")
    parser.add_argument("--interval", type=float, default=1.0, help="Seconds between generated logs.")
    parser.add_argument("--loop", action="store_true", help="Generate logs continuously until stopped.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_generator(Path(args.log_file), args.count, args.interval, args.loop)


if __name__ == "__main__":
    main()
