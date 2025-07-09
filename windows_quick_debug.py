"""
Quick Debug for Windows - Find the exact problem
Run: python windows_quick_debug.py
"""

import sys
import os
import subprocess

def check_everything():
    print("="*50)
    print("WINDOWS BIGQUERY DEBUG")
    print("="*50)
    
    # 1. Environment
    print("\n1. ENVIRONMENT:")
    print(f"   Python: {sys.version.split()[0]}")
    print(f"   Platform: {sys.platform}")
    print(f"   Directory: {os.getcwd()}")
    
    # 2. Check packages
    print("\n2. PACKAGES:")
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True)
        packages = result.stdout.lower()
        
        key_packages = ['google-cloud-bigquery', 'pandas', 'numpy']
        for pkg in key_packages:
            status = "✓" if pkg.lower() in packages else "✗"
            print(f"   {status} {pkg}")
    except Exception as e:
        print(f"   Error checking packages: {e}")
    
    # 3. Check authentication
    print("\n3. AUTHENTICATION:")
    try:
        result = subprocess.run(['gcloud', 'auth', 'list'], 
                              capture_output=True, text=True)
        
        if 'ACTIVE' in result.stdout:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'ACTIVE' in line:
                    print(f"   ✓ Active: {line.split()[0]}")
                    break
        else:
            print("   ✗ No active account")
            print("   FIX: gcloud auth login")
    except:
        print("   ✗ gcloud not found")
        print("   FIX: Install Google Cloud CLI")
    
    # 4. Test BigQuery connection
    print("\n4. BIGQUERY TEST:")
    try:
        from google.cloud import bigquery
        from google.auth import default
        
        # Try to create client
        credentials, project = default()
        client = bigquery.Client(
            credentials=credentials,
            project='data-platform-dev-448613',
            location='europe-west1'  # IMPORTANT: Fixed location
        )
        
        # Test simple query with location
        job_config = bigquery.QueryJobConfig()
        job_config.location = 'europe-west1'  # IMPORTANT: Fixed location
        
        query = "SELECT 1 as test"
        result = client.query(query, job_config=job_config).result()
        
        print("   ✓ BigQuery connection successful!")
        print("   ✓ Location: europe-west1 working")
        
        return True
        
    except Exception as e:
        print(f"   ✗ BigQuery error: {e}")
        
        # Diagnose specific errors
        error_str = str(e).lower()
        if "not found" in error_str and "location us" in error_str:
            print("   DIAGNOSIS: Location issue (looking in US instead of europe-west1)")
            print("   SOLUTION: Use the FIXED version with location='europe-west1'")
        elif "credentials" in error_str:
            print("   DIAGNOSIS: Authentication issue")
            print("   SOLUTION: gcloud auth application-default login")
        elif "charmap" in error_str or "unicode" in error_str:
            print("   DIAGNOSIS: Windows Unicode issue")
            print("   SOLUTION: Use the FIXED version with Windows encoding fix")
        elif "403" in error_str:
            print("   DIAGNOSIS: Permission issue")
            print("   SOLUTION: Contact admin for BigQuery permissions")
        
        return False

if __name__ == "__main__":
    success = check_everything()
    
    print("\n" + "="*50)
    if success:
        print("✓ ALL TESTS PASSED!")
        print("Your BigQuery setup is working correctly.")
        print("\nNext step:")
        print("  python personal_account_example_FIXED.py")
    else:
        print("✗ ISSUES FOUND")
        print("Follow the SOLUTION steps above.")
        print("\nCommon fixes:")
        print("  gcloud auth login")
        print("  gcloud auth application-default login") 
        print("  python personal_account_example_FIXED.py")
    print("="*50)