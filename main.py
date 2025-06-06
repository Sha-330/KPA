import logging
import sys
from datetime import datetime
from pathlib import Path
import argparse
import json
from src.data_handler import DataHandler
from src.analyzer import PoliticalAnalyzer
from src.query_processor import QueryProcessor
from src.visualizer import PoliticalVisualizer
# At the top of main.py
from kpa_config import POLITICAL_PARTIES, KERALA_DISTRICTS, LOGS_DIR, LOG_LEVEL, LOG_FORMAT

# Update logging setup
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOGS_DIR / 'kpa_app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Import our modules


class KeralaAnalyzerApp:
    """Main application class"""
    
    def __init__(self):
        self.data_handler = DataHandler()
        self.analyzer = PoliticalAnalyzer()
        self.query_processor = QueryProcessor()
        self.visualizer = PoliticalVisualizer()
        
        logger.info("Kerala Political Analyzer initialized")
    
    def run_analysis(self, mode: str = "interactive"):
        """Run the political analysis"""
        try:
            if mode == "interactive":
                self._interactive_mode()
            elif mode == "batch":
                self._batch_analysis()
            elif mode == "query":
                self._query_mode()
            else:
                logger.error(f"Unknown mode: {mode}")
                
        except KeyboardInterrupt:
            logger.info("Analysis interrupted by user")
        except Exception as e:
            logger.error(f"Error in analysis: {str(e)}")
    
    def _interactive_mode(self):
        """Interactive mode for user queries"""
        print("\n" + "="*60)
        print("       KERALA POLITICAL ANALYZER")
        print("="*60)
        print("Ask me about Kerala politics! (Type 'quit' to exit)")
        print("Examples:")
        print("  - 'What is the sentiment towards CPM?'")
        print("  - 'Show me trending political topics'")
        print("  - 'How is the political situation in Thiruvananthapuram?'")
        print("  - 'Compare LDF and UDF'")
        print("-"*60)
        
        while True:
            try:
                query = input("\n🗳️  Your question: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("Thank you for using Kerala Political Analyzer!")
                    break
                
                if not query:
                    continue
                
                print("\n🔍 Analyzing... Please wait...")
                
                # Process the query
                result = self.query_processor.process_query(query)
                
                # Display results
                self._display_results(result)
                
                # Ask if user wants visualization
                if result['status'] == 'success':
                    viz_choice = input("\n📊 Generate charts? (y/n): ").strip().lower()
                    if viz_choice in ['y', 'yes']:
                        self._generate_visualizations(result)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error processing query: {str(e)}")
                print(f"❌ Error: {str(e)}")
    
    def _batch_analysis(self):
        """Batch analysis mode"""
        print("\n🔄 Running batch analysis...")
        
        # Collect data from all sources
        all_articles = []
        sources = ['manorama', 'mathrubhumi']
        
        for source in sources:
            print(f"📰 Scraping {source}...")
            articles = self.data_handler.scrape_news(source, max_articles=50)
            all_articles.extend(articles)
            print(f"   Collected {len(articles)} articles")
        
        if not all_articles:
            print("❌ No articles collected. Check your internet connection.")
            return
        
        print(f"\n📊 Processing {len(all_articles)} articles...")
        
        # Process data
        processed_data = self.data_handler.process_news_data(all_articles)
        
        # Generate insights
        insights = self.analyzer.generate_insights(processed_data)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path("outputs/reports") / f"batch_analysis_{timestamp}.json"
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(insights, f, indent=2, default=str)
        
        print(f"✅ Analysis complete! Results saved to: {output_file}")
        
        # Generate comprehensive dashboard
        print("📈 Generating comprehensive dashboard...")
        dashboard_path = self.visualizer.create_comprehensive_dashboard(insights)
        if dashboard_path:
            print(f"📊 Dashboard saved: {dashboard_path}")
        
        # Print summary
        self._print_summary(insights)
    
    def _query_mode(self):
        """Single query mode"""
        if len(sys.argv) < 3:
            print("Usage: python main.py query \"Your question here\"")
            return
        
        query = sys.argv[2]
        print(f"\n🔍 Processing query: {query}")
        
        result = self.query_processor.process_query(query)
        self._display_results(result)
        
        # Auto-generate visualization
        if result['status'] == 'success':
            self._generate_visualizations(result)
    
    def _display_results(self, result: dict):
        """Display query results"""
        print("\n" + "="*60)
        print("ANALYSIS RESULTS")
        print("="*60)
        
        if result['status'] == 'success':
            print(f"🎯 Intent: {result['intent']}")
            if result['entities']['parties']:
                print(f"🏛️  Parties: {', '.join(result['entities']['parties'])}")
            if result['entities']['districts']:
                print(f"📍 Districts: {', '.join(result['entities']['districts'])}")
            
            print(f"\n📝 Response:\n{result['response']['message']}")
            
            if 'suggestions' in result['response']:
                print(f"\n💡 Suggestions:")
                for suggestion in result['response']['suggestions']:
                    print(f"   • {suggestion}")
        else:
            print(f"❌ Error: {result['response']['message']}")
    
    def _generate_visualizations(self, result: dict):
        """Generate visualizations based on query result"""
        try:
            print("\n📊 Generating visualizations...")
            
            viz_type = result.get('visualization_type', 'summary')
            data = result.get('data', {})
            
            # Create visualization based on type
            if viz_type == 'sentiment':
                chart_path = self.visualizer.create_sentiment_chart(data)
            elif viz_type == 'comparison':
                chart_path = self.visualizer.create_comparison_chart(data)
            elif viz_type == 'trend':
                chart_path = self.visualizer.create_trend_chart(data)
            elif viz_type == 'regional':
                chart_path = self.visualizer.create_regional_chart(data)
            else:
                chart_path = self.visualizer.create_summary_chart(data)
            
            if chart_path:
                print(f"📈 Chart saved: {chart_path}")
                
                # Ask if user wants to open the chart
                open_choice = input("🖼️  Open chart? (y/n): ").strip().lower()
                if open_choice in ['y', 'yes']:
                    import webbrowser
                    webbrowser.open(f'file://{Path(chart_path).absolute()}')
            else:
                print("❌ Could not generate visualization")
                
        except Exception as e:
            logger.error(f"Error generating visualizations: {str(e)}")
            print(f"❌ Visualization error: {str(e)}")
    
    def _print_summary(self, insights: dict):
        """Print analysis summary"""
        print("\n" + "="*60)
        print("ANALYSIS SUMMARY")
        print("="*60)
        
        # Overall metrics
        if 'metrics' in insights:
            metrics = insights['metrics']
            print(f"📊 Total Articles Analyzed: {metrics.get('total_articles', 0)}")
            print(f"📅 Date Range: {metrics.get('date_range', 'N/A')}")
            print(f"🎯 Political Mentions: {metrics.get('political_mentions', 0)}")
        
        # Top topics
        if 'top_topics' in insights:
            print(f"\n🔥 Top Topics:")
            for i, topic in enumerate(insights['top_topics'][:5], 1):
                print(f"   {i}. {topic['topic']} ({topic['frequency']} mentions)")
        
        # Sentiment overview
        if 'sentiment_overview' in insights:
            sentiment = insights['sentiment_overview']
            print(f"\n😊 Overall Sentiment:")
            print(f"   Positive: {sentiment.get('positive', 0):.1f}%")
            print(f"   Neutral:  {sentiment.get('neutral', 0):.1f}%")
            print(f"   Negative: {sentiment.get('negative', 0):.1f}%")
        
        # Key parties mentioned
        if 'party_mentions' in insights:
            print(f"\n🏛️  Party Mentions:")
            for party, count in list(insights['party_mentions'].items())[:5]:
                print(f"   {party}: {count} mentions")
        
        # Regional insights
        if 'regional_insights' in insights:
            print(f"\n📍 Top Districts:")
            for district, count in list(insights['regional_insights'].items())[:5]:
                print(f"   {district}: {count} mentions")
        
        print("\n" + "="*60)
    
    def health_check(self):
        """Check system health and dependencies"""
        print("\n🔍 System Health Check")
        print("="*40)
        
        checks = [
            ("Data directories", self._check_directories),
            ("Network connectivity", self._check_network),
            ("Dependencies", self._check_dependencies),
            ("Cache system", self._check_cache),
            ("Log system", self._check_logging)
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            try:
                result = check_func()
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{check_name}: {status}")
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"{check_name}: ❌ ERROR - {str(e)}")
                all_passed = False
        
        print(f"\nOverall Status: {'✅ HEALTHY' if all_passed else '⚠️  ISSUES DETECTED'}")
        return all_passed
    
    def _check_directories(self):
        """Check if required directories exist"""
        required_dirs = ['data/raw', 'data/processed', 'data/cache', 
                        'outputs/charts', 'outputs/reports', 'logs']
        
        for dir_path in required_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        return all(Path(dir_path).exists() for dir_path in required_dirs)
    
    def _check_network(self):
        """Check network connectivity"""
        import requests
        try:
            response = requests.get('https://httpbin.org/status/200', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _check_dependencies(self):
        """Check if all required packages are available"""
        required_packages = ['pandas', 'numpy', 'matplotlib', 'requests', 'beautifulsoup4']
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                return False
        return True
    
    def _check_cache(self):
        """Check cache system"""
        cache_dir = Path('data/cache')
        return cache_dir.exists() and cache_dir.is_dir()
    
    def _check_logging(self):
        """Check logging system"""
        try:
            logger.info("Health check logging test")
            return True
        except:
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Kerala Political Analyzer')
    parser.add_argument('mode', nargs='?', default='interactive',
                       choices=['interactive', 'batch', 'query', 'health'],
                       help='Run mode (default: interactive)')
    parser.add_argument('query', nargs='?', help='Query for single query mode')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Set debug level if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Initialize app
    app = KeralaAnalyzerApp()
    
    # Run health check if requested
    if args.mode == 'health':
        app.health_check()
        return
    
    # Run the analysis
    logger.info(f"Starting Kerala Political Analyzer in {args.mode} mode")
    app.run_analysis(args.mode)
    logger.info("Kerala Political Analyzer session ended")


if __name__ == "__main__":
    main()