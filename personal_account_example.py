"""
Personal Account BigQuery Data Quality Example
For users who cannot create service accounts
"""

from bigquery_personal_auth import PersonalBigQueryDataQualityChecker

def main():
    """
    Simple example using your personal Google account
    No service account required!
    """
    print("🚀 BIGQUERY DATA QUALITY - PERSONAL ACCOUNT")
    print("=" * 50)
    
    # Step 1: Enter your project ID
    project_id = input("Enter your Google Cloud Project ID: ").strip()
    
    if not project_id:
        print("❌ Project ID is required")
        return
    
    try:
        # Step 2: Initialize with personal account
        print(f"\n🔍 Connecting to project: {project_id}")
        checker = PersonalBigQueryDataQualityChecker(project_id=project_id)
        
        # Step 3: List what you have access to
        print(f"\n📂 Checking your access...")
        datasets = checker.list_accessible_datasets()
        
        if not datasets:
            print("❌ No datasets found. You may need access permissions.")
            print("💡 Contact your administrator to request access.")
            return
        
        # Step 4: Choose a dataset
        print(f"\nChoose a dataset to explore:")
        for i, dataset in enumerate(datasets[:10], 1):
            print(f"   {i}. {dataset}")
        
        try:
            choice = int(input(f"\nEnter dataset number (1-{min(len(datasets), 10)}): ")) - 1
            if choice < 0 or choice >= len(datasets):
                print("❌ Invalid choice")
                return
            
            selected_dataset = datasets[choice]
            
        except ValueError:
            print("❌ Please enter a valid number")
            return
        
        # Step 5: List tables in selected dataset
        print(f"\n📋 Tables in {selected_dataset}:")
        tables = checker.list_tables_in_dataset(selected_dataset)
        
        if not tables:
            print("❌ No tables found in this dataset.")
            return
        
        # Step 6: Choose a table
        print(f"\nChoose a table to analyze:")
        for i, table in enumerate(tables[:10], 1):
            print(f"   {i}. {table}")
        
        try:
            table_choice = int(input(f"\nEnter table number (1-{min(len(tables), 10)}): ")) - 1
            if table_choice < 0 or table_choice >= len(tables):
                print("❌ Invalid choice")
                return
            
            selected_table = tables[table_choice]
            
        except ValueError:
            print("❌ Please enter a valid number")
            return
        
        # Step 7: Analyze the table
        print(f"\n🎯 Analyzing {selected_dataset}.{selected_table}...")
        print("This may take a moment for large tables...")
        
        try:
            report = checker.analyze_table_basic(selected_dataset, selected_table)
            
            # Step 8: Show results
            print("\n" + checker.generate_simple_report(report))
            
            # Step 9: Save results to file
            import json
            output_file = f"quality_report_{selected_dataset}_{selected_table}.json"
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"\n💾 Detailed report saved to: {output_file}")
            print("📂 Open this file in VS Code to explore the complete analysis!")
            
        except Exception as analysis_error:
            print(f"❌ Analysis failed: {str(analysis_error)}")
            print("💡 You may not have sufficient permissions for this table.")
        
    except Exception as e:
        if "Access Denied" in str(e):
            print(f"❌ Access denied to project: {project_id}")
            print()
            print("💡 TROUBLESHOOTING STEPS:")
            print("1. Verify the project ID is correct")
            print("2. Check if you have access to this project")
            print("3. Contact your administrator to request:")
            print("   • BigQuery Data Viewer role")
            print("   • BigQuery Job User role")
            print()
            print("📧 Send this to your administrator:")
            print(f"   Project: {project_id}")
            print("   User: [your-email@company.com]")
            print("   Requested roles: BigQuery Data Viewer, BigQuery Job User")
        else:
            print(f"❌ Connection failed: {str(e)}")
            print()
            print("💡 Make sure you've run:")
            print("   gcloud auth login")
            print("   gcloud auth application-default login")

def quick_test():
    """Quick connection test only"""
    print("🔍 QUICK CONNECTION TEST")
    print("=" * 30)
    
    project_id = input("Enter your Google Cloud Project ID: ").strip()
    
    try:
        checker = PersonalBigQueryDataQualityChecker(project_id=project_id)
        datasets = checker.list_accessible_datasets()
        
        if datasets:
            print(f"\n✅ SUCCESS! You have access to {len(datasets)} datasets.")
            print("🎉 Your BigQuery data quality system is ready to use!")
        else:
            print(f"\n⚠️ Connected but no datasets found.")
            print("You may need additional permissions.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Quick connection test")
    print("2. Full table analysis")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        quick_test()
    elif choice == "2":
        main()
    else:
        print("❌ Invalid choice")
    
    print(f"\n📚 Next steps:")
    print(f"   • Use this script to analyze any BigQuery table")
    print(f"   • Save reports as JSON files for further analysis")
    print(f"   • Contact admin if you need access to more datasets")