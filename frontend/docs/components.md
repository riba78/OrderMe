# OrderMe Frontend Components Documentation

## Core Components

### UserManagement
The UserManagement component provides an interface for administrators to manage system users.

**Features:**
- View all users in a table format
- Create new users
- Edit existing user details
- Delete users
- Toggle user active status
- Role-based user management (ADMIN, USER, CUSTOMER)

**Props:**
None

**Events:**
None

**Usage:**
```vue
<template>
  <UserManagement />
</template>
```

### CustomerManagement
The CustomerManagement component allows users to manage customer accounts and their status.

**Features:**
- View all customers in a table format
- Search customers
- Add new customers
- Edit customer details
- Toggle customer active status
- View customer creation date

**Props:**
None

**Events:**
None

**Usage:**
```vue
<template>
  <CustomerManagement />
</template>
```

### OrderManagement
The OrderManagement component provides a comprehensive interface for managing orders.

**Features:**
- View all orders in a table format
- Search orders
- Filter orders by status
- Create new orders
- View order details
- Edit order information
- Cancel pending orders
- Status tracking (PENDING, CONFIRMED, PREPARING, READY, DELIVERED, CANCELLED)

**Props:**
None

**Events:**
None

**Usage:**
```vue
<template>
  <OrderManagement />
</template>
```

### UserDashboard
The UserDashboard component provides a comprehensive overview of system statistics and recent activities.

**Features:**
- Display key statistics (total customers, active customers, total orders, pending orders, revenue)
- Show recent orders
- Refresh statistics
- Status indicators for orders
- Responsive grid layout

**Props:**
None

**Events:**
None

**Usage:**
```vue
<template>
  <UserDashboard />
</template>
```

### AdminDashboard
The AdminDashboard component serves as the main interface for administrators.

**Features:**
- Navigation to user and customer management
- Display system-wide statistics
- Logout functionality
- Overview of total users and active customers

**Props:**
None

**Events:**
None

**Usage:**
```vue
<template>
  <AdminDashboard />
</template>
```

## Authentication Components

### SignIn
The SignIn component handles user authentication.

**Features:**
- Email and password login
- Remember me functionality
- Form validation
- Error handling
- Social login options (Google, Facebook)

**Props:**
None

**Events:**
None

**Usage:**
```vue
<template>
  <SignIn />
</template>
```

### SignUp
The SignUp component handles new user registration.

**Features:**
- Email and password registration
- Password strength validation
- Terms of service acceptance
- Form validation
- Social registration options
- Email verification requirement

**Props:**
None

**Events:**
None

**Usage:**
```vue
<template>
  <SignUp />
</template>
```

## Legal Components

### PrivacyPolicy
The PrivacyPolicy component displays the application's privacy policy.

**Features:**
- Structured privacy policy content
- Responsive layout
- Clear section organization

**Props:**
None

**Events:**
None

**Usage:**
```vue
<template>
  <PrivacyPolicy />
</template>
```

### TermsOfService
The TermsOfService component displays the application's terms of service.

**Features:**
- Structured terms of service content
- Responsive layout
- Clear section organization

**Props:**
None

**Events:**
None

**Usage:**
```vue
<template>
  <TermsOfService />
</template>
```

### DataDeletion
The DataDeletion component handles user data deletion requests.

**Features:**
- Data deletion request form
- Email verification
- Optional reason submission
- Confirmation checkbox
- Success message display

**Props:**
None

**Events:**
None

**Usage:**
```vue
<template>
  <DataDeletion />
</template>
```

## Styling Notes

All components use SCSS for styling and follow a consistent design system with:
- Primary color variables
- Responsive layouts
- Consistent spacing
- Modern UI elements
- Status indicators
- Form styling
- Modal dialogs
- Table layouts
- Card-based designs

## Common Features Across Components

1. **Error Handling**
   - Form validation
   - API error display
   - User feedback

2. **Loading States**
   - Loading indicators
   - Disabled buttons during operations
   - Skeleton loading where appropriate

3. **Responsive Design**
   - Mobile-first approach
   - Flexible layouts
   - Adaptive tables

4. **Accessibility**
   - ARIA labels
   - Keyboard navigation
   - Screen reader support

5. **State Management**
   - Vuex integration
   - Local component state
   - Props and events 