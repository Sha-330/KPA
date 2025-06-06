import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Optional, Any
import re
import time
import hashlib
# At the top of the file
from kpa_config import POLITICAL_PARTIES, KERALA_DISTRICTS, NEWS_SOURCES, CACHE_DIR, CACHE_EXPIRY_HOURS, MAX_CACHE_SIZE_MB


logger = logging.getLogger(__name__)

class DataHandler:
    """Handles data ingestion, cleaning, and basic processing"""
    
    def __init__(self):
        self.cache_dir = CACHE_DIR
        self.raw_dir = RAW_DATA_DIR
        self.processed_dir = PROCESSED_DATA_DIR
        
    def scrape_news(self, source: str, max_articles: int = 50) -> List[Dict]:
        """Scrape news articles from Kerala news sources"""
        cache_key = f"news_{source}_{datetime.now().strftime('%Y%m%d')}"
        cached_data = self._get_cache(cache_key)
        
        if cached_data:
            logger.info(f"Using cached data for {source}")
            return cached_data
        
        articles = []
        try:
            if source in NEWS_SOURCES:
                url = NEWS_SOURCES[source]
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Generic article extraction (adjust selectors for each source)
                article_elements = soup.find_all(['article', 'div'], 
                                               class_=re.compile(r'.*article.*|.*news.*|.*story.*'))
                
                for element in article_elements[:max_articles]:
                    title_elem = element.find(['h1', 'h2', 'h3', 'a'])
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        link = title_elem.get('href', '') if title_elem.name == 'a' else ''
                        
                        # Extract date if available
                        date_elem = element.find(['time', 'span'], 
                                                class_=re.compile(r'.*date.*|.*time.*'))
                        date = date_elem.get_text(strip=True) if date_elem else str(datetime.now().date())
                        
                        if title and len(title) > 20:  # Filter out short/irrelevant titles
                            articles.append({
                                'title': title,
                                'source': source,
                                'link': link,
                                'date': date,
                                'scraped_at': datetime.now().isoformat()
                            })
                
                logger.info(f"Scraped {len(articles)} articles from {source}")
                
        except Exception as e:
            logger.error(f"Error scraping {source}: {str(e)}")
        
        # Cache the results
        self._set_cache(cache_key, articles)
        return articles
    
    def load_historical_data(self, file_path: str) -> pd.DataFrame:
        """Load historical election/political data"""
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.json'):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                df = pd.DataFrame(data)
            else:
                raise ValueError("Unsupported file format")
            
            logger.info(f"Loaded {len(df)} records from {file_path}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading historical data: {str(e)}")
            return pd.DataFrame()
    
    def clean_text_data(self, text: str) -> str:
        """Clean and preprocess text data"""
        if not isinstance(text, str):
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep Malayalam characters
        text = re.sub(r'[^\w\s\u0D00-\u0D7F]', '', text)
        
        return text.strip()
    
    def process_news_data(self, articles: List[Dict]) -> pd.DataFrame:
        """Process scraped news articles"""
        df = pd.DataFrame(articles)
        
        if df.empty:
            return df
        
        # Clean titles
        df['title_cleaned'] = df['title'].apply(self.clean_text_data)
        
        # Extract political entities
        df['parties_mentioned'] = df['title_cleaned'].apply(self._extract_parties)
        df['districts_mentioned'] = df['title_cleaned'].apply(self._extract_districts)
        
        # Sentiment scoring (basic)
        df['sentiment_score'] = df['title_cleaned'].apply(self._basic_sentiment)
        
        # Political relevance score
        df['political_relevance'] = df.apply(self._calculate_relevance, axis=1)
        
        # Save processed data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.processed_dir / f"processed_news_{timestamp}.csv"
        df.to_csv(output_file, index=False)
        
        return df
    
    def _extract_parties(self, text: str) -> List[str]:
        """Extract mentioned political parties from text"""
        parties_found = []
        text_upper = text.upper()
        
        for party in POLITICAL_PARTIES:
            if party.upper() in text_upper:
                parties_found.append(party)
        
        return parties_found
    
    def _extract_districts(self, text: str) -> List[str]:
        """Extract mentioned districts from text"""
        districts_found = []
        text_upper = text.upper()
        
        for district in KERALA_DISTRICTS:
            if district.upper() in text_upper:
                districts_found.append(district)
        
        return districts_found
    
    def _basic_sentiment(self, text: str) -> float:
        """Basic sentiment analysis"""
        positive_words = ['good', 'great', 'excellent', 'positive', 'success', 'victory', 'win']
        negative_words = ['bad', 'terrible', 'negative', 'failure', 'defeat', 'loss', 'crisis']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count + neg_count == 0:
            return 0.0
        
        return (pos_count - neg_count) / (pos_count + neg_count)
    
    def _calculate_relevance(self, row) -> float:
        """Calculate political relevance score"""
        score = 0.0
        
        # Points for party mentions
        score += len(row['parties_mentioned']) * 0.3
        
        # Points for district mentions
        score += len(row['districts_mentioned']) * 0.2
        
        # Points for political keywords
        political_keywords = ['election', 'vote', 'campaign', 'politics', 'government', 'minister']
        title_lower = row['title_cleaned'].lower()
        score += sum(0.1 for keyword in political_keywords if keyword in title_lower)
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _get_cache(self, key: str) -> Optional[Any]:
        """Get data from cache"""
        cache_file = self.cache_dir / f"{key}.pkl"
        
        if cache_file.exists():
            # Check if cache is still valid
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age < timedelta(hours=CACHE_EXPIRY_HOURS):
                try:
                    with open(cache_file, 'rb') as f:
                        return pickle.load(f)
                except Exception as e:
                    logger.error(f"Error reading cache: {str(e)}")
        
        return None
    
    def _set_cache(self, key: str, data: Any) -> None:
        """Set data in cache"""
        try:
            cache_file = self.cache_dir / f"{key}.pkl"
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            logger.error(f"Error writing to cache: {str(e)}")