#!/usr/bin/env python3
"""
Setup script for Enhanced Patent Search Agent
Run this to verify your installation and set up API keys
"""

import os
import sys
from pathlib import Path
import requests

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7+ required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'requests', 'pathlib', 'dataclasses', 'typing'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package}")
    
    if missing:
        print(f"\nInstall missing packages with:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    return True

def setup_directories():
    """Create necessary directories"""
    directories = [
        'patent_data',
        'patent_data/downloaded_pdfs',
        'logs',
        'cache'
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directory: {dir_path}")

def setup_env_file():
    """Create .env file template"""
    env_file = Path('.env')
    
    if not env_file.exists():
        env_content = """# Enhanced Patent Search Agent Configuration
# Get your SearchAPI key from: https://www.searchapi.io/
SEARCHAPI_KEY=your_searchapi_key_here

# Optional: USPTO API key
USPTO_API_KEY=your_uspto_key_here

# Download settings
MAX_DOWNLOAD_SIZE_MB=100
DOWNLOAD_TIMEOUT_SECONDS=60
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print("✅ Created .env file template")
        print("   📝 Edit .env file to add your API keys")
    else:
        print("✅ .env file exists")

def test_internet_connection():
    """Test internet connectivity"""
    try:
        response = requests.get('https://patents.google.com', timeout=10)
        if response.status_code == 200:
            print("✅ Internet connection to patents.google.com")
            return True
    except:
        pass
    
    print("❌ Cannot connect to patents.google.com")
    return False

def test_searchapi_key():
    """Test SearchAPI key if provided"""
    api_key = os.getenv('SEARCHAPI_KEY')
    
    if not api_key or api_key == 'your_searchapi_key_here':
        print("⚠️  SearchAPI key not configured")
        print("   You can still use web scraping fallback")
        return False
    
    try:
        response = requests.get(
            'https://api.searchapi.io/api/v1/search',
            params={
                'engine': 'google_patents',
                'q': 'test',
                'num': 1,
                'api_key': api_key
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ SearchAPI key is valid")
            return True
        else:
            print(f"❌ SearchAPI key error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ SearchAPI test failed: {e}")
        return False

def run_quick_test():
    """Run a quick test of the enhanced agent"""
    try:
        print("\n🧪 Running quick test...")
        
        # Import the agent
        from enhanced_patent_agent import EnhancedPatentAgent
        
        # Create agent
        agent = EnhancedPatentAgent()
        print("✅ Agent created successfully")
        
        # Test capabilities
        capabilities = agent.get_capabilities()
        print(f"✅ Agent capabilities: {len(capabilities)} features")
        
        # Test download directory
        status = agent.get_download_status()
        print(f"✅ Download directory: {status['download_directory']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🔧 Enhanced Patent Search Agent Setup")
    print("=" * 50)
    
    # Check system requirements
    print("\n📋 Checking system requirements:")
    if not check_python_version():
        return
    
    if not check_dependencies():
        print("\n💡 Install dependencies with: pip install -r requirements.txt")
        return
    
    # Test connectivity
    print("\n🌐 Testing connectivity:")
    test_internet_connection()
    
    # Setup directories and files
    print("\n📁 Setting up directories:")
    setup_directories()
    
    print("\n⚙️ Setting up configuration:")
    setup_env_file()
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("💡 Install python-dotenv for .env file support: pip install python-dotenv")
    
    # Test API keys
    print("\n🔑 Testing API access:")
    test_searchapi_key()
    
    # Run quick test
    if run_quick_test():
        print("\n🎉 Setup complete!")
        print("\nNext steps:")
        print("1. Edit .env file to add your SearchAPI key (optional)")
        print("2. Run: python patent_cli.py --help")
        print("3. Try: python patent_cli.py search-keywords 'FOXP2' --max-results 5")
        print("4. Or run: python patent_cli.py interactive")
    else:
        print("\n❌ Setup incomplete - check errors above")

if __name__ == "__main__":
    main()