# Database Migration Updates Guide

This document outlines the necessary updates to the codebase following the database migration to the new schema. The updates are organized by component and include explanations of why each change is required.

## Backend Updates

### Models

1. **`models/user.py`**
   - **Why Update?**: Enhanced user management, verification, and security features
   - **Changes Made**:
     - Added composite indexes for search and verification
     - Added proper foreign key constraints with `ondelete` rules
     - Enhanced `UserRole` enum with `SYSTEM` role
     - Added `VerificationMethod` enum
     - Added verification tracking fields
     - Added audit fields (created_at, updated_at)
     - Added relationship tracking (created_by)
     - Added proper nullable constraints
     - Added metadata fields for extensibility

2. **`models/customer.py`**
   - **Why Update?**: Enhanced customer management and payment handling
   - **Changes Made**:
     - Added composite indexes for search and assignment
     - Enhanced `PaymentMethod` model with additional fields
     - Enhanced `PaymentInfo` model with detailed billing fields
     - Added proper foreign key constraints with `ondelete` rules
     - Added metadata fields for extensibility
     - Added search optimization fields
     - Added assignment tracking
     - Added proper nullable constraints

3. **`models/activity_log.py`**
   - **Why Create?**: Track user actions with efficient data management
   - **Features Implemented**:
     - Range partitioning by created_at
     - Composite primary key for partitioning
     - Proper indexing for performance
     - Metadata fields for extensibility
     - IP address and user agent tracking
     - Proper foreign key constraints
     - Proper nullable constraints

4. **`models/verification_message_log.py`**
   - **Why Create?**: Track verification attempts with efficient data management
   - **Features Implemented**:
     - Range partitioning by created_at
     - Composite primary key for partitioning
     - Proper indexing for performance
     - Provider information tracking
     - Status tracking
     - Error message tracking
     - Metadata fields for extensibility

### Database Schema Changes

1. **Partitioned Tables**:
   - `activity_logs`: Range partitioning by created_at
   - `verification_messages_log`: Range partitioning by created_at
   - Optimized for efficient data cleanup and archival
   - Enhanced query performance for date-based searches

2. **Indexing Strategy**:
   - Composite indexes for frequently used queries
   - Search optimization indexes
   - Foreign key indexes
   - Verification status indexes
   - Assignment tracking indexes

3. **Data Integrity**:
   - Proper foreign key constraints with appropriate ondelete rules
   - NOT NULL constraints where appropriate
   - Unique constraints for critical fields
   - Default values for required fields

4. **Extensibility**:
   - JSON metadata fields for future extensions
   - Search vector fields for text search
   - Computed fields for optimization

### Required Code Updates

1. **Authentication System**:
   ```python
   # Update token generation to include verification status
   def create_access_token(user_id: int) -> str:
       user = User.query.get(user_id)
       return jwt.encode({
           'sub': str(user_id),
           'role': str(user.role),
           'is_verified': user.is_verified,
           'exp': datetime.utcnow() + timedelta(days=1)
       }, settings.SECRET_KEY)
   ```

2. **User Management**:
   ```python
   # Example of creating a new user with verification
   def create_user(email: str, password: str, role: UserRole) -> User:
       user = User(
           uuid=str(uuid.uuid4()),
           email=email,
           role=role,
           created_as_role=UserRole.SYSTEM
       )
       user.set_password(password)
       user.profile = UserProfile()
       return user
   ```

3. **Activity Logging**:
   ```python
   # Example of logging user activity
   def log_user_activity(user_id: int, action: str, entity_type: str, 
                        entity_id: int, request: Request) -> None:
       ActivityLog.log_activity(
           user_id=user_id,
           action_type=action,
           entity_type=entity_type,
           entity_id=entity_id,
           ip_address=request.remote_addr,
           user_agent=request.user_agent.string
       )
   ```

### Migration Steps

1. **Database Setup**:
   ```sql
   -- Enable partitioning
   SET GLOBAL innodb_file_per_table=1;
   SET GLOBAL innodb_file_format=Barracuda;
   ```

2. **Create Partitioned Tables**:
   ```sql
   -- Example for activity_logs
   CREATE TABLE activity_logs (
       id INT,
       created_at DATETIME,
       -- other fields
       PRIMARY KEY (id, created_at)
   ) PARTITION BY RANGE (TO_DAYS(created_at)) (
       PARTITION p_current VALUES LESS THAN (TO_DAYS(NOW())),
       PARTITION p_future VALUES LESS THAN MAXVALUE
   );
   ```

3. **Data Migration**:
   ```python
   # Example of migrating user data
   def migrate_user_data():
       for user in legacy_users.find():
           new_user = User(
               uuid=str(uuid.uuid4()),
               email=user['email'],
               role=UserRole.coerce(user['role']),
               is_verified=user.get('verified', False)
           )
           db.session.add(new_user)
   ```

### Testing Requirements

1. **Database Tests**:
   - Verify partitioning functionality
   - Test foreign key constraints
   - Validate indexes
   - Check data integrity

2. **Model Tests**:
   - Test relationship cascades
   - Verify computed fields
   - Test data serialization
   - Validate business logic

3. **Integration Tests**:
   - Test authentication flow
   - Verify activity logging
   - Test verification process
   - Validate customer management

