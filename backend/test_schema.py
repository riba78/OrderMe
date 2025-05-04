from app.schemas.admin_manager import AdminManagerCreate
from app.models.admin_manager import VerificationMethod

def test_admin_manager_create():
    try:
        # Test with minimum required fields
        creds = AdminManagerCreate(
            email="test@example.com",
            password="testpass",
            verification_method=VerificationMethod.email
        )
        print(f"Created AdminManagerCreate successfully: {creds}")
        
        # Test dictionary conversion
        creds_dict = creds.dict()
        print(f"Converted to dict: {creds_dict}")
        
        # Test that tin_trunk_number is optional
        assert 'tin_trunk_number' in creds_dict
        assert creds_dict['tin_trunk_number'] is None
        print("The tin_trunk_number field is properly optional")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_admin_manager_create()
    print(f"Test {'passed' if success else 'failed'}") 