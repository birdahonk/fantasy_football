#!/bin/bash
# Post-Game Analysis Automation Script
# 
# This script runs the complete post-game analysis workflow
# Scheduled to run: Tuesday 9:00 AM Pacific Time
# 
# CRON JOB (DISABLED FOR MANUAL TESTING):
# 0 9 * * 2 cd /path/to/fantasy_football && ./scripts/automation/run_post_game_analysis.sh
# 
# To enable: Uncomment the cron job line above and update the path

# Set working directory
cd "$(dirname "$0")/../.."

# Set up logging
LOG_DIR="logs/automation"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/post_game_analysis_$(date +%Y%m%d_%H%M%S).log"

echo "Starting post-game analysis workflow at $(date)" | tee -a "$LOG_FILE"

# Get current week (simplified - in production this would be more sophisticated)
WEEK=$(date +%V)
if [ $WEEK -lt 36 ]; then
    WEEK=$((WEEK - 35))
else
    WEEK=$((WEEK - 35 + 1))
fi

echo "Processing Week $WEEK" | tee -a "$LOG_FILE"

# Step 1: Process post-game data
echo "Step 1: Processing post-game data..." | tee -a "$LOG_FILE"
python3 data_collection/scripts/analysis/post_game_analysis_data_processor.py --week $WEEK 2>&1 | tee -a "$LOG_FILE"

if [ $? -ne 0 ]; then
    echo "Post-game data processing failed at $(date)" | tee -a "$LOG_FILE"
    exit 1
fi

# Step 2: Run Quant AI analysis
echo "Step 2: Running Quant AI analysis..." | tee -a "$LOG_FILE"
python3 data_collection/scripts/analysis/quant_post_game_analysis_agent.py --week $WEEK 2>&1 | tee -a "$LOG_FILE"

if [ $? -ne 0 ]; then
    echo "Quant AI analysis failed at $(date)" | tee -a "$LOG_FILE"
    exit 1
fi

echo "Post-game analysis workflow completed successfully at $(date)" | tee -a "$LOG_FILE"
exit 0
