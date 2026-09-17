from pathlib import Path
from collections import Counter


project_directory = Path(__file__).resolve().parent.parent
log_file = project_directory / "logs" / "application.log"


def analyze_logs():

    if not log_file.exists():
        print("Log file not found.")
        return

    total_lines = 0
    error_count = 0
    warning_count = 0

    incident_types = Counter()

    with open(log_file, "r", encoding="utf-8") as file:

        for line in file:

            total_lines += 1

            if "ERROR" in line:
                error_count += 1

            if "WARN" in line:
                warning_count += 1

            if "HTTP 500" in line:
                incident_types["HTTP 500 Errors"] += 1

            if "HTTP 403" in line:
                incident_types["HTTP 403 Access Errors"] += 1

            if "HTTP 401" in line:
                incident_types["HTTP 401 Authentication Errors"] += 1

            if "Authentication failed" in line:
                incident_types["Failed Logins"] += 1

            if "Database connection timeout" in line:
                incident_types["Database Timeouts"] += 1

            if "Internal application unreachable" in line:
                incident_types["Application Connectivity Issues"] += 1


    print("=" * 55)
    print("APPLICATION SUPPORT LOG ANALYSIS REPORT")
    print("=" * 55)

    print(f"\nTotal log entries: {total_lines}")
    print(f"Errors detected: {error_count}")
    print(f"Warnings detected: {warning_count}")

    print("\nIncident Summary")
    print("-" * 55)

    for incident, count in incident_types.items():
        print(f"{incident}: {count}")

    print("\nRecommended Investigation Priorities")
    print("-" * 55)

    if incident_types["HTTP 500 Errors"] > 0:
        print(
            "- Investigate application/API errors and backend service health."
        )

    if incident_types["Database Timeouts"] > 0:
        print(
            "- Review database connectivity and application database configuration."
        )

    if incident_types["Failed Logins"] > 0:
        print(
            "- Review authentication events and affected user accounts."
        )

    if incident_types["HTTP 403 Access Errors"] > 0:
        print(
            "- Review user permissions and application access controls."
        )

    if incident_types["HTTP 401 Authentication Errors"] > 0:
        print(
            "- Validate API credentials and authentication configuration."
        )

    if incident_types["Application Connectivity Issues"] > 0:
        print(
            "- Verify VPN, routing, DNS, and internal application connectivity."
        )

    print("\nAnalysis complete.")


if __name__ == "__main__":
    analyze_logs()