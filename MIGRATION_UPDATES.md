# Database Migration Updates Guide

This document outlines the necessary updates to the codebase following the database migration to the new schema. The updates are organized by component and include explanations of why each change is required.

## Backend Updates

### Models

1. **`models/user.py`**
   - **Why Update?**: New fields and relationships added to support enhanced user management and verification
   - **Changes Required**:
     - Add `primary_verification_method` field
     - Add `created_as_role` field
     - Add relationship with `user_verification_methods`
     - Update role validation
     - Add verification status tracking

2. **`models/customer.py`**
   - **Why Update?**: New computed fields and relationships for improved customer management
   - **Changes Required**:
     - Add `shipping_address` computed field
     - Add `search_vector` computed field
     - Add relationships with `assigned_to` and `last_assigned_by`
     - Update validation rules

3. **`models/user_profile.py`**
   - **Why Update?**: New fields for enhanced profile management
   - **Changes Required**:
     - Add `search_vector` computed field
     - Add business information fields
     - Update validation rules

4. **New Models to Create**:
   - **`models/activity_log.py`**
     - **Why Create?**: New table for tracking user actions
     - **Required Fields**:
       - `user_id`
       - `action_type`
       - `entity_type`
       - `entity_id`
       - `metadata`
       - `ip_address`
       - `user_agent`

   - **`models/verification_message_log.py`**
     - **Why Create?**: New table for tracking verification attempts
     - **Required Fields**:
       - `user_id`
       - `method_type`
       - `message_type`
       - `identifier`
       - `status`
       - `provider`
       - `provider_message_id`

### Routes

1. **`routes/auth.py`**
   - **Why Update?**: Support for multiple verification methods
   - **Changes Required**:
     - Update registration endpoint to handle multiple verification methods
     - Add verification method selection
     - Implement verification message logging
     - Update token generation and validation

2. **`routes/user.py`**
   - **Why Update?**: Enhanced user management features
   - **Changes Required**:
     - Update user creation to track `created_as_role`
     - Add verification method management endpoints
     - Implement activity logging
     - Update user search functionality

3. **`routes/customer.py`**
   - **Why Update?**: Improved customer management and search
   - **Changes Required**:
     - Update customer creation with new fields
     - Implement customer assignment tracking
     - Add search functionality using computed fields
     - Update customer update endpoints

### Configuration

1. **`config.py`**
   - **Why Update?**: New configuration options needed
   - **Changes Required**:
     - Add verification method settings
     - Add rate limiting configuration
     - Add activity logging settings
     - Update database configuration

2. **`.env`**
   - **Why Update?**: New environment variables needed
   - **Changes Required**:
     - Add `VERIFICATION_METHODS`
     - Add `RATE_LIMIT_ATTEMPTS`
     - Add `RATE_LIMIT_WINDOW`
     - Add `ACTIVITY_LOG_ENABLED`

### Authentication

1. **`auth.py`**
   - **Why Update?**: Enhanced authentication flow
   - **Changes Required**:
     - Update token generation to include verification status
     - Add verification method validation
     - Implement rate limiting
     - Add activity tracking

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