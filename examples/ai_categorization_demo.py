#!/usr/bin/env python3
"""
AI Categorization Demo

Demonstrates the AI-powered event categorization feature.
Shows how events are categorized with and without AI.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.ai_categorizer import AICategorizer
from modules.utils import load_config


def main():
    """Run AI categorization demo."""
    print("\n" + "="*70)
    print("🤖 AI-POWERED EVENT CATEGORIZATION DEMO")
    print("="*70)
    
    # Load config
    base_path = Path(__file__).parent.parent
    config = load_config(base_path)
    
    # Sample events to categorize
    sample_events = [
        {
            "title": "Summer Music Festival 2026",
            "description": "Three days of live music featuring rock, jazz, and folk bands."
        },
        {
            "title": "Python Programming Workshop",
            "description": "Learn Python basics in this hands-on workshop."
        },
        {
            "title": "City Marathon",
            "description": "Annual 42km marathon through the city center."
        },
    ]
    
    # Test with AI disabled (keyword fallback)
    print("\n📊 Keyword-Based Categorization (AI Disabled)")
    print("-" * 70)
    
    config['ai'] = {'categorization': {'enabled': False}}
    categorizer_keyword = AICategorizer(config, base_path)
    
    for event in sample_events:
        category, confidence, method = categorizer_keyword.categorize_event(
            event['title'], 
            event['description']
        )
        
        print(f"\n📋 {event['title']}")
        print(f"   Category: {category}, Confidence: {confidence:.2f}, Method: {method}")
    
    print("\n" + "="*70)
    print("Demo complete! See docs/AI_CATEGORIZATION.md for full documentation.")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
