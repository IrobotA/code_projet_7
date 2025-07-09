"""
Example usage of the Data Quality Checker
Shows how to use the system with different SQL databases and configurations
"""

import pandas as pd
import json
from data_quality_checker import DataQualityChecker

def example_postgresql():
    """Example with PostgreSQL database"""
    print("=== PostgreSQL Example ===")
    
    # Connection string for PostgreSQL
    connection_string = "postgresql://username:password@localhost:5432/database_name"
    
    # Initialize checker
    checker = DataQualityChecker(connection_string)
    
    # Basic analysis
    report = checker.analyze_table('customers', schema='public')
    
    # Print summary
    print(checker.generate_summary_report(report))
    
    # Save detailed report to JSON
    with open('quality_report_postgresql.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)

def example_mysql():
    """Example with MySQL database"""
    print("=== MySQL Example ===")
    
    # Connection string for MySQL
    connection_string = "mysql+pymysql://username:password@localhost:3306/database_name"
    
    # Initialize checker
    checker = DataQualityChecker(connection_string)
    
    # Analyze with sample size for large tables
    report = checker.analyze_table('orders', sample_size=10000)
    
    print(checker.generate_summary_report(report))

def example_sqlserver():
    """Example with SQL Server database"""
    print("=== SQL Server Example ===")
    
    # Connection string for SQL Server
    connection_string = "mssql+pyodbc://username:password@server:port/database?driver=ODBC+Driver+17+for+SQL+Server"
    
    # Initialize checker
    checker = DataQualityChecker(connection_string)
    
    # Analyze with custom validation rules
    custom_rules = {
        'email_column': {
            'max_length': 100,
            'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        },
        'age_column': {
            'min_value': 0,
            'max_value': 120
        }
    }
    
    report = checker.analyze_table('users', custom_rules=custom_rules)
    print(checker.generate_summary_report(report))

def example_sqlite():
    """Example with SQLite database"""
    print("=== SQLite Example ===")
    
    # Connection string for SQLite
    connection_string = "sqlite:///path/to/database.db"
    
    # Initialize checker
    checker = DataQualityChecker(connection_string)
    
    # Analyze all tables in database
    tables = ['customers', 'orders', 'products']
    
    for table in tables:
        print(f"\n--- Analyzing table: {table} ---")
        report = checker.analyze_table(table)
        print(checker.generate_summary_report(report))

def example_custom_validation():
    """Example with comprehensive custom validation rules"""
    print("=== Custom Validation Example ===")
    
    connection_string = "postgresql://username:password@localhost:5432/database_name"
    checker = DataQualityChecker(connection_string)
    
    # Define comprehensive custom validation rules
    custom_rules = {
        'varchar': {
            'max_length_check': True,
            'pattern_checks': {
                'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                'phone': r'^\+?[\d\s\-\(\)]{10,}$',
                'postal_code': r'^\d{5}(-\d{4})?$'
            }
        },
        'numeric': {
            'range_check': True,
            'min_value': -1000000,
            'max_value': 1000000
        },
        'datetime': {
            'date_range_check': True,
            'min_date': '2000-01-01',
            'max_date': '2030-12-31'
        }
    }
    
    # Analyze customer table with custom rules
    report = checker.analyze_table('customers', custom_rules=custom_rules)
    
    # Generate detailed analysis
    print(checker.generate_summary_report(report))
    
    # Save comprehensive report
    with open('comprehensive_quality_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)

def example_monitoring_workflow():
    """Example of setting up automated quality monitoring"""
    print("=== Quality Monitoring Workflow ===")
    
    connection_string = "postgresql://username:password@localhost:5432/database_name"
    checker = DataQualityChecker(connection_string)
    
    # Define quality thresholds
    quality_thresholds = {
        'completeness_minimum': 95.0,
        'validity_minimum': 90.0,
        'uniqueness_minimum': 99.0  # For ID columns
    }
    
    # Tables to monitor
    critical_tables = ['customers', 'orders', 'payments']
    
    quality_alerts = []
    
    for table in critical_tables:
        print(f"\n🔍 Monitoring table: {table}")
        
        # Run analysis
        report = checker.analyze_table(table)
        
        # Check quality metrics against thresholds
        for column, completeness in report['completeness'].items():
            if completeness['completeness_score'] < quality_thresholds['completeness_minimum']:
                quality_alerts.append({
                    'table': table,
                    'column': column,
                    'issue': 'completeness',
                    'value': completeness['completeness_score'],
                    'threshold': quality_thresholds['completeness_minimum']
                })
        
        for column, validity in report['validity'].items():
            if 'validity_percentage' in validity:
                if validity['validity_percentage'] < quality_thresholds['validity_minimum']:
                    quality_alerts.append({
                        'table': table,
                        'column': column,
                        'issue': 'validity',
                        'value': validity['validity_percentage'],
                        'threshold': quality_thresholds['validity_minimum']
                    })
        
        # Check uniqueness for ID columns
        for column, uniqueness in report['uniqueness'].items():
            if 'id' in column.lower() or 'key' in column.lower():
                if uniqueness['uniqueness_percentage'] < quality_thresholds['uniqueness_minimum']:
                    quality_alerts.append({
                        'table': table,
                        'column': column,
                        'issue': 'uniqueness',
                        'value': uniqueness['uniqueness_percentage'],
                        'threshold': quality_thresholds['uniqueness_minimum']
                    })
    
    # Report alerts
    if quality_alerts:
        print("\n🚨 QUALITY ALERTS DETECTED:")
        for alert in quality_alerts:
            print(f"  ❌ {alert['table']}.{alert['column']}: {alert['issue']} = {alert['value']:.1f}% (threshold: {alert['threshold']}%)")
    else:
        print("\n✅ All quality metrics meet thresholds!")
    
    # Save monitoring report
    monitoring_report = {
        'monitoring_timestamp': pd.Timestamp.now().isoformat(),
        'thresholds': quality_thresholds,
        'tables_monitored': critical_tables,
        'alerts': quality_alerts
    }
    
    with open('quality_monitoring_report.json', 'w') as f:
        json.dump(monitoring_report, f, indent=2, default=str)

def example_dataframe_analysis():
    """Example analyzing pandas DataFrames directly"""
    print("=== DataFrame Analysis Example ===")
    
    # Create sample DataFrame
    data = {
        'id': [1, 2, 3, 4, 5, None],
        'name': ['John', 'Jane', 'Bob', '', None, 'Alice'],
        'email': ['john@email.com', 'invalid-email', 'jane@email.com', 'bob@email.com', None, 'alice@email.com'],
        'age': [25, 30, -5, 45, None, 35],
        'salary': [50000, 60000, 75000, float('inf'), None, 55000]
    }
    
    df = pd.DataFrame(data)
    
    # Use demo checker for DataFrames
    from demo_quality_checker import DemoDataQualityChecker
    
    checker = DemoDataQualityChecker()
    report = checker.analyze_dataframe(df, "sample_dataframe")
    
    print(checker.generate_summary_report(report))

def main():
    """Run all examples"""
    print("🚀 DATA QUALITY CHECKER - USAGE EXAMPLES")
    print("=" * 60)
    
    print("\n📋 Available Examples:")
    print("1. PostgreSQL Database Analysis")
    print("2. MySQL Database Analysis") 
    print("3. SQL Server Database Analysis")
    print("4. SQLite Database Analysis")
    print("5. Custom Validation Rules")
    print("6. Quality Monitoring Workflow")
    print("7. DataFrame Analysis")
    
    print("\n💡 To run these examples:")
    print("- Update connection strings with your database credentials")
    print("- Install required database drivers (psycopg2, pymysql, pyodbc)")
    print("- Ensure your databases contain the referenced tables")
    
    # Run DataFrame example (works without database)
    example_dataframe_analysis()
    
    print("\n✅ Example completed!")
    print("\n📚 Usage Summary:")
    print("1. Initialize DataQualityChecker with connection string")
    print("2. Call analyze_table() with table name and optional parameters")
    print("3. Use generate_summary_report() for human-readable output")
    print("4. Save detailed results to JSON for further analysis")
    print("5. Set up monitoring workflows with quality thresholds")

if __name__ == "__main__":
    main()