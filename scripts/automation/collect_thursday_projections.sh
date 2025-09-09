#!/bin/bash
# Tank01 Thursday Projections Collection Script
# 
# This script collects projections for Thursday night players
# Scheduled to run: Thursday 2:00 PM Pacific Time
# 
# CRON JOB (DISABLED FOR MANUAL TESTING):
# 0 14 * * 4 cd /path/to/fantasy_football && ./scripts/automation/collect_thursday_projections.sh
# 
# To enable: Uncomment the cron job line above and update the path

# Set working directory
cd "$(dirname "$0")/../.."

# Set up logging
LOG_DIR="logs/automation"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/thursday_projections_$(date +%Y%m%d_%H%M%S).log"

echo "Starting Thursday projections collection at $(date)" | tee -a "$LOG_FILE"

# Run the projections archive script
python3 data_collection/scripts/tank01/tank01_weekly_projections_archive.py --phase thursday_afternoon 2>&1 | tee -a "$LOG_FILE"

# Check exit status
if [ $? -eq 0 ]; then
    echo "Thursday projections collection completed successfully at $(date)" | tee -a "$LOG_FILE"
    exit 0
else
    echo "Thursday projections collection failed at $(date)" | tee -a "$LOG_FILE"
    exit 1
fi
