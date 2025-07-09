"""
Test BigQuery Connection Script
Quick connection test for VS Code development
"""

import os
import sys
from bigquery_data_quality import BigQueryDataQualityChecker

def test_connection():
    """Test BigQuery connection and list available datasets"""
    print("🔍 TESTING BIGQUERY CONNECTION")
    print("=" * 40)
    
    # Get environment variables
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    if not project_id:
        project_id = input("Enter Google Cloud Project ID: ").strip()
    
    print(f"📋 Project ID: {project_id}")
    print(f"🔑 Credentials: {credentials_path if credentials_path else 'Default credentials'}")
    
    try:
        # Initialize checker
        checker = BigQueryDataQualityChecker(
            project_id=project_id,
            credentials_path=credentials_path
        )
        
        print("\n✅ Connection successful!")
        
        # List datasets
        print("\n📂 Available datasets:")
        datasets = list(checker.client.list_datasets())
        
        if datasets:
            for i, dataset in enumerate(datasets[:10], 1):  # Show first 10
                print(f"   {i}. {dataset.dataset_id}")
            
            if len(datasets) > 10:
                print(f"   ... and {len(datasets) - 10} more")
        else:
            print("   No datasets found")
        
        # Test a simple query
        print("\n🔍 Testing query execution...")
        query = f"""
        SELECT 
            table_catalog,
            table_schema, 
            table_name,
            table_type
        FROM `{project_id}.INFORMATION_SCHEMA.TABLES`
        LIMIT 5
        """
        
        result = checker.client.query(query).to_dataframe()
        print(f"✅ Query successful! Found {len(result)} tables")
        
        if not result.empty:
            print("\n📋 Sample tables:")
            for _, row in result.iterrows():
                print(f"   {row['table_schema']}.{row['table_name']} ({row['table_type']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("\n💡 Troubleshooting tips:")
        print("1. Check your Google Cloud Project ID")
        print("2. Verify service account credentials")
        print("3. Ensure BigQuery API is enabled")
        print("4. Check IAM permissions (BigQuery Data Viewer, BigQuery Job User)")
        return False

def quick_table_info():
    """Get quick info about a specific table"""
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    
    if not project_id:
        project_id = input("Enter Google Cloud Project ID: ").strip()
    
    dataset_id = input("Enter Dataset ID: ").strip()
    table_id = input("Enter Table ID: ").strip()
    
    try:
        checker = BigQueryDataQualityChecker(project_id=project_id)
        schema_info = checker.get_table_schema(dataset_id, table_id)
        
        print(f"\n📊 TABLE INFO: {schema_info['project_id']}.{schema_info['dataset_id']}.{schema_info['table_id']}")
        print("-" * 60)
        print(f"Rows: {schema_info['num_rows']:,}")
        print(f"Size: {schema_info['num_bytes']:,} bytes")
        print(f"Columns: {schema_info['total_columns']}")
        
        print(f"\n📋 SCHEMA:")
        for col in schema_info['schema'][:10]:  # Show first 10 columns
            print(f"   {col['column_name']}: {col['data_type']} ({col['mode']})")
        
        if len(schema_info['schema']) > 10:
            print(f"   ... and {len(schema_info['schema']) - 10} more columns")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 BIGQUERY CONNECTION TESTER")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "table":
        quick_table_info()
    else:
        test_connection()