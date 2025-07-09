#!/usr/bin/env python3
"""
Debug Toolkit - Practical debugging utilities
Use this to quickly diagnose common issues
"""

import sys
import os
import subprocess
import traceback
from datetime import datetime
import json

class DebugToolkit:
    """Collection of debugging utilities"""
    
    def __init__(self):
        self.results = {}
        self.start_time = datetime.now()
    
    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "="*60)
        print(f" {title}")
        print("="*60)
    
    def print_section(self, title):
        """Print formatted section header"""
        print(f"\n--- {title} ---")
    
    def check_python_environment(self):
        """Check Python environment details"""
        self.print_section("PYTHON ENVIRONMENT")
        
        env_info = {
            'python_version': sys.version,
            'python_executable': sys.executable,
            'platform': sys.platform,
            'current_directory': os.getcwd(),
            'python_path': sys.path[:3]  # First 3 entries
        }
        
        for key, value in env_info.items():
            print(f"  {key}: {value}")
        
        self.results['python_environment'] = env_info
        return env_info
    
    def check_required_packages(self, packages=None):
        """Check if required packages are installed"""
        self.print_section("PACKAGE CHECK")
        
        if packages is None:
            packages = [
                'google-cloud-bigquery',
                'pandas', 
                'numpy',
                'requests',
                'jupyter'
            ]
        
        package_status = {}
        
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                                  capture_output=True, text=True)
            installed_packages = result.stdout.lower()
            
            for package in packages:
                is_installed = package.lower() in installed_packages
                status = "✅" if is_installed else "❌"
                print(f"  {status} {package}")
                package_status[package] = is_installed
                
        except Exception as e:
            print(f"  ❌ Error checking packages: {e}")
            package_status = {pkg: False for pkg in packages}
        
        self.results['packages'] = package_status
        return package_status
    
    def check_authentication(self):
        """Check Google Cloud authentication"""
        self.print_section("AUTHENTICATION CHECK")
        
        auth_info = {
            'gcloud_available': False,
            'active_account': None,
            'default_project': None,
            'application_default_credentials': False
        }
        
        # Check if gcloud is available
        try:
            result = subprocess.run(['gcloud', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                auth_info['gcloud_available'] = True
                print("  ✅ Google Cloud CLI available")
            else:
                print("  ❌ Google Cloud CLI not available")
                
        except FileNotFoundError:
            print("  ❌ Google Cloud CLI not found")
        
        # Check active account
        if auth_info['gcloud_available']:
            try:
                result = subprocess.run(['gcloud', 'auth', 'list'], 
                                      capture_output=True, text=True)
                
                if 'ACTIVE' in result.stdout:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'ACTIVE' in line:
                            auth_info['active_account'] = line.split()[0]
                            print(f"  ✅ Active account: {auth_info['active_account']}")
                            break
                else:
                    print("  ❌ No active authentication")
                    
            except Exception as e:
                print(f"  ❌ Error checking auth: {e}")
        
        # Check default project
        if auth_info['gcloud_available']:
            try:
                result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                      capture_output=True, text=True)
                
                project = result.stdout.strip()
                if project and project != '(unset)':
                    auth_info['default_project'] = project
                    print(f"  ✅ Default project: {project}")
                else:
                    print("  ❌ No default project set")
                    
            except Exception as e:
                print(f"  ❌ Error checking project: {e}")
        
        # Check application default credentials
        try:
            from google.auth import default
            credentials, project = default()
            auth_info['application_default_credentials'] = True
            print(f"  ✅ Application default credentials: {project}")
            
        except Exception as e:
            print(f"  ❌ Application default credentials: {e}")
        
        self.results['authentication'] = auth_info
        return auth_info
    
    def check_connectivity(self):
        """Check network connectivity"""
        self.print_section("CONNECTIVITY CHECK")
        
        connectivity = {
            'internet': False,
            'google_cloud': False,
            'bigquery_api': False
        }
        
        # Test internet connectivity
        try:
            import requests
            response = requests.get('https://www.google.com', timeout=10)
            if response.status_code == 200:
                connectivity['internet'] = True
                print("  ✅ Internet connectivity")
            else:
                print(f"  ❌ Internet issue: Status {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Internet connectivity: {e}")
        
        # Test Google Cloud connectivity
        if connectivity['internet']:
            try:
                response = requests.get('https://cloud.google.com', timeout=10)
                if response.status_code == 200:
                    connectivity['google_cloud'] = True
                    print("  ✅ Google Cloud reachable")
                else:
                    print(f"  ❌ Google Cloud issue: Status {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Google Cloud connectivity: {e}")
        
        # Test BigQuery API (if authenticated)
        if connectivity['google_cloud'] and self.results.get('authentication', {}).get('application_default_credentials'):
            try:
                from google.cloud import bigquery
                client = bigquery.Client()
                
                # Simple query test
                query = "SELECT 1 as test"
                result = client.query(query).result()
                
                connectivity['bigquery_api'] = True
                print("  ✅ BigQuery API accessible")
                
            except Exception as e:
                print(f"  ❌ BigQuery API: {e}")
        
        self.results['connectivity'] = connectivity
        return connectivity
    
    def check_environment_variables(self):
        """Check important environment variables"""
        self.print_section("ENVIRONMENT VARIABLES")
        
        important_vars = [
            'GOOGLE_APPLICATION_CREDENTIALS',
            'GOOGLE_CLOUD_PROJECT',
            'GOOGLE_CLOUD_REGION',
            'PATH',
            'PYTHONPATH',
            'HOME',
            'USER'
        ]
        
        env_vars = {}
        
        for var in important_vars:
            value = os.environ.get(var)
            if value:
                # Truncate long values
                display_value = value[:50] + "..." if len(value) > 50 else value
                print(f"  ✅ {var}: {display_value}")
                env_vars[var] = value
            else:
                print(f"  ❌ {var}: Not set")
                env_vars[var] = None
        
        self.results['environment_variables'] = env_vars
        return env_vars
    
    def test_bigquery_basic(self, project_id=None):
        """Test basic BigQuery functionality"""
        self.print_section("BIGQUERY BASIC TEST")
        
        test_results = {
            'client_creation': False,
            'simple_query': False,
            'dataset_listing': False,
            'project_id': project_id
        }
        
        try:
            from google.cloud import bigquery
            
            # Create client
            if project_id:
                client = bigquery.Client(project=project_id)
            else:
                client = bigquery.Client()
            
            test_results['client_creation'] = True
            print("  ✅ BigQuery client created")
            
            # Test simple query
            query = "SELECT 1 as test_value, 'hello' as test_string"
            result = client.query(query).result()
            
            # Verify result
            rows = list(result)
            if len(rows) == 1 and rows[0]['test_value'] == 1:
                test_results['simple_query'] = True
                print("  ✅ Simple query successful")
            else:
                print("  ❌ Simple query returned unexpected results")
            
            # Test dataset listing
            datasets = list(client.list_datasets())
            test_results['dataset_listing'] = True
            print(f"  ✅ Dataset listing successful ({len(datasets)} datasets found)")
            
        except Exception as e:
            print(f"  ❌ BigQuery test failed: {e}")
            print(f"      Error type: {type(e).__name__}")
        
        self.results['bigquery_test'] = test_results
        return test_results
    
    def quick_diagnosis(self):
        """Run quick diagnosis of common issues"""
        self.print_header("QUICK DIAGNOSIS")
        
        issues = []
        suggestions = []
        
        # Check results
        if not self.results.get('connectivity', {}).get('internet'):
            issues.append("No internet connectivity")
            suggestions.append("Check your network connection")
        
        if not self.results.get('authentication', {}).get('gcloud_available'):
            issues.append("Google Cloud CLI not available")
            suggestions.append("Install Google Cloud CLI: https://cloud.google.com/sdk/docs/install")
        
        if not self.results.get('authentication', {}).get('active_account'):
            issues.append("No active Google Cloud authentication")
            suggestions.append("Run: gcloud auth login")
        
        if not self.results.get('authentication', {}).get('application_default_credentials'):
            issues.append("No application default credentials")
            suggestions.append("Run: gcloud auth application-default login")
        
        packages = self.results.get('packages', {})
        missing_packages = [pkg for pkg, installed in packages.items() if not installed]
        if missing_packages:
            issues.append(f"Missing packages: {', '.join(missing_packages)}")
            suggestions.append(f"Install: pip install {' '.join(missing_packages)}")
        
        # Print diagnosis
        if issues:
            print("\n🚨 ISSUES FOUND:")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
            
            print("\n💡 SUGGESTIONS:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
        else:
            print("\n✅ No obvious issues found!")
            print("   Your environment appears to be properly configured.")
        
        return issues, suggestions
    
    def generate_report(self):
        """Generate comprehensive debug report"""
        self.print_header("DEBUG REPORT SUMMARY")
        
        duration = datetime.now() - self.start_time
        
        print(f"Debug session completed in {duration.total_seconds():.1f} seconds")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        # Save detailed report
        report_file = f"debug_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'duration_seconds': duration.total_seconds(),
                    'results': self.results
                }, f, indent=2, default=str)
            
            print(f"Detailed report saved to: {report_file}")
            
        except Exception as e:
            print(f"Could not save report: {e}")
        
        return self.results


