import subprocess
import csv
import os

image = "centos:7"
output_csv = "container_packages.csv"

# Bash command to try pip (python3 or python) and rpm
command = (
    "bash -c \""
    "echo '__PYTHON_PACKAGES__'; "
    "(python3 -m pip list || python -m pip list || echo 'No pip found') 2>/dev/null; "
    "echo '__RPM_PACKAGES__'; "
    "(rpm -qa || echo 'No rpm found') 2>/dev/null\""
)

try:
    print(f"Running container from image: {image}")
    result = subprocess.run(
        ["docker", "run", "--rm", image, command],
        capture_output=True,
        text=True,
        check=True
    )

    output = result.stdout

    # Split the output
    python_packages = []
    rpm_packages = []

    in_python = False
    in_rpm = False

    for line in output.splitlines():
        if line.strip() == "__PYTHON_PACKAGES__":
            in_python = True
            in_rpm = False
            continue
        elif line.strip() == "__RPM_PACKAGES__":
            in_python = False
            in_rpm = True
            continue

        if in_python:
            if "Package" in line and "Version" in line:
                continue  # header line
            parts = line.strip().split()
            if len(parts) == 2:
                python_packages.append(parts)
        elif in_rpm:
            rpm_packages.append([line.strip()])

    # Write to CSV
    with open(output_csv, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(["Python Packages"])
        writer.writerow(["Package", "Version"])
        writer.writerows(python_packages)

        writer.writerow([])
        writer.writerow(["RPM Packages"])
        writer.writerow(["Package"])
        writer.writerows(rpm_packages)

    print(f"\nPackage lists written to: {output_csv}")

except subprocess.CalledProcessError as e:
    print("Error running container or command:")
    print(e.stderr)
