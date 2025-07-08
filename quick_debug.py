#!/usr/bin/env python3
"""
Quick Debug Commands - Memorize these for instant troubleshooting
Run: python3 quick_debug.py [command]
"""

import sys
import os
import subprocess

def cmd_env():
    """Show environment info"""
    print("=== ENVIRONMENT ===")
    print(f"Python: {sys.version.split()[0]} ({sys.executable})")
    print(f"Platform: {sys.platform}")
    print(f"Directory: {os.getcwd()}")
    
def cmd_packages():
    """Check key packages"""
    print("=== PACKAGES ===")
    key_packages = ['google-cloud-bigquery', 'pandas', 'numpy']
    
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True)
        installed = result.stdout.lower()
        
        for pkg in key_packages:
            status = "✅" if pkg.lower() in installed else "❌"
            print(f"{status} {pkg}")
    except Exception as e:
        print(f"Error: {e}")

def cmd_auth():
    """Check authentication"""
    print("=== AUTHENTICATION ===")
    
    try:
        result = subprocess.run(['gcloud', 'auth', 'list'], 
                              capture_output=True, text=True)
        
        if 'ACTIVE' in result.stdout:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'ACTIVE' in line:
                    print(f"✅ {line.split()[0]}")
                    break
        else:
            print("❌ No active account")
            print("Fix: gcloud auth login")
    except:
        print("❌ gcloud not found")
        print("Fix: Install Google Cloud CLI")

def cmd_bigquery(project_id=None):
    """Test BigQuery"""
    print("=== BIGQUERY ===")
    
    if not project_id:
        project_id = input("Project ID: ").strip()
    
    try:
        from google.cloud import bigquery
        client = bigquery.Client(project=project_id)
        result = client.query("SELECT 1").result()
        print("✅ BigQuery working")
    except Exception as e:
        print(f"❌ Error: {e}")
        
        # Quick diagnosis
        if "default credentials" in str(e).lower():
            print("Fix: gcloud auth application-default login")
        elif "not found" in str(e).lower() and "location" in str(e).lower():
            print("Fix: Check BigQuery location (use europe-west1)")
        elif "403" in str(e):
            print("Fix: Check BigQuery permissions")

def cmd_network():
    """Test connectivity"""
    print("=== NETWORK ===")
    
    try:
        import requests
        
        # Test internet
        resp = requests.get('https://www.google.com', timeout=5)
        print(f"✅ Internet: {resp.status_code}")
        
        # Test Google Cloud
        resp = requests.get('https://cloud.google.com', timeout=5)
        print(f"✅ Google Cloud: {resp.status_code}")
        
    except Exception as e:
        print(f"❌ Network issue: {e}")

def cmd_fix_unicode():
    """Fix Windows Unicode issues"""
    print("=== UNICODE FIX ===")
    
    if sys.platform.startswith('win'):
        print("Applying Windows Unicode fix...")
        
        try:
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
            print("✅ Unicode fix applied")
        except Exception as e:
            print(f"❌ Fix failed: {e}")
    else:
        print("Not needed on this platform")

def cmd_all():
    """Run all checks"""
    print("=== COMPLETE CHECK ===")
    cmd_env()
    print()
    cmd_packages()
    print()
    cmd_auth()
    print()
    cmd_network()

def cmd_help():
    """Show available commands"""
    print("=== QUICK DEBUG COMMANDS ===")
    commands = {
        'env': 'Show environment info',
        'packages': 'Check key packages',
        'auth': 'Check authentication',
        'bigquery': 'Test BigQuery (will prompt for project)',
        'network': 'Test connectivity',
        'unicode': 'Fix Windows Unicode issues',
        'all': 'Run all checks',
        'help': 'Show this help'
    }
    
    for cmd, desc in commands.items():
        print(f"  {cmd:10} - {desc}")
    
    print("\nUsage:")
    print("  python3 quick_debug.py [command]")
    print("  python3 quick_debug.py env")
    print("  python3 quick_debug.py bigquery")

# Command mapping
COMMANDS = {
    'env': cmd_env,
    'packages': cmd_packages,
    'auth': cmd_auth,
    'bigquery': cmd_bigquery,
    'network': cmd_network,
    'unicode': cmd_fix_unicode,
    'all': cmd_all,
    'help': cmd_help
}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        cmd_help()
    else:
        command = sys.argv[1].lower()
        
        if command in COMMANDS:
            try:
                COMMANDS[command]()
            except KeyboardInterrupt:
                print("\nCancelled")
            except Exception as e:
                print(f"Error running {command}: {e}")
        else:
            print(f"Unknown command: {command}")
            print("Available commands:")
            for cmd in COMMANDS.keys():
                print(f"  {cmd}")