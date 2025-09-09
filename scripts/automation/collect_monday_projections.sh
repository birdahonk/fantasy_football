#!/bin/bash
# Tank01 Monday Projections Collection Script
# 
# This script collects projections for Monday night players
# Scheduled to run: Monday 2:00 PM Pacific Time
# 
# CRON JOB (DISABLED FOR MANUAL TESTING):
# 0 14 * * 1 cd /path/to/fantasy_football && ./scripts/automation/collect_monday_projections.sh
# 
# To enable: Uncomment the cron job line above and update the path

# Set working directory
cd "$(dirname "$0")/../.."

# Set up logging
LOG_DIR="logs/automation"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/monday_projections_$(date +%Y%m%d_%H%M%S).log"

echo "Starting Monday projections collection at $(date)" | tee -a "$LOG_FILE"

# Run the projections archive script
python3 data_collection/scripts/tank01/tank01_weekly_projections_archive.py --phase monday_afternoon 2>&1 | tee -a "$LOG_FILE"

# Check exit status
if [ $? -eq 0 ]; then
    echo "Monday projections collection completed successfully at $(date)" | tee -a "$LOG_FILE"
    exit 0
else
    echo "Monday projections collection failed at $(date)" | tee -a "$LOG_FILE"
    exit 1
fi
