# 🚀 BigQuery Data Quality Checker - VS Code Setup Guide

Complete setup guide for using the BigQuery Data Quality Checker in Visual Studio Code.

## 📋 Prerequisites

### Required Software
- **Python 3.8+** installed
- **Visual Studio Code** with extensions:
  - Python (Microsoft)
  - Jupyter (Microsoft) 
  - SQLTools (optional, for SQL editing)
  - Python Docstring Generator (optional)

### Google Cloud Requirements
- **Google Cloud Project** with BigQuery enabled
- **BigQuery API** enabled in your project
- **Service Account** with appropriate permissions OR default credentials

## 🛠️ Step-by-Step Setup

### 1. Clone/Download the Project
```bash
# Create project directory
mkdir bigquery-data-quality
cd bigquery-data-quality

# Copy all the files we created:
# - bigquery_data_quality.py
# - test_bigquery_connection.py  
# - analyze_table.py
# - requirements_bigquery.txt
# - .vscode/settings.json
# - .vscode/launch.json
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements_bigquery.txt
```

### 3. Configure Google Cloud Authentication

#### Option A: Service Account (Recommended for Production)
1. **Create Service Account:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to `IAM & Admin > Service Accounts`
   - Click `Create Service Account`
   - Name: `bigquery-data-quality`

2. **Grant Permissions:**
   - `BigQuery Data Viewer` - Read table data
   - `BigQuery Job User` - Run queries
   - `BigQuery Metadata Viewer` - Access table schemas

3. **Create JSON Key:**
   - Click on your service account
   - Go to `Keys` tab
   - Click `Add Key > Create New Key`
   - Choose `JSON` format
   - Download the file

4. **Set Up Credentials in VS Code:**
   ```bash
   # Create credentials directory
   mkdir credentials
   
   # Copy your downloaded JSON file to:
   credentials/bigquery-service-account.json
   ```

#### Option B: Default Application Credentials (Development)
```bash
# Install Google Cloud CLI
# Then authenticate:
gcloud auth application-default login
```

### 4. Configure Environment Variables

Create `.env` file in project root:
```env
# .env file
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=./credentials/bigquery-service-account.json
```

Or set environment variables in VS Code:
- Open VS Code
- `Ctrl+Shift+P` → "Python: Select Interpreter"
- Choose your virtual environment

## 🚀 Quick Start in VS Code

### 1. Test Your Connection
```python
# Run test_bigquery_connection.py
python test_bigquery_connection.py
```

**Expected Output:**
```
🔍 TESTING BIGQUERY CONNECTION
========================================
📋 Project ID: your-project-id
🔑 Credentials: ./credentials/bigquery-service-account.json
✅ Connection successful!
📂 Available datasets:
   1. dataset1
   2. dataset2
   ...
```

### 2. Analyze a Table
```python
# Run analyze_table.py
python analyze_table.py
```

**Or use VS Code Debugger:**
1. Press `F5`
2. Select "Run Quality Analysis on Specific Table"
3. Enter your table details when prompted

## 📊 Using the Data Quality Checker

### Basic Usage Example
```python
from bigquery_data_quality import BigQueryDataQualityChecker

# Initialize
checker = BigQueryDataQualityChecker(
    project_id="your-project-id",
    credentials_path="./credentials/bigquery-service-account.json"
)

# Analyze a table
report = checker.analyze_table_bigquery(
    dataset_id="your_dataset",
    table_id="your_table"
)

# Generate summary
print(checker.generate_summary_report(report))

# Save detailed report
checker.save_report_to_file(report, "quality_report.json")
```

### Advanced Usage
```python
# Large table with sampling
report = checker.analyze_table_bigquery(
    dataset_id="big_dataset",
    table_id="huge_table", 
    include_sample=True,
    sample_size=50000
)

# Quick completeness check only
completeness = checker.check_completeness_bigquery("dataset", "table")

# Uniqueness check only
uniqueness = checker.check_uniqueness_bigquery("dataset", "table")

# String validation with pattern
validity = checker.check_validity_string_bigquery(
    "dataset", "table", "email_column",
    max_length=100,
    pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)
```

## 🔧 VS Code Development Features

### Debugging
1. **Set Breakpoints** - Click left margin in code
2. **Press F5** - Start debugging
3. **Choose Configuration** - Select appropriate launch config
4. **Step Through Code** - Use F10/F11 for debugging

### Running Specific Functions
- **Ctrl+Shift+P** → "Python: Run Selection/Line in Python Terminal"
- Select code and press **Shift+Enter**

### Jupyter Integration
- **Open `.ipynb` files** directly in VS Code
- **Run cells** with `Ctrl+Enter`
- **Add new cells** with `A` (above) or `B` (below)

