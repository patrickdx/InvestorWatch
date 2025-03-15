// Initialize the Vue application
const app = new Vue({
    el: '#app',
    data: {
        // Stock data
        stocks: [],
        selectedStock: 'AAPL',
        currentStock: {
            ticker: 'AAPL',
            company: 'Apple Inc',
            price: '173.45',
            change: 1.23,
            changePercent: 0.72,
            marketCap: 2710,  // in billions
            sector: 'Technology',
            industry: 'Consumer Electronics'
        },
        
        // Chart data
        timePeriods: ['1D', '1W', '1M', '3M', '1Y'],
        selectedPeriod: '1D',
        chartInstance: null,
        
        // News data
        news: [],
        loading: false,
        
        // Watchlist
        watchlist: [
            { ticker: 'AAPL', company: 'Apple Inc', price: '173.45', change: 1.23 },
            { ticker: 'MSFT', company: 'Microsoft Corp', price: '415.50', change: -0.45 },
            { ticker: 'GOOGL', company: 'Alphabet Inc', price: '147.60', change: 0.78 },
            { ticker: 'AMZN', company: 'Amazon.com Inc', price: '178.25', change: 2.15 },
            { ticker: 'META', company: 'Meta Platforms Inc', price: '485.90', change: -1.20 }
        ]
    },
    methods: {
        // Format market cap to display in billions/trillions
        formatMarketCap(value) {
            if (!value) return '0';
            if (value >= 1000) {
                return (value / 1000).toFixed(2) + 'T';
            }
            return value.toFixed(2) + 'B';
        },
        
        // Format date for news items
        formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        
        // Load stock data from API
        loadStockData() {
            this.loading = true;
            
            // In a real application, you would fetch data from your backend API
            // For now, we'll simulate an API call with setTimeout
            setTimeout(() => {
                // Update current stock info based on selection
                const selectedStockInfo = this.watchlist.find(s => s.ticker === this.selectedStock);
                if (selectedStockInfo) {
                    this.currentStock = {
                        ticker: selectedStockInfo.ticker,
                        company: selectedStockInfo.company,
                        price: selectedStockInfo.price,
                        change: selectedStockInfo.change,
                        changePercent: Math.abs(selectedStockInfo.change / parseFloat(selectedStockInfo.price) * 100).toFixed(2),
                        marketCap: Math.random() * 3000, // Random value for demo
                        sector: 'Technology', // Placeholder
                        industry: 'Various' // Placeholder
                    };
                }
                
                // Load news for the selected stock
                this.loadNewsData();
                
                // Update chart
                this.updateChart();
                
                this.loading = false;
            }, 500);
        },
        
        // Load news data
        loadNewsData() {
            // Simulate API call to get news
            // In a real app, you would fetch from your backend
            setTimeout(() => {
                // Generate some dummy news data
                const dummyNews = [
                    {
                        title: `${this.selectedStock} Reports Strong Quarterly Earnings`,
                        date: new Date(Date.now() - 2 * 3600 * 1000).toISOString(),
                        source: 'Bloomberg',
                        link: '#'
                    },
                    {
                        title: `Analysts Upgrade ${this.selectedStock} to Buy Rating`,
                        date: new Date(Date.now() - 6 * 3600 * 1000).toISOString(),
                        source: 'Reuters',
                        link: '#'
                    },
                    {
                        title: `${this.selectedStock} Announces New Product Line`,
                        date: new Date(Date.now() - 24 * 3600 * 1000).toISOString(),
                        source: 'Bloomberg',
                        link: '#'
                    },
                    {
                        title: `Industry Outlook Positive for ${this.selectedStock}`,
                        date: new Date(Date.now() - 48 * 3600 * 1000).toISOString(),
                        source: 'Reuters',
                        link: '#'
                    }
                ];
                
                this.news = dummyNews;
            }, 300);
        },
        
        // Change time period for chart
        changeTimePeriod(period) {
            this.selectedPeriod = period;
            this.updateChart();
        },
        
        // Update chart with new data
        updateChart() {
            const ctx = document.getElementById('stockChart').getContext('2d');
            
            // Generate random data points for the chart
            const dataPoints = 24; // Number of data points
            const data = [];
            const labels = [];
            
            // Generate different data based on time period
            let startPrice = parseFloat(this.currentStock.price);
            let volatility;
            
            switch(this.selectedPeriod) {
                case '1D': 
                    volatility = 0.002;
                    for (let i = 0; i < dataPoints; i++) {
                        const hour = 9 + Math.floor(i / 2);
                        const minute = (i % 2) * 30;
                        labels.push(`${hour}:${minute === 0 ? '00' : minute}`);
                    }
                    break;
                case '1W':
                    volatility = 0.01;
                    for (let i = 0; i < 7; i++) {
                        const date = new Date();
                        date.setDate(date.getDate() - (6 - i));
                        labels.push(date.toLocaleDateString('en-US', { weekday: 'short' }));
                    }
                    break;
                case '1M':
                    volatility = 0.03;
                    for (let i = 0; i < 30; i += 3) {
                        const date = new Date();
                        date.setDate(date.getDate() - (29 - i));
                        labels.push(date.toLocaleDateString('en-US', { day: 'numeric' }));
                    }
                    break;
                case '3M':
                    volatility = 0.05;
                    for (let i = 0; i < 12; i++) {
                        const date = new Date();
                        date.setDate(date.getDate() - (90 - i * 7));
                        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
                    }
                    break;
                case '1Y':
                    volatility = 0.1;
                    for (let i = 0; i < 12; i++) {
                        const date = new Date();
                        date.setMonth(date.getMonth() - (11 - i));
                        labels.push(date.toLocaleDateString('en-US', { month: 'short' }));
                    }
                    break;
            }
            
            // Generate price data
            for (let i = 0; i < labels.length; i++) {
                const change = (Math.random() - 0.5) * volatility * startPrice;
                startPrice += change;
                data.push(startPrice);
            }
            
            // Destroy previous chart if it exists
            if (this.chartInstance) {
                this.chartInstance.destroy();
            }
            
            // Create new chart
            this.chartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: this.selectedStock,
                        data: data,
                        borderColor: this.currentStock.change >= 0 ? '#4caf50' : '#f44336',
                        backgroundColor: this.currentStock.change >= 0 ? 'rgba(76, 175, 80, 0.1)' : 'rgba(244, 67, 54, 0.1)',
                        borderWidth: 2,
                        pointRadius: 0,
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: false
                            }
                        },
                        y: {
                            position: 'right',
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)'
                            }
                        }
                    }
                }
            });
        },
        
        // Refresh all data
        refreshData() {
            this.loadStockData();
        },
        
        // Initialize the application
        initializeApp() {
            // In a real app, you would fetch the list of stocks from your backend
            this.stocks = this.watchlist.map(stock => ({
                ticker: stock.ticker,
                company: stock.company
            }));
            
            // Load initial data
            this.loadStockData();
        }
    },
    mounted() {
        // Initialize when Vue is mounted
        this.initializeApp();
    }
});

// Function to create a backend API connector
// This would be used in a real application to connect to your Python backend
function createApiConnector() {
    const BASE_URL = '/api'; // Change this to your actual API endpoint
    
    return {
        // Get all stocks
        getStocks: async () => {
            try {
                const response = await axios.get(`${BASE_URL}/stocks`);
                return response.data;
            } catch (error) {
                console.error('Error fetching stocks:', error);
                return [];
            }
        },
        
        // Get stock details
        getStockDetails: async (ticker) => {
            try {
                const response = await axios.get(`${BASE_URL}/stocks/${ticker}`);
                return response.data;
            } catch (error) {
                console.error(`Error fetching details for ${ticker}:`, error);
                return null;
            }
        },
        
        // Get news for a stock
        getStockNews: async (ticker) => {
            try {
                const response = await axios.get(`${BASE_URL}/news/${ticker}`);
                return response.data;
            } catch (error) {
                console.error(`Error fetching news for ${ticker}:`, error);
                return [];
            }
        }
    };
}

// Create the API connector (commented out for now)
// const api = createApiConnector(); 