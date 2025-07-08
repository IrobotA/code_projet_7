"""
Simple BigQuery Data Quality Example
Minimal setup example for VS Code
"""

from bigquery_data_quality import BigQueryDataQualityChecker

def simple_example():
    """
    Simple example to get you started quickly
    """
    print("🚀 SIMPLE BIGQUERY DATA QUALITY EXAMPLE")
    print("=" * 50)
    
    # Step 1: Set your project details
    PROJECT_ID = "your-project-id"  # ← Change this!
    DATASET_ID = "your-dataset"     # ← Change this!
    TABLE_ID = "your-table"         # ← Change this!
    
    print(f"🎯 Analyzing: {PROJECT_ID}.{DATASET_ID}.{TABLE_ID}")
    
    try:
        # Step 2: Initialize the checker
        # Option A: With service account JSON file
        checker = BigQueryDataQualityChecker(
            project_id=PROJECT_ID,
            credentials_path="./credentials/bigquery-service-account.json"
        )
        
        # Option B: With default credentials (uncomment if using gcloud auth)
        # checker = BigQueryDataQualityChecker(project_id=PROJECT_ID)
        
        print("✅ Connected to BigQuery successfully!")
        
        # Step 3: Get basic table information
        print(f"\n🔍 Getting table information...")
        schema_info = checker.get_table_schema(DATASET_ID, TABLE_ID)
        
        print(f"📊 Table has {schema_info['num_rows']:,} rows and {schema_info['total_columns']} columns")
        
        # Step 4: Run quick completeness check
        print(f"\n📋 Checking data completeness...")
        completeness = checker.check_completeness_bigquery(DATASET_ID, TABLE_ID)
        
        print(f"📈 COMPLETENESS RESULTS:")
        for column, metrics in list(completeness.items())[:5]:  # Show first 5 columns
            status = "✅" if metrics['completeness_rate'] >= 95 else "⚠️" if metrics['completeness_rate'] >= 80 else "❌"
            print(f"   {status} {column}: {metrics['completeness_rate']:.1f}% complete")
        
        # Step 5: Run quick uniqueness check  
        print(f"\n🔑 Checking data uniqueness...")
        uniqueness = checker.check_uniqueness_bigquery(DATASET_ID, TABLE_ID, 
                                                       columns=list(completeness.keys())[:3])  # First 3 columns
        
        print(f"🔄 UNIQUENESS RESULTS:")
        for column, metrics in uniqueness.items():
            status = "✅" if metrics['uniqueness_rate'] >= 95 else "⚠️" if metrics['uniqueness_rate'] >= 80 else "❌"
            print(f"   {status} {column}: {metrics['uniqueness_rate']:.1f}% unique")
        
        # Step 6: Full analysis (optional - for smaller tables)
        if schema_info['num_rows'] < 100000:  # Only for smaller tables
            print(f"\n🎯 Running full data quality analysis...")
            report = checker.analyze_table_bigquery(DATASET_ID, TABLE_ID)
            
            # Save report
            output_file = checker.save_report_to_file(report)
            print(f"💾 Full report saved to: {output_file}")
            
            # Show summary
            print(f"\n📊 SUMMARY:")
            print(checker.generate_summary_report(report))
        else:
            print(f"\n💡 Table is large ({schema_info['num_rows']:,} rows)")
            print(f"   Use analyze_table.py for full analysis with sampling")
        
        print(f"\n🎉 Analysis complete! Your BigQuery data quality system is working!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"\n💡 Troubleshooting steps:")
        print(f"1. Check your project ID: {PROJECT_ID}")
        print(f"2. Verify table exists: {DATASET_ID}.{TABLE_ID}")
        print(f"3. Confirm BigQuery permissions")
        print(f"4. Test connection with: python test_bigquery_connection.py")

def quick_test():
    """
    Very quick connection test
    """
    PROJECT_ID = input("Enter your Google Cloud Project ID: ").strip()
    
    try:
        checker = BigQueryDataQualityChecker(project_id=PROJECT_ID)
        
        # List some datasets
        datasets = list(checker.client.list_datasets())
        print(f"✅ Connected! Found {len(datasets)} datasets")
        
        if datasets:
            print(f"📂 Sample datasets:")
            for dataset in datasets[:3]:
                print(f"   - {dataset.dataset_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Quick connection test")
    print("2. Full example (requires table details)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        quick_test()
    elif choice == "2":
        simple_example()
    else:
        print("❌ Invalid choice")
        
    print(f"\n📚 For more examples, see:")
    print(f"   - test_bigquery_connection.py")
    print(f"   - analyze_table.py") 
    print(f"   - BIGQUERY_VSCODE_SETUP.md")