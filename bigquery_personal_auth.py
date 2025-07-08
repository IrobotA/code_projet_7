"""
BigQuery Data Quality Checker - Personal Account Authentication
For users who cannot create service accounts but have personal access
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

# Configure logging for VS Code
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bigquery_quality.log')
    ]
)
logger = logging.getLogger(__name__)

class PersonalBigQueryDataQualityChecker:
    """
    BigQuery data quality checker using personal authentication
    No service account required - uses your personal Google account
    """
    
    def __init__(self, project_id: str, location: str = 'US'):
        """
        Initialize BigQuery client with personal authentication
        
        Args:
            project_id: Google Cloud Project ID you have access to
            location: BigQuery location/region
        """
        self.project_id = project_id
        self.location = location
        
        try:
            # Use default credentials (your personal account via gcloud)
            credentials, project = default()
            self.client = bigquery.Client(credentials=credentials, project=project_id)
            
            # Test connection immediately
            self._test_connection()
            
            logger.info(f"✅ Connected to BigQuery with personal account")
            logger.info(f"📋 Project: {project_id}")
            
        except Exception as e:
            logger.error(f"❌ Authentication failed: {str(e)}")
            self._show_auth_help()
            raise
        
        self.validation_rules = self._get_bigquery_validation_rules()
    
    def _test_connection(self):
        """Test the BigQuery connection with a simple query"""
        try:
            query = f"""
            SELECT 
                COUNT(*) as table_count
            FROM `{self.project_id}.INFORMATION_SCHEMA.TABLES`
            LIMIT 1
            """
            
            result = self.client.query(query).result()
            logger.info("🔍 Connection test successful")
            
        except Exception as e:
            if "Access Denied" in str(e):
                logger.error("❌ Access denied - you may not have BigQuery permissions")
                self._show_permission_help()
            else:
                logger.error(f"❌ Connection test failed: {str(e)}")
            raise
    
    def _show_auth_help(self):
        """Show authentication help for personal accounts"""
        print("\n🔧 PERSONAL ACCOUNT AUTHENTICATION SETUP")
        print("=" * 50)
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
        print("5. Re-run this script")
    
    def _show_permission_help(self):
        """Show help for permission issues"""
        print("\n🛡️ PERMISSION TROUBLESHOOTING")
        print("=" * 40)
        print(f"❌ You don't have access to project: {self.project_id}")
        print()
        print("💡 What you need:")
        print("   • BigQuery Data Viewer role")
        print("   • BigQuery Job User role")
        print()
        print("📧 Contact your project administrator with:")
        print(f"   • Project ID: {self.project_id}")
        print(f"   • Your email: [your-email@company.com]")
        print(f"   • Required roles: BigQuery Data Viewer, BigQuery Job User")
        print()
        print("🔍 Or try a different project you have access to")
    
    def _get_bigquery_validation_rules(self) -> Dict:
        """BigQuery-specific validation rules"""
        return {
            'STRING': {
                'max_length_check': True,
                'pattern_checks': {
                    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                    'phone': r'^\+?[\d\s\-\(\)]{10,}$',
                    'url': r'https?://[^\s]+'
                }
            },
            'INT64': {
                'range_check': True,
                'min_value': -9223372036854775808,
                'max_value': 9223372036854775807
            },
            'FLOAT64': {
                'range_check': True,
                'min_value': -1.7976931348623157e+308,
                'max_value': 1.7976931348623157e+308
            }
        }
    
    def list_accessible_datasets(self) -> List[str]:
        """List datasets you have access to"""
        try:
            datasets = list(self.client.list_datasets())
            dataset_names = [dataset.dataset_id for dataset in datasets]
            
            print(f"📂 Found {len(dataset_names)} accessible datasets:")
            for i, name in enumerate(dataset_names[:10], 1):  # Show first 10
                print(f"   {i}. {name}")
            
            if len(dataset_names) > 10:
                print(f"   ... and {len(dataset_names) - 10} more")
            
            return dataset_names
            
        except Exception as e:
            logger.error(f"Error listing datasets: {str(e)}")
            return []
    
    def list_tables_in_dataset(self, dataset_id: str) -> List[str]:
        """List tables in a specific dataset"""
        try:
            dataset_ref = self.client.dataset(dataset_id)
            tables = list(self.client.list_tables(dataset_ref))
            table_names = [table.table_id for table in tables]
            
            print(f"📋 Found {len(table_names)} tables in {dataset_id}:")
            for i, name in enumerate(table_names[:10], 1):  # Show first 10
                print(f"   {i}. {name}")
            
            if len(table_names) > 10:
                print(f"   ... and {len(table_names) - 10} more")
            
            return table_names
            
        except Exception as e:
            logger.error(f"Error listing tables in {dataset_id}: {str(e)}")
            return []
    
    def get_table_info(self, dataset_id: str, table_id: str) -> Dict:
        """Get basic table information"""
        try:
            table_ref = self.client.dataset(dataset_id).table(table_id)
            table = self.client.get_table(table_ref)
            
            schema_info = []
            for field in table.schema:
                schema_info.append({
                    'column_name': field.name,
                    'data_type': field.field_type,
                    'mode': field.mode,
                    'description': field.description or ''
                })
            
            return {
                'project_id': table.project,
                'dataset_id': table.dataset_id,
                'table_id': table.table_id,
                'full_name': f"{table.project}.{table.dataset_id}.{table.table_id}",
                'num_rows': table.num_rows,
                'num_bytes': table.num_bytes,
                'created': table.created.isoformat() if table.created else None,
                'modified': table.modified.isoformat() if table.modified else None,
                'schema': schema_info,
                'total_columns': len(schema_info)
            }
            
        except Exception as e:
            logger.error(f"Error getting table info: {str(e)}")
            raise
    
    def quick_completeness_check(self, dataset_id: str, table_id: str) -> Dict[str, Any]:
        """
        Quick completeness check using BigQuery SQL
        """
        try:
            table_ref = f"`{self.project_id}.{dataset_id}.{table_id}`"
            
            # Get table schema first
            table_info = self.get_table_info(dataset_id, table_id)
            total_rows = table_info['num_rows']
            
            # Build query to count nulls for all columns (limit to first 20 columns for safety)
            columns_to_check = table_info['schema'][:20]  # Limit to avoid query complexity
            
            null_checks = []
            for column in columns_to_check:
                col_name = column['column_name']
                null_checks.append(f"COUNTIF({col_name} IS NULL) as {col_name}_nulls")
            
            query = f"""
            SELECT 
                COUNT(*) as total_rows,
                {', '.join(null_checks)}
            FROM {table_ref}
            """
            
            result = self.client.query(query).to_dataframe().iloc[0]
            
            # Process results
            completeness_results = {}
            actual_total = int(result['total_rows'])
            
            for column in columns_to_check:
                col_name = column['column_name']
                null_count = int(result[f'{col_name}_nulls'])
                present_count = actual_total - null_count
                completeness_rate = (present_count / actual_total) * 100 if actual_total > 0 else 0
                
                completeness_results[col_name] = {
                    'total_rows': actual_total,
                    'missing_count': null_count,
                    'present_count': present_count,
                    'completeness_rate': round(completeness_rate, 2),
                    'data_type': column['data_type']
                }
            
            logger.info(f"✅ Completeness check completed for {dataset_id}.{table_id}")
            return completeness_results
            
        except Exception as e:
            logger.error(f"Error in completeness check: {str(e)}")
            raise
    
    def quick_uniqueness_check(self, dataset_id: str, table_id: str, 
                              columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Quick uniqueness check using BigQuery SQL
        """
        try:
            table_ref = f"`{self.project_id}.{dataset_id}.{table_id}`"
            
            if columns is None:
                table_info = self.get_table_info(dataset_id, table_id)
                # Limit to first 5 columns for performance
                columns = [col['column_name'] for col in table_info['schema'][:5]]
            
            uniqueness_results = {}
            
            for column in columns:
                try:
                    query = f"""
                    SELECT 
                        COUNT(*) as total_rows,
                        COUNT(DISTINCT {column}) as unique_count,
                        COUNT({column}) as non_null_count
                    FROM {table_ref}
                    """
                    
                    result = self.client.query(query).to_dataframe().iloc[0]
                    
                    total_rows = int(result['total_rows'])
                    unique_count = int(result['unique_count'])
                    duplicate_rows = total_rows - unique_count
                    uniqueness_rate = (unique_count / total_rows) * 100 if total_rows > 0 else 0
                    
                    uniqueness_results[column] = {
                        'total_rows': total_rows,
                        'unique_count': unique_count,
                        'duplicate_rows': duplicate_rows,
                        'uniqueness_rate': round(uniqueness_rate, 2)
                    }
                    
                except Exception as col_error:
                    logger.warning(f"Skipping column {column}: {str(col_error)}")
                    continue
            
            logger.info(f"✅ Uniqueness check completed for {dataset_id}.{table_id}")
            return uniqueness_results
            
        except Exception as e:
            logger.error(f"Error in uniqueness check: {str(e)}")
            raise
    
    def analyze_table_basic(self, dataset_id: str, table_id: str) -> Dict[str, Any]:
        """
        Basic table analysis (completeness + uniqueness)
        Safe for users with limited permissions
        """
        logger.info(f"🔍 Starting basic analysis for {dataset_id}.{table_id}")
        
        try:
            # Get table metadata
            table_info = self.get_table_info(dataset_id, table_id)
            
            print(f"📊 Table: {table_info['full_name']}")
            print(f"   Rows: {table_info['num_rows']:,}")
            print(f"   Columns: {table_info['total_columns']}")
            
            # Run completeness check
            print(f"\n🔍 Checking completeness...")
            completeness_results = self.quick_completeness_check(dataset_id, table_id)
            
            # Run uniqueness check (limited columns)
            print(f"🔍 Checking uniqueness...")
            uniqueness_results = self.quick_uniqueness_check(dataset_id, table_id)
            
            # Compile report
            report = {
                'table_info': {
                    'project_id': self.project_id,
                    'dataset_id': dataset_id,
                    'table_id': table_id,
                    'full_table_id': table_info['full_name'],
                    'analysis_timestamp': datetime.now().isoformat(),
                    'analysis_type': 'basic_personal_account'
                },
                'schema': table_info,
                'completeness': completeness_results,
                'uniqueness': uniqueness_results
            }
            
            logger.info(f"✅ Basic analysis completed for {dataset_id}.{table_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error in table analysis: {str(e)}")
            raise
    
    def generate_simple_report(self, analysis_result: Dict) -> str:
        """Generate a simple summary report"""
        report = []
        report.append("📊 BIGQUERY DATA QUALITY REPORT (Personal Account)")
        report.append("=" * 60)
        
        # Table info
        info = analysis_result['table_info']
        schema = analysis_result['schema']
        
        report.append(f"🏷️  Table: {info['full_table_id']}")
        report.append(f"📊 Rows: {schema['num_rows']:,}")
        report.append(f"📋 Columns: {schema['total_columns']}")
        report.append(f"🕐 Analysis: {info['analysis_timestamp']}")
        report.append("")
        
        # Completeness summary
        completeness = analysis_result['completeness']
        report.append("🔍 COMPLETENESS SUMMARY")
        report.append("-" * 40)
        
        for col, metrics in completeness.items():
            status = "✅" if metrics['completeness_rate'] >= 95 else "⚠️" if metrics['completeness_rate'] >= 80 else "❌"
            report.append(f"{status} {col}: {metrics['completeness_rate']:.1f}% complete")
        
        report.append("")
        
        # Uniqueness summary
        uniqueness = analysis_result['uniqueness']
        report.append("🔑 UNIQUENESS SUMMARY")
        report.append("-" * 40)
        
        for col, metrics in uniqueness.items():
            status = "✅" if metrics['uniqueness_rate'] >= 95 else "⚠️" if metrics['uniqueness_rate'] >= 80 else "❌"
            report.append(f"{status} {col}: {metrics['uniqueness_rate']:.1f}% unique")
        
        return "\n".join(report)


