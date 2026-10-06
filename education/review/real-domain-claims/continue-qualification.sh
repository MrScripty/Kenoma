#!/usr/bin/env bash
set -u
cd /tmp/kenoma-real-claims/education
# Wait for the already authorized official dependency process; never interrupt it.
while kill -0 13569 2>/dev/null; do sleep 10; done
if ! rg -q '^SOURCE_BUILD_COMPLETE ' /tmp/kenoma-real-mathlib-dependency.log; then
  printf 'Official dependency build did not complete; inspect /tmp/kenoma-real-mathlib-dependency.log\n'
  exit 1
fi
python3 tools/check_real_lesson_proofs.py > /tmp/kenoma-real-proofs-qualification.log 2>&1
proof_exit=$?
printf 'New real-proof checker exit: %s\n' "$proof_exit"
LEAN=/workspace/Kenoma/education/.tools/lean-4.19.0-linux/bin/lean python3 tools/build.py > /tmp/kenoma-real-full-book.log 2>&1
book_exit=$?
printf 'Full book build exit: %s\n' "$book_exit"
if [ "$proof_exit" -ne 0 ] || [ "$book_exit" -ne 0 ]; then exit 1; fi
