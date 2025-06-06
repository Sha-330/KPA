# Kerala Political Analyzer (KPA)
## A modular political data analytics tool focused on the Kerala political landscape. It scrapes regional news, extracts political sentiment, visualizes trends, and supports natural language query processing.


## Project Structure
```bash
├── __pycache__/            # Python cache files
├── logs/                   # Logging information
├── src/                    # Source code directory
│   ├── __pycache__/        # Python cache files for src
├── data/                   # Cached, raw, and processed data
│   ├── cache/              # Cached data
│   ├── processed/          # Processed data
│   ├── raw/                # Raw scraped data
├── logs/                   # Logging information (appears duplicated in image)
├── models/                 # Model storage directory
├── outputs/                # Output visualizations
│   ├── charts/             # Generated charts
│   │   ├── party_dominant_regions.png   # Party dominance chart
│   │   ├── political_dashboard.png     # Political dashboard chart
│   │   ├── regional_activity.png       # Regional activity chart
│   │   ├── sentiment_analysis.png      # Sentiment analysis chart
│   │   ├── temporal_trends.png         # Temporal trends chart
│   │   ├── trending_topics.png         # Trending topics chart
│   ├── __init__.py             # Package initializer
│   ├── analyzer.py             # Handles sentiment and entity analysis
│   ├── data_handler.py         # News scraping, cleaning, and caching
│   ├── kpa_config.py           # Configuration for paths, constants, and news sources
│   ├── query_processor.py      # NLP-based query parsing and response generation
│   ├── visualizer.py           # Chart generation using Matplotlib and Seaborn
├── main.py                 # Entry point to launch the KPA app
├── test.py                 # Unit and functional tests
```

🚀 Features

🔎 News Scraping: Scrapes live political news from trusted Kerala news sources.
💬 Query Understanding: Interprets natural language questions like "What’s the sentiment about BJP in Ernakulam?"
🧠 Sentiment & Entity Analysis: Identifies political parties, regions, and evaluates tone.
📊 Insightful Charts: Generates sentiment plots, trending topics, regional activity, and more.
🌐 Web Interface: Lightweight index.html frontend for querying insights.
📦 Caching & Logging: Efficient disk caching and log-based debugging.


⚙️ Installation
Prerequisites

Python 3.8+
pip

Setup
```bash
git clone https://github.com/yourusername/kerala-political-analyzer.git
cd kerala-political-analyzer
pip install -r requirements.txt
```

▶️ Usage
🧠 Run via Terminal
python main.py

This starts the CLI or backend API for processing and responding to queries.
🌍 Web Interface (Optional)
Open index.html in your browser. It connects to the backend (if integrated via Flask/FastAPI) to query live insights.
🧪 Running Tests
python test.py

Includes test cases for scraping, sentiment analysis, and query parsing.
📈 Sample Query
from query_processor import QueryProcessor

processor = QueryProcessor()
query = "What is the sentiment about UDF in Thrissur?"
result = processor.process_query(query)
print(result["response"]["message"])


📊 Visualizations
Example output charts generated under /outputs/charts/:

Party Sentiment Bar Plot
Regional Activity Heatmap
Temporal Trends Over Time
Party Comparison Charts
Trending Topic Pie Charts


🔐 Environment Variables
Create a .env file or export manually:
export NEWS_API_KEY=your_api_key_here
export DATABASE_URL=sqlite:///kerala_politics.db


🧠 Contributors

Ajmal Shan. P (@Sha-330)


📝 TODO

Enhance NLP query parser with transformer models.
Integrate live dashboards via Streamlit or Flask.
Improve entity recognition using spaCy or NER models.
Dockerize the application.


🙌 Acknowledgments
Special thanks to Kerala news sources and open-source communities for enabling this political insight engine.
