#!/bin/bash
# TrendPulse — One full pipeline cycle
# Producer → Kafka → Spark → Bronze → Silver → Gold

set -e  # exit on error

echo "=========================================="
echo "TrendPulse — Full Pipeline Cycle"
echo "=========================================="
echo ""

# Activate venv
source tenv/bin/activate

# ---------- Step 1 & 2: Produce + Consume in parallel ----------
echo "[1/4] Starting producer (60s)..."
timeout 300 python -m src.ingestion.kafka_producer &
PRODUCER_PID=$!

echo "[2/4] Starting Spark consumer (60s)..."
timeout 60 python -m src.processing.spark_consumer &
CONSUMER_PID=$!

# Wait for both
wait $PRODUCER_PID || true
wait $CONSUMER_PID || true

echo ""
echo "[3/4] Processing bronze → silver (LLM enrichment)..."
python -m src.processing.silver_worker

echo ""
echo "[4/4] Aggregating silver → gold..."
python -m src.processing.gold_worker

echo ""
echo "=========================================="
echo "✅ Pipeline cycle complete"
echo "=========================================="