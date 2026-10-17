#!/bin/sh
# 장르 7개 규칙 시뮬레이션을 모두 돌리고 passed n/n 을 모은다. 종료 코드 = 실패한 장르 수.
cd "$(dirname "$0")" || exit 1
fail=0
for g in strategy shooter moba casual rpg horror arcade; do
  f="$g/sim/${g}_sim.py"
  if [ -f "$f" ]; then
    out=$(python3 -I "$f" --test 2>&1); rc=$?
    echo "$g: $(echo "$out" | tail -1) (exit $rc)"
    [ "$rc" -ne 0 ] && fail=$((fail+1))
  else
    echo "$g: (sim 없음)"; fail=$((fail+1))
  fi
done
find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null
exit $fail
