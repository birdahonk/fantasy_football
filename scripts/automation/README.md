# 🤖 Fantasy Football Post-Game Analysis Automation

This directory contains automation scripts for the Post-Game Analysis System, including cron job scheduling for automated projection collection and analysis.

## 📋 **Scripts Overview**

### **Projection Collection Scripts**
- **`collect_thursday_projections.sh`** - Collects Thursday night player projections
- **`collect_sunday_projections.sh`** - Collects Sunday player projections  
- **`collect_monday_projections.sh`** - Collects Monday night player projections

### **Analysis Scripts**
- **`run_post_game_analysis.sh`** - Runs complete post-game analysis workflow
- **`setup_cron_jobs.sh`** - Sets up cron job scheduling (disabled by default)

## ⏰ **Automation Schedule**

### **Projection Collection**
- **Thursday 2:00 PM Pacific** - Thursday night players
- **Sunday 8:00 AM Pacific** - Sunday players
- **Monday 2:00 PM Pacific** - Monday night players

### **Post-Game Analysis**
- **Tuesday 9:00 AM Pacific** - Complete analysis workflow

## 🚀 **Manual Testing (Current Mode)**

All scripts are currently configured for **manual testing**. Cron jobs are **disabled** by default.

### **Test Projection Collection**
```bash
# Test Thursday projections
./scripts/automation/collect_thursday_projections.sh

# Test Sunday projections  
./scripts/automation/collect_sunday_projections.sh

# Test Monday projections
./scripts/automation/collect_monday_projections.sh
```

### **Test Post-Game Analysis**
```bash
# Test complete analysis workflow
./scripts/automation/run_post_game_analysis.sh
```

## 🔧 **Enabling Automation (For Webserver Deployment)**

### **Step 1: Setup Cron Jobs**
```bash
# Run the setup script (adds commented cron jobs)
./scripts/automation/setup_cron_jobs.sh
```

### **Step 2: Enable Cron Jobs**
```bash
# Edit crontab
crontab -e

# Uncomment the lines you want to enable:
# 0 14 * * 4 cd /path/to/fantasy_football && ./scripts/automation/collect_thursday_projections.sh
# 0 8 * * 0 cd /path/to/fantasy_football && ./scripts/automation/collect_sunday_projections.sh
# 0 14 * * 1 cd /path/to/fantasy_football && ./scripts/automation/collect_monday_projections.sh
# 0 9 * * 2 cd /path/to/fantasy_football && ./scripts/automation/run_post_game_analysis.sh
```

### **Step 3: Verify Setup**
```bash
# View current cron jobs
crontab -l

# Check logs
tail -f logs/automation/*.log
```

## 📁 **Output Structure**

### **Projection Archives**
```
data_collection/outputs/tank01/projections_archive/
├── 2025/
│   ├── week_01/
│   │   ├── 20250108_140000_wk01_thursday_afternoon_projections_archive.md
│   │   ├── 20250108_140000_wk01_thursday_afternoon_projections_archive_raw.json
│   │   ├── 20250112_080000_wk01_sunday_morning_projections_archive.md
│   │   ├── 20250112_080000_wk01_sunday_morning_projections_archive_raw.json
│   │   ├── 20250113_140000_wk01_monday_afternoon_projections_archive.md
│   │   └── 20250113_140000_wk01_monday_afternoon_projections_archive_raw.json
│   └── week_02/
│       └── ...
```

### **Analysis Outputs**
```
data_collection/outputs/analysis/post_game/
├── 2025/
│   ├── week_01/
│   │   ├── 20250114_090000_wk01_post_game_processed_raw.json
│   │   ├── 20250114_090000_wk01_quant_post_game_analysis.md
│   │   └── 20250114_090000_wk01_quant_post_game_analysis_raw.json
│   └── week_02/
│       └── ...
```

## 📊 **Logging**

All automation scripts log to:
```
logs/automation/
├── thursday_projections_YYYYMMDD_HHMMSS.log
├── sunday_projections_YYYYMMDD_HHMMSS.log
├── monday_projections_YYYYMMDD_HHMMSS.log
└── post_game_analysis_YYYYMMDD_HHMMSS.log
```

## ⚠️ **Important Notes**

### **API Limits**
- Tank01 API has 1000 calls/day limit
- Projection collection uses 1 call per phase
- Monitor usage to avoid hitting limits

### **Error Handling**
- All scripts include error checking
- Failed runs are logged with timestamps
- Exit codes indicate success/failure

### **Path Configuration**
- Update paths in cron jobs for your specific deployment
- Ensure all scripts have execute permissions
- Verify Python environment and dependencies

## 🔍 **Troubleshooting**

### **Common Issues**
1. **Permission Denied**: Run `chmod +x scripts/automation/*.sh`
2. **Python Not Found**: Ensure Python 3 is in PATH
3. **API Key Missing**: Check `.env` file for `RAPIDAPI_KEY`
4. **Path Issues**: Update paths in cron job definitions

### **Debug Mode**
```bash
# Run with verbose output
bash -x scripts/automation/collect_thursday_projections.sh
```

### **Check Logs**
```bash
# View latest logs
ls -la logs/automation/
tail -f logs/automation/*.log
```

## 🎯 **Next Steps**

1. **Test All Scripts Manually** - Verify functionality before enabling automation
2. **Deploy to Webserver** - Move code to production environment
3. **Enable Cron Jobs** - Activate automated scheduling
4. **Monitor Performance** - Check logs and API usage regularly
5. **Optimize Schedule** - Adjust timing based on actual NFL schedule

**Status**: ✅ **Ready for Manual Testing** - All scripts implemented with cron job functionality (disabled for safety)
