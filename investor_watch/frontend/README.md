# Investor Watch Frontend

A simple, responsive web interface for viewing stock information and news from your SQL database.

## Overview

This frontend is built with:
- **Vue.js** (2.x) - For reactive data binding and UI components
- **Bootstrap** (5.x) - For responsive layout and styling
- **Chart.js** - For stock price charts
- **Axios** - For API requests

## Getting Started

### Running the Application

1. Make sure you have Python installed
2. Install Flask: `pip install flask`
3. Run the API server:
   ```
   cd investor_watch/frontend
   python api.py
   ```
4. Open your browser to `http://localhost:5000`

## Project Structure

- `index.html` - Main HTML file with Vue.js components
- `styles.css` - Custom CSS styles (minimal since we use Bootstrap)
- `app.js` - Vue.js application code
- `api.py` - Flask API server to connect to your database

## Customizing the Frontend

### Adding New Features

1. **Adding a New Page**:
   - Create a new route in the Vue.js application
   - Add a link in the navigation bar

2. **Adding TradingView Charts**:
   - Replace the Chart.js implementation with TradingView widgets
   - Add this script to your HTML:
     ```html
     <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
     ```
   - Create a TradingView widget:
     ```javascript
     new TradingView.widget({
       "width": "100%",
       "height": 500,
       "symbol": "NASDAQ:" + this.selectedStock,
       "interval": "D",
       "timezone": "exchange",
       "theme": "light",
       "style": "1",
       "toolbar_bg": "#f1f3f6",
       "withdateranges": true,
       "allow_symbol_change": true,
       "container_id": "tradingview_chart"
     });
     ```

3. **Adding Stock Filtering**:
   - Add filter controls to the UI
   - Update the API calls to include filter parameters

### Modifying the API

The `api.py` file connects to your SQL database using the `Driver` class. To modify:

1. Add new routes for additional data
2. Update existing routes to include more information
3. Add error handling and logging

## Connecting to Real Data

Currently, the frontend uses placeholder data. To connect to real data:

1. Uncomment the API connector in `app.js`
2. Update the Vue methods to use the API connector
3. Make sure your backend API is returning data in the expected format

## Mobile Responsiveness

The application is already responsive thanks to Bootstrap. Test on different devices and adjust as needed.

## Troubleshooting

- **API Connection Issues**: Check that your database is running and accessible
- **Chart Not Displaying**: Ensure the canvas element has a proper height
- **Data Not Loading**: Check browser console for JavaScript errors

## Next Steps

Consider these enhancements:
- Add user authentication
- Implement real-time data updates
- Add portfolio tracking functionality
- Integrate with external APIs for more data 