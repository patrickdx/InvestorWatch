# 📈 Investor Watch

A real-time stock market monitoring and news analysis platform that tracks S&P 500 companies, analyzes financial news sentiment, and provides an interactive dashboard for market insights.

- **Real-time News Aggregation**: Fetches latest financial news for S&P 500 companies
- **Sentiment Analysis**: Uses a fine-tuned RoBERTa model to analyze news sentiment
- **Interactive Dashboard**: Streamlit-based web interface for data visualization
- **Sector & Ticker Analysis**: Track mentions and sentiment across different market sectors

## Technologies used

- **Backend**: Python 3.8+
- **Database**: MongoDB (Atlas)
- **NLP**: Hugging Face Transformers (cardiffnlp/twitter-roberta-base-sentiment)
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly, Streamlit

<img width="2020" height="1092" alt="image" src="https://github.com/user-attachments/assets/5e99a1a1-b21b-43b1-9500-e3df1cb09da6" />

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/investor_watch.git
   cd investor_watch
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory with the following variables:
   ```
   MONGODB_USERNAME=your_mongodb_username
   MONGODB_PASSWORD=your_mongodb_password
   MONGODB_CLUSTER=your_cluster_address
   MONGODB_DATABASE=stocks
   MONGODB_COLLECTION=articles
   ```




## Usage

1. Run the data ingestion script to fetch and analyze news:
   ```bash
   python ingest.py
   ```

2. Start the Streamlit dashboard:
   ```bash
   streamlit run dashboard.py
   ```

3. Open your browser and navigate to the provided local URL (typically http://localhost:8501)
