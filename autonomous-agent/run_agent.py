#!/usr/bin/env python3
"""
Run the Autonomous Financial Analysis Agent
"""

import asyncio
import sys
import os
import logging

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import app, agent
from config import get_config

def main():
    """Main entry point for the autonomous agent"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('autonomous_agent.log')
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        print("🤖 Autonomous Financial Analysis Agent")
        print("=" * 50)
        print("🚀 Initializing advanced AI agent with:")
        print("   • Multi-step reasoning engine")
        print("   • Hallucination prevention system") 
        print("   • Confidence scoring engine")
        print("   • Prompt engine integration")
        print("   • Vector database acceleration")
        print("=" * 50)
        
        config = get_config()
        
        # Show configuration
        print(f"📊 Configuration:")
        print(f"   • Prompt Engine: {config['prompt_engine']['url']}")
        print(f"   • LLM Provider: {config['llm']['ollama']['host']}:{config['llm']['ollama']['port']}")
        print(f"   • Vector DB: {config['vector_db']['host']}:{config['vector_db']['port']}")
        print(f"   • Min Confidence: {config['agent']['min_confidence_threshold']}")
        print(f"   • Max Reasoning Steps: {config['agent']['max_reasoning_steps']}")
        
        # Initialize and run
        logger.info("Starting autonomous agent server...")
        
        app.run(
            host=config["flask"]["host"],
            port=config["flask"]["port"],
            debug=config["flask"]["debug"]
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down autonomous agent...")
        logger.info("Agent shutdown requested by user")
    except Exception as e:
        print(f"❌ Error starting agent: {e}")
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()