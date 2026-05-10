#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

RUN_APP="false"
SKIP_TESTS="false"

for arg in "$@"; do
  case "$arg" in
    --run)
      RUN_APP="true"
      ;;
    --skip-tests)
      SKIP_TESTS="true"
      ;;
    -h|--help)
      cat <<'USAGE'
Usage: ./setup_all.sh [--run] [--skip-tests]

Options:
  --run         Start the Flask app after setup and tests.
  --skip-tests  Install dependencies but do not run pytest.
  -h, --help   Show this help message.
USAGE
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg"
      echo "Run ./setup_all.sh --help for usage."
      exit 1
      ;;
  esac
done

echo "Project: $PROJECT_DIR"
echo "Checking Python..."
python3 --version

echo "Creating virtual environment..."
python3 -m venv .venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Preparing runtime folders..."
mkdir -p backups

if [[ "$SKIP_TESTS" == "false" ]]; then
  echo "Running automated tests..."
  pytest -v
fi

echo
echo "All setup checks passed."
echo "Run tests: source .venv/bin/activate && pytest -v"
echo "Run app:   source .venv/bin/activate && python main.py"
echo "Open:      http://127.0.0.1:5000"
echo "Guide:     $PROJECT_DIR/SETUP_GUIDE.md"
echo "Overview:  $PROJECT_DIR/interview_overview.html"

if [[ "$RUN_APP" == "true" ]]; then
  echo
  echo "Starting Flask app..."
  python main.py
fi
