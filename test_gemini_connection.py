"""
Test script to verify Gemini 3 Pro connection and basic analysis.
Run this before building the full UI to ensure everything works.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_engine import GeminiClient, CodeAnalyzer


def test_connection():
    """Test basic connection to Gemini 3 Pro."""
    print("=" * 60)
    print("GREENCODE SENTINEL - GEMINI CONNECTION TEST")
    print("=" * 60)
    
    try:
        print("\n1. Initializing Gemini client...")
        client = GeminiClient()
        
        print(f"   Model: {client.model_id}")
        print(f"   Thinking Level: {client.thinking_level}")
        print(f"   Temperature: {client.temperature}")
        
        print("\n2. Testing connection...")
        if client.test_connection():
            print("   ✅ Connection successful!")
        else:
            print("   ❌ Connection failed!")
            return False
        
        return True
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease follow these steps:")
        print("1. Copy .env.template to .env")
        print("2. Get your API key from: https://aistudio.google.com/app/apikey")
        print("3. Add your API key to the .env file")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_simple_analysis():
    """Test analyzing a simple code snippet."""
    print("\n" + "=" * 60)
    print("TESTING CODE ANALYSIS")
    print("=" * 60)
    
    # Simple inefficient Python code
    test_code = """
def inefficient_sum(numbers):
    total = 0
    for i in range(len(numbers)):
        for j in range(len(numbers)):
            if i == j:
                total += numbers[i]
    return total
"""
    
    try:
        print("\n1. Initializing analyzer...")
        analyzer = CodeAnalyzer()
        
        print("\n2. Analyzing test code...")
        print("   Code snippet:")
        print("   " + "\n   ".join(test_code.strip().split("\n")))
        
        print("\n3. Sending to Gemini 3 Pro (with high thinking level)...")
        results = analyzer.analyze_code(test_code, language="python", file_name="test.py")
        
        print("\n4. Results:")
        print(f"   Sustainability Score: {results['score']}/100 (Grade: {results['grade']})")
        print(f"   Total Issues: {results['total_issues']}")
        print(f"   CO₂ Savings Potential: {results['co2_savings_kg_year']} kg/year")
        
        if results['total_issues'] > 0:
            print("\n5. Issues Found:")
            for i, issue in enumerate(results['issues'][:3], 1):  # Show first 3
                print(f"\n   Issue {i}:")
                print(f"   - Severity: {issue.get('severity', 'Unknown')}")
                print(f"   - Category: {issue.get('category', 'Unknown')}")
                print(f"   - Description: {issue.get('description', 'N/A')}")
        
        print("\n✅ Analysis completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n🚀 Starting GreenCode Sentinel Tests...\n")
    
    # Test 1: Connection
    if not test_connection():
        print("\n❌ Connection test failed. Please fix configuration before proceeding.")
        return
    
    # Test 2: Simple analysis
    if not test_simple_analysis():
        print("\n❌ Analysis test failed. Please check the error messages above.")
        return
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nYou're ready to:")
    print("1. Analyze sample files in data/samples/")
    print("2. Build the Flet UI")
    print("3. Deploy with Docker")
    print("\nNext step: Run 'python app/main.py' to start the UI")


if __name__ == "__main__":
    main()

# Made with Bob
