#!/usr/bin/env python
"""
Test script to verify the merge was successful and all modules work correctly.
"""
import sys
import traceback

def test_imports():
    """Test that all key modules can be imported successfully."""
    print("=" * 60)
    print("Testing imports after merge...")
    print("=" * 60)
    
    tests = [
        ("addtask_interfaces", "API_Layer.interfaces.addtask_interfaces", None),
        ("addtask_routes", "API_Layer.routes.addtask_routes", None),
        ("addtask_service", "Business_Layer.services.addtask_service", None),
        ("addtask_dao", "DAL.dao.addtask_dao", None),
        ("EmployeeTasks model", "DAL.models.models", "EmployeeTasks"),
        ("offer_approval_action_routes", "API_Layer.routes.offer_approval_action_routes", "router"),
        ("offer_approval_action_service", "Business_Layer.services.offer_approval_action_service", None),
        ("Database models", "DAL.models.models", None),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, module_path, attr_name in tests:
        try:
            module = __import__(module_path, fromlist=[attr_name] if attr_name else [])
            if attr_name:
                getattr(module, attr_name)
            print(f"✓ {test_name:<40} - OK")
            passed += 1
        except Exception as e:
            print(f"✗ {test_name:<40} - FAILED")
            print(f"  Error: {str(e)}")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    return failed == 0

def test_syntax():
    """Verify syntax of key files."""
    print("\nVerifying Python syntax of modified files...")
    print("=" * 60)
    
    import py_compile
    import os
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    files = [
        "main.py",
        "API_Layer/routes/offer_approval_action_routes.py",
        "API_Layer/interfaces/addtask_interfaces.py",
        "API_Layer/routes/addtask_routes.py",
        "Business_Layer/services/addtask_service.py",
        "DAL/dao/addtask_dao.py",
        "DAL/models/models.py",
    ]
    
    passed = 0
    failed = 0
    
    for file_path in files:
        full_path = os.path.join(base_path, file_path)
        try:
            py_compile.compile(full_path, doraise=True)
            print(f"✓ {file_path:<60} - OK")
            passed += 1
        except py_compile.PyCompileError as e:
            print(f"✗ {file_path:<60} - FAILED")
            print(f"  Error: {str(e)}")
            failed += 1
    
    print("=" * 60)
    print(f"Syntax check results: {passed} passed, {failed} failed")
    print("=" * 60)
    return failed == 0

if __name__ == "__main__":
    syntax_ok = test_syntax()
    imports_ok = test_imports()
    
    print("\n" + "=" * 60)
    if syntax_ok and imports_ok:
        print("✓ All tests PASSED! Merge was successful.")
        sys.exit(0)
    else:
        print("✗ Some tests FAILED! Please review the errors above.")
        sys.exit(1)
