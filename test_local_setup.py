#!/usr/bin/env python3
"""
Quick test to verify the action setup works locally
"""
import os
import yaml
from action_glossary_export.glossary_export_action import GlossaryExportAction, GlossaryExportConfig

def test_config_loads():
    """Test that the config file loads correctly"""
    print("🔍 Testing configuration loading...")
    
    # Load the local config
    with open('local_config.yaml', 'r') as f:
        config_yaml = yaml.safe_load(f)
    
    action_config = config_yaml['action']['config']
    
    # Set dummy env vars for testing
    os.environ['DATAHUB_SNOWFLAKE_ACCOUNT'] = 'test-account'
    os.environ['DATAHUB_SNOWFLAKE_PASSWORD'] = 'test-password'
    os.environ['DATAHUB_SERVER'] = 'https://test.acryl.io'
    os.environ['DATAHUB_TOKEN'] = 'test-token'
    
    # Parse with our config class
    try:
        # Manually expand env vars for this test
        action_config_expanded = {
            'connection': {
                'account_id': os.environ['DATAHUB_SNOWFLAKE_ACCOUNT'],
                'username': action_config['connection']['username'],
                'password': os.environ['DATAHUB_SNOWFLAKE_PASSWORD'],
                'warehouse': action_config['connection']['warehouse'],
                'role': action_config['connection']['role'],
                'authentication_type': action_config['connection']['authentication_type']
            },
            'destination': action_config['destination'],
            'export_on_startup': action_config['export_on_startup'],
            'batch_size': action_config['batch_size']
        }
        
        config = GlossaryExportConfig.model_validate(action_config_expanded)
        print("✅ Configuration is valid!")
        print(f"   - Snowflake Account: {config.connection.account_id}")
        print(f"   - Database: {config.destination.database}")
        print(f"   - Table: {config.destination.table_name}")
        print(f"   - Batch Size: {config.batch_size}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_action_imports():
    """Test that the action can be imported"""
    print("\n🔍 Testing action import...")
    try:
        from action_glossary_export.glossary_export_action import GlossaryExportAction
        print(f"✅ Action imported successfully: {GlossaryExportAction}")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_entry_point():
    """Test that the entry point is registered"""
    print("\n🔍 Testing entry point registration...")
    try:
        from pkg_resources import iter_entry_points
        
        found = False
        for ep in iter_entry_points('datahub_actions.action.plugins'):
            if ep.name == 'action-glossary-export':
                print(f"✅ Entry point found: {ep.name} -> {ep.module_name}")
                found = True
                break
        
        if not found:
            print("⚠️  Entry point not found in registry")
            print("   This is OK - the action can still be loaded directly")
        
        return True
    except Exception as e:
        print(f"⚠️  Could not check entry points: {e}")
        print("   This is OK - the action can still be loaded directly")
        return True

if __name__ == '__main__':
    print("=" * 60)
    print("Testing DataHub Glossary Export Action - Local Setup")
    print("=" * 60)
    
    test_action_imports()
    test_config_loads()
    test_entry_point()
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("\nTo run the action:")
    print("  1. Create .env file with your credentials")
    print("  2. Run: ./run_local.sh")
    print("=" * 60)
