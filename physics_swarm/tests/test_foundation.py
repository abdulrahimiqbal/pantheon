"""
Test script to verify the foundation setup for the Physics AI Agent Swarm.

This script tests the basic functionality of shared modules and base agent framework.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from datetime import datetime

def test_shared_imports():
    """Test that all shared modules can be imported correctly."""
    print("Testing shared module imports...")
    
    try:
        from shared import (
            ConfidenceLevel, SourceType, ComplexityLevel, AgentRole,
            DataSource, PhysicsQuery, AgentResponse, SwarmResponse,
            settings, swarm_config, setup_logger, validate_source
        )
        print("✅ All shared imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_types_functionality():
    """Test basic functionality of type definitions."""
    print("\nTesting type definitions...")
    
    try:
        from shared import DataSource, SourceType, PhysicsQuery, ComplexityLevel
        
        # Test DataSource creation
        source = DataSource(
            url="https://arxiv.org/abs/2024.12345",
            title="Test Physics Paper",
            source_type=SourceType.PREPRINT,
            credibility_score=0.8
        )
        
        # Test PhysicsQuery creation
        query = PhysicsQuery(
            question="What is quantum entanglement?",
            context="Student learning quantum mechanics",
            complexity_level=ComplexityLevel.INTERMEDIATE
        )
        
        print(f"✅ DataSource created: {source.title}")
        print(f"✅ PhysicsQuery created: {query.question}")
        return True
        
    except Exception as e:
        print(f"❌ Type functionality error: {e}")
        return False

def test_config_loading():
    """Test configuration loading."""
    print("\nTesting configuration loading...")
    
    try:
        from shared import settings, swarm_config
        
        print(f"✅ Settings loaded - App Name: {settings.app_name}")
        print(f"✅ Swarm config loaded - Max Agents: {swarm_config.max_parallel_agents}")
        print(f"✅ Agent configs available: {len(swarm_config.agent_configs)}")
        return True
        
    except Exception as e:
        print(f"❌ Config loading error: {e}")
        return False

def test_utilities():
    """Test utility functions."""
    print("\nTesting utility functions...")
    
    try:
        from shared import setup_logger, URLValidator, SourceValidator, DataSource, SourceType
        
        # Test logger
        logger = setup_logger("test_logger")
        logger.info("Test log message")
        
        # Test URL validator
        is_valid = URLValidator.is_valid_url("https://arxiv.org/abs/2024.12345")
        is_trusted = URLValidator.is_trusted_domain("https://arxiv.org/abs/2024.12345")
        
        # Test source validator
        test_source = DataSource(
            url="https://arxiv.org/abs/2024.12345",
            title="Test Paper",
            source_type=SourceType.PREPRINT,
            credibility_score=0.8
        )
        
        validation_result = SourceValidator.validate_source(test_source)
        
        print(f"✅ Logger created successfully")
        print(f"✅ URL validation: {is_valid}, trusted: {is_trusted}")
        print(f"✅ Source validation: {validation_result.is_valid}, credibility: {validation_result.credibility_score:.2f}")
        return True
        
    except Exception as e:
        print(f"❌ Utilities error: {e}")
        return False

def test_base_agent_import():
    """Test base agent import (without full initialization)."""
    print("\nTesting base agent import...")
    
    try:
        from agents import BasePhysicsAgent, communication_protocol
        
        print("✅ BasePhysicsAgent imported successfully")
        print("✅ Communication protocol imported successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Base agent import error: {e}")
        return False

def test_agent_config_creation():
    """Test agent configuration creation."""
    print("\nTesting agent configuration creation...")
    
    try:
        from shared import AgentSettings, settings, AgentRole
        
        # Test creating different agent configs
        web_crawler_config = AgentSettings.create_web_crawler_config(settings)
        physicist_config = AgentSettings.create_physicist_master_config(settings)
        tesla_config = AgentSettings.create_tesla_principles_config(settings)
        questioner_config = AgentSettings.create_curious_questioner_config(settings)
        
        print(f"✅ Web Crawler config: {web_crawler_config.agent_role.value}")
        print(f"✅ Physicist config: {physicist_config.agent_role.value}")
        print(f"✅ Tesla config: {tesla_config.agent_role.value}")
        print(f"✅ Questioner config: {questioner_config.agent_role.value}")
        return True
        
    except Exception as e:
        print(f"❌ Agent config creation error: {e}")
        return False

def main():
    """Run all foundation tests."""
    print("🧪 Physics AI Agent Swarm - Foundation Test Suite")
    print("=" * 60)
    
    tests = [
        test_shared_imports,
        test_types_functionality,
        test_config_loading,
        test_utilities,
        test_base_agent_import,
        test_agent_config_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All foundation tests passed! Ready for Phase 2.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 