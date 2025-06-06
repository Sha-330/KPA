import matplotlib
# Set backend to Agg for non-interactive environments; change to TkAgg for interactive display if needed
matplotlib.use('Agg')  # Fallback for non-GUI environments
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, List, Any, Optional
import seaborn as sns
from datetime import datetime
import numpy as np
from pathlib import Path
import logging

# At the top of the file
from kpa_config import LOGS_DIR, LOG_LEVEL, LOG_FORMAT, OUTPUTS_DIR

# Update logging setup
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOGS_DIR / 'visualizer.log'),
        logging.StreamHandler()
    ]
)

# Update output_dir in __init__
# Assumes config.py is in the same directory

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PoliticalVisualizer:
    """Charts and basic visualization for political data"""
    
    def __init__(self, show_charts: bool = False):
        self.output_dir = OUTPUTS_DIR / "charts"
        self.output_dir.mkdir(exist_ok=True)
        self.show_charts = show_charts  # Flag to control interactive display
        
        # Set modern Seaborn style
        sns.set_theme(style="whitegrid", palette="husl")
    
    def create_sentiment_chart(self, party_analysis: Dict, title: str = "Party Sentiment Analysis") -> str:
        """Create sentiment analysis chart"""
        try:
            parties = list(party_analysis.keys())
            sentiments = [analysis.get('average_sentiment', 0) for analysis in party_analysis.values()]
            mentions = [analysis.get('total_mentions', 0) for analysis in party_analysis.values()]
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Sentiment bar chart
            colors = ['green' if s > 0 else 'red' if s < 0 else 'gray' for s in sentiments]
            bars1 = ax1.bar(parties, sentiments, color=colors, alpha=0.7)
            ax1.set_title('Average Sentiment by Party')
            ax1.set_ylabel('Sentiment Score')
            ax1.set_xlabel('Political Parties')
            ax1.tick_params(axis='x', rotation=45)
            ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            # Add value labels on bars
            for bar, sentiment in zip(bars1, sentiments):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + (0.01 if height >= 0 else -0.03),
                         f'{sentiment:.2f}', ha='center', va='bottom' if height >= 0 else 'top')
            
            # Mentions bar chart
            bars2 = ax2.bar(parties, mentions, color='skyblue', alpha=0.7)
            ax2.set_title('Media Mentions by Party')
            ax2.set_ylabel('Number of Mentions')
            ax2.set_xlabel('Political Parties')
            ax2.tick_params(axis='x', rotation=45)
            
            # Add value labels
            for bar, mention in zip(bars2, mentions):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                         f'{mention}', ha='center', va='bottom')
            
            plt.tight_layout()
            
            # Save chart
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sentiment_analysis_{timestamp}.png"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            
            # Show chart if enabled
            if self.show_charts:
                plt.show()
            
            plt.close()
            
            logger.info(f"Sentiment chart saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating sentiment chart: {str(e)}")
            return ""
    
    def create_regional_activity_chart(self, regional_analysis: Dict, title: str = "Regional Political Activity") -> str:
        """Create regional activity chart"""
        try:
            districts = list(regional_analysis.keys())
            activity_scores = [analysis.get('political_activity_score', 0) for analysis in regional_analysis.values()]
            news_counts = [analysis.get('total_news_items', 0) for analysis in regional_analysis.values()]
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # Activity scores
            bars1 = ax1.barh(districts, activity_scores, color='orange', alpha=0.7)
            ax1.set_title('Political Activity Score by District')
            ax1.set_xlabel('Activity Score')
            ax1.set_ylabel('Districts')
            
            # Add value labels
            for bar, score in zip(bars1, activity_scores):
                width = bar.get_width()
                ax1.text(width + 0.01, bar.get_y() + bar.get_height()/2.,
                         f'{score:.2f}', ha='left', va='center')
            
            # News counts
            bars2 = ax2.barh(districts, news_counts, color='lightcoral', alpha=0.7)
            ax2.set_title('News Volume by District')
            ax2.set_xlabel('Number of News Items')
            ax2.set_ylabel('Districts')
            
            # Add value labels
            for bar, count in zip(bars2, news_counts):
                width = bar.get_width()
                ax2.text(width + 0.5, bar.get_y() + bar.get_height()/2.,
                         f'{count}', ha='left', va='center')
            
            plt.tight_layout()
            
            # Save chart
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"regional_activity_{timestamp}.png"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            
            # Show chart if enabled
            if self.show_charts:
                plt.show()
            
            plt.close()
            
            logger.info(f"Regional activity chart saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating regional activity chart: {str(e)}")
            return ""
    
    def create_trending_topics_chart(self, trending_topics: List[Dict], title: str = "Trending Political Topics") -> str:
        """Create trending topics visualization"""
        try:
            if not trending_topics:
                return ""
            
            topics = [', '.join(topic['keywords'][:2]) for topic in trending_topics[:8]]
            article_counts = [topic['article_count'] for topic in trending_topics[:8]]
            sentiments = [topic['average_sentiment'] for topic in trending_topics[:8]]
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            
            # Article counts pie chart
            ax1.pie(article_counts, labels=topics, autopct='%1.1f%%', startangle=90)
            ax1.set_title('Distribution of Articles by Topic')
            
            # Sentiment by topic
            colors = ['green' if s > 0 else 'red' if s < 0 else 'gray' for s in sentiments]
            bars = ax2.barh(topics, sentiments, color=colors, alpha=0.7)
            ax2.set_title('Topic Sentiment Analysis')
            ax2.set_xlabel('Average Sentiment Score')
            ax2.axvline(x=0, color='black', linestyle='-', alpha=0.3)
            
            # Add value labels
            for bar, sentiment in zip(bars, sentiments):
                width = bar.get_width()
                ax2.text(width + (0.01 if width >= 0 else -0.01), bar.get_y() + bar.get_height()/2.,
                         f'{sentiment:.2f}', ha='left' if width >= 0 else 'right', va='center')
            
            plt.tight_layout()
            
            # Save chart
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"trending_topics_{timestamp}.png"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            
            # Show chart if enabled
            if self.show_charts:
                plt.show()
            
            plt.close()
            
            logger.info(f"Trending topics chart saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating trending topics chart: {str(e)}")
            return ""
    
    def create_temporal_trends_chart(self, temporal_data: Dict, title: str = "Political Trends Over Time") -> str:
        """Create temporal trends chart"""
        try:
            dates = temporal_data.get('dates', [])
            sentiment = temporal_data.get('sentiment_trend', [])
            volume = temporal_data.get('volume_trend', [])
            
            if not dates or not sentiment:
                return ""
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # Convert dates to datetime for better plotting
            date_objects = [datetime.strptime(date, '%Y-%m-%d') for date in dates]
            
            # Sentiment trend
            ax1.plot(date_objects, sentiment, marker='o', linewidth=2, markersize=6, color='blue')
            ax1.set_title('Sentiment Trend Over Time')
            ax1.set_ylabel('Average Sentiment Score')
            ax1.axhline(y=0, color='black', linestyle='--', alpha=0.5)
            ax1.grid(True, alpha=0.3)
            ax1.tick_params(axis='x', rotation=45)
            
            # Volume trend
            if volume:
                ax2.bar(date_objects, volume, alpha=0.7, color='green')
                ax2.set_title('News Volume Over Time')
                ax2.set_ylabel('Number of Articles')
                ax2.set_xlabel('Date')
                ax2.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            # Save chart
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"temporal_trends_{timestamp}.png"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            
            # Show chart if enabled
            if self.show_charts:
                plt.show()
            
            plt.close()
            
            logger.info(f"Temporal trends chart saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating temporal trends chart: {str(e)}")
            return ""
    
    def create_party_dominance_chart(self, dominance_scores: Dict, title: str = "Party Dominance Analysis") -> str:
        """Create party dominance chart"""
        try:
            parties = list(dominance_scores.keys())
            scores = list(dominance_scores.values())
            
            # Sort by scores
            sorted_data = sorted(zip(parties, scores), key=lambda x: x[1], reverse=True)
            parties, scores = zip(*sorted_data)
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Create horizontal bar chart
            bars = ax.barh(parties, scores, color='purple', alpha=0.7)
            ax.set_title('Political Party Dominance Scores')
            ax.set_xlabel('Dominance Score')
            ax.set_ylabel('Political Parties')
            
            # Add value labels
            for bar, score in zip(bars, scores):
                width = bar.get_width()
                ax.text(width + 0.005, bar.get_y() + bar.get_height()/2.,
                        f'{score:.3f}', ha='left', va='center')
            
            plt.tight_layout()
            
            # Save chart
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"party_dominance_{timestamp}.png"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            
            # Show chart if enabled
            if self.show_charts:
                plt.show()
            
            plt.close()
            
            logger.info(f"Party dominance chart saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating party dominance chart: {str(e)}")
            return ""
    
    def create_comprehensive_dashboard(self, insights: Dict) -> str:
        """Create a comprehensive dashboard with multiple visualizations"""
        try:
            fig = plt.figure(figsize=(20, 15))
            
            # Create subplots
            gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
            
            # 1. Party sentiment (top-left)
            ax1 = fig.add_subplot(gs[0, 0])
            party_analysis = insights.get('party_analysis', {})
            if party_analysis:
                parties = list(party_analysis.keys())[:6]  # Top 6 parties
                sentiments = [party_analysis[p].get('average_sentiment', 0) for p in parties]
                colors = ['green' if s > 0 else 'red' if s < 0 else 'gray' for s in sentiments]
                ax1.bar(parties, sentiments, color=colors, alpha=0.7)
                ax1.set_title('Party Sentiment')
                ax1.tick_params(axis='x', rotation=45)
                ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            # 2. Regional activity (top-center)
            ax2 = fig.add_subplot(gs[0, 1])
            regional_analysis = insights.get('regional_analysis', {})
            if regional_analysis:
                districts = list(regional_analysis.keys())[:6]  # Top 6 districts
                activities = [regional_analysis[d].get('political_activity_score', 0) for d in districts]
                ax2.barh(districts, activities, color='orange', alpha=0.7)
                ax2.set_title('Regional Activity')
            
            # 3. Party dominance (top-right)
            ax3 = fig.add_subplot(gs[0, 2])
            dominance = insights.get('party_dominance', {})
            if dominance:
                parties = list(dominance.keys())[:6]
                scores = [dominance[p] for p in parties]
                ax3.pie(scores, labels=parties, autopct='%1.1f%%')
                ax3.set_title('Party Dominance')
            
            # 4. Trending topics (middle-left)
            ax4 = fig.add_subplot(gs[1, 0])
            trending = insights.get('trending_topics', [])
            if trending:
                topics = [', '.join(t['keywords'][:2]) for t in trending[:5]]
                counts = [t['article_count'] for t in trending[:5]]
                ax4.barh(topics, counts, color='lightblue', alpha=0.7)
                ax4.set_title('Trending Topics')
            
            # 5. Temporal sentiment (middle-center and right - spanning 2 columns)
            ax5 = fig.add_subplot(gs[1, 1:])
            temporal = insights.get('temporal_trends', {})
            if temporal and temporal.get('dates'):
                dates = temporal['dates']
                sentiment = temporal.get('sentiment_trend', [])
                volume = temporal.get('volume_trend', [])
                
                # Plot sentiment
                ax5_twin = ax5.twinx()
                
                date_objects = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
                line1 = ax5.plot(date_objects, sentiment, 'b-', marker='o', label='Sentiment')
                ax5.set_ylabel('Sentiment Score', color='b')
                ax5.tick_params(axis='y', labelcolor='b')
                
                if volume:
                    line2 = ax5_twin.bar(date_objects, volume, alpha=0.3, color='g', label='Volume')
                    ax5_twin.set_ylabel('Article Volume', color='g')
                    ax5_twin.tick_params(axis='y', labelcolor='g')
                
                ax5.set_title('Temporal Trends')
                ax5.tick_params(axis='x', rotation=45)
            
            # 6. Summary statistics (bottom row)
            ax6 = fig.add_subplot(gs[2, :])
            ax6.axis('off')  # Turn off axis
            
            summary = insights.get('summary', {})
            summary_text = f"""
            KERALA POLITICAL ANALYSIS SUMMARY
            
            • Total Articles Analyzed: {summary.get('total_articles', 0)}
            • Analysis Period: {summary.get('date_range', 'N/A')}
            • Overall Sentiment: {summary.get('overall_sentiment', 0):.3f}
            • Political Relevance: {summary.get('avg_political_relevance', 0):.3f}
            
            Top Active Parties: {', '.join(list(dominance.keys())[:3]) if dominance else 'N/A'}
            Most Active Region: {max(regional_analysis.keys(), key=lambda x: regional_analysis[x]['political_activity_score']) if regional_analysis else 'N/A'}
            """
            
            ax6.text(0.1, 0.5, summary_text, fontsize=12, verticalalignment='center',
                     bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.5))
            
            plt.suptitle('Kerala Political Landscape Dashboard', fontsize=16, fontweight='bold')
            
            # Save dashboard
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"political_dashboard_{timestamp}.png"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            
            # Show dashboard if enabled
            if self.show_charts:
                plt.show()
            
            plt.close()
            
            logger.info(f"Comprehensive dashboard saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating comprehensive dashboard: {str(e)}")
            return ""

