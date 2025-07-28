# test_e2e.py

import os
import subprocess
import time

print("🔍 Challenge 1B: End-to-End Test")

start = time.time()

# Docker Build
print("🔨 Building Docker image...")
build = subprocess.run([
    "docker", "build", "--platform", "linux/amd64", "-t", "adobe-challenge1b", "."
], cwd="Challenge_1b")

if build.returncode != 0:
    print("❌ Docker build failed")
    exit(1)
print("✅ Docker build successful")

# Run container
print("🚀 Running Docker container...")
runtime = subprocess.run([
    "docker", "run", "--rm",
    "-v", f"{os.getcwd()}/Challenge_1b:/app/collections",
    "--network", "none",
    "adobe-challenge1b"
])

if runtime.returncode != 0:
    print("❌ Docker run failed")
    exit(1)

print("✅ Docker run successful")

# Output Check
expected = ["Collection 1", "Collection 2", "Collection 3"]
actual = sum(os.path.exists(f"Challenge_1b/{c}/challenge1b_output.json") for c in expected)
print(f"📄 Output files: {actual}/3 found")

# Performance
end = time.time()
print(f"⏱ Total time: {end - start:.1f}s")
if end - start <= 60:
    print("✅ Performance within limits")
else:
    print("⚠️ May exceed 60s limit")
