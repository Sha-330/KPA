import re
from typing import Dict, List, Any, Optional, Tuple  # Added Tuple
import logging
from datetime import datetime
import json

from data_handler import DataHandler
from analyzer import PoliticalAnalyzer
from kpa_config import POLITICAL_PARTIES, KERALA_DISTRICTS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QueryProcessor:
    """Handles query parsing, intent classification, and response generation"""
    
    def __init__(self):
        self.data_handler = DataHandler()
        self.analyzer = PoliticalAnalyzer()
        
        # Query patterns for intent classification
        self.query_patterns = {
            'party_sentiment': [
                r'sentiment.*?({})',
                r'how.*?({}).*?doing',
                r'opinion.*?({})',
                r'public.*?view.*?({})'
            ],
            'regional_analysis': [
                r'({}).*?politics',
                r'political.*?situation.*?({})',
                r'what.*?happening.*?({})',
                r'news.*?from.*?({})'
            ],
            'trending_topics': [
                r'trending.*?topics?',
                r'what.*?popular',
                r'current.*?issues?',
                r'hot.*?topics?'
            ],
            'party_comparison': [
                r'compare.*?({}).*?({})',
                r'({}).*?vs.*?({})',
                r'difference.*?({}).*?({})',
                r'which.*?better.*?({}).*?({})'
            ],
            'temporal_analysis': [
                r'trend.*?over.*?time',
                r'recent.*?changes?',
                r'past.*?week',
                r'monthly.*?analysis'
            ]
        }
    
    def process_query(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process natural language query and return structured response"""
        try:
            # Clean and normalize query
            normalized_query = self._normalize_query(query)
            
            # Classify intent
            intent, entities = self._classify_intent(normalized_query)
            
            # Get latest data
            data = self._get_relevant_data(intent, entities)
            
            # Generate response based on intent
            response = self._generate_response(intent, entities, data, normalized_query)
            
            return {
                'query': query,
                'intent': intent,
                'entities': entities,
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                'query': query,
                'intent': 'unknown',
                'entities': {},
                'response': {
                    'message': 'I encountered an error while processing your query. Please try rephrasing it.',
                    'suggestions': ['Try asking about party sentiment', 'Ask about regional politics', 'Inquire about trending topics']
                },
                'timestamp': datetime.now().isoformat(),
                'status': 'error'
            }
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query text"""
        # Convert to lowercase
        query = query.lower().strip()
        
        # Remove punctuation except relevant ones
        query = re.sub(r'[^\w\s\?]', ' ', query)
        
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query)
        
        return query
    
    def _classify_intent(self, query: str) -> Tuple[str, Dict]:
        """Classify query intent and extract entities"""
        entities = {
            'parties': [],
            'districts': [],
            'timeframe': None
        }
        
        # Extract parties
        for party in POLITICAL_PARTIES:
            if party.lower() in query:
                entities['parties'].append(party)
        
        # Extract districts
        for district in KERALA_DISTRICTS:
            if district.lower() in query:
                entities['districts'].append(district)
        
        # Extract timeframe
        if any(word in query for word in ['recent', 'latest', 'current']):
            entities['timeframe'] = 'recent'
        elif any(word in query for word in ['past', 'previous', 'last']):
            entities['timeframe'] = 'past'
        
        # Match intent patterns
        for intent, patterns in self.query_patterns.items():
            for pattern in patterns:
                # Format pattern with party/district names if needed
                if '{}' in pattern:
                    all_entities = POLITICAL_PARTIES + KERALA_DISTRICTS
                    for entity in all_entities:
                        formatted_pattern = pattern.format(entity.lower())
                        if re.search(formatted_pattern, query):
                            return intent, entities
                else:
                    if re.search(pattern, query):
                        return intent, entities
        
        # Default intent based on entities
        if entities['parties'] and entities['districts']:
            return 'regional_party_analysis', entities
        elif entities['parties']:
            return 'party_sentiment', entities
        elif entities['districts']:
            return 'regional_analysis', entities
        else:
            return 'general_analysis', entities
    
    def _get_relevant_data(self, intent: str, entities: Dict) -> Any:
        """Fetch relevant data based on intent and entities"""
        # Get recent news data
        all_articles = []
        
        # Scrape from multiple sources
        for source in ['manorama', 'mathrubhumi']:
            try:
                articles = self.data_handler.scrape_news(source, max_articles=30)
                all_articles.extend(articles)
            except Exception as e:
                logger.error(f"Error scraping {source}: {str(e)}")
        
        if not all_articles:
            logger.warning("No articles scraped, using empty dataset")
            return self.data_handler.process_news_data([])
        
        # Process the data
        processed_data = self.data_handler.process_news_data(all_articles)
        
        return processed_data
    
    def _generate_response(self, intent: str, entities: Dict, data: Any, query: str) -> Dict[str, Any]:
        """Generate response based on intent and data"""
        if data.empty:
            return {
                'message': 'I could not find recent political news data. Please try again later.',
                'data': {},
                'suggestions': ['Check your internet connection', 'Try a different query']
            }
        
        # Generate insights
        insights = self.analyzer.generate_insights(data)
        
        response_generators = {
            'party_sentiment': self._generate_party_sentiment_response,
            'regional_analysis': self._generate_regional_response,
            'trending_topics': self._generate_trending_response,
            'party_comparison': self._generate_comparison_response,
            'temporal_analysis': self._generate_temporal_response,
            'general_analysis': self._generate_general_response
        }
        
        generator = response_generators.get(intent, self._generate_general_response)
        return generator(entities, insights, data)
    
    def _generate_party_sentiment_response(self, entities: Dict, insights: Dict, data: Any) -> Dict[str, Any]:
        """Generate party sentiment analysis response"""
        party_analysis = insights['party_analysis']
        
        if entities['parties']:
            # Focus on specific parties
            focused_analysis = {party: party_analysis.get(party, {}) for party in entities['parties']}
            
            message = f"Here's the sentiment analysis for {', '.join(entities['parties'])}:\n\n"
            for party, analysis in focused_analysis.items():
                if analysis:
                    message += f"**{party}**: {analysis['sentiment_category']} sentiment "
                    message += f"(Score: {analysis['average_sentiment']}) "
                    message += f"with {analysis['total_mentions']} recent mentions.\n"
                else:
                    message += f"**{party}**: No recent mentions found.\n"
        else:
            # General party sentiment overview
            sorted_parties = sorted(party_analysis.items(), 
                                  key=lambda x: x[1].get('total_mentions', 0), reverse=True)
            
            message = "Recent party sentiment analysis:\n\n"
            for party, analysis in sorted_parties[:5]:  # Top 5 parties
                message += f"**{party}**: {analysis['sentiment_category']} "
                message += f"({analysis['total_mentions']} mentions)\n"
        
        return {
            'message': message,
            'data': party_analysis,
            'chart_data': {
                'type': 'sentiment_chart',
                'parties': list(party_analysis.keys()),
                'sentiments': [analysis.get('average_sentiment', 0) for analysis in party_analysis.values()]
            }
        }
    
    def _generate_regional_response(self, entities: Dict, insights: Dict, data: Any) -> Dict[str, Any]:
        """Generate regional analysis response"""
        regional_analysis = insights['regional_analysis']
        
        if entities['districts']:
            # Focus on specific districts
            message = f"Political activity in {', '.join(entities['districts'])}:\n\n"
            for district in entities['districts']:
                if district in regional_analysis:
                    analysis = regional_analysis[district]
                    message += f"**{district}**:\n"
                    message += f"- {analysis['total_news_items']} recent news items\n"
                    message += f"- Top parties: {', '.join(analysis['top_parties'].keys())}\n"
                    message += f"- Activity score: {analysis['political_activity_score']}\n\n"
                else:
                    message += f"**{district}**: No recent political activity detected.\n\n"
        else:
            # General regional overview
            sorted_districts = sorted(regional_analysis.items(), 
                                    key=lambda x: x[1]['political_activity_score'], reverse=True)
            
            message = "Most politically active districts:\n\n"
            for district, analysis in sorted_districts[:5]:
                message += f"**{district}**: Activity score {analysis['political_activity_score']} "
                message += f"({analysis['total_news_items']} news items)\n"
        
        return {
            'message': message,
            'data': regional_analysis,
            'chart_data': {
                'type': 'regional_activity',
                'districts': list(regional_analysis.keys()),
                'activity_scores': [analysis['political_activity_score'] for analysis in regional_analysis.values()]
            }
        }
    
    def _generate_trending_response(self, entities: Dict, insights: Dict, data: Any) -> Dict[str, Any]:
        """Generate trending topics response"""
        trending_topics = insights['trending_topics']
        
        if not trending_topics:
            return {
                'message': 'No trending political topics detected in recent news.',
                'data': {},
                'suggestions': ['Try asking about specific parties', 'Ask about regional politics']
            }
        
        message = "Current trending political topics in Kerala:\n\n"
        for i, topic in enumerate(trending_topics[:5], 1):
            keywords = ', '.join(topic['keywords'])
            message += f"**Topic {i}**: {keywords}\n"
            message += f"- {topic['article_count']} articles discussing this\n"
            message += f"- Sentiment: {topic['average_sentiment']:.2f}\n"
            if topic['sample_titles']:
                message += f"- Sample: {topic['sample_titles'][0][:100]}...\n\n"
        
        return {
            'message': message,
            'data': trending_topics,
            'chart_data': {
                'type': 'trending_topics',
                'topics': [', '.join(topic['keywords'][:2]) for topic in trending_topics[:5]],
                'article_counts': [topic['article_count'] for topic in trending_topics[:5]]
            }
        }
    
    def _generate_comparison_response(self, entities: Dict, insights: Dict, data: Any) -> Dict[str, Any]:
        """Generate party comparison response"""
        party_analysis = insights['party_analysis']
        
        if len(entities['parties']) >= 2:
            parties = entities['parties'][:2]  # Compare first two parties
            
            message = f"Comparison between {parties[0]} and {parties[1]}:\n\n"
            
            for party in parties:
                if party in party_analysis:
                    analysis = party_analysis[party]
                    message += f"**{party}**:\n"
                    message += f"- Sentiment: {analysis['sentiment_category']} ({analysis['average_sentiment']})\n"
                    message += f"- Media mentions: {analysis['total_mentions']}\n"
                    message += f"- Recent activity: {analysis['recent_mentions']} mentions this week\n\n"
                else:
                    message += f"**{party}**: No recent data available\n\n"
        else:
            # General party comparison
            dominance = insights['party_dominance']
            sorted_parties = sorted(dominance.items(), key=lambda x: x[1], reverse=True)
            
            message = "Party dominance comparison:\n\n"
            for party, score in sorted_parties[:5]:
                message += f"**{party}**: Dominance score {score}\n"
        
        return {
            'message': message,
            'data': party_analysis,
            'chart_data': {
                'type': 'party_comparison',
                'parties': list(insights['party_dominance'].keys()),
                'dominance_scores': list(insights['party_dominance'].values())
            }
        }
    
    def _generate_temporal_response(self, entities: Dict, insights: Dict, data: Any) -> Dict[str, Any]:
        """Generate temporal analysis response"""
        temporal_trends = insights['temporal_trends']
        
        if not temporal_trends:
            return {
                'message': 'Insufficient temporal data for trend analysis.',
                'data': {},
                'suggestions': ['Ask about current sentiment', 'Try regional analysis']
            }
        
        message = "Recent political trends in Kerala:\n\n"
        
        if temporal_trends.get('sentiment_trend'):
            avg_sentiment = sum(temporal_trends['sentiment_trend']) / len(temporal_trends['sentiment_trend'])
            message += f"- Average sentiment over time: {avg_sentiment:.3f}\n"
        
        if temporal_trends.get('volume_trend'):
            total_volume = sum(temporal_trends['volume_trend'])
            message += f"- Total news volume: {total_volume} articles\n"
        
        if temporal_trends.get('relevance_trend'):
            avg_relevance = sum(temporal_trends['relevance_trend']) / len(temporal_trends['relevance_trend'])
            message += f"- Average political relevance: {avg_relevance:.3f}\n"
        
        message += "\nTrend direction: "
        if len(temporal_trends.get('sentiment_trend', [])) > 1:
            recent_sentiment = temporal_trends['sentiment_trend'][-1]
            earlier_sentiment = temporal_trends['sentiment_trend'][0]
            if recent_sentiment > earlier_sentiment:
                message += "Sentiment improving"
            elif recent_sentiment < earlier_sentiment:
                message += "Sentiment declining"
            else:
                message += "Sentiment stable"
        
        return {
            'message': message,
            'data': temporal_trends,
            'chart_data': {
                'type': 'temporal_trends',
                'dates': temporal_trends.get('dates', []),
                'sentiment': temporal_trends.get('sentiment_trend', []),
                'volume': temporal_trends.get('volume_trend', [])
            }
        }
    
    def _generate_general_response(self, entities: Dict, insights: Dict, data: Any) -> Dict[str, Any]:
        """Generate general analysis response"""
        summary = insights['summary']
        
        message = f"Kerala Political Landscape Overview:\n\n"
        message += f"- Analyzed {summary['total_articles']} recent articles\n"
        message += f"- Overall sentiment: {summary['overall_sentiment']:.3f}\n"
        message += f"- Political relevance: {summary['avg_political_relevance']:.3f}\n\n"
        
        # Top parties by dominance
        dominance = insights['party_dominance']
        sorted_parties = sorted(dominance.items(), key=lambda x: x[1], reverse=True)
        message += "Most active parties:\n"
        for party, score in sorted_parties[:3]:
            message += f"- {party}: {score}\n"
        
        # Most active regions
        regional = insights['regional_analysis']
        if regional:
            sorted_regions = sorted(regional.items(), 
                                  key=lambda x: x[1]['political_activity_score'], reverse=True)
            message += "\nMost active regions:\n"
            for region, analysis in sorted_regions[:3]:
                message += f"- {region}: Activity score {analysis['political_activity_score']}\n"
        
        return {
            'message': message,
            'data': insights,
            'chart_data': {
                'type': 'overview',
                'summary': summary,
                'top_parties': dict(sorted_parties[:5])
            }
        }

if __name__ == "__main__":
    # Example usage for testing
    processor = QueryProcessor()
    query = "What is the sentiment for BJP in Kerala?"
    result = processor.process_query(query)
    print(json.dumps(result, indent=2))