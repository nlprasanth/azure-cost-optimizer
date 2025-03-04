import os
import sys
import unittest
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from optimizers.vm.optimizer import VMOptimizer

class TestVMOptimizer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        load_dotenv()
        cls.subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
        cls.resource_group = os.getenv('TEST_RESOURCE_GROUP')
        cls.vm_name = os.getenv('TEST_VM_NAME')
        
        if not all([cls.subscription_id, cls.resource_group, cls.vm_name]):
            raise ValueError("Missing required environment variables")
        
        cls.optimizer = VMOptimizer(cls.subscription_id)

    def test_vm_optimization(self):
        """Test VM optimization for a single VM."""
        result = self.optimizer.optimize_vm(self.resource_group, self.vm_name)
        
        # Verify result structure
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['vm_name'], self.vm_name)
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
            self.assertIn('estimated_savings', rec)

    def test_resource_group_optimization(self):
        """Test VM optimization for a resource group."""
        result = self.optimizer.optimize_resource_group(self.resource_group)
        
        # Verify result structure
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['resource_group'], self.resource_group)
        self.assertIn('vm_count', result)
        self.assertIn('results', result)
        
        # Verify results for each VM
        for vm_result in result['results']:
            self.assertIn('status', vm_result)
            self.assertIn('vm_name', vm_result)
            self.assertIn('recommendations', vm_result)

    def test_subscription_optimization(self):
        """Test VM optimization for entire subscription."""
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

if __name__ == '__main__':
    unittest.main()
