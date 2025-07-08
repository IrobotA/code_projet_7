# BigQuery Data Quality Checker - FIXES

## Issues Fixed ✅

### 1. Location Issue (FIXED)
**Problem:** 
- Your BigQuery was in `europe-west1` but code was looking in `US`
- Error: `Dataset not found in location US`

**Solution:**
- Set default location to `europe-west1`
- All queries now use `job_config.location = 'europe-west1'`
- Configurable location parameter

### 2. Windows Unicode Issue (FIXED)
**Problem:** 
- Emoji characters (❌) couldn't display in Windows terminal
- Error: `'charmap' codec can't encode character '\u274c'`

**Solution:**
- Added Windows encoding fix
- Removed emoji characters from output
- Windows-compatible logging configuration

## Files

### 🔧 Fixed Files
- `bigquery_personal_auth_fixed.py` - **Use this version**
- `test_bigquery_fixed.py` - Test script for the fixed version

### 📁 Original Files (for reference)
- `bigquery_personal_auth.py` - Original version (has issues)
- `personal_account_example.py` - Original test (has issues)

## Quick Start

### 1. Run the Test Script
```bash
python test_bigquery_fixed.py
```

### 2. Or Use Directly
```python
from bigquery_personal_auth_fixed import PersonalBigQueryDataQualityChecker

# Create checker with correct location
checker = PersonalBigQueryDataQualityChecker(
    project_id="data-platform-dev-448613",
    location="europe-west1"  # Fixed location
)

# List your datasets
datasets = checker.list_accessible_datasets()

# Analyze a table
result = checker.analyze_table_basic("your_dataset", "your_table")

# Generate report
report = checker.generate_simple_report(result)
print(report)
```

## Key Changes Made

### 1. Location Configuration
```python
# OLD (broken)
self.client = bigquery.Client(credentials=credentials, project=project_id)

# NEW (fixed)
self.client = bigquery.Client(
    credentials=credentials, 
    project=project_id,
    location='europe-west1'  # Added location
)

# All queries now use correct location
job_config = bigquery.QueryJobConfig()
job_config.location = self.location
result = self.client.query(query, job_config=job_config)
```

### 2. Windows Unicode Fix
```python
# Fix Windows encoding issues
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Use text instead of emojis
print("[SUCCESS] Connection successful")  # Instead of ✅
print("[ERROR] Connection failed")        # Instead of ❌
```

### 3. Better Error Handling
- Clear error messages for location issues
- Specific help for permission problems
- Windows-compatible logging

## Authentication Setup

Make sure you have:

1. **Google Cloud CLI installed**
   ```bash
   # Download from: https://cloud.google.com/sdk/docs/install
   ```

2. **Authentication completed**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   gcloud config set project data-platform-dev-448613
   gcloud config set compute/region europe-west1
   ```

3. **Required permissions** (contact your admin):
   - BigQuery Data Viewer
   - BigQuery Job User

## Verification

Run this to verify everything works:
```bash
python test_bigquery_fixed.py
```

You should see:
```
[INFO] Connecting to BigQuery...
[INFO] Project: data-platform-dev-448613
[INFO] Location: europe-west1
[SUCCESS] Connection test passed! Found X dataset(s)
[SUCCESS] Connected to BigQuery successfully!
```

## Next Steps

Once the connection works, you can:

1. **Explore your data:**
   ```python
   datasets = checker.list_accessible_datasets()
   tables = checker.list_tables_in_dataset("your_dataset")
   ```

2. **Run data quality checks:**
   ```python
   completeness = checker.quick_completeness_check("dataset", "table")
   uniqueness = checker.quick_uniqueness_check("dataset", "table")
   ```

3. **Generate reports:**
   ```python
   analysis = checker.analyze_table_basic("dataset", "table")
   report = checker.generate_simple_report(analysis)
   print(report)
   ```

## Support

If you still have issues:

1. **Check your permissions** - Make sure you have access to the BigQuery project
2. **Verify authentication** - Run `gcloud auth list` to see active accounts
3. **Check project ID** - Make sure `data-platform-dev-448613` is correct
4. **Test location** - Your BigQuery should be in `europe-west1`

The fixes address both the location and Unicode issues you encountered. Use `bigquery_personal_auth_fixed.py` going forward!