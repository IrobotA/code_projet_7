"""
Standalone Demo of Data Quality Checker
Works without database - uses sample data to demonstrate all features
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Simplified version of the DataQualityChecker for demo purposes
class DemoDataQualityChecker:
    """
    Demo version of DataQualityChecker that works with pandas DataFrames
    instead of SQL connections
    """
    
    def __init__(self):
        self.validation_rules = self._get_default_validation_rules()
    
    def _get_default_validation_rules(self):
        """Default validation rules for common data types"""
        return {
            'varchar': {
                'max_length_check': True,
                'pattern_checks': {
                    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                    'phone': r'^\+?[\d\s\-\(\)]{10,}$'
                }
            },
            'numeric': {
                'range_check': True,
                'min_value': -1e10,
                'max_value': 1e10
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
    
    def check_completeness(self, df: pd.DataFrame):
        """Check data completeness (missing values)"""
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
    
    def check_validity_varchar(self, series: pd.Series, max_length: int = 255, pattern: str = None):
        """Validate VARCHAR/TEXT columns"""
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
    
    def check_validity_numeric(self, series: pd.Series, min_value: float = None, max_value: float = None):
        """Validate numeric columns"""
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
    
    def check_validity_datetime(self, series: pd.Series, min_date: str = '1900-01-01', max_date: str = '2100-01-01'):
        """Validate datetime columns"""
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
    
    def check_validity_boolean(self, series: pd.Series):
        """Validate boolean columns"""
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
    
    def check_uniqueness(self, df: pd.DataFrame, columns: list = None):
        """Check data uniqueness"""
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
    
    def analyze_dataframe(self, df: pd.DataFrame, table_name: str = "demo_table"):
        """Perform comprehensive data quality analysis on a DataFrame"""
        print(f"🔍 Starting analysis for: {table_name}")
        
        # Run all checks
        completeness_results = self.check_completeness(df)
        uniqueness_results = self.check_uniqueness(df)
        
        # Auto-detect data types and run validity checks
        validity_results = {}
        for column in df.columns:
            column_dtype = str(df[column].dtype).lower()
            
            if 'object' in column_dtype or 'string' in column_dtype:
                validity_results[column] = self.check_validity_varchar(df[column])
            elif 'int' in column_dtype or 'float' in column_dtype:
                validity_results[column] = self.check_validity_numeric(df[column])
            elif 'datetime' in column_dtype:
                validity_results[column] = self.check_validity_datetime(df[column])
            elif 'bool' in column_dtype:
                validity_results[column] = self.check_validity_boolean(df[column])
            else:
                validity_results[column] = {'note': f'Unsupported data type: {column_dtype}'}
        
        # Compile report
        report = {
            'table_info': {
                'table_name': table_name,
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'analysis_timestamp': datetime.now().isoformat()
            },
            'completeness': completeness_results,
            'validity': validity_results,
            'uniqueness': uniqueness_results
        }
        
        print(f"✅ Analysis completed for: {table_name}")
        return report
    
    def generate_summary_report(self, analysis_result):
        """Generate a human-readable summary report"""
        report = []
        report.append(f"📊 DATA QUALITY REPORT")
        report.append(f"{'='*50}")
        
        # Table info
        info = analysis_result['table_info']
        report.append(f"Table: {info['table_name']}")
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


def create_sample_data():
    """Create sample data with various quality issues for demonstration"""
    np.random.seed(42)  # For reproducible results
    
    # Create sample customer data with intentional quality issues
    n_rows = 1000
    
    data = {
        # ID column - should be unique
        'customer_id': list(range(1, n_rows + 1)) + [999, 999, 998],  # Add some duplicates
        
        # Names - some missing and length issues
        'first_name': ['John', 'Jane', 'Bob', 'Alice'] * (n_rows // 4) + [None] * 20 + ['VeryLongFirstNameThatExceedsTypicalLimits'] * 10,
        
        # Emails - mix of valid and invalid
        'email': (['john.doe@email.com', 'jane.smith@company.org', 'bob@test.co.uk', 'alice.wilson@domain.net'] * (n_rows // 4) + 
                 ['invalid-email', 'missing@', '@domain.com', 'no-at-sign.com'] * 5 + [None] * 30),
        
        # Ages - some out of reasonable range
        'age': (list(np.random.randint(18, 80, n_rows - 50)) + 
                [-5, 150, 999] * 10 + [None] * 20),
        
        # Purchase amounts - some negative values
        'purchase_amount': (list(np.random.uniform(10, 1000, n_rows - 30)) + 
                           [-100, -50] * 10 + [None] * 10),
        
        # Registration dates - some future dates and very old dates
        'registration_date': ([datetime.now() - timedelta(days=int(x)) for x in np.random.randint(1, 365, n_rows - 40)] + 
                             [datetime(1850, 1, 1)] * 10 + 
                             [datetime(2150, 1, 1)] * 10 + 
                             [None] * 20),
        
        # Boolean flags - mix of valid and invalid values
        'is_active': ([True, False] * (n_rows // 2) + 
                     ['yes', 'no', 'maybe', 1, 0] * 6 + [None] * 20),
        
        # Phone numbers - mix of formats
        'phone': (['+1-555-123-4567', '555.987.6543', '(555) 111-2222', '+44 20 7946 0958'] * (n_rows // 4) + 
                 ['123', 'invalid-phone', ''] * 10 + [None] * 40)
    }
    
    # Ensure all lists are the same length
    max_len = max(len(v) for v in data.values())
    for key, values in data.items():
        if len(values) < max_len:
            data[key] = values + [None] * (max_len - len(values))
        elif len(values) > max_len:
            data[key] = values[:max_len]
    
    df = pd.DataFrame(data)
    print(f"📋 Created sample dataset with {len(df)} rows and {len(df.columns)} columns")
    print(f"   Intentionally includes quality issues for demonstration")
    return df


def demonstrate_original_vs_improved():
    """Show comparison between the original problematic approach and the improved version"""
    print("\n" + "="*60)
    print("🔍 COMPARISON: ORIGINAL vs IMPROVED APPROACH")
    print("="*60)
    
    # Create a simple test dataset
    test_data = pd.Series(['abc', 'toolongtext', None, 'xyz', 'waytoolongforthelimitthatwehave'])
    
    print("\n📊 Test Data:", test_data.tolist())
    print("\n❌ ORIGINAL APPROACH PROBLEMS:")
    print("1. Mixed logic: res and isna creates confusing results")
    print("2. Manual loops instead of vectorized operations")
    print("3. Inconsistent return types")
    print("4. Performance issues on large datasets")
    
    print("\n✅ IMPROVED APPROACH BENEFITS:")
    print("1. Clear separation: NULL handling vs validity checking")
    print("2. Vectorized pandas operations for speed")
    print("3. Consistent return format across all functions")
    print("4. Comprehensive metrics and detailed reporting")
    
    # Demonstrate the improved varchar validation
    checker = DemoDataQualityChecker()
    result = checker.check_validity_varchar(test_data, max_length=10)
    
    print(f"\n📈 IMPROVED VALIDATION RESULTS:")
    print(f"   Total values: {result['total_values']}")
    print(f"   Non-null values: {result['non_null_values']}")
    print(f"   Valid count: {result['valid_count']}")
    print(f"   Invalid count: {result['invalid_count']}")
    print(f"   Validity percentage: {result['validity_percentage']}%")
    print(f"   Issues found: {result['issues']}")


def main():
    """Main demonstration function"""
    print("🚀 DATA QUALITY CHECKER DEMONSTRATION")
    print("=====================================")
    
    # Show the comparison first
    demonstrate_original_vs_improved()
    
    print("\n\n🎯 COMPREHENSIVE ANALYSIS DEMONSTRATION")
    print("======================================")
    
    # Create sample data with quality issues
    df = create_sample_data()
    
    # Initialize the checker
    checker = DemoDataQualityChecker()
    
    # Run comprehensive analysis
    print("\n🔍 Running comprehensive data quality analysis...")
    report = checker.analyze_dataframe(df, "customers_demo")
    
    # Generate and display summary
    print("\n📊 SUMMARY REPORT:")
    print(checker.generate_summary_report(report))
    
    # Show detailed results for one column as example
    print("\n🔬 DETAILED ANALYSIS EXAMPLE (email column):")
    print("-" * 50)
    email_completeness = report['completeness']['email']
    email_validity = report['validity']['email']
    email_uniqueness = report['uniqueness']['email']
    
    print(f"Completeness: {email_completeness['completeness_score']}% complete")
    print(f"  - Missing values: {email_completeness['missing_count']:,}")
    
    print(f"Validity: {email_validity['validity_percentage']}% valid")
    print(f"  - Valid emails: {email_validity['valid_count']:,}")
    print(f"  - Invalid emails: {email_validity['invalid_count']:,}")
    if email_validity.get('issues'):
        print(f"  - Issues: {email_validity['issues']}")
    
    print(f"Uniqueness: {email_uniqueness['uniqueness_percentage']}% unique")
    print(f"  - Unique values: {email_uniqueness['unique_count']:,}")
    print(f"  - Duplicates: {email_uniqueness['duplicate_count']:,}")
    
    # Save detailed report to JSON
    try:
        with open('data_quality_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n💾 Detailed report saved to: data_quality_report.json")
    except Exception as e:
        print(f"\n⚠️ Could not save report: {e}")
    
    print("\n✅ DEMONSTRATION COMPLETE!")
    print("\nThis system can automatically:")
    print("✓ Work with any SQL table or DataFrame")
    print("✓ Auto-detect column data types")
    print("✓ Check completeness, validity, and uniqueness")
    print("✓ Generate comprehensive reports")
    print("✓ Handle large datasets efficiently with vectorized operations")
    print("✓ Provide detailed insights for data quality improvement")


if __name__ == "__main__":
    main()