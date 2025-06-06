# C:\Users\Ajmal\Documents\programs\KPA\src\analyzer.py
import logging
from kpa_config import POLITICAL_PARTIES, KERALA_DISTRICTS

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/analyzer.log'),
        logging.StreamHandler()
    ]
)

class PoliticalAnalyzer:
    """Class to analyze political data for the Kerala Political Analyzer"""
    
    def __init__(self):
        """Initialize the PoliticalAnalyzer"""
        self.parties = POLITICAL_PARTIES
        self.districts = KERALA_DISTRICTS
        logging.info("PoliticalAnalyzer initialized")

    def analyze_sentiment(self, text):
        """Analyze the sentiment of a text"""
        if not text or not isinstance(text, str):
            return {'sentiment': 'neutral', 'confidence': 0.0}
        
        text = text.lower()
        if 'excellent' in text or 'success' in text:
            sentiment = 'positive'
            confidence = 0.8
        elif 'failed' in text or 'disappointing' in text:
            sentiment = 'negative'
            confidence = 0.7
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {'sentiment': sentiment, 'confidence': confidence}

    def extract_entities(self, text):
        """Extract entities from text"""
        if not text or not isinstance(text, str):
            return {'parties': [], 'districts': [], 'persons': []}
        
        text = text.lower()
        entities = {'parties': [], 'districts': [], 'persons': []}
        
        for party in self.parties:
            if party.lower() in text:
                entities['parties'].append(party)
        for district in self.districts:
            if district.lower() in text:
                entities['districts'].append(district)
        
        return entities

    def generate_insights(self, data):
        """Generate insights from processed data"""
        if not data or 'articles' not in data:
            return {
                'metrics': {},
                'sentiment_overview': {},
                'party_mentions': {},
                'trends': {}
            }
        
        articles = data['articles']
        party_mentions = {party: 0 for party in self.parties}
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for article in articles:
            entities = article.get('entities', {})
            sentiment = article.get('sentiment', {}).get('sentiment', 'neutral')
            
            for party in entities.get('parties', []):
                if party in party_mentions:
                    party_mentions[party] += 1
            
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        return {
            'metrics': {'total_articles': len(articles)},
            'sentiment_overview': sentiment_counts,
            'party_mentions': party_mentions,
            'trends': {}  # Placeholder for trend analysis
        }

    def compare_parties(self, party1, party1_data, party2, party2_data):
        """Compare two parties based on their data"""
        return {
            'party1': party1,
            'party2': party2,
            'comparison_metrics': {
                'mentions_diff': party1_data['mentions'] - party2_data['mentions'],
                'sentiment_diff': sum(party1_data['sentiment_scores']) / len(party1_data['sentiment_scores']) -
                                 sum(party2_data['sentiment_scores']) / len(party2_data['sentiment_scores'])
            }
        }