### IntelliSense & Code Completion
- **Auto-completion** - Type and see suggestions
- **Documentation** - Hover over functions
- **Go to Definition** - F12 on function names

## 📈 Performance Optimization

### For Large Tables (>1M rows)
```python
# Use sampling for faster analysis
checker.analyze_table_bigquery(
    dataset_id="big_dataset",
    table_id="big_table",
    sample_size=10000  # Adjust based on table size
)

# Or use SQL-only checks (fastest)
completeness = checker.check_completeness_bigquery(dataset, table)
uniqueness = checker.check_uniqueness_bigquery(dataset, table)
```

### Query Optimization
- **Use TABLESAMPLE** for random sampling
- **Limit columns** in analysis if needed
- **Run during off-peak hours** for large tables

## 🛡️ Security Best Practices

### Credentials Security
```bash
# Add to .gitignore
echo "credentials/" >> .gitignore
echo ".env" >> .gitignore
echo "*.json" >> .gitignore
```

### IAM Permissions (Minimal)
- `BigQuery Data Viewer` - Read access only
- `BigQuery Job User` - Query execution only
- Avoid `BigQuery Admin` unless necessary

### Network Security
- **Use Private Google Access** for compute instances
- **Restrict service account keys** to specific IPs if possible
- **Rotate service account keys** regularly

## 🐛 Troubleshooting

### Common Issues

#### 1. Authentication Errors
```
❌ Connection failed: Could not automatically determine credentials
```
**Solutions:**
- Check `GOOGLE_APPLICATION_CREDENTIALS` path
- Verify JSON key file exists and is valid
- Try `gcloud auth application-default login`

#### 2. Permission Errors
```
❌ Access Denied: BigQuery BigQuery: Permission denied while getting Drive credentials
```
**Solutions:**
- Grant `BigQuery Data Viewer` role
- Grant `BigQuery Job User` role
- Check project-level permissions

#### 3. Table Not Found
```
❌ Not found: Table project:dataset.table
```
**Solutions:**
- Verify table exists: `project.dataset.table`
- Check spelling and case sensitivity
- Ensure you have access to the dataset

#### 4. Large Table Timeouts
```
❌ Query timeout exceeded
```
**Solutions:**
- Use smaller sample sizes
- Use `quick_completeness_check()` instead
- Run during off-peak hours

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug logging
checker = BigQueryDataQualityChecker(project_id="...", debug=True)
```

## 📚 VS Code Extensions for Enhanced Experience

### Recommended Extensions
1. **Python** (ms-python.python) - Core Python support
2. **Jupyter** (ms-toolsai.jupyter) - Notebook support
3. **SQLTools** (mtxr.sqltools) - SQL editing and querying
4. **BigQuery** (GoogleCloudPlatform.bigquery) - BigQuery integration
5. **GitLens** (eamodio.gitlens) - Git integration
6. **Python Docstring Generator** (njpwerner.autodocstring) - Auto-generate docstrings

### Optional Extensions
- **Black Formatter** (ms-python.black-formatter) - Code formatting
- **Pylint** (ms-python.pylint) - Code linting
- **Python Test Explorer** (LittleFoxTeam.vscode-python-test-adapter) - Test running

## 🎯 Example Workflows

### Daily Quality Monitoring
```python
# Create monitoring script
tables_to_monitor = [
    ("dataset1", "important_table1"),
    ("dataset1", "important_table2"),
    ("dataset2", "user_events"),
]

for dataset, table in tables_to_monitor:
    report = checker.analyze_table_bigquery(dataset, table)
    # Check thresholds and send alerts if needed
```

### Data Pipeline Validation
```python
# Validate new data loads
def validate_daily_load(date_partition):
    report = checker.analyze_table_bigquery(
        "data_warehouse", 
        f"daily_events${date_partition}"
    )
    
    # Check quality metrics
    completeness = report['completeness']
    if any(m['completeness_rate'] < 95 for m in completeness.values()):
        raise Exception("Data quality below threshold")
```

## 📖 Additional Resources

- **BigQuery Documentation:** https://cloud.google.com/bigquery/docs
- **Google Cloud Python Client:** https://googleapis.dev/python/bigquery/latest/
- **VS Code Python Tutorial:** https://code.visualstudio.com/docs/python/python-tutorial
- **VS Code Jupyter Guide:** https://code.visualstudio.com/docs/datascience/jupyter-notebooks

---

## 🎉 You're Ready!

Your BigQuery Data Quality Checker is now fully configured for VS Code development! 

**Next Steps:**
1. Test your connection with `test_bigquery_connection.py`
2. Run analysis on a sample table with `analyze_table.py`
3. Explore the generated JSON reports in VS Code
4. Customize validation rules for your specific use cases
5. Set up automated quality monitoring for your data pipelines