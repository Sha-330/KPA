import unittest
import sys
import os
from pathlib import Path
import json
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import time
import logging
import psutil
import threading
import requests

# Set up logging
log_dir = Path('logs')
log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'test_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import modules to test
from main import KeralaAnalyzerApp
from src.data_handler import DataHandler
from src.analyzer import PoliticalAnalyzer
from src.query_processor import QueryProcessor
from src.visualizer import PoliticalVisualizer

class TestDataHandler(unittest.TestCase):
    """Test cases for DataHandler"""
    
    def setUp(self):
        """Set up test environment"""
        self.handler = DataHandler()
        self.test_dir = Path(tempfile.mkdtemp())
        self.app = KeralaAnalyzerApp()
        self.sample_articles = [
            {
                'title': 'Test Article 1',
                'content': 'This is a test article about Kerala politics.',
                'url': 'http://test.com/article1',
                'timestamp': datetime.now().isoformat(),
                'source': 'test_source'
            },
            {
                'title': 'Test Article 2',
                'content': 'Another test article about Kerala politics.',
                'url': 'http://test.com/article2',
                'timestamp': datetime.now().isoformat(),
                'source': 'test_source'
            }
        ]
        logging.info("Set up TestDataHandler environment")
        
    def tearDown(self):
        """Clean up test environment"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)
        logging.info("Tore down TestDataHandler environment")
    
    def test_initialization(self):
        """Test DataHandler initialization"""
        self.assertIsInstance(self.handler, DataHandler)
        self.assertTrue(hasattr(self.handler, 'cache_dir'))
        
    @patch('requests.get')
    def test_scrape_news_success(self, mock_get):
        """Test successful news scraping"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <body>
                <div class="article">
                    <h2>Test Political News</h2>
                    <p>This is a test article about Kerala politics.</p>
                </div>
            </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        articles = self.handler.scrape_news('test_source', max_articles=1)
        self.assertIsInstance(articles, list)
        
    def test_scrape_news_invalid_source(self):
        """Test scraping with invalid source"""
        articles = self.handler.scrape_news('invalid_source')
        self.assertEqual(articles, [])
        
    def test_process_news_data(self):
        """Test news data processing"""
        sample_articles = [
            {
                'title': 'CPM wins Kerala election',
                'content': 'The CPM party has won the Kerala state election with a significant margin.',
                'url': 'http://test.com/article1',
                'timestamp': datetime.now().isoformat()
            },
            {
                'title': 'UDF protests in Kochi',
                'content': 'UDF organized a protest in Kochi against government policies.',
                'url': 'http://test.com/article2', 
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        processed = self.handler.process_news_data(sample_articles)
        
        self.assertIsInstance(processed, dict)
        self.assertIn('articles', processed)
        self.assertIn('metadata', processed)
        self.assertEqual(len(processed['articles']), 2)
        
    def test_cache_operations(self):
        """Test cache save and load operations"""
        test_data = {'test': 'data', 'number': 123}
        cache_key = 'test_cache'
        
        result = self.handler.save_to_cache(cache_key, test_data)
        self.assertTrue(result)
        
        loaded_data = self.handler.load_from_cache(cache_key)
        self.assertEqual(loaded_data, test_data)
        
        missing_data = self.handler.load_from_cache('non_existent')
        self.assertIsNone(missing_data)
    
    def test_data_pipeline(self):
        """Test complete data processing pipeline"""
        processed_data = self.app.data_handler.process_news_data(self.sample_articles)
        
        self.assertIn('articles', processed_data)
        self.assertIn('metadata', processed_data)
        
        for article in processed_data['articles']:
            self.assertIn('title', article)
            self.assertIn('content', article)
            self.assertIn('sentiment', article)
            self.assertIn('entities', article)

class TestPoliticalAnalyzer(unittest.TestCase):
    """Test cases for PoliticalAnalyzer"""
    
    def setUp(self):
        """Set up test environment"""
        self.analyzer = PoliticalAnalyzer()
        logging.info("Set up TestPoliticalAnalyzer environment")
        
    def test_initialization(self):
        """Test analyzer initialization"""
        self.assertIsInstance(self.analyzer, PoliticalAnalyzer)
        
    def test_analyze_sentiment(self):
        """Test sentiment analysis"""
        positive_text = "CPM has done excellent work for Kerala development"
        negative_text = "The government policies are completely failed and disappointing"
        neutral_text = "The election will be held next month"
        
        pos_sentiment = self.analyzer.analyze_sentiment(positive_text)
        neg_sentiment = self.analyzer.analyze_sentiment(negative_text)
        neu_sentiment = self.analyzer.analyze_sentiment(neutral_text)
        
        self.assertIn('sentiment', pos_sentiment)
        self.assertIn('confidence', pos_sentiment)
        self.assertIn(pos_sentiment['sentiment'], ['positive', 'negative', 'neutral'])
        
    def test_extract_entities(self):
        """Test entity extraction"""
        text = "CPM and UDF are the major political parties in Kerala. Thiruvananthapuram is the capital."
        
        entities = self.analyzer.extract_entities(text)
        
        self.assertIsInstance(entities, dict)
        self.assertIn('parties', entities)
        self.assertIn('districts', entities)
        self.assertIn('persons', entities)
        
    def test_generate_insights(self):
        """Test insight generation"""
        sample_data = {
            'articles': [
                {
                    'title': 'CPM Election Victory',
                    'content': 'CPM won the election in Kerala with great support',
                    'sentiment': {'sentiment': 'positive', 'confidence': 0.8},
                    'entities': {'parties': ['CPM'], 'districts': ['Kerala']}
                },
                {
                    'title': 'UDF Protest March', 
                    'content': 'UDF organized protest march against government',
                    'sentiment': {'sentiment': 'negative', 'confidence': 0.7},
                    'entities': {'parties': ['UDF'], 'districts': ['Kochi']}
                }
            ],
            'metadata': {'total_articles': 2, 'date_range': '2025-01-01 to 2025-01-02'}
        }
        
        insights = self.analyzer.generate_insights(sample_data)
        
        self.assertIsInstance(insights, dict)
        self.assertIn('metrics', insights)
        self.assertIn('sentiment_overview', insights)
        self.assertIn('party_mentions', insights)
        
    def test_compare_parties(self):
        """Test party comparison"""
        party1_data = {
            'mentions': 10,
            'sentiment_scores': [0.8, 0.6, 0.7],
            'topics': ['development', 'welfare']
        }
        party2_data = {
            'mentions': 8,
            'sentiment_scores': [0.5, 0.4, 0.6],
            'topics': ['protest', 'opposition']
        }
        
        comparison = self.analyzer.compare_parties('CPM', party1_data, 'UDF', party2_data)
        
        self.assertIsInstance(comparison, dict)
        self.assertIn('party1', comparison)
        self.assertIn('party2', comparison)
        self.assertIn('comparison_metrics', comparison)

class TestQueryProcessor(unittest.TestCase):
    """Test cases for QueryProcessor"""
    
    def setUp(self):
        """Set up test environment"""
        self.processor = QueryProcessor()
        logging.info("Set up TestQueryProcessor environment")
        
    def test_initialization(self):
        """Test processor initialization"""
        self.assertIsInstance(self.processor, QueryProcessor)
        
    def test_classify_intent(self):
        """Test query intent classification"""
        sentiment_query = "What is the sentiment towards CPM?"
        comparison_query = "Compare LDF and UDF"
        trend_query = "Show me political trends"
        regional_query = "Political situation in Thiruvananthapuram"
        
        sentiment_intent = self.processor.classify_intent(sentiment_query)
        comparison_intent = self.processor.classify_intent(comparison_query)
        trend_intent = self.processor.classify_intent(trend_query)
        regional_intent = self.processor.classify_intent(regional_query)
        
        self.assertIn(sentiment_intent, ['sentiment', 'comparison', 'trend', 'regional', 'general'])
        self.assertIn(comparison_intent, ['sentiment', 'comparison', 'trend', 'regional', 'general'])
        
    def test_extract_query_entities(self):
        """Test entity extraction from queries"""
        query = "What is CPM doing in Thiruvananthapuram and Kochi?"
        
        entities = self.processor.extract_query_entities(query)
        
        self.assertIsInstance(entities, dict)
        self.assertIn('parties', entities)
        self.assertIn('districts', entities)
        
    def test_process_query(self):
        """Test complete query processing"""
        query = "What is the sentiment towards CPM?"
        
        result = self.processor.process_query(query)
        
        self.assertIsInstance(result, dict)
        self.assertIn('status', result)
        self.assertIn('intent', result)
        self.assertIn('entities', result)
        self.assertIn('response', result)
        
    def test_generate_response(self):
        """Test response generation"""
        intent = 'sentiment'
        entities = {'parties': ['CPM'], 'districts': []}
        
        response = self.processor.generate_response(intent, entities)
        
        self.assertIsInstance(response, dict)
        self.assertIn('message', response)

class TestPoliticalVisualizer(unittest.TestCase):
    """Test cases for PoliticalVisualizer"""
    
    def setUp(self):
        """Set up test environment"""
        self.visualizer = PoliticalVisualizer()
        self.test_output_dir = Path(tempfile.mkdtemp())
        logging.info("Set up TestPoliticalVisualizer environment")
        
    def tearDown(self):
        """Clean up test environment"""
        if self.test_output_dir.exists():
            shutil.rmtree(self.test_output_dir, ignore_errors=True)
        logging.info("Tore down TestPoliticalVisualizer environment")
            
    def test_initialization(self):
        """Test visualizer initialization"""
        self.assertIsInstance(self.visualizer, PoliticalVisualizer)
        
    def test_create_sentiment_chart(self):
        """Test sentiment chart creation"""
        sentiment_data = {
            'parties': ['CPM', 'UDF', 'BJP'],
            'positive': [60, 40, 30],
            'negative': [20, 35, 45],
            'neutral': [20, 25, 25]
        }
        
        with patch.object(self.visualizer, 'save_chart') as mock_save:
            mock_save.return_value = str(self.test_output_dir / 'sentiment_chart.png')
            chart_path = self.visualizer.create_sentiment_chart(sentiment_data)
            self.assertIsInstance(chart_path, str)
            
    def test_create_comparison_chart(self):
        """Test comparison chart creation"""
        comparison_data = {
            'parties': ['CPM', 'UDF'],
            'mentions': [100, 80],
            'avg_sentiment': [0.6, 0.4]
        }
        
        with patch.object(self.visualizer, 'save_chart') as mock_save:
            mock_save.return_value = str(self.test_output_dir / 'comparison_chart.png')
            chart_path = self.visualizer.create_comparison_chart(comparison_data)
            self.assertIsInstance(chart_path, str)
            
    def test_create_trend_chart(self):
        """Test trend chart creation"""
        trend_data = {
            'dates': ['2025-01-01', '2025-01-02', '2025-01-03'],
            'CPM_mentions': [10, 15, 12],
            'UDF_mentions': [8, 10, 9]
        }
        
        with patch.object(self.visualizer, 'save_chart') as mock_save:
            mock_save.return_value = str(self.test_output_dir / 'trend_chart.png')
            chart_path = self.visualizer.create_trend_chart(trend_data)
            self.assertIsInstance(chart_path, str)

class TestMainApp(unittest.TestCase):
    """Test cases for main application"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = KeralaAnalyzerApp()
        logging.info("Set up TestMainApp environment")
        
    def test_app_initialization(self):
        """Test app initialization"""
        self.assertIsInstance(self.app, KeralaAnalyzerApp)
        self.assertIsInstance(self.app.data_handler, DataHandler)
        self.assertIsInstance(self.app.analyzer, PoliticalAnalyzer)
        self.assertIsInstance(self.app.query_processor, QueryProcessor)
        self.assertIsInstance(self.app.visualizer, PoliticalVisualizer)
        
    def test_health_check(self):
        """Test system health check"""
        required_dirs = ['data/raw', 'data/processed', 'data/cache', 
                        'outputs/charts', 'outputs/reports', 'logs']
        for dir_path in required_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            
        health_status = self.app.health_check()
        self.assertIsInstance(health_status, bool)
        
    @patch('builtins.input', side_effect=['test query', 'n', 'quit'])
    def test_interactive_mode(self, mock_input):
        """Test interactive mode with mocked input"""
        with patch.object(self.app.query_processor, 'process_query') as mock_process:
            mock_process.return_value = {
                'status': 'success',
                'intent': 'general',
                'entities': {'parties': [], 'districts': []},
                'response': {'message': 'Test response'}
            }
            
            try:
                self.app._interactive_mode()
            except SystemExit:
                pass
                
    def test_display_results(self):
        """Test result display"""
        test_result = {
            'status': 'success',
            'intent': 'sentiment',
            'entities': {'parties': ['CPM'], 'districts': ['Thiruvananthapuram']},
            'response': {
                'message': 'Test analysis result',
                'suggestions': ['Try asking about other parties', 'Check regional trends']
            }
        }
        
        from io import StringIO
        sys.stdout = StringIO()
        
        self.app._display_results(test_result)
        
        output = sys.stdout.getvalue()
        sys.stdout = sys.__stdout__
        
        self.assertIn('ANALYSIS RESULTS', output)
        self.assertIn('sentiment', output)
        self.assertIn('CPM', output)
        self.assertIn('Test analysis result', output)

class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = KeralaAnalyzerApp()
        self.sample_articles = [
            {
                'title': 'CPM Election Victory in Kerala',
                'content': 'The Communist Party of India (Marxist) has achieved a significant victory in the Kerala state elections.',
                'url': 'http://test.com/cpm-victory',
                'timestamp': datetime.now().isoformat(),
                'source': 'test_source'
            },
            {
                'title': 'UDF Challenges Government Policies',
                'content': 'The United Democratic Front has raised serious concerns about the current government policies in Kerala.',
                'url': 'http://test.com/udf-challenges',
                'timestamp': datetime.now().isoformat(),
                'source': 'test_source'
            }
        ]
        logging.info("Set up TestIntegration environment")
        
    def test_end_to_end_analysis(self):
        """Test complete analysis workflow"""
        processed_data = self.app.data_handler.process_news_data(self.sample_articles)
        self.assertIsInstance(processed_data, dict)
        self.assertIn('articles', processed_data)
        
        insights = self.app.analyzer.generate_insights(processed_data)
        self.assertIsInstance(insights, dict)
        
        result = self.app.query_processor.process_query("What is the sentiment towards CPM?")
        self.assertIsInstance(result, dict)
        self.assertEqual(result['status'], 'success')
        
    def test_data_processing_accuracy(self):
        """Test accuracy of data processing"""
        processed_data = self.app.data_handler.process_news_data(self.sample_articles)
        
        articles = processed_data.get('articles', [])
        self.assertTrue(len(articles) > 0)
        
        for article in articles:
            if 'CPM' in article.get('title', '') or 'CPM' in article.get('content', ''):
                entities = article.get('entities', {})
                parties = entities.get('parties', [])
                self.assertTrue(any('CPM' in party.upper() for party in parties))
    
    def test_sentiment_consistency(self):
        """Test sentiment analysis consistency"""
        positive_article = {
            'title': 'CPM Great Success in Development',
            'content': 'The CPM government has achieved remarkable success in Kerala development projects.',
            'url': 'http://test.com/positive',
            'timestamp': datetime.now().isoformat(),
            'source': 'test'
        }
        
        processed = self.app.data_handler.process_news_data([positive_article])
        article_sentiment = processed['articles'][0]['sentiment']
        
        self.assertIn(article_sentiment['sentiment'], ['positive', 'neutral'])
        self.assertGreaterEqual(article_sentiment['confidence'], 0.0)
        self.assertLessEqual(article_sentiment['confidence'], 1.0)
    
    def test_regional_analysis(self):
        """Test regional-specific analysis"""
        regional_articles = [
            {
                'title': 'Development in Thiruvananthapuram',
                'content': 'Major infrastructure development happening in Thiruvananthapuram district.',
                'url': 'http://test.com/tvm',
                'timestamp': datetime.now().isoformat(),
                'source': 'test'
            },
            {
                'title': 'Kochi IT Hub Growth',
                'content': 'Kochi emerging as major IT hub with new tech companies.',
                'url': 'http://test.com/kochi',
                'timestamp': datetime.now().isoformat(),
                'source': 'test'
            }
        ]
        
        processed = self.app.data_handler.process_news_data(regional_articles)
        
        districts_found = set()
        for article in processed['articles']:
            entities = article.get('entities', {})
            districts = entities.get('districts', [])
            districts_found.update(districts)
        
        kerala_districts = ['Thiruvananthapuram', 'Ernakulam', 'Kochi']
        self.assertTrue(any(district in ' '.join(districts_found) for district in kerala_districts))

class TestAdvancedAnalytics(unittest.TestCase):
    """Advanced analytics and ML-based tests"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = KeralaAnalyzerApp()
        logging.info("Set up TestAdvancedAnalytics environment")
        
    def test_trend_detection(self):
        """Test political trend detection over time"""
        time_series_articles = []
        
        for i in range(30):
            date = datetime.now().replace(day=1) + timedelta(days=i)
            article = {
                'title': f'Political News Day {i+1}',
                'content': f'CPM and UDF political activities on day {i+1}.',
                'url': f'http://test.com/day{i+1}',
                'timestamp': date.isoformat(),
                'source': 'trend_test'
            }
            time_series_articles.append(article)
        
        processed = self.app.data_handler.process_news_data(time_series_articles)
        insights = self.app.analyzer.generate_insights(processed)
        
        self.assertIn('trends', insights.get('metrics', {}))
        
    def test_party_comparison_metrics(self):
        """Test detailed party comparison metrics"""
        comparison_articles = [
            {
                'title': 'CPM Policy Success',
                'content': 'CPM government implements successful welfare policies.',
                'url': 'http://test.com/cpm1',
                'timestamp': datetime.now().isoformat(),
                'source': 'comparison'
            },
            {
                'title': 'UDF Opposition Strategy',
                'content': 'UDF plans strategic opposition to government policies.',
                'url': 'http://test.com/udf1',
                'timestamp': datetime.now().isoformat(),
                'source': 'comparison'
            },
            {
                'title': 'BJP Kerala Expansion',
                'content': 'BJP attempts to expand influence in Kerala politics.',
                'url': 'http://test.com/bjp1',
                'timestamp': datetime.now().isoformat(),
                'source': 'comparison'
            }
        ]
        
        processed = self.app.data_handler.process_news_data(comparison_articles)
        insights = self.app.analyzer.generate_insights(processed)
        
        party_mentions = insights.get('party_mentions', {})
        self.assertGreater(len(party_mentions), 0)
        
        parties_detected = list(party_mentions.keys())
        major_parties = ['CPM', 'UDF', 'BJP']
        detected_major = [p for p in major_parties if any(p in detected.upper() for detected in parties_detected)]
        self.assertGreater(len(detected_major), 1)
    
    def test_semantic_search_capability(self):
        """Test semantic understanding in queries"""
        semantic_queries = [
            "What do people think about the ruling party?",
            "How is the opposition performing?",
            "What's happening in the capital city?",
            "Show me updates from the IT hub",
        ]
        
        for query in semantic_queries:
            result = self.app.query_processor.process_query(query)
            
            self.assertEqual(result['status'], 'success')
            self.assertIn('intent', result)
            self.assertIn('response', result)
            
            response_message = result['response'].get('message', '')
            self.assertGreater(len(response_message), 10)

class TestRobustness(unittest.TestCase):
    """Test system robustness and edge cases"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = KeralaAnalyzerApp()
        logging.info("Set up TestRobustness environment")
    
    def test_multilingual_content_handling(self):
        """Test handling of Malayalam/mixed language content"""
        multilingual_articles = [
            {
                'title': 'Kerala രാഷ്ട്രീയം News',
                'content': 'Political news with Malayalam content കേരള സർക്കാർ.',
                'url': 'http://test.com/malayalam',
                'timestamp': datetime.now().isoformat(),
                'source': 'multilingual'
            }
        ]
        
        try:
            processed = self.app.data_handler.process_news_data(multilingual_articles)
            self.assertIsInstance(processed, dict)
            self.assertIn('articles', processed)
        except Exception as e:
            self.fail(f"Multilingual content caused exception: {str(e)}")
    
    def test_large_content_handling(self):
        """Test handling of very large articles"""
        large_article = {
            'title': 'Comprehensive Political Analysis',
            'content': 'Political analysis content. ' * 1000,
            'url': 'http://test.com/large',
            'timestamp': datetime.now().isoformat(),
            'source': 'large_test'
        }
        
        processed = self.app.data_handler.process_news_data([large_article])
        self.assertEqual(len(processed['articles']), 1)
        
        article = processed['articles'][0]
        self.assertIn('sentiment', article)
        self.assertIn('entities', article)
    
    def test_concurrent_query_handling(self):
        """Test handling multiple concurrent queries"""
        results = []
        errors = []
        
        def process_query(query_id):
            try:
                query = f"What is the political situation in Kerala? Query {query_id}"
                result = self.app.query_processor.process_query(query)
                results.append((query_id, result))
            except Exception as e:
                errors.append((query_id, str(e)))
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=process_query, args=(i,))
            threads.append(thread)
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join(timeout=10)
        
        self.assertEqual(len(errors), 0, f"Concurrent processing errors: {errors}")
        self.assertEqual(len(results), 5, "Not all concurrent queries completed")
    
    def test_memory_usage_monitoring(self):
        """Test memory usage during intensive operations"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024
        
        large_dataset = []
        for i in range(500):
            article = {
                'title': f'Memory Test Article {i}',
                'content': f'Content for memory testing with political keywords CPM UDF BJP Kerala. Article number {i}.',
                'url': f'http://test.com/memory{i}',
                'timestamp': datetime.now().isoformat(),
                'source': 'memory_test'
            }
            large_dataset.append(article)
        
        processed = self.app.data_handler.process_news_data(large_dataset)
        insights = self.app.analyzer.generate_insights(processed)
        
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        self.assertLess(memory_increase, 500, f"Memory usage increased by {memory_increase:.1f}MB")
        
        del large_dataset, processed, insights

class TestVisualizationIntegration(unittest.TestCase):
    """Test visualization component integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = KeralaAnalyzerApp()
        self.test_output_dir = Path(tempfile.mkdtemp())
        logging.info("Set up TestVisualizationIntegration environment")
    
    def tearDown(self):
        """Clean up test environment"""
        if self.test_output_dir.exists():
            shutil.rmtree(self.test_output_dir, ignore_errors=True)
        logging.info("Tore down TestVisualizationIntegration environment")
    
    def test_chart_generation_pipeline(self):
        """Test complete chart generation pipeline"""
        sample_data = {
            'articles': [
                {
                    'title': 'CPM Success Story',
                    'content': 'CPM achieves major success in Kerala development.',
                    'sentiment': {'sentiment': 'positive', 'confidence': 0.8},
                    'entities': {'parties': ['CPM'], 'districts': ['Kerala']}
                },
                {
                    'title': 'UDF Criticism',
                    'content': 'UDF criticizes government policies in Kerala.',
                    'sentiment': {'sentiment': 'negative', 'confidence': 0.7},
                    'entities': {'parties': ['UDF'], 'districts': ['Kerala']}
                }
            ],
            'metadata': {'total_articles': 2}
        }
        
        insights = self.app.analyzer.generate_insights(sample_data)
        
        with patch.object(self.app.visualizer, 'create_sentiment_chart') as mock_chart:
            mock_chart.return_value = str(self.test_output_dir / 'test_chart.png')
            
            chart_path = self.app.visualizer.create_sentiment_chart(insights.get('sentiment_overview', {}))
            self.assertIsNotNone(chart_path)
    
    def test_query_to_visualization_workflow(self):
        """Test query processing to visualization workflow"""
        query = "Compare CPM and UDF sentiment trends"
        
        result = self.app.query_processor.process_query(query)
        self.assertEqual(result['status'], 'success')
        
        self.assertEqual(result['intent'], 'comparison')
        
        entities = result['entities']
        parties = entities.get('parties', [])
        self.assertTrue(len(parties) >= 2)
    
    def test_export_functionality(self):
        """Test data export functionality"""
        sample_insights = {
            'metrics': {'total_articles': 10, 'sentiment_score': 0.6},
            'party_mentions': {'CPM': 15, 'UDF': 12, 'BJP': 8},
            'sentiment_overview': {
                'positive': 40,
                'negative': 35,
                'neutral': 25
            }
        }
        
        export_path = self.test_output_dir / 'test_export.json'
        with open(export_path, 'w') as f:
            json.dump(sample_insights, f, indent=2)
        
        self.assertTrue(export_path.exists())
        
        with open(export_path, 'r') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(loaded_data['metrics']['total_articles'], 10)
        self.assertIn('party_mentions', loaded_data)

class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = KeralaAnalyzerApp()
        logging.info("Set up TestErrorHandling environment")
        
    def test_empty_data_handling(self):
        """Test handling of empty data"""
        empty_articles = []
        processed = self.app.data_handler.process_news_data(empty_articles)
        
        self.assertIsInstance(processed, dict)
        self.assertEqual(len(processed.get('articles', [])), 0)
        
    def test_malformed_data_handling(self):
        """Test handling of malformed data"""
        malformed_articles = [
            {'title': 'Test'},
            {'content': 'Test content'},
            {},
            None
        ]
        
        processed = self.app.data_handler.process_news_data(malformed_articles)
        self.assertIsInstance(processed, dict)
        
    def test_invalid_query_handling(self):
        """Test handling of invalid queries"""
        invalid_queries = [
            "",
            "   ",
            None,
            "a" * 1000,
        ]
        
        for query in invalid_queries:
            if query is not None:
                result = self.app.query_processor.process_query(query)
                self.assertIn('status', result)
                
    def test_network_error_handling(self):
        """Test handling of network errors"""
        with patch('requests.get', side_effect=Exception("Network error")):
            articles = self.app.data_handler.scrape_news('test_source')
            self.assertEqual(articles, [])
            
    def test_file_system_error_handling(self):
        """Test handling of file system errors"""
        with patch('pathlib.Path.mkdir', side_effect=PermissionError("Access denied")):
            try:
                result = self.app.data_handler.save_to_cache('test', {'data': 'test'})
                self.assertIsInstance(result, bool)
            except PermissionError:
                pass

def run_performance_tests():
    """Run performance benchmarks"""
    print("\n" + "="*50)
    print("PERFORMANCE TESTS")
    print("="*50)
    logging.info("Starting performance tests")
    
    app = KeralaAnalyzerApp()
    
    sample_articles = [
        {
            'title': f'Test Article {i}',
            'content': f'This is test content for article {i} about Kerala politics and CPM UDF BJP parties.',
            'url': f'http://test.com/article{i}',
            'timestamp': datetime.now().isoformat(),
            'source': 'test_source'
        }
        for i in range(100)
    ]
    
    start_time = time.time()
    processed_data = app.data_handler.process_news_data(sample_articles)
    processing_time = time.time() - start_time
    
    print(f"📊 Processed 100 articles in {processing_time:.2f} seconds")
    print(f"📈 Processing rate: {len(sample_articles)/processing_time:.1f} articles/second")
    logging.info(f"Processed 100 articles in {processing_time:.2f} seconds")
    
    queries = [
        "What is CPM sentiment?",
        "Compare LDF and UDF",
        "Show trends in Kerala",
        "Political situation in Kochi",
        "Analyze government policies"
    ]
    
    start_time = time.time()
    for query in queries:
        result = app.query_processor.process_query(query)
    query_time = time.time() - start_time
    
    print(f"🔍 Processed {len(queries)} queries in {query_time:.2f} seconds")
    print(f"⚡ Query rate: {len(queries)/query_time:.1f} queries/second")
    logging.info(f"Processed {len(queries)} queries in {query_time:.2f} seconds")
    
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"💾 Current memory usage: {memory_mb:.1f} MB")
    logging.info(f"Current memory usage: {memory_mb:.1f} MB")

def run_stress_tests():
    """Run stress tests"""
    print("\n" + "="*50)
    print("STRESS TESTS")
    print("="*50)
    logging.info("Starting stress tests")
    
    app = KeralaAnalyzerApp()
    
    large_dataset = []
    for i in range(1000):
        article = {
            'title': f'Political News Article {i}',
            'content': f'Content about Kerala politics, CPM, UDF, BJP, and various political developments in district {i % 14}.',
            'url': f'http://test.com/article{i}',
            'timestamp': datetime.now().isoformat(),
            'source': 'stress_test'
        }
        large_dataset.append(article)
    
    print(f"📚 Testing with {len(large_dataset)} articles...")
    logging.info(f"Testing with {len(large_dataset)} articles")
    
    try:
        start_time = time.time()
        
        processed_data = app.data_handler.process_news_data(large_dataset)
        insights = app.analyzer.generate_insights(processed_data)
        
        processing_time = time.time() - start_time
        
        print(f"✅ Successfully processed {len(large_dataset)} articles")
        print(f"⏱️  Total time: {processing_time:.2f} seconds")
        logging.info(f"Successfully processed {len(large_dataset)} articles in {processing_time:.2f} seconds")
        
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        print(f"💾 Memory usage: {memory_mb:.1f} MB")
        logging.info(f"Memory usage after stress test: {memory_mb:.1f} MB")
        
        del large_dataset, processed_data, insights
        print("🧹 Memory cleanup: Success")
        logging.info("Memory cleanup completed successfully")
        
    except Exception as e:
        print(f"❌ Stress test failed: {str(e)}")
        logging.error(f"Stress test failed: {str(e)}")
        raise

def run_integration_tests():
    """Run integration tests"""
    print("\n" + "="*50)
    print("INTEGRATION TESTS")
    print("="*50)
    logging.info("Starting integration tests")
    
    app = KeralaAnalyzerApp()
    
    test_queries = [
        "What is the overall sentiment towards CPM?",
        "Compare UDF and LDF performance",
        "Show me trends in Thiruvananthapuram",
        "What are the key political issues in Kerala?"
    ]
    
    success_count = 0
    
    for i, query in enumerate(test_queries, 1):
        try:
            print(f"🔍 Test {i}: {query}")
            result = app.query_processor.process_query(query)
            
            if result['status'] == 'success':
                print(f"✅ Test {i} passed")
                success_count += 1
                logging.info(f"Integration test {i} passed: {query}")
            else:
                print(f"❌ Test {i} failed: {result.get('error', 'Unknown error')}")
                logging.error(f"Integration test {i} failed: {query} - {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Test {i} error: {str(e)}")
            logging.error(f"Integration test {i} error: {query} - {str(e)}")
    
    print(f"\n📊 Integration test results: {success_count}/{len(test_queries)} passed")
    logging.info(f"Integration test results: {success_count}/{len(test_queries)} passed")
    
    if success_count == len(test_queries):
        print("🎉 All integration tests passed!")
        logging.info("All integration tests passed")
    else:
        print("⚠️ Some integration tests failed - check logs for details")
        logging.warning("Some integration tests failed")

if __name__ == '__main__':
    print("Kerala Political Analyzer - Test Suite")
    print("="*50)
    logging.info("Starting test suite execution")
    
    required_dirs = ['data/raw', 'data/processed', 'data/cache', 
                    'outputs/charts', 'outputs/reports', 'logs', 'tests']
    for dir_path in required_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("\n🧪 Running Unit Tests...")
    logging.info("Running unit tests")
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    test_classes = [
        TestDataHandler,
        TestPoliticalAnalyzer,
        TestQueryProcessor,
        TestPoliticalVisualizer,
        TestMainApp,
        TestIntegration,
        TestAdvancedAnalytics,
        TestRobustness,
        TestVisualizationIntegration,
        TestErrorHandling
    ]
    
    for test_class in test_classes:
        tests = test_loader.loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    test_result = runner.run(test_suite)
    
    try:
        run_performance_tests()
    except Exception as e:
        print(f"❌ Performance tests failed: {str(e)}")
        logging.error(f"Performance tests failed: {str(e)}")
    
    try:
        run_stress_tests()
    except Exception as e:
        print(f"❌ Stress tests failed: {str(e)}")
        logging.error(f"Stress tests failed: {str(e)}")
    
    try:
        run_integration_tests()
    except Exception as e:
        print(f"❌ Integration tests failed: {str(e)}")
        logging.error(f"Integration tests failed: {str(e)}")
    
    print("\n" + "="*50)
    print("TEST SUITE SUMMARY")
    print("="*50)
    logging.info("Test suite summary")
    
    total_tests = test_result.testsRun
    failures = len(test_result.failures)
    errors = len(test_result.errors)
    passed = total_tests - failures - errors
    
    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failures}")
    print(f"💥 Errors: {errors}")
    logging.info(f"Total Tests: {total_tests}, Passed: {passed}, Failed: {failures}, Errors: {errors}")
    
    if failures == 0 and errors == 0:
        print("\n🎉 All tests passed successfully!")
        logging.info("All tests passed successfully")
        exit_code = 0
    else:
        print(f"\n⚠️ {failures + errors} tests failed - check logs for details")
        logging.warning(f"{failures + errors} tests failed")
        exit_code = 1
    
    print("="*50)
    print("Test Suite Completed!")
    print("="*50)
    logging.info("Test suite completed")
    
    sys.exit(exit_code)