### Deployment Considerations

1. **Database Configuration**:
   - Enable partitioning support
   - Configure proper character sets
   - Set appropriate buffer pool size
   - Enable performance schema

2. **Backup Strategy**:
   - Implement partition-aware backups
   - Set up point-in-time recovery
   - Configure binary logging
   - Implement backup rotation

3. **Monitoring Setup**:
   - Monitor partition usage
   - Track index performance
   - Monitor foreign key operations
   - Track verification attempts

### Next Steps

1. **Critical Updates** (Immediate):
   - Implement partitioned tables
   - Update indexes
   - Migrate existing data
   - Update authentication

2. **High Priority** (Within Week):
   - Implement activity logging
   - Update verification system
   - Enhance customer management
   - Update search functionality

3. **Medium Priority** (Within Two Weeks):
   - Implement monitoring
   - Enhance backup system
   - Update documentation
   - Add performance optimizations

4. **Low Priority** (Within Month):
   - Add advanced features
   - Enhance reporting
   - Optimize queries
   - Add analytics

## Frontend Updates

### Views

1. **`views/auth/SignUp.vue`**
   - **Why Update?**: Support for multiple verification methods
   - **Changes Required**:
     - Add verification method selection
     - Update form validation
     - Add verification status display

2. **`views/auth/Verify.vue`**
   - **Why Update?**: Multi-method verification support
   - **Changes Required**:
     - Update verification flow
     - Add method-specific verification UI
     - Add verification status tracking

3. **`views/user/UserDashboard.vue`**
   - **Why Update?**: New activity logging feature
   - **Changes Required**:
     - Add activity log display
     - Update user statistics
     - Add verification status display

4. **`views/user/UserProfile.vue`**
   - **Why Update?**: Enhanced profile management
   - **Changes Required**:
     - Add business information fields
     - Update form validation
     - Add verification method management

5. **`views/customer/CustomerList.vue`**
   - **Why Update?**: Improved search functionality
   - **Changes Required**:
     - Update search to use new computed fields
     - Add assignment status display
     - Update filtering options

6. **`views/customer/CustomerForm.vue`**
   - **Why Update?**: New customer fields
   - **Changes Required**:
     - Add new field inputs
     - Update form validation
     - Add computed address display

### Components

1. **New Component: `components/VerificationMethodSelector.vue`**
   - **Why Create?**: Reusable verification method selection
   - **Required Features**:
     - Method selection UI
     - Validation
     - Status display

2. **New Component: `components/ActivityLog.vue`**
   - **Why Create?**: Reusable activity log display
   - **Required Features**:
     - Log entry display
     - Filtering
     - Pagination

3. **Update: `components/CustomerSearch.vue`**
   - **Why Update?**: Enhanced search functionality
   - **Changes Required**:
     - Update search to use new computed fields
     - Add advanced filtering
     - Improve search results display

### Store

1. **`store/auth.js`**
   - **Why Update?**: Enhanced authentication state
   - **Changes Required**:
     - Add verification method state
     - Update token handling
     - Add verification status tracking

2. **`store/user.js`**
   - **Why Update?**: Enhanced user management
   - **Changes Required**:
     - Add activity logging
     - Update user state
     - Add verification method management

3. **`store/customer.js`**
   - **Why Update?**: Enhanced customer management
   - **Changes Required**:
     - Update customer state
     - Add assignment tracking
     - Update search functionality

### API

1. **`api/auth.js`**
   - **Why Update?**: New authentication endpoints
   - **Changes Required**:
     - Add verification method endpoints
     - Update token endpoints
     - Add verification status endpoints

2. **`api/user.js`**
   - **Why Update?**: Enhanced user management
   - **Changes Required**:
     - Add activity logging endpoints
     - Update user management endpoints
     - Add verification method endpoints

3. **`api/customer.js`**
   - **Why Update?**: Enhanced customer management
   - **Changes Required**:
     - Update customer endpoints
     - Add assignment endpoints
     - Update search endpoints

### Types

1. **`types/user.ts`**
   - **Why Update?**: New user fields and types
   - **Changes Required**:
     - Add new field types
     - Add verification method types
     - Update role types

2. **`types/customer.ts`**
   - **Why Update?**: New customer fields and types
   - **Changes Required**:
     - Add new field types
     - Add assignment types
     - Update search types

## Implementation Priority

1. **Critical Updates** (Must be done immediately after migration):
   - Backend models
   - Authentication updates
   - Basic user management

2. **High Priority** (Should be done within first week):
   - Customer management updates
   - Verification system
   - Activity logging

3. **Medium Priority** (Can be done within two weeks):
   - Frontend UI updates
   - Search functionality
   - Profile management

4. **Low Priority** (Can be done within a month):
   - Enhanced features
   - UI improvements
   - Performance optimizations

## Testing Requirements

1. **Database Tests**:
   - Verify all new tables and fields
   - Test constraints and relationships
   - Validate computed fields

2. **API Tests**:
   - Test all new endpoints
   - Verify authentication flow
   - Test rate limiting

3. **UI Tests**:
   - Test new forms and fields
   - Verify search functionality
   - Test activity logging

4. **Integration Tests**:
   - Test complete user flows
   - Verify data consistency
   - Test error handling 