"""
Simple test script for the FIXED BigQuery Data Quality Checker
Handles europe-west1 location and Windows Unicode issues
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the fixed version
from bigquery_personal_auth_fixed import PersonalBigQueryDataQualityChecker

def test_bigquery_connection():
    """Test BigQuery connection with the fixed version"""
    print("BIGQUERY CONNECTION TEST (FIXED VERSION)")
    print("=" * 50)
    print("Fixed for:")
    print("  - europe-west1 location")
    print("  - Windows Unicode issues")
    print("  - Better error handling")
    print()
    
    # Get project ID
    project_id = input("Enter your Google Cloud Project ID: ").strip()
    
    if not project_id:
        print("[ERROR] Project ID is required")
        return False
    
    try:
        # Create checker with fixed location
        print(f"\n[INFO] Creating BigQuery client...")
        print(f"[INFO] Project: {project_id}")
        print(f"[INFO] Location: europe-west1 (FIXED)")
        
        checker = PersonalBigQueryDataQualityChecker(
            project_id=project_id, 
            location='europe-west1'  # Fixed location
        )
        
        print(f"\n[SUCCESS] BigQuery client created successfully!")
        
        # List datasets
        print(f"\n[INFO] Listing accessible datasets...")
        datasets = checker.list_accessible_datasets()
        
        if not datasets:
            print(f"[WARNING] No datasets found. You may need additional permissions.")
            return False
        
        # Let user choose a dataset to explore
        if len(datasets) > 0:
            print(f"\nWhich dataset would you like to explore?")
            for i, dataset in enumerate(datasets[:5], 1):  # Show first 5
                print(f"  {i}. {dataset}")
            
            try:
                choice = input(f"\nEnter number (1-{min(5, len(datasets))}): ").strip()
                dataset_idx = int(choice) - 1
                
                if 0 <= dataset_idx < len(datasets):
                    selected_dataset = datasets[dataset_idx]
                    
                    print(f"\n[INFO] Exploring dataset: {selected_dataset}")
                    tables = checker.list_tables_in_dataset(selected_dataset)
                    
                    if tables and len(tables) > 0:
                        # Try to analyze the first table
                        first_table = tables[0]
                        print(f"\n[INFO] Analyzing first table: {first_table}")
                        
                        try:
                            # Basic analysis
                            result = checker.analyze_table_basic(selected_dataset, first_table)
                            
                            # Generate and display report
                            report = checker.generate_simple_report(result)
                            print("\n" + "="*60)
                            print(report)
                            print("="*60)
                            
                            print(f"\n[SUCCESS] Analysis completed successfully!")
                            return True
                            
                        except Exception as analysis_error:
                            print(f"[WARNING] Could not analyze table {first_table}: {analysis_error}")
                            print(f"[INFO] Connection test was successful though!")
                            return True
                    
                    else:
                        print(f"[INFO] No tables found in {selected_dataset}")
                        print(f"[INFO] Connection test was successful though!")
                        return True
                
                else:
                    print(f"[WARNING] Invalid choice. Connection test was successful though!")
                    return True
                    
            except (ValueError, IndexError):
                print(f"[WARNING] Invalid input. Connection test was successful though!")
                return True
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        print(f"\nTROUBLESHOoting STEPS:")
        print(f"1. Make sure you've run: gcloud auth login")
        print(f"2. Make sure you've run: gcloud auth application-default login")
        print(f"3. Make sure you have access to project: {project_id}")
        print(f"4. Make sure your project is in europe-west1 region")
        print(f"5. Check you have BigQuery permissions (BigQuery Data Viewer, BigQuery Job User)")
        return False


def quick_demo():
    """Quick demo with example usage"""
    print("QUICK DEMO - BIGQUERY DATA QUALITY")
    print("=" * 40)
    
    project_id = "data-platform-dev-448613"  # Your project
    
    print(f"Demo project: {project_id}")
    print(f"Location: europe-west1 (Fixed)")
    print()
    
    try:
        # Create checker
        checker = PersonalBigQueryDataQualityChecker(
            project_id=project_id,
            location='europe-west1'
        )
        
        # Show available datasets
        datasets = checker.list_accessible_datasets()
        
        if datasets:
            print(f"\n[SUCCESS] Found {len(datasets)} accessible datasets!")
            print(f"You can now use this checker to analyze any table in these datasets.")
            
            # Example usage
            print(f"\nEXAMPLE USAGE:")
            print(f"```python")
            print(f"# Analyze a table")
            print(f"result = checker.analyze_table_basic('your_dataset', 'your_table')")
            print(f"")
            print(f"# Generate report")
            print(f"report = checker.generate_simple_report(result)")
            print(f"print(report)")
            print(f"```")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Demo failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("Choose test mode:")
    print("1. Interactive test")
    print("2. Quick demo")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_bigquery_connection()
    elif choice == "2":
        quick_demo()
    else:
        print("Running interactive test by default...")
        test_bigquery_connection()