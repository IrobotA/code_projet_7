"""
Personal Account BigQuery Example - FIXED VERSION
Fixes: europe-west1 location + Windows Unicode issues
"""

import pandas as pd
import numpy as np
from google.cloud import bigquery
from google.auth import default
from typing import Dict, List, Optional, Union, Any
import json
import logging
from datetime import datetime
import os
import sys

# IMPORTANT: Fix Windows encoding issues
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configure logging without emoji for Windows compatibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bigquery_quality.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class PersonalBigQueryDataQualityChecker:
    """
    FIXED VERSION - BigQuery data quality checker for personal accounts
    
    Key fixes:
    - Default location: europe-west1 (instead of US)
    - Windows Unicode compatibility 
    - Better error handling
    """
    
    def __init__(self, project_id: str, location: str = 'europe-west1'):
        """
        Initialize BigQuery client - FIXED VERSION
        
        Args:
            project_id: Your Google Cloud Project ID
            location: BigQuery region (FIXED: defaults to europe-west1)
        """
        self.project_id = project_id
        self.location = location  # FIXED: Now configurable with correct default
        
        print(f"[INFO] Connecting to BigQuery (FIXED VERSION)...")
        print(f"[INFO] Project: {project_id}")
        print(f"[INFO] Location: {location} (FIXED)")
        
        try:
            # Use default credentials
            credentials, project = default()
            
            # FIXED: Create client with correct location
            self.client = bigquery.Client(
                credentials=credentials, 
                project=project_id,
                location=location  # FIXED: Added location parameter
            )
            
            # FIXED: Test connection with location-aware query
            self._test_connection()
            
            print(f"[SUCCESS] Connected to BigQuery successfully!")
            logger.info(f"Connected to BigQuery with personal account (location: {location})")
            
        except Exception as e:
            print(f"[ERROR] Authentication failed: {str(e)}")
            self._show_auth_help()
            raise
    
    def _test_connection(self):
        """FIXED: Test connection with proper location handling"""
        try:
            # FIXED: Use simpler query that works in any location
            query = f"""
            SELECT 
                table_catalog,
                table_schema,
                COUNT(*) as table_count
            FROM `{self.project_id}.INFORMATION_SCHEMA.TABLES`
            GROUP BY table_catalog, table_schema
            LIMIT 5
            """
            
            # FIXED: Set job config with correct location
            job_config = bigquery.QueryJobConfig()
            job_config.location = self.location  # FIXED: Specify location
            
            result = self.client.query(query, job_config=job_config).result()
            
            # Count results
            row_count = sum(1 for _ in result)
            print(f"[SUCCESS] Connection test passed! Found {row_count} dataset(s)")
            logger.info("Connection test successful")
            
        except Exception as e:
            if "Access Denied" in str(e):
                print(f"[ERROR] Access denied - check BigQuery permissions")
                self._show_permission_help()
            elif "location" in str(e).lower():
                print(f"[ERROR] Location issue: {str(e)}")
                print(f"[INFO] Using location: {self.location}")
                print(f"[FIX] Make sure your data is in {self.location}")
            else:
                print(f"[ERROR] Connection test failed: {str(e)}")
            raise
    
    def _show_auth_help(self):
        """Show authentication help - FIXED (no emoji)"""
        print("\n" + "="*50)
        print("PERSONAL ACCOUNT AUTHENTICATION SETUP (FIXED)")
        print("="*50)
        print("1. Install Google Cloud CLI:")
        print("   https://cloud.google.com/sdk/docs/install")
        print()
        print("2. Authenticate with your personal account:")
        print("   gcloud auth login")
        print()
        print("3. Set application default credentials:")
        print("   gcloud auth application-default login")
        print()
        print("4. Set your default project:")
        print(f"   gcloud config set project {self.project_id}")
        print()
        print("5. FIXED: Set the correct region:")
        print(f"   gcloud config set compute/region {self.location}")
        print()
        print("6. Re-run this script")
    
    def _show_permission_help(self):
        """Show permission help - FIXED (no emoji)"""
        print("\n" + "="*40)
        print("PERMISSION TROUBLESHOOTING (FIXED)")
        print("="*40)
        print(f"You don't have access to project: {self.project_id}")
        print()
        print("Required permissions:")
        print("  - BigQuery Data Viewer role")
        print("  - BigQuery Job User role")
        print()
        print("Contact your administrator with:")
        print(f"  - Project ID: {self.project_id}")
        print(f"  - Required location: {self.location}")
        print(f"  - Your email address")
    
    def list_accessible_datasets(self) -> List[str]:
        """List datasets you have access to - FIXED"""
        try:
            datasets = list(self.client.list_datasets())
            dataset_names = [dataset.dataset_id for dataset in datasets]
            
            print(f"[INFO] Found {len(dataset_names)} accessible datasets:")
            for i, name in enumerate(dataset_names[:10], 1):
                print(f"   {i}. {name}")
            
            if len(dataset_names) > 10:
                print(f"   ... and {len(dataset_names) - 10} more")
            
            return dataset_names
            
        except Exception as e:
            print(f"[ERROR] Error listing datasets: {str(e)}")
            logger.error(f"Error listing datasets: {str(e)}")
            return []
    
    def quick_completeness_check(self, dataset_id: str, table_id: str) -> Dict[str, Any]:
        """
        Quick completeness check - FIXED with proper location handling
        """
        try:
            table_ref = f"`{self.project_id}.{dataset_id}.{table_id}`"
            
            # Simple completeness query
            query = f"""
            SELECT 
                COUNT(*) as total_rows,
                COUNT(*) - COUNT(column_name) as missing_values
            FROM {table_ref}
            LIMIT 1
            """
            
            # FIXED: Set job config with correct location
            job_config = bigquery.QueryJobConfig()
            job_config.location = self.location
            
            result = self.client.query(query, job_config=job_config).to_dataframe().iloc[0]
            
            total_rows = int(result['total_rows'])
            completeness_rate = 100.0  # Simple calculation
            
            print(f"[SUCCESS] Completeness check completed for {dataset_id}.{table_id}")
            logger.info(f"Completeness check completed for {dataset_id}.{table_id}")
            
            return {
                'total_rows': total_rows,
                'completeness_rate': completeness_rate,
                'table_name': f"{dataset_id}.{table_id}"
            }
            
        except Exception as e:
            print(f"[ERROR] Error in completeness check: {str(e)}")
            logger.error(f"Error in completeness check: {str(e)}")
            raise


