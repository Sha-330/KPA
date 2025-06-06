# C:\Users\Ajmal\Documents\programs\KPA\kpa_config.py
import os
from pathlib import Path

# Base Configuration
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
OUTPUTS_DIR = BASE_DIR / "outputs"
LOGS_DIR = BASE_DIR / "logs"

# Data Directories
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
CACHE_DIR = DATA_DIR / "cache"

# Create directories if they don't exist
for dir_path in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, CACHE_DIR, 
                 MODELS_DIR, OUTPUTS_DIR, LOGS_DIR]:
    dir_path.mkdir(exist_ok=True)

# API Configuration
NEWS_SOURCES = {
    'manorama': 'https://www.manoramaonline.com/news/kerala.html',
    'mathrubhumi': 'https://www.mathrubhumi.com/news/kerala',
    'malayala_manorama': 'https://malayalam.manoramaonline.com/news/kerala.html'
}

# Analysis Configuration
POLITICAL_PARTIES = [
    'LDF', 'UDF', 'BJP', 'CPM', 'INC', 'IUML', 'KC(M)', 'RSP', 'CPI'
]

KERALA_DISTRICTS = [
    'Thiruvananthapuram', 'Kollam', 'Pathanamthitta', 'Alappuzha', 'Kottayam',
    'Idukki', 'Ernakulam', 'Thrissur', 'Palakkad', 'Malappuram', 'Kozhikode',
    'Wayanad', 'Kannur', 'Kasaragod'
]

# Cache settings
CACHE_EXPIRY_HOURS = 24
MAX_CACHE_SIZE_MB = 100

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Environment variables
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///kerala_politics.db')
API_KEY = os.getenv('NEWS_API_KEY', '')