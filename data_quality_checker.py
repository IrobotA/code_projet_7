"""
Data Quality Checker for SQL Tables
Checks completeness, validity, and uniqueness for any table automatically
"""

import pandas as pd
import numpy as np
import sqlalchemy as sa
from typing import Dict, List, Optional, Union, Any
from collections import Counter
import re
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataQualityChecker:
    """
    Comprehensive data quality checker for SQL tables
    Supports completeness, validity, and uniqueness checks
    """
    
    def __init__(self, connection: Union[str, sa.engine.Engine]):
        """
        Initialize with database connection
        
        Args:
            connection: SQLAlchemy connection string or engine
        """
        if isinstance(connection, str):
            self.engine = sa.create_engine(connection)
        else:
            self.engine = connection
        
        self.validation_rules = self._get_default_validation_rules()
    
    def _get_default_validation_rules(self) -> Dict:
        """Default validation rules for common SQL data types"""
        return {
            'varchar': {
                'max_length_check': True,
                'pattern_checks': {
                    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                    'phone': r'^\+?[\d\s\-\(\)]{10,}$'
                }
            },
            'bigint': {
                'range_check': True,
                'min_value': -9223372036854775808,
                'max_value': 9223372036854775807
            },
            'int': {
                'range_check': True,
                'min_value': -2147483648,
                'max_value': 2147483647
            },
            'real': {
                'range_check': True,
                'min_value': -3.4028235e+38,
                'max_value': 3.4028235e+38
            },
            'datetime': {
                'date_range_check': True,
                'min_date': '1900-01-01',
                'max_date': '2100-01-01'
            },
            'boolean': {
                'valid_values': [True, False, 1, 0, 'true', 'false', 'TRUE', 'FALSE']
            }
        }
    
    def load_table_data(self, table_name: str, schema: Optional[str] = None, 
                       sample_size: Optional[int] = None) -> pd.DataFrame:
        """
        Load table data from SQL database
        
        Args:
            table_name: Name of the table
            schema: Schema name (optional)
            sample_size: Number of rows to sample (optional)
            
        Returns:
            DataFrame with the table data
        """
        try:
            table_ref = f"{schema}.{table_name}" if schema else table_name
            
            if sample_size:
                query = f"SELECT * FROM {table_ref} TABLESAMPLE SYSTEM (10) LIMIT {sample_size}"
            else:
                query = f"SELECT * FROM {table_ref}"
            
            df = pd.read_sql(query, self.engine)
            logger.info(f"Loaded {len(df)} rows from {table_ref}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading table {table_name}: {str(e)}")
            raise
    
    def get_table_info(self, table_name: str, schema: Optional[str] = None) -> Dict:
        """Get table metadata including column types"""
        try:
            table_ref = f"{schema}.{table_name}" if schema else table_name
            
            # Get column information
            query = f"""
            SELECT column_name, data_type, is_nullable, character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            """ + (f" AND table_schema = '{schema}'" if schema else "")
            
            columns_info = pd.read_sql(query, self.engine)
            
            return {
                'columns': columns_info.to_dict('records'),
                'total_columns': len(columns_info)
            }
            
        except Exception as e:
            logger.warning(f"Could not get table metadata: {str(e)}")
            return {'columns': [], 'total_columns': 0}
    
    # ── COMPLETENESS CHECKS ──
    def check_completeness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Check data completeness (missing values)
        
        Returns:
            Dictionary with completeness metrics for each column
        """
        results = {}
        total_rows = len(df)
        
        for column in df.columns:
            missing_count = df[column].isnull().sum()
            missing_percentage = (missing_count / total_rows) * 100
            
            results[column] = {
                'total_rows': total_rows,
                'missing_count': missing_count,
                'missing_percentage': round(missing_percentage, 2),
                'completeness_score': round(100 - missing_percentage, 2)
            }
        
        return results
    
    # ── VALIDITY CHECKS ──
    def check_validity_varchar(self, series: pd.Series, max_length: int = 255,
                              pattern: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate VARCHAR/TEXT columns
        
        Args:
            series: Pandas Series to validate
            max_length: Maximum allowed length
            pattern: Regex pattern for validation (optional)
            
        Returns:
            Dictionary with validity metrics
        """
        # Handle missing values separately
        non_null_data = series.dropna()
        total_non_null = len(non_null_data)
        
        if total_non_null == 0:
            return {
                'total_values': len(series),
                'valid_count': 0,
                'invalid_count': 0,
                'validity_percentage': 100.0,
                'issues': ['All values are NULL']
            }
        
        # Length validation (vectorized)
        length_valid = non_null_data.str.len() <= max_length
        
        # Pattern validation if provided
        pattern_valid = pd.Series([True] * total_non_null, index=non_null_data.index)
        if pattern:
            pattern_valid = non_null_data.str.match(pattern, na=False)
        
        # Combine validations
        all_valid = length_valid & pattern_valid
        valid_count = all_valid.sum()
        invalid_count = total_non_null - valid_count
        
        issues = []
        if not length_valid.all():
            issues.append(f"Length > {max_length}")
        if pattern and not pattern_valid.all():
            issues.append(f"Pattern mismatch: {pattern}")
        
        return {
            'total_values': len(series),
            'non_null_values': total_non_null,
            'valid_count': valid_count,
            'invalid_count': invalid_count,
            'validity_percentage': round((valid_count / total_non_null) * 100, 2),
            'issues': issues
        }
    
    def check_validity_numeric(self, series: pd.Series, min_value: Optional[float] = None,
                              max_value: Optional[float] = None) -> Dict[str, Any]:
        """
        Validate numeric columns (INT, BIGINT, REAL, etc.)
        
        Args:
            series: Pandas Series to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            Dictionary with validity metrics
        """
        # Handle missing values separately
        non_null_data = series.dropna()
        total_non_null = len(non_null_data)
        
        if total_non_null == 0:
            return {
                'total_values': len(series),
                'valid_count': 0,
                'invalid_count': 0,
                'validity_percentage': 100.0,
                'issues': ['All values are NULL']
            }
        
        # Range validation (vectorized)
        valid_mask = pd.Series([True] * total_non_null, index=non_null_data.index)
        
        if min_value is not None:
            valid_mask &= (non_null_data >= min_value)
        if max_value is not None:
            valid_mask &= (non_null_data <= max_value)
        
        valid_count = valid_mask.sum()
        invalid_count = total_non_null - valid_count
        
        issues = []
        if min_value is not None and (non_null_data < min_value).any():
            issues.append(f"Values < {min_value}")
        if max_value is not None and (non_null_data > max_value).any():
            issues.append(f"Values > {max_value}")
        
        return {
            'total_values': len(series),
            'non_null_values': total_non_null,
            'valid_count': valid_count,
            'invalid_count': invalid_count,
            'validity_percentage': round((valid_count / total_non_null) * 100, 2),
            'issues': issues
        }
    
    def check_validity_datetime(self, series: pd.Series, min_date: str = '1900-01-01',
                               max_date: str = '2100-01-01') -> Dict[str, Any]:
        """
        Validate datetime columns
        
        Args:
            series: Pandas Series to validate
            min_date: Minimum allowed date (ISO format)
            max_date: Maximum allowed date (ISO format)
            
        Returns:
            Dictionary with validity metrics
        """
        # Convert to datetime if not already
        try:
            if not pd.api.types.is_datetime64_any_dtype(series):
                datetime_series = pd.to_datetime(series, errors='coerce')
            else:
                datetime_series = series
        except Exception:
            return {
                'total_values': len(series),
                'valid_count': 0,
                'invalid_count': len(series),
                'validity_percentage': 0.0,
                'issues': ['Cannot convert to datetime']
            }
        
        # Handle missing values
        non_null_data = datetime_series.dropna()
        total_non_null = len(non_null_data)
        
        if total_non_null == 0:
            return {
                'total_values': len(series),
                'valid_count': 0,
                'invalid_count': 0,
                'validity_percentage': 100.0,
                'issues': ['All values are NULL or invalid dates']
            }
        
        # Date range validation
        min_dt = pd.to_datetime(min_date)
        max_dt = pd.to_datetime(max_date)
        
        valid_mask = (non_null_data >= min_dt) & (non_null_data <= max_dt)
        valid_count = valid_mask.sum()
        invalid_count = total_non_null - valid_count
        
        issues = []
        if (non_null_data < min_dt).any():
            issues.append(f"Dates before {min_date}")
        if (non_null_data > max_dt).any():
            issues.append(f"Dates after {max_date}")
        
        return {
            'total_values': len(series),
            'non_null_values': total_non_null,
            'valid_count': valid_count,
            'invalid_count': invalid_count,
            'validity_percentage': round((valid_count / total_non_null) * 100, 2),
            'issues': issues
        }
    
    def check_validity_boolean(self, series: pd.Series) -> Dict[str, Any]:
        """
        Validate boolean columns
        
        Args:
            series: Pandas Series to validate
            
        Returns:
            Dictionary with validity metrics
        """
        valid_values = {True, False, 1, 0, '1', '0', 'true', 'false', 'TRUE', 'FALSE'}
        
        non_null_data = series.dropna()
        total_non_null = len(non_null_data)
        
        if total_non_null == 0:
            return {
                'total_values': len(series),
                'valid_count': 0,
                'invalid_count': 0,
                'validity_percentage': 100.0,
                'unique_values': [],
                'issues': ['All values are NULL']
            }
        
        # Check if values are in valid set
        valid_mask = non_null_data.isin(valid_values)
        valid_count = valid_mask.sum()
        invalid_count = total_non_null - valid_count
        
        unique_values = non_null_data.unique().tolist()
        invalid_values = [v for v in unique_values if v not in valid_values]
        
        issues = []
        if invalid_values:
            issues.append(f"Invalid boolean values: {invalid_values}")
        
        return {
            'total_values': len(series),
            'non_null_values': total_non_null,
            'valid_count': valid_count,
            'invalid_count': invalid_count,
            'validity_percentage': round((valid_count / total_non_null) * 100, 2),
            'unique_values': unique_values,
            'issues': issues
        }
    
    # ── UNIQUENESS CHECKS ──
    def check_uniqueness(self, df: pd.DataFrame, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Check data uniqueness
        
        Args:
            df: DataFrame to analyze
            columns: List of columns to check (if None, checks all columns)
            
        Returns:
            Dictionary with uniqueness metrics
        """
        if columns is None:
            columns = df.columns.tolist()
        
        results = {}
        
        for column in columns:
            total_rows = len(df)
            unique_count = df[column].nunique(dropna=False)
            duplicate_count = total_rows - unique_count
            uniqueness_percentage = (unique_count / total_rows) * 100 if total_rows > 0 else 100
            
            # Find duplicate values
            duplicates = df[df.duplicated(subset=[column], keep=False)][column].value_counts()
            top_duplicates = duplicates.head(5).to_dict()
            
            results[column] = {
                'total_rows': total_rows,
                'unique_count': unique_count,
                'duplicate_count': duplicate_count,
                'uniqueness_percentage': round(uniqueness_percentage, 2),
                'top_duplicates': top_duplicates
            }
        
        return results
    
    # ── MAIN ANALYSIS FUNCTION ──
    def analyze_table(self, table_name: str, schema: Optional[str] = None,
                     sample_size: Optional[int] = None, 
                     custom_rules: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Perform comprehensive data quality analysis on a table
        
        Args:
            table_name: Name of the table to analyze
            schema: Schema name (optional)
            sample_size: Number of rows to sample (optional)
            custom_rules: Custom validation rules (optional)
            
        Returns:
            Complete data quality report
        """
        logger.info(f"Starting analysis for table: {table_name}")
        
        # Load data
        df = self.load_table_data(table_name, schema, sample_size)
        table_info = self.get_table_info(table_name, schema)
        
        # Merge custom rules if provided
        rules = self.validation_rules.copy()
        if custom_rules:
            rules.update(custom_rules)
        
        # Run all checks
        completeness_results = self.check_completeness(df)
        uniqueness_results = self.check_uniqueness(df)
        
        # Validity checks (auto-detect data types)
        validity_results = {}
        for column in df.columns:
            column_dtype = str(df[column].dtype).lower()
            
            if 'object' in column_dtype or 'string' in column_dtype:
                validity_results[column] = self.check_validity_varchar(df[column])
            elif 'int' in column_dtype:
                validity_results[column] = self.check_validity_numeric(df[column])
            elif 'float' in column_dtype:
                validity_results[column] = self.check_validity_numeric(df[column])
            elif 'datetime' in column_dtype:
                validity_results[column] = self.check_validity_datetime(df[column])
            elif 'bool' in column_dtype:
                validity_results[column] = self.check_validity_boolean(df[column])
            else:
                validity_results[column] = {'note': f'Unsupported data type: {column_dtype}'}
        
        # Compile final report
        report = {
            'table_info': {
                'table_name': table_name,
                'schema': schema,
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'analysis_timestamp': datetime.now().isoformat(),
                'sample_size': sample_size
            },
            'metadata': table_info,
            'completeness': completeness_results,
            'validity': validity_results,
            'uniqueness': uniqueness_results
        }
        
        logger.info(f"Analysis completed for table: {table_name}")
        return report
    
    def generate_summary_report(self, analysis_result: Dict) -> str:
        """
        Generate a human-readable summary report
        
        Args:
            analysis_result: Result from analyze_table()
            
        Returns:
            Formatted summary string
        """
        report = []
        report.append(f"📊 DATA QUALITY REPORT")
        report.append(f"{'='*50}")
        
        # Table info
        info = analysis_result['table_info']
        report.append(f"Table: {info['table_name']}")
        if info['schema']:
            report.append(f"Schema: {info['schema']}")
        report.append(f"Rows: {info['total_rows']:,}")
        report.append(f"Columns: {info['total_columns']}")
        report.append(f"Analysis Time: {info['analysis_timestamp']}")
        report.append("")
        
        # Completeness summary
        completeness = analysis_result['completeness']
        report.append("🔍 COMPLETENESS SUMMARY")
        report.append("-" * 30)
        
        for col, metrics in completeness.items():
            status = "✅" if metrics['missing_percentage'] < 5 else "⚠️" if metrics['missing_percentage'] < 20 else "❌"
            report.append(f"{status} {col}: {metrics['completeness_score']:.1f}% complete")
        
        report.append("")
        
        # Validity summary
        validity = analysis_result['validity']
        report.append("✅ VALIDITY SUMMARY")
        report.append("-" * 30)
        
        for col, metrics in validity.items():
            if 'validity_percentage' in metrics:
                status = "✅" if metrics['validity_percentage'] > 95 else "⚠️" if metrics['validity_percentage'] > 80 else "❌"
                report.append(f"{status} {col}: {metrics['validity_percentage']:.1f}% valid")
                if metrics.get('issues'):
                    for issue in metrics['issues']:
                        report.append(f"    ⚠️  {issue}")
        
        report.append("")
        
        # Uniqueness summary
        uniqueness = analysis_result['uniqueness']
        report.append("🔑 UNIQUENESS SUMMARY")
        report.append("-" * 30)
        
        for col, metrics in uniqueness.items():
            status = "✅" if metrics['uniqueness_percentage'] > 95 else "⚠️" if metrics['uniqueness_percentage'] > 80 else "❌"
            report.append(f"{status} {col}: {metrics['uniqueness_percentage']:.1f}% unique")
            if metrics['duplicate_count'] > 0:
                report.append(f"    📊 {metrics['duplicate_count']} duplicates found")
        
        return "\n".join(report)