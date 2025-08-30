# Webserver Deployment for Yahoo! Fantasy Football API

This directory contains the files needed to deploy the API verification endpoints to your webserver at `tools.birdahonk.com/fantasy`.

## 📁 File Structure

```
webserver_deploy/
├── index.html              # Main API landing page
├── oauth/
│   └── callback/
│       └── index.html      # OAuth callback handler
├── verify/
│   └── index.html          # API verification endpoint
├── deploy.sh               # Deployment script
└── README.md               # This file
```

## 🚀 Quick Deployment

1. **Make sure you have SSH access** to your webserver
2. **Run the deployment script:**
   ```bash
   ./webserver_deploy/deploy.sh
   ```

## 🔧 Manual Deployment

If you prefer to deploy manually:

1. **Upload files to your webserver:**
   - `index.html` → `/fantasy/`
   - `oauth/callback/index.html` → `/fantasy/oauth/callback/`
   - `verify/index.html` → `/fantasy/verify/`

2. **Set proper permissions:**
   ```bash
   chmod 644 /fantasy/*.html
   chmod 644 /fantasy/oauth/callback/*.html
   chmod 644 /fantasy/verify/*.html
   ```

## 🌐 Available Endpoints

After deployment, these URLs will be available:

- **Main API Page:** https://tools.birdahonk.com/fantasy/
- **OAuth Callback:** https://tools.birdahonk.com/fantasy/oauth/callback/
- **Verification:** https://tools.birdahonk.com/fantasy/verify/

## 📋 For Yahoo! API Setup

Use these URLs when creating your Yahoo! API application:

- **Application URL:** https://tools.birdahonk.com/fantasy/
- **Callback URL:** https://tools.birdahonk.com/fantasy/oauth/callback/
- **Verification URL:** https://tools.birdahonk.com/fantasy/verify/

## 🔄 Updating

To update the files on your webserver:

1. **Make changes** to the local files
2. **Run the deployment script again:**
   ```bash
   ./webserver_deploy/deploy.sh
   ```

## 🏈 What These Files Do

- **`index.html`** - Landing page that shows your API is ready
- **`oauth/callback/index.html`** - Placeholder for OAuth callback handling
- **`verify/index.html`** - Verification endpoint for Yahoo! to confirm domain ownership

## ⚠️ Important Notes

- These are **static HTML files** for verification purposes
- The **actual OAuth logic** will be implemented in your Python scripts
- Make sure your **webserver is configured** to serve these files
- **HTTPS is required** for Yahoo! API integration
