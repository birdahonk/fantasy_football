#!/bin/bash

# Birdahonk Fantasy Football API - Webserver Deployment Script
# This script deploys the API verification files to tools.birdahonk.com/fantasy

set -e

# Configuration
REMOTE_HOST="birdahonk"  # SSH alias from ~/.ssh/config
REMOTE_PATH="/usr/home/birdahonk/public_html/tools.birdahonk.com/fantasy"
LOCAL_PATH="./webserver_deploy"

echo "🏈 Deploying Fantasy Football API files to $REMOTE_HOST..."

# Check if we have the necessary files
if [ ! -d "$LOCAL_PATH" ]; then
    echo "❌ Error: Local webserver_deploy directory not found!"
    exit 1
fi

# Create remote directory structure
echo "📁 Creating remote directory structure..."
ssh $REMOTE_HOST "mkdir -p $REMOTE_PATH/oauth/callback $REMOTE_PATH/verify"

# Deploy files
echo "📤 Deploying files..."
scp -r $LOCAL_PATH/index.html $REMOTE_HOST:$REMOTE_PATH/
scp -r $LOCAL_PATH/oauth/callback/index.html $REMOTE_HOST:$REMOTE_PATH/oauth/callback/
scp -r $LOCAL_PATH/verify/index.html $REMOTE_HOST:$REMOTE_PATH/verify/

# Set proper permissions
echo "🔐 Setting file permissions..."
ssh $REMOTE_HOST "chmod 644 $REMOTE_PATH/*.html $REMOTE_PATH/oauth/callback/*.html $REMOTE_PATH/verify/*.html"

echo "✅ Deployment complete!"
echo ""
echo "🌐 Your API endpoints are now available at:"
echo "   Main: https://tools.birdahonk.com/fantasy/"
echo "   OAuth Callback: https://tools.birdahonk.com/fantasy/oauth/callback/"
echo "   Verification: https://tools.birdahonk.com/fantasy/verify/"
echo ""
echo "🔗 You can now use these URLs in your Yahoo! API application setup."
