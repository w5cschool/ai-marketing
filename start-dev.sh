#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

BACKEND_PID_FILE="/tmp/ai-email-marketing-backend.pid"
FRONTEND_PID_FILE="/tmp/ai-email-marketing-frontend.pid"
BACKEND_LOG_FILE="/tmp/ai-email-marketing-backend.log"
FRONTEND_LOG_FILE="/tmp/ai-email-marketing-frontend.log"

log() {
  printf '\n[%s] %s\n' "$(date '+%H:%M:%S')" "$1"
}

cleanup() {
  log "Shutting down services..."

  if [ -f "$BACKEND_PID_FILE" ]; then
    BACKEND_PID="$(cat "$BACKEND_PID_FILE")"
    if ps -p "$BACKEND_PID" >/dev/null 2>&1; then
      log "Stopping backend (PID: $BACKEND_PID)"
      kill "$BACKEND_PID" 2>/dev/null || true
    fi
    rm -f "$BACKEND_PID_FILE"
  fi

  if [ -f "$FRONTEND_PID_FILE" ]; then
    FRONTEND_PID="$(cat "$FRONTEND_PID_FILE")"
    if ps -p "$FRONTEND_PID" >/dev/null 2>&1; then
      log "Stopping frontend (PID: $FRONTEND_PID)"
      kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    rm -f "$FRONTEND_PID_FILE"
  fi

  log "All services stopped"
  exit 0
}

trap cleanup SIGINT SIGTERM EXIT

ensure_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    log "Required command not found: $1"
    exit 1
  fi
}

normalize_backend_env() {
  local env_file="$BACKEND_DIR/.env"
  if [ -f "$env_file" ] && grep -q 'sslmode=' "$env_file"; then
    log "Normalizing DATABASE_URL query param: sslmode -> ssl for asyncpg"
    sed -i '' 's/sslmode=/ssl=/g' "$env_file"
  fi
}

install_frontend_dependencies() {
  local max_attempts="${NPM_INSTALL_RETRIES:-4}"
  local attempt=1
  local backoff=2
  local npm_registry="${NPM_REGISTRY:-https://registry.npmjs.org/}"

  while [ "$attempt" -le "$max_attempts" ]; do
    log "Installing frontend dependencies (attempt ${attempt}/${max_attempts})..."

    if npm install \
      --registry "$npm_registry" \
      --fetch-retries 5 \
      --fetch-retry-factor 2 \
      --fetch-retry-mintimeout 20000 \
      --fetch-retry-maxtimeout 120000; then
      log "Frontend dependencies installed"
      return 0
    fi

    if [ "$attempt" -lt "$max_attempts" ]; then
      log "npm install failed, running npm cache verify and retrying in ${backoff}s..."
      npm cache verify >/dev/null 2>&1 || true
      sleep "$backoff"
      backoff=$((backoff * 2))
    fi

    attempt=$((attempt + 1))
  done

  log "ERROR: frontend dependency installation failed after ${max_attempts} attempts"
  log "Check npm log files under ~/.npm/_logs"
  return 1
}

kill_port_if_busy() {
  local port="$1"
  if lsof -ti:"$port" >/dev/null 2>&1; then
    log "Port $port is in use, killing existing process..."
    lsof -ti:"$port" | xargs kill -9 2>/dev/null || true
    sleep 1
  fi
}

wait_for_port() {
  local pid="$1"
  local port="$2"
  local name="$3"

  log "Waiting for $name to start..."
  for _ in {1..30}; do
    sleep 1
    if ! ps -p "$pid" >/dev/null 2>&1; then
      log "ERROR: $name process (PID: $pid) died"
      return 1
    fi
    if lsof -ti:"$port" >/dev/null 2>&1; then
      log "$name is ready (port $port listening)"
      return 0
    fi
  done

  log "WARNING: $name port $port not confirmed after 30s"
  return 0
}