def setup_personal_authentication():
    """Interactive setup for personal authentication"""
    print("🔧 PERSONAL ACCOUNT SETUP FOR BIGQUERY")
    print("=" * 50)
    
    print("This will guide you through setting up BigQuery access with your personal account.")
    print()
    
    # Check if gcloud is installed
    try:
        import subprocess
        result = subprocess.run(['gcloud', '--version'], capture_output=True, text=True)
        print("✅ Google Cloud CLI is installed")
    except FileNotFoundError:
        print("❌ Google Cloud CLI not found")
        print()
        print("📥 Please install Google Cloud CLI:")
        print("   https://cloud.google.com/sdk/docs/install")
        print()
        return False
    
    # Guide through authentication
    print("\n🔑 AUTHENTICATION STEPS:")
    print("1. Run: gcloud auth login")
    print("2. Run: gcloud auth application-default login")
    print("3. Run: gcloud config set project YOUR_PROJECT_ID")
    print()
    
    project_id = input("Enter your Google Cloud Project ID: ").strip()
    
    try:
        # Test the setup
        checker = PersonalBigQueryDataQualityChecker(project_id=project_id)
        datasets = checker.list_accessible_datasets()
        
        if datasets:
            print(f"\n✅ Setup successful! You have access to {len(datasets)} datasets.")
            return True
        else:
            print(f"\n⚠️ No datasets found. You may need additional permissions.")
            return False
            
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        return False


if __name__ == "__main__":
    setup_personal_authentication()