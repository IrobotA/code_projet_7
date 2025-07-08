"""
BigQuery Data Quality Checker
Specialized version for Google BigQuery with VS Code integration
"""

import pandas as pd
import numpy as np
from google.cloud import bigquery
from google.oauth2 import service_account
from typing import Dict, List, Optional, Union, Any
import json
import logging
from datetime import datetime
import os
from pathlib import Path

# Configure logging for VS Code
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # For VS Code terminal
        logging.FileHandler('bigquery_quality.log')  # For file logging
    ]
)
logger = logging.getLogger(__name__)

class BigQueryDataQualityChecker:
    """
    BigQuery-specific data quality checker for VS Code development
    Supports completeness, validity, and uniqueness checks
    """
    
    def __init__(self, project_id: str, credentials_path: Optional[str] = None, 
                 location: str = 'US'):
        """
        Initialize BigQuery client
        
        Args:
            project_id: Google Cloud Project ID
            credentials_path: Path to service account JSON file (optional)
            location: BigQuery location/region
        """
        self.project_id = project_id
        self.location = location
        
        # Setup authentication
        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            self.client = bigquery.Client(credentials=credentials, project=project_id)
            logger.info(f"✅ Connected to BigQuery using service account: {credentials_path}")
        else:
            # Use default credentials (gcloud auth application-default login)
            self.client = bigquery.Client(project=project_id)
            logger.info(f"✅ Connected to BigQuery using default credentials")
        
        self.validation_rules = self._get_bigquery_validation_rules()
    
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
            },
            'NUMERIC': {
                'precision_check': True,
                'scale_check': True
            },
            'DATE': {
                'date_range_check': True,
                'min_date': '1900-01-01',
                'max_date': '2100-01-01'
            },
            'DATETIME': {
                'datetime_range_check': True,
                'min_datetime': '1900-01-01 00:00:00',
                'max_datetime': '2100-01-01 00:00:00'
            },
            'TIMESTAMP': {
                'timestamp_range_check': True,
                'min_timestamp': '1900-01-01 00:00:00 UTC',
                'max_timestamp': '2100-01-01 00:00:00 UTC'
            },
            'BOOL': {
                'valid_values': [True, False]
            }
        }
    
    def get_table_schema(self, dataset_id: str, table_id: str) -> Dict:
        """Get BigQuery table schema and metadata"""
        try:
            table_ref = self.client.dataset(dataset_id).table(table_id)
            table = self.client.get_table(table_ref)
            
            schema_info = []
            for field in table.schema:
                schema_info.append({
                    'column_name': field.name,
                    'data_type': field.field_type,
                    'mode': field.mode,  # NULLABLE, REQUIRED, REPEATED
                    'description': field.description or ''
                })
            
            return {
                'project_id': table.project,
                'dataset_id': table.dataset_id,
                'table_id': table.table_id,
                'num_rows': table.num_rows,
                'num_bytes': table.num_bytes,
                'created': table.created.isoformat() if table.created else None,
                'modified': table.modified.isoformat() if table.modified else None,
                'schema': schema_info,
                'total_columns': len(schema_info)
            }
            
        except Exception as e:
            logger.error(f"Error getting table schema: {str(e)}")
            raise
    
    def load_table_sample(self, dataset_id: str, table_id: str, 
                         sample_size: int = 10000, sample_method: str = 'TABLESAMPLE') -> pd.DataFrame:
        """
        Load a sample of BigQuery table data
        
        Args:
            dataset_id: BigQuery dataset ID
            table_id: BigQuery table ID
            sample_size: Number of rows to sample
            sample_method: 'TABLESAMPLE' or 'LIMIT' or 'RANDOM'
        """
        try:
            table_ref = f"`{self.project_id}.{dataset_id}.{table_id}`"
            
            if sample_method == 'TABLESAMPLE':
                # Use BigQuery's TABLESAMPLE for efficient sampling
                query = f"""
                SELECT *
                FROM {table_ref} TABLESAMPLE SYSTEM (10 PERCENT)
                LIMIT {sample_size}
                """
            elif sample_method == 'RANDOM':
                # Random sampling using RAND()
                query = f"""
                SELECT *
                FROM {table_ref}
                WHERE RAND() < 0.1
                LIMIT {sample_size}
                """
            else:
                # Simple LIMIT (fastest but not random)
                query = f"""
                SELECT *
                FROM {table_ref}
                LIMIT {sample_size}
                """
            
            df = self.client.query(query).to_dataframe()
            logger.info(f"✅ Loaded {len(df)} rows from {dataset_id}.{table_id}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading table sample: {str(e)}")
            raise
    
    def check_completeness_bigquery(self, dataset_id: str, table_id: str) -> Dict[str, Any]:
        """
        Check completeness using BigQuery SQL (faster for large tables)
        """
        try:
            table_ref = f"`{self.project_id}.{dataset_id}.{table_id}`"
            
            # Get table schema first
            schema_info = self.get_table_schema(dataset_id, table_id)
            total_rows = schema_info['num_rows']
            
            # Build query to count nulls for all columns
            null_checks = []
            for column in schema_info['schema']:
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
            
            for column in schema_info['schema']:
                col_name = column['column_name']
                null_count = int(result[f'{col_name}_nulls'])
                present_count = actual_total - null_count
                completeness_rate = (present_count / actual_total) * 100 if actual_total > 0 else 0
                
                completeness_results[col_name] = {
                    'total_rows': actual_total,
                    'missing_count': null_count,
                    'present_count': present_count,
                    'completeness_rate': round(completeness_rate, 2),
                    'data_type': column['data_type'],
                    'mode': column['mode']
                }
            
            logger.info(f"✅ Completeness check completed for {dataset_id}.{table_id}")
            return completeness_results
            
        except Exception as e:
            logger.error(f"Error in completeness check: {str(e)}")
            raise
    
    def check_uniqueness_bigquery(self, dataset_id: str, table_id: str, 
                                 columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Check uniqueness using BigQuery SQL (faster for large tables)
        """
        try:
            table_ref = f"`{self.project_id}.{dataset_id}.{table_id}`"
            
            if columns is None:
                schema_info = self.get_table_schema(dataset_id, table_id)
                columns = [col['column_name'] for col in schema_info['schema']]
            
            uniqueness_results = {}
            
            for column in columns:
                query = f"""
                WITH stats AS (
                    SELECT 
                        COUNT(*) as total_rows,
                        COUNT(DISTINCT {column}) as unique_count,
                        COUNT({column}) as non_null_count
                    FROM {table_ref}
                ),
                duplicates AS (
                    SELECT 
                        {column},
                        COUNT(*) as duplicate_count
                    FROM {table_ref}
                    WHERE {column} IS NOT NULL
                    GROUP BY {column}
                    HAVING COUNT(*) > 1
                    ORDER BY duplicate_count DESC
                    LIMIT 10
                )
                SELECT 
                    s.total_rows,
                    s.unique_count,
                    s.non_null_count,
                    s.total_rows - s.unique_count as duplicate_rows,
                    ARRAY_AGG(
                        STRUCT(d.{column} as value, d.duplicate_count as count)
                        ORDER BY d.duplicate_count DESC
                    ) as top_duplicates
                FROM stats s
                LEFT JOIN duplicates d ON TRUE
                GROUP BY s.total_rows, s.unique_count, s.non_null_count
                """
                
                result = self.client.query(query).to_dataframe().iloc[0]
                
                total_rows = int(result['total_rows'])
                unique_count = int(result['unique_count'])
                duplicate_rows = int(result['duplicate_rows'])
                uniqueness_rate = (unique_count / total_rows) * 100 if total_rows > 0 else 0
                
                # Process top duplicates
                top_duplicates = {}
                if result['top_duplicates'] and len(result['top_duplicates']) > 0:
                    for dup in result['top_duplicates'][:5]:  # Top 5 duplicates
                        if dup['value'] is not None:
                            top_duplicates[str(dup['value'])] = int(dup['count'])
                
                uniqueness_results[column] = {
                    'total_rows': total_rows,
                    'unique_count': unique_count,
                    'duplicate_rows': duplicate_rows,
                    'uniqueness_rate': round(uniqueness_rate, 2),
                    'top_duplicates': top_duplicates
                }
            
            logger.info(f"✅ Uniqueness check completed for {dataset_id}.{table_id}")
            return uniqueness_results
            
        except Exception as e:
            logger.error(f"Error in uniqueness check: {str(e)}")
            raise
    
    def check_validity_string_bigquery(self, dataset_id: str, table_id: str, 
                                      column: str, max_length: int = 255,
                                      pattern: Optional[str] = None) -> Dict[str, Any]:
        """
        Check STRING column validity using BigQuery SQL
        """
        try:
            table_ref = f"`{self.project_id}.{dataset_id}.{table_id}`"
            
            # Build validation query
            validations = [f"LENGTH({column}) <= {max_length} as length_valid"]
            
            if pattern:
                validations.append(f"REGEXP_CONTAINS({column}, r'{pattern}') as pattern_valid")
            
            query = f"""
            SELECT 
                COUNT(*) as total_rows,
                COUNT({column}) as non_null_count,
                COUNTIF({' AND '.join(validations.copy())}) as valid_count,
                COUNTIF(LENGTH({column}) > {max_length}) as length_invalid_count
            """ + (f", COUNTIF(NOT REGEXP_CONTAINS({column}, r'{pattern}')) as pattern_invalid_count" if pattern else "") + f"""
            FROM {table_ref}
            WHERE {column} IS NOT NULL
            """
            
            result = self.client.query(query).to_dataframe().iloc[0]
            
            total_rows = int(result['total_rows'])
            non_null_count = int(result['non_null_count'])
            valid_count = int(result['valid_count'])
            invalid_count = non_null_count - valid_count
            validity_rate = (valid_count / non_null_count) * 100 if non_null_count > 0 else 0
            
            issues = []
            if result['length_invalid_count'] > 0:
                issues.append(f"Length > {max_length}: {result['length_invalid_count']} rows")
            if pattern and result.get('pattern_invalid_count', 0) > 0:
                issues.append(f"Pattern mismatch: {result['pattern_invalid_count']} rows")
            
            return {
                'total_values': total_rows,
                'non_null_values': non_null_count,
                'valid_count': valid_count,
                'invalid_count': invalid_count,
                'validity_rate': round(validity_rate, 2),
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"Error in string validity check: {str(e)}")
            raise
    
    def analyze_table_bigquery(self, dataset_id: str, table_id: str,
                              include_sample: bool = True, sample_size: int = 10000) -> Dict[str, Any]:
        """
        Comprehensive BigQuery table analysis
        """
        logger.info(f"🔍 Starting analysis for {dataset_id}.{table_id}")
        
        try:
            # Get table metadata
            schema_info = self.get_table_schema(dataset_id, table_id)
            
            # Run completeness check (uses BigQuery SQL)
            completeness_results = self.check_completeness_bigquery(dataset_id, table_id)
            
            # Run uniqueness check (uses BigQuery SQL)
            uniqueness_results = self.check_uniqueness_bigquery(dataset_id, table_id)
            
            # Load sample for detailed analysis if requested
            sample_df = None
            validity_results = {}
            
            if include_sample and schema_info['num_rows'] > 0:
                sample_df = self.load_table_sample(dataset_id, table_id, sample_size)
                
                # Run validity checks on sample
                for column_info in schema_info['schema']:
                    col_name = column_info['column_name']
                    col_type = column_info['data_type']
                    
                    if col_name in sample_df.columns:
                        if col_type == 'STRING':
                            validity_results[col_name] = self._check_validity_string_sample(
                                sample_df[col_name], col_name
                            )
                        elif col_type in ['INT64', 'FLOAT64', 'NUMERIC']:
                            validity_results[col_name] = self._check_validity_numeric_sample(
                                sample_df[col_name], col_type
                            )
                        elif col_type in ['DATE', 'DATETIME', 'TIMESTAMP']:
                            validity_results[col_name] = self._check_validity_datetime_sample(
                                sample_df[col_name], col_type
                            )
            
            # Compile report
            report = {
                'table_info': {
                    'project_id': self.project_id,
                    'dataset_id': dataset_id,
                    'table_id': table_id,
                    'full_table_id': f"{self.project_id}.{dataset_id}.{table_id}",
                    'analysis_timestamp': datetime.now().isoformat(),
                    'sample_size': sample_size if include_sample else 0
                },
                'schema': schema_info,
                'completeness': completeness_results,
                'uniqueness': uniqueness_results,
                'validity': validity_results
            }
            
            logger.info(f"✅ Analysis completed for {dataset_id}.{table_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error in table analysis: {str(e)}")
            raise
    
    def _check_validity_string_sample(self, series: pd.Series, column_name: str) -> Dict[str, Any]:
        """Helper: Check string validity on pandas sample"""
        non_null_data = series.dropna()
        if len(non_null_data) == 0:
            return {'note': 'No non-null values in sample'}
        
        # Basic checks
        max_length = non_null_data.str.len().max()
        avg_length = non_null_data.str.len().mean()
        empty_count = (non_null_data == '').sum()
        
        return {
            'sample_size': len(series),
            'non_null_count': len(non_null_data),
            'max_length': int(max_length) if pd.notna(max_length) else 0,
            'avg_length': round(avg_length, 2) if pd.notna(avg_length) else 0,
            'empty_strings': int(empty_count),
            'note': 'Sample-based analysis'
        }
    
    def _check_validity_numeric_sample(self, series: pd.Series, data_type: str) -> Dict[str, Any]:
        """Helper: Check numeric validity on pandas sample"""
        non_null_data = series.dropna()
        if len(non_null_data) == 0:
            return {'note': 'No non-null values in sample'}
        
        return {
            'sample_size': len(series),
            'non_null_count': len(non_null_data),
            'min_value': float(non_null_data.min()),
            'max_value': float(non_null_data.max()),
            'mean_value': float(non_null_data.mean()),
            'data_type': data_type,
            'note': 'Sample-based analysis'
        }
    
    def _check_validity_datetime_sample(self, series: pd.Series, data_type: str) -> Dict[str, Any]:
        """Helper: Check datetime validity on pandas sample"""
        non_null_data = series.dropna()
        if len(non_null_data) == 0:
            return {'note': 'No non-null values in sample'}
        
        return {
            'sample_size': len(series),
            'non_null_count': len(non_null_data),
            'min_date': str(non_null_data.min()),
            'max_date': str(non_null_data.max()),
            'data_type': data_type,
            'note': 'Sample-based analysis'
        }
    
    def generate_summary_report(self, analysis_result: Dict) -> str:
        """Generate VS Code friendly summary report"""
        report = []
        report.append("📊 BIGQUERY DATA QUALITY REPORT")
        report.append("=" * 60)
        
        # Table info
        info = analysis_result['table_info']
        schema = analysis_result['schema']
        
        report.append(f"🏷️  Table: {info['full_table_id']}")
        report.append(f"📊 Rows: {schema['num_rows']:,}")
        report.append(f"📋 Columns: {schema['total_columns']}")
        report.append(f"💾 Size: {schema['num_bytes']:,} bytes")
        report.append(f"🕐 Analysis: {info['analysis_timestamp']}")
        report.append("")
        
        # Completeness summary
        completeness = analysis_result['completeness']
        report.append("🔍 COMPLETENESS SUMMARY")
        report.append("-" * 40)
        
        for col, metrics in completeness.items():
            status = "✅" if metrics['completeness_rate'] >= 95 else "⚠️" if metrics['completeness_rate'] >= 80 else "❌"
            report.append(f"{status} {col}: {metrics['completeness_rate']:.1f}% complete ({metrics['missing_count']:,} missing)")
        
        report.append("")
        
        # Uniqueness summary
        uniqueness = analysis_result['uniqueness']
        report.append("🔑 UNIQUENESS SUMMARY")
        report.append("-" * 40)
        
        for col, metrics in uniqueness.items():
            status = "✅" if metrics['uniqueness_rate'] >= 95 else "⚠️" if metrics['uniqueness_rate'] >= 80 else "❌"
            report.append(f"{status} {col}: {metrics['uniqueness_rate']:.1f}% unique ({metrics['duplicate_rows']:,} duplicates)")
        
        report.append("")
        
        # Validity summary (if available)
        if analysis_result.get('validity'):
            validity = analysis_result['validity']
            report.append("✅ VALIDITY SUMMARY (Sample)")
            report.append("-" * 40)
            
            for col, metrics in validity.items():
                if 'note' not in metrics:
                    report.append(f"📋 {col}: {metrics}")
        
        return "\n".join(report)
    
    def save_report_to_file(self, analysis_result: Dict, output_path: str = None) -> str:
        """Save report to JSON file for VS Code inspection"""
        if output_path is None:
            table_info = analysis_result['table_info']
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"bigquery_quality_report_{table_info['dataset_id']}_{table_info['table_id']}_{timestamp}.json"
        
        try:
            with open(output_path, 'w') as f:
                json.dump(analysis_result, f, indent=2, default=str)
            logger.info(f"💾 Report saved to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving report: {str(e)}")
            raise


# VS Code helper functions
def setup_bigquery_credentials():
    """Helper function to setup BigQuery credentials in VS Code"""
    print("🔧 BIGQUERY CREDENTIALS SETUP")
    print("=" * 40)
    print("Choose your authentication method:")
    print("1. Service Account JSON file")
    print("2. Default Application Credentials (gcloud)")
    print()
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        print("\n📝 Using Service Account JSON:")
        print("1. Go to Google Cloud Console > IAM & Admin > Service Accounts")
        print("2. Create a new service account or select existing")
        print("3. Grant BigQuery permissions (BigQuery Data Viewer, BigQuery Job User)")
        print("4. Create and download JSON key file")
        print("5. Save the JSON file in your VS Code workspace")
        print()
        
        credentials_path = input("Enter path to JSON file (or press Enter to skip): ").strip()
        return credentials_path if credentials_path else None
    
    elif choice == "2":
        print("\n🔑 Using Default Credentials:")
        print("Run this command in VS Code terminal:")
        print("gcloud auth application-default login")
        print()
        return None
    
    else:
        print("❌ Invalid choice")
        return None


def create_bigquery_checker_example():
    """Example function for VS Code testing"""
    print("🚀 BIGQUERY DATA QUALITY CHECKER EXAMPLE")
    print("=" * 50)
    
    # Get credentials
    credentials_path = setup_bigquery_credentials()
    
    # Get project details
    project_id = input("\nEnter your Google Cloud Project ID: ").strip()
    dataset_id = input("Enter BigQuery Dataset ID: ").strip()
    table_id = input("Enter BigQuery Table ID: ").strip()
    
    try:
        # Initialize checker
        checker = BigQueryDataQualityChecker(
            project_id=project_id,
            credentials_path=credentials_path
        )
        
        # Run analysis
        print(f"\n🔍 Analyzing {project_id}.{dataset_id}.{table_id}...")
        report = checker.analyze_table_bigquery(dataset_id, table_id)
        
        # Display summary
        print("\n" + checker.generate_summary_report(report))
        
        # Save detailed report
        output_file = checker.save_report_to_file(report)
        print(f"\n💾 Detailed report saved to: {output_file}")
        print("📂 Open this file in VS Code to explore the complete analysis!")
        
        return checker, report
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("💡 Check your credentials and table access permissions")
        return None, None


if __name__ == "__main__":
    # Run example when script is executed directly in VS Code
    create_bigquery_checker_example()