start_backend() {
  log "Starting backend..."
  cd "$BACKEND_DIR"

  ensure_command python3
  ensure_command lsof
  normalize_backend_env

  local venv_dir="$BACKEND_DIR/.venv"
  local app_module="app.main:app"
  local host="${BACKEND_HOST:-0.0.0.0}"
  local port="${BACKEND_PORT:-8000}"

  if [ ! -d "$venv_dir" ]; then
    log "Creating backend virtual environment in $venv_dir"
    python3 -m venv "$venv_dir"
  fi

  kill_port_if_busy "$port"

  bash -c "
    cd '$BACKEND_DIR'
    if [ -f '.env' ]; then
      set -a
      source '.env'
      set +a
    fi
    source '$venv_dir/bin/activate'
    python -m pip install --upgrade pip >/dev/null 2>&1
    python -m pip install -e . >/dev/null 2>&1
    uvicorn '$app_module' --host '$host' --port '$port' --reload
  " >"$BACKEND_LOG_FILE" 2>&1 &

  local backend_pid=$!
  echo "$backend_pid" >"$BACKEND_PID_FILE"

  log "Backend started (PID: $backend_pid)"
  log "Backend logs: tail -f $BACKEND_LOG_FILE"

  if ! wait_for_port "$backend_pid" "$port" "Backend"; then
    log "Last 40 lines of backend log:"
    tail -40 "$BACKEND_LOG_FILE" || true
    exit 1
  fi

  export BACKEND_EFFECTIVE_PORT="$port"
}

start_frontend() {
  log "Starting frontend..."
  cd "$FRONTEND_DIR"

  ensure_command npm
  ensure_command lsof

  local web_port="${WEB_PORT:-3000}"
  local api_base="${NEXT_PUBLIC_API_BASE:-http://127.0.0.1:${BACKEND_EFFECTIVE_PORT}/api/v1}"

  kill_port_if_busy "$web_port"

  if [ ! -d "node_modules" ]; then
    install_frontend_dependencies
  fi

  env NEXT_PUBLIC_API_BASE="$api_base" npm run dev -- --port "$web_port" >"$FRONTEND_LOG_FILE" 2>&1 &

  local frontend_pid=$!
  echo "$frontend_pid" >"$FRONTEND_PID_FILE"

  log "Frontend started (PID: $frontend_pid)"
  log "Frontend logs: tail -f $FRONTEND_LOG_FILE"

  if ! wait_for_port "$frontend_pid" "$web_port" "Frontend"; then
    log "Frontend failed to start, attempting one recovery install + restart..."
    kill "$frontend_pid" 2>/dev/null || true
    rm -rf node_modules
    install_frontend_dependencies

    env NEXT_PUBLIC_API_BASE="$api_base" npm run dev -- --port "$web_port" >"$FRONTEND_LOG_FILE" 2>&1 &
    frontend_pid=$!
    echo "$frontend_pid" >"$FRONTEND_PID_FILE"

    if ! wait_for_port "$frontend_pid" "$web_port" "Frontend"; then
      log "Last 60 lines of frontend log:"
      tail -60 "$FRONTEND_LOG_FILE" || true
      exit 1
    fi
  fi

  export FRONTEND_EFFECTIVE_PORT="$web_port"
  export FRONTEND_API_BASE="$api_base"
}

monitor_processes() {
  while true; do
    sleep 5

    if [ -f "$BACKEND_PID_FILE" ]; then
      local backend_pid
      backend_pid="$(cat "$BACKEND_PID_FILE")"
      if ! ps -p "$backend_pid" >/dev/null 2>&1; then
        log "WARNING: backend process exited (PID: $backend_pid)"
      fi
    fi

    if [ -f "$FRONTEND_PID_FILE" ]; then
      local frontend_pid
      frontend_pid="$(cat "$FRONTEND_PID_FILE")"
      if ! ps -p "$frontend_pid" >/dev/null 2>&1; then
        log "WARNING: frontend process exited (PID: $frontend_pid)"
      fi
    fi
  done
}

start_backend
start_frontend

log "=========================================="
log "Both services are running"
log "Backend:  http://127.0.0.1:${BACKEND_EFFECTIVE_PORT}"
log "Frontend: http://localhost:${FRONTEND_EFFECTIVE_PORT}"
log "API Base: ${FRONTEND_API_BASE}"
log "=========================================="
log "Press Ctrl+C to stop all services"
log "View backend logs:  tail -f $BACKEND_LOG_FILE"
log "View frontend logs: tail -f $FRONTEND_LOG_FILE"

monitor_processes
