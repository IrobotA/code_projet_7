"""
Analyze Specific BigQuery Table
VS Code script for running data quality analysis on a specific table
"""

import os
import sys
from bigquery_data_quality import BigQueryDataQualityChecker

def analyze_table():
    """Analyze a specific BigQuery table"""
    print("📊 BIGQUERY TABLE ANALYSIS")
    print("=" * 40)
    
    # Get parameters from environment or user input
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    dataset_id = os.getenv('BQ_DATASET_ID')
    table_id = os.getenv('BQ_TABLE_ID')
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    # Prompt for missing values
    if not project_id:
        project_id = input("Enter Google Cloud Project ID: ").strip()
    
    if not dataset_id:
        dataset_id = input("Enter BigQuery Dataset ID: ").strip()
    
    if not table_id:
        table_id = input("Enter BigQuery Table ID: ").strip()
    
    print(f"\n🎯 Target: {project_id}.{dataset_id}.{table_id}")
    print(f"🔑 Credentials: {credentials_path if credentials_path else 'Default'}")
    
    try:
        # Initialize checker
        checker = BigQueryDataQualityChecker(
            project_id=project_id,
            credentials_path=credentials_path
        )
        
        # Get table info first
        print(f"\n🔍 Getting table information...")
        schema_info = checker.get_table_schema(dataset_id, table_id)
        
        print(f"✅ Table found!")
        print(f"   Rows: {schema_info['num_rows']:,}")
        print(f"   Columns: {schema_info['total_columns']}")
        print(f"   Size: {schema_info['num_bytes']:,} bytes")
        
        # Ask about sample size for large tables
        if schema_info['num_rows'] > 100000:
            print(f"\n⚠️  Large table detected ({schema_info['num_rows']:,} rows)")
            sample_choice = input("Use sampling for faster analysis? (y/n): ").strip().lower()
            
            if sample_choice == 'y':
                sample_size = input("Enter sample size (default 10000): ").strip()
                sample_size = int(sample_size) if sample_size else 10000
            else:
                sample_size = None
        else:
            sample_size = 10000  # Default sample size
        
        # Run comprehensive analysis
        print(f"\n🔍 Running comprehensive analysis...")
        if sample_size:
            print(f"   Using sample size: {sample_size:,} rows")
        
        report = checker.analyze_table_bigquery(
            dataset_id=dataset_id,
            table_id=table_id,
            include_sample=True,
            sample_size=sample_size or 10000
        )
        
        # Display summary report
        print("\n" + "="*60)
        print(checker.generate_summary_report(report))
        
        # Save detailed report
        output_file = checker.save_report_to_file(report)
        
        print(f"\n💾 Detailed analysis saved to: {output_file}")
        print(f"📂 Open in VS Code to explore complete results!")
        
        # Show some key insights
        print(f"\n🔍 KEY INSIGHTS:")
        print("-" * 30)
        
        # Completeness insights
        completeness = report['completeness']
        low_completeness = [col for col, metrics in completeness.items() 
                          if metrics['completeness_rate'] < 80]
        
        if low_completeness:
            print(f"⚠️  Low completeness columns: {', '.join(low_completeness[:3])}")
        else:
            print(f"✅ All columns have good completeness (>80%)")
        
        # Uniqueness insights
        uniqueness = report['uniqueness']
        low_uniqueness = [col for col, metrics in uniqueness.items() 
                         if metrics['uniqueness_rate'] < 95 and metrics['duplicate_rows'] > 10]
        
        if low_uniqueness:
            print(f"🔄 High duplicate columns: {', '.join(low_uniqueness[:3])}")
        else:
            print(f"✅ Most columns have good uniqueness")
        
        # Size insights
        if schema_info['num_rows'] > 1000000:
            print(f"📈 Large table: Consider partitioning or clustering")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        print(f"\n💡 Troubleshooting:")
        print(f"1. Verify table exists: {project_id}.{dataset_id}.{table_id}")
        print(f"2. Check BigQuery permissions")
        print(f"3. Ensure table is not view-only")
        return False

def quick_completeness_check():
    """Quick completeness check only (faster for large tables)"""
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT') or input("Project ID: ").strip()
    dataset_id = os.getenv('BQ_DATASET_ID') or input("Dataset ID: ").strip() 
    table_id = os.getenv('BQ_TABLE_ID') or input("Table ID: ").strip()
    
    try:
        checker = BigQueryDataQualityChecker(project_id=project_id)
        
        print(f"\n🔍 Quick completeness check for {project_id}.{dataset_id}.{table_id}")
        
        completeness = checker.check_completeness_bigquery(dataset_id, table_id)
        
        print(f"\n📊 COMPLETENESS RESULTS:")
        print("-" * 40)
        
        for col, metrics in completeness.items():
            status = "✅" if metrics['completeness_rate'] >= 95 else "⚠️" if metrics['completeness_rate'] >= 80 else "❌"
            print(f"{status} {col}: {metrics['completeness_rate']:.1f}% ({metrics['missing_count']:,} missing)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_completeness_check()
    else:
        analyze_table()