if __name__ == "__main__":
    # Example usage for testing
    visualizer = PoliticalVisualizer(show_charts=True)  # Enable interactive display
    
    # Sample data for testing
    party_analysis = {
        "BJP": {"average_sentiment": 0.123, "total_mentions": 45, "recent_mentions": 10, "sentiment_category": "Positive"},
        "Congress": {"average_sentiment": -0.050, "total_mentions": 60, "recent_mentions": 15, "sentiment_category": "Negative"},
        "CPI(M)": {"average_sentiment": 0.080, "total_mentions": 50, "recent_mentions": 12, "sentiment_category": "Positive"}
    }
    
    regional_analysis = {
        "Thiruvananthapuram": {"political_activity_score": 0.75, "total_news_items": 30, "top_parties": {"BJP": 10, "Congress": 15}},
        "Kollam": {"political_activity_score": 0.60, "total_news_items": 20, "top_parties": {"Congress": 10, "CPI(M)": 8}},
        "Ernakulam": {"political_activity_score": 0.85, "total_news_items": 40, "top_parties": {"CPI(M)": 20, "BJP": 10}}
    }
    
    trending_topics = [
        {"keywords": ["budget", "policy"], "article_count": 25, "average_sentiment": 0.1, "sample_titles": ["Budget 2025 Announced"]},
        {"keywords": ["election", "campaign"], "article_count": 15, "average_sentiment": -0.05, "sample_titles": ["Election Rally in Kollam"]},
        {"keywords": ["protest", "strike"], "article_count": 10, "average_sentiment": -0.2, "sample_titles": ["Strike in Ernakulam"]}
    ]
    
    temporal_data = {
        "dates": ["2025-06-01", "2025-06-02", "2025-06-03"],
        "sentiment_trend": [0.1, 0.15, 0.12],
        "volume_trend": [20, 25, 30]
    }
    
    dominance_scores = {
        "BJP": 0.35,
        "Congress": 0.40,
        "CPI(M)": 0.25
    }
    
    insights = {
        "party_analysis": party_analysis,
        "regional_analysis": regional_analysis,
        "trending_topics": trending_topics,
        "party_dominance": dominance_scores,
        "temporal_trends": temporal_data,
        "summary": {
            "total_articles": 100,
            "date_range": "2025-06-01 to 2025-06-03",
            "overall_sentiment": 0.067,
            "avg_political_relevance": 0.85
        }
    }
    
    # Test chart methods
    logger.info("Creating sentiment chart...")
    print(visualizer.create_sentiment_chart(party_analysis))
    
    logger.info("Creating regional activity chart...")
    print(visualizer.create_regional_activity_chart(regional_analysis))
    
    logger.info("Creating trending topics chart...")
    print(visualizer.create_trending_topics_chart(trending_topics))
    
    logger.info("Creating temporal trends chart...")
    print(visualizer.create_temporal_trends_chart(temporal_data))
    
    logger.info("Creating party dominance chart...")
    print(visualizer.create_party_dominance_chart(dominance_scores))
    
    logger.info("Creating comprehensive dashboard...")
    print(visualizer.create_comprehensive_dashboard(insights))