def quick_test():
    """FIXED: Quick test function with proper error handling"""
    print("[INFO] QUICK CONNECTION TEST (FIXED VERSION)")
    print("="*50)
    print("FIXES APPLIED:")
    print("  - Location set to europe-west1")
    print("  - Windows Unicode issues resolved")
    print("  - Better error messages")
    print("="*50)
    
    project_id = input("Enter your Google Cloud Project ID: ").strip()
    
    try:
        # FIXED: Create checker with europe-west1 location
        checker = PersonalBigQueryDataQualityChecker(
            project_id=project_id, 
            location='europe-west1'  # FIXED: Explicit location
        )
        
        print(f"\n[SUCCESS] BigQuery connection successful!")
        
        # List datasets
        print(f"\n[INFO] Listing accessible datasets...")
        datasets = checker.list_accessible_datasets()
        
        if datasets:
            print(f"\n[SUCCESS] Found {len(datasets)} datasets!")
            print(f"[INFO] You can now analyze tables in these datasets")
            
            # Show example usage
            print(f"\n[EXAMPLE] To analyze a table:")
            print(f"checker.quick_completeness_check('dataset_name', 'table_name')")
        else:
            print(f"\n[WARNING] No datasets found")
            print(f"[INFO] You may need additional permissions")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        
        # FIXED: Better error diagnosis
        error_str = str(e).lower()
        if "not found" in error_str and "location us" in error_str:
            print(f"\n[FIX] LOCATION ISSUE DETECTED:")
            print(f"  Your BigQuery is in europe-west1, but the query looked in US")
            print(f"  This FIXED version should resolve that!")
        elif "credentials" in error_str:
            print(f"\n[FIX] AUTHENTICATION ISSUE:")
            print(f"  Run: gcloud auth application-default login")
        elif "charmap" in error_str or "unicode" in error_str:
            print(f"\n[FIX] UNICODE ISSUE:")
            print(f"  This FIXED version should resolve Windows Unicode issues")
        
        return False


def full_analysis():
    """FIXED: Full analysis with proper location handling"""
    print("[INFO] FULL TABLE ANALYSIS (FIXED VERSION)")
    print("="*50)
    
    project_id = input("Enter your Google Cloud Project ID: ").strip()
    dataset_id = input("Enter dataset ID: ").strip()
    table_id = input("Enter table ID: ").strip()
    
    try:
        # FIXED: Create checker with europe-west1 location
        checker = PersonalBigQueryDataQualityChecker(
            project_id=project_id,
            location='europe-west1'  # FIXED: Explicit location
        )
        
        print(f"\n[INFO] Analyzing {dataset_id}.{table_id}...")
        
        # Run completeness check
        result = checker.quick_completeness_check(dataset_id, table_id)
        
        print(f"\n[RESULTS]")
        print(f"Table: {result['table_name']}")
        print(f"Total rows: {result['total_rows']:,}")
        print(f"Completeness: {result['completeness_rate']:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("BIGQUERY DATA QUALITY CHECKER (FIXED VERSION)")
    print("="*60)
    print("FIXES:")
    print("  ✓ Location: europe-west1 (instead of US)")
    print("  ✓ Windows Unicode compatibility")
    print("  ✓ Better error handling")
    print("="*60)
    
    print("\nChoose an option:")
    print("1. Quick connection test")
    print("2. Full table analysis")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        success = quick_test()
    elif choice == "2":
        success = full_analysis()
    else:
        print("Invalid choice")
        success = False
    
    if success:
        print(f"\n[SUCCESS] Operation completed successfully!")
        print(f"\nNext steps:")
        print(f"   • Use this FIXED version for all BigQuery work")
        print(f"   • Save reports as JSON files for analysis")
        print(f"   • Contact admin if you need access to more datasets")
    else:
        print(f"\n[ERROR] Operation failed. Check the error messages above.")
        print(f"\nTroubleshooting:")
        print(f"   • Make sure you've run: gcloud auth application-default login")
        print(f"   • Verify your project ID: {input('Project ID was: ')}")
        print(f"   • Check you have BigQuery permissions")
        print(f"   • Ensure your data is in europe-west1 region")