def run_full_diagnosis(project_id=None):
    """Run complete diagnosis"""
    toolkit = DebugToolkit()
    
    toolkit.print_header("COMPREHENSIVE DEBUG TOOLKIT")
    print(f"Starting diagnosis at {datetime.now()}")
    
    # Run all checks
    toolkit.check_python_environment()
    toolkit.check_required_packages()
    toolkit.check_environment_variables()
    toolkit.check_authentication()
    toolkit.check_connectivity()
    
    if project_id:
        toolkit.test_bigquery_basic(project_id)
    
    # Generate diagnosis
    toolkit.quick_diagnosis()
    toolkit.generate_report()
    
    return toolkit.results


def quick_auth_check():
    """Quick authentication check"""
    print("=== QUICK AUTH CHECK ===")
    
    try:
        result = subprocess.run(['gcloud', 'auth', 'list'], 
                              capture_output=True, text=True)
        
        if 'ACTIVE' in result.stdout:
            print("✅ Authentication active")
            
            lines = result.stdout.split('\n')
            for line in lines:
                if 'ACTIVE' in line:
                    print(f"   Account: {line.split()[0]}")
                    break
        else:
            print("❌ No active authentication")
            print("   Run: gcloud auth login")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def quick_bigquery_test(project_id):
    """Quick BigQuery connectivity test"""
    print("=== QUICK BIGQUERY TEST ===")
    
    try:
        from google.cloud import bigquery
        
        client = bigquery.Client(project=project_id)
        query = "SELECT 1 as test"
        result = client.query(query).result()
        
        print("✅ BigQuery connection successful")
        return True
        
    except Exception as e:
        print(f"❌ BigQuery test failed: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Debug Toolkit")
    parser.add_argument('--project', help='BigQuery project ID to test')
    parser.add_argument('--quick-auth', action='store_true', help='Quick auth check only')
    parser.add_argument('--quick-bq', help='Quick BigQuery test with project ID')
    
    args = parser.parse_args()
    
    if args.quick_auth:
        quick_auth_check()
    elif args.quick_bq:
        quick_bigquery_test(args.quick_bq)
    else:
        run_full_diagnosis(args.project)