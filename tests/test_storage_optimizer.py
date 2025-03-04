import os
import sys
import unittest
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from optimizers.storage.optimizer import StorageOptimizer

class TestStorageOptimizer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        load_dotenv()
        cls.subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
        cls.resource_group = os.getenv('TEST_RESOURCE_GROUP')
        cls.storage_account = os.getenv('TEST_STORAGE_ACCOUNT')
        
        if not all([cls.subscription_id, cls.resource_group, cls.storage_account]):
            raise ValueError("Missing required environment variables")
        
        cls.optimizer = StorageOptimizer(cls.subscription_id)

    def test_storage_account_optimization(self):
        """Test storage optimization for a single account."""
        result = self.optimizer.optimize_storage_account(
            self.resource_group,
            self.storage_account
        )
        
        # Verify result structure
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['account_name'], self.storage_account)
        self.assertEqual(result['resource_group'], self.resource_group)
        
        # Verify analysis data
        self.assertIn('analysis', result)
        self.assertIn('metrics', result['analysis'])
        self.assertIn('recommendations', result)
        
        # Verify recommendations
        self.assertIsInstance(result['recommendations'], list)
        if result['recommendations']:
            rec = result['recommendations'][0]
            self.assertIn('type', rec)
            self.assertIn('action', rec)
            self.assertIn('impact', rec)
            self.assertIn('description', rec)

    def test_resource_group_optimization(self):
        """Test storage optimization for a resource group."""
        result = self.optimizer.optimize_resource_group(self.resource_group)
        
        # Verify result structure
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['resource_group'], self.resource_group)
        self.assertIn('account_count', result)
        self.assertIn('results', result)
        
        # Verify results for each storage account
        for account_result in result['results']:
            self.assertIn('status', account_result)
            self.assertIn('account_name', account_result)
            self.assertIn('recommendations', account_result)

    def test_subscription_optimization(self):
        """Test storage optimization for entire subscription."""
        result = self.optimizer.optimize_subscription()
        
        # Verify result structure
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['subscription_id'], self.subscription_id)
        self.assertIn('resource_group_count', result)
        self.assertIn('results', result)
        
        # Verify results for each resource group
        for rg_result in result['results']:
            self.assertIn('status', rg_result)
            self.assertIn('resource_group', rg_result)
            self.assertIn('results', rg_result)

    def test_optimization_summary(self):
        """Test optimization summary generation."""
        # First get optimization results
        result = self.optimizer.optimize_storage_account(
            self.resource_group,
            self.storage_account
        )
        
        # Generate summary
        summary = self.optimizer.get_optimization_summary(result)
        
        # Verify summary structure
        self.assertIn('total_accounts_analyzed', summary)
        self.assertIn('accounts_with_recommendations', summary)
        self.assertIn('total_recommendations', summary)
        self.assertIn('recommendation_types', summary)
        self.assertIn('potential_savings', summary)
        self.assertIn('high_impact_recommendations', summary)

if __name__ == '__main__':
    unittest.main()
