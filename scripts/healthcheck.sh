#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${HEALTH_URL:-http://localhost:8000}"
TIMEOUT=5
MAX_RETRIES=3

check_endpoint() {
    local url="$1"
    local name="$2"
    local attempt=1

    while [ $attempt -le $MAX_RETRIES ]; do
        HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$url" 2>/dev/null || echo "000")
        if [ "$HTTP_CODE" = "200" ]; then
            echo "[OK]  $name => HTTP $HTTP_CODE"
            return 0
        fi
        echo "[WARN] $name attempt $attempt/$MAX_RETRIES => HTTP $HTTP_CODE"
        attempt=$((attempt + 1))
        sleep 2
    done
    echo "[FAIL] $name => after $MAX_RETRIES attempts"
    return 1
}

FAILED=0
check_endpoint "$BASE_URL/health"     "API Health"     || FAILED=$((FAILED+1))
check_endpoint "$BASE_URL/api/v1/geo" "GEO Endpoint"   || FAILED=$((FAILED+1))

if [ $FAILED -gt 0 ]; then
    echo "HEALTH CHECK FAILED ($FAILED endpoints down)"
    exit 1
fi
echo "ALL HEALTH CHECKS PASSED"
