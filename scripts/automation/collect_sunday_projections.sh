#!/bin/bash
# Tank01 Sunday Projections Collection Script
# 
# This script collects projections for Sunday players
# Scheduled to run: Sunday 8:00 AM Pacific Time
# 
# CRON JOB (DISABLED FOR MANUAL TESTING):
# 0 8 * * 0 cd /path/to/fantasy_football && ./scripts/automation/collect_sunday_projections.sh
# 
# To enable: Uncomment the cron job line above and update the path

# Set working directory
cd "$(dirname "$0")/../.."

# Set up logging
LOG_DIR="logs/automation"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/sunday_projections_$(date +%Y%m%d_%H%M%S).log"

echo "Starting Sunday projections collection at $(date)" | tee -a "$LOG_FILE"

# Run the projections archive script
python3 data_collection/scripts/tank01/tank01_weekly_projections_archive.py --phase sunday_morning 2>&1 | tee -a "$LOG_FILE"

# Check exit status
if [ $? -eq 0 ]; then
    echo "Sunday projections collection completed successfully at $(date)" | tee -a "$LOG_FILE"
    exit 0
else
    echo "Sunday projections collection failed at $(date)" | tee -a "$LOG_FILE"
    exit 1
fi
