# 🔧 BigQuery Data Quality - Personal Account Setup

**For users who CANNOT create service accounts but have personal access**

## 🎯 Your Situation
You received an error like:
```
Vous avez besoin d'un accès supplémentaire à projet : data-platform-dev
Il est possible que vous ne disposiez pas d'autorisations suffisantes...
```

**This is normal!** Many organizations restrict service account creation to administrators. You can still use the data quality checker with your personal account.

## 🚀 Quick Setup (5 Minutes)

### Step 1: Install Google Cloud CLI
**Download and install from:** https://cloud.google.com/sdk/docs/install

**Verify installation:**
```bash
gcloud --version
```

### Step 2: Authenticate with Your Personal Account
```bash
# Login with your personal Google account
gcloud auth login

# Set up application credentials
gcloud auth application-default login

# Set your project (replace with your actual project ID)
gcloud config set project data-platform-dev
```

### Step 3: Install Python Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:  
source venv/bin/activate

# Install packages
pip install google-cloud-bigquery pandas numpy
```

### Step 4: Test Your Access
```bash
# Download the personal account script
python personal_account_example.py
```

## 🎯 What You Can Do

### ✅ **With Personal Account Access:**
- **Read BigQuery tables** you have access to
- **Run data quality analysis** on any accessible table
- **Generate quality reports** in JSON format
- **Check completeness and uniqueness** efficiently
- **Work in VS Code** with full IntelliSense support

### ❌ **Limitations (vs Service Account):**
- **Project dependent** - only works with projects you have access to
- **Permission dependent** - limited by your assigned roles
- **Manual authentication** - need to re-authenticate periodically

## 📊 Quick Usage Example

```python
from bigquery_personal_auth import PersonalBigQueryDataQualityChecker

# Initialize (no credentials file needed!)
checker = PersonalBigQueryDataQualityChecker(project_id="data-platform-dev")

# See what you have access to
datasets = checker.list_accessible_datasets()

# Analyze a table
report = checker.analyze_table_basic("dataset_name", "table_name")

# View results
print(checker.generate_simple_report(report))
```

## 🛡️ Permission Requirements

### **What You Need from Your Administrator:**
1. **BigQuery Data Viewer** - Read table data and metadata
2. **BigQuery Job User** - Execute queries for analysis

### **How to Request Access:**
**Send this to your project administrator:**

```
Subject: BigQuery Access Request for Data Quality Analysis

Hi [Admin Name],

I need access to run data quality checks on BigQuery tables.

Project: data-platform-dev
User: [your-email@company.com]
Required Roles:
• BigQuery Data Viewer
• BigQuery Job User

Purpose: Data quality analysis and monitoring

Please let me know if you need any additional information.

Thanks!
```

## 🔍 Troubleshooting

### **Error: "Access Denied"**
**Solution:** You need the required BigQuery roles (see above)

### **Error: "Project not found"**
**Solution:** Verify the project ID and your access to it

### **Error: "Could not determine credentials"**
**Solution:** Run the authentication commands again:
```bash
gcloud auth login
gcloud auth application-default login
```

### **Error: "Table not found"**
**Solution:** You may not have access to that specific dataset/table

## 📁 Files for Personal Account Usage

### **Core Files You Need:**
1. **`bigquery_personal_auth.py`** - Personal account data quality checker
2. **`personal_account_example.py`** - Simple interactive example
3. **`.vscode/settings_personal.json`** - VS Code settings for personal auth

### **Quick Start:**
```bash
# Test your connection
python personal_account_example.py

# Choose option 1 for quick test
# Choose option 2 for full analysis
```

## 🎯 VS Code Integration

### **Copy Personal Settings:**
```bash
# Replace the main settings with personal account version
cp .vscode/settings_personal.json .vscode/settings.json
```

### **Update Project ID:**
Edit `.vscode/settings.json` and change:
```json
"GOOGLE_CLOUD_PROJECT": "data-platform-dev"
```

### **Use VS Code:**
1. **Open VS Code** in your project folder
2. **Press F5** to run/debug scripts
3. **Use terminal** to run Python scripts
4. **Explore JSON reports** in VS Code's built-in viewer

## 🎉 You're Ready!

### **What You Can Do Now:**
1. **Analyze any BigQuery table** you have access to
2. **Check data completeness** across all columns
3. **Identify uniqueness issues** and duplicates
4. **Generate automated reports** for data quality monitoring
5. **Work efficiently in VS Code** with full development support

### **Example Workflow:**
1. Run `python personal_account_example.py`
2. Choose your project and dataset
3. Select a table to analyze
4. Review the generated quality report
5. Open the JSON file in VS Code for detailed analysis

**No service account needed - just your personal Google account!** 🚀

---

## 📞 Need More Help?

- **Authentication issues:** Run `gcloud auth login` again
- **Permission issues:** Contact your project administrator
- **Technical issues:** Check the error messages and logs
- **VS Code issues:** Ensure Python extension is installed

**You now have a production-ready BigQuery data quality system using just your personal account!**