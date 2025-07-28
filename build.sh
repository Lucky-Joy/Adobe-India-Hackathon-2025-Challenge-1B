# build.sh

#!/bin/bash
set -e

# Colour codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }

check_prerequisites() {
    log_info "Checking prerequisites..."
    command -v docker >/dev/null || { log_error "Docker not found"; exit 1; }
    command -v python3 >/dev/null || { log_error "Python 3 not found"; exit 1; }
    log_success "All prerequisites found"
}

install_dependencies() {
    log_info "Installing dependencies..."
    if [ -f "Challenge_1b/requirements.txt" ]; then
        pip install -r Challenge_1b/requirements.txt && log_success "Challenge 1B dependencies installed"
    fi
}

build_challenge_1b() {
    log_info "Building Challenge 1B Docker image..."
    cd Challenge_1b
    docker build --platform linux/amd64 -t adobe-challenge1b . || {
        log_error "Docker build failed"; exit 1;
    }
    log_success "Challenge 1B Docker image built"
    cd ..
}

test_challenge_1b() {
    log_info "Running Challenge 1B Docker container..."
    docker run --rm \
        -v "$(pwd)/Challenge_1b:/app/collections" \
        --network none \
        adobe-challenge1b
    log_success "Challenge 1B executed"
}

validate_documentation() {
    log_info "Validating documentation..."
    local required=(
        "Challenge_1b/Dockerfile"
        "Challenge_1b/requirements.txt"
        "Challenge_1b/README.md"
        "Challenge_1b/approach_explanation.md"
    )
    for file in "${required[@]}"; do
        [ -f "$file" ] || log_warning "Missing $file"
    done
}

summary() {
    echo -e "\n${GREEN}🎉 Challenge 1B build & test complete${NC}"
}

check_prerequisites
install_dependencies
build_challenge_1b
test_challenge_1b
validate_documentation
summary