#!/bin/bash
cd "$(dirname "$0")"
for n in $(seq 1 200); do
  python3 -I check_terms.py >> loop10.log 2>&1
  sleep 1800
done
