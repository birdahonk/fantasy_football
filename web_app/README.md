# Fantasy Football Web App

## 🚧 Development Status

This is the **web interface** for the Fantasy Football AI General Manager, currently under development on the `feature/web-app` branch.

## 🏗️ Architecture

- **Framework**: Flask (Python)
- **Database**: SQLite (local)
- **Styling**: Retro green-screen terminal aesthetic
- **Responsive**: Mobile-first design
- **Mock Data**: Currently using sample data for development

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Flask dependencies (see `requirements.txt`)

### Installation
```bash
cd web_app
pip install -r requirements.txt
```

### Running the App
```bash
python app.py
```

The app will be available at `http://localhost:5000`

## 📁 File Structure

```
web_app/
├── app.py              # Main Flask application
├── templates/          # HTML templates
│   ├── base.html      # Base template with ASCII art header
│   └── dashboard.html # Dashboard page
├── static/            # Static assets
│   ├── css/          # Stylesheets
│   │   └── style.css # Retro terminal styling
│   └── js/           # JavaScript
│       └── app.js    # Basic app functionality
├── database/          # SQLite database files
└── requirements.txt   # Python dependencies
```

## 🎯 Development Notes

### Mock Data Strategy
- Currently using `get_mock_data()` function for development
- Will be replaced with real API calls once Yahoo! authentication is working
- No modifications to existing analysis scripts during development

### ASCII Art Header
- BIRDAHONKERS branding on all pages
- Retro terminal aesthetic throughout
- Responsive design for mobile and desktop

### Database Schema
- `weekly_analysis`: Store analysis reports
- `roster_data`: Current team roster
- `free_agents`: Available players

## 🔄 Integration Plan

1. **Phase 1**: Complete web interface with mock data ✅
2. **Phase 2**: Wait for Yahoo! API authentication on main branch
3. **Phase 3**: Merge feature branch and replace mock data with real API calls
4. **Phase 4**: End-to-end testing and optimization

## 🎨 Design Philosophy

- **Simplicity**: Single-user utility tool
- **Retro Aesthetic**: Green-screen terminal style
- **Mobile-First**: Optimized for mobile use
- **Performance**: Fast loading and responsive interactions

## 🚧 Current Features

- ✅ Basic Flask application structure
- ✅ ASCII art header and navigation
- ✅ Dashboard with mock data
- ✅ Retro CSS styling
- ✅ Mobile-responsive design
- ✅ SQLite database setup
- ✅ API endpoints for data

## 📱 Mobile Optimization

- Touch-friendly buttons (44px minimum)
- Responsive grid layouts
- Optimized ASCII art scaling
- Mobile-first CSS breakpoints

## 🔮 Next Steps

1. Complete remaining page templates
2. Add AI chat interface
3. Implement roster management
4. Add analysis viewing
5. Prepare for API integration
