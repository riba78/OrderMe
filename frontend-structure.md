# Vue Frontend Project Structure

## Current Directory Structure

```
src/
│
├── assets/                  # Static assets
│   ├── styles/             # Global styles
│   │   ├── _dashboard.scss # Dashboard-specific styles
│   │   ├── _variables.scss # SCSS variables
│   │   └── main.scss      # Main styles
│   ├── facebook-icon.svg   # Social login icon
│   └── google-icon.svg     # Social login icon
│
├── components/             # Reusable UI components
│   ├── Auth/              # Authentication components
│   │   ├── SignInForm.vue # Sign in form with validation
│   │   └── SignUpForm.vue # Sign up form with validation
│   ├── common/            # Common, generic UI components
│   │   ├── ActionButton.vue # Versatile button component
│   │   └── UserTable.vue    # Reusable table for displaying users
│   └── MainNavigation.vue # Main navigation component
│
├── pages/                 # Route-level views
│   ├── Home.vue           # Landing page
│   ├── SignIn.vue         # Sign in page
│   ├── SignUp.vue         # Sign up page
│   ├── AdminDashboard.vue # Admin dashboard
│   └── ManagerDashboard.vue # Manager dashboard
│
├── views/                 # Feature-specific views
│   └── admin/
│       └── Users.vue      # User management view for admin
│
├── router/                # Vue Router setup
│   └── index.js           # Routes and navigation guards
│
├── store/                 # Vuex store
│   ├── index.js           # Store configuration
│   └── modules/
│       └── users.js       # Users Vuex module
│
├── services/              # API and business logic
│   ├── api.js             # Axios instance and API helpers
│   └── authService.js     # Authentication service
│
├── layouts/               # Layout components (empty, prepared for future use)
│
├── utils/                 # Utility functions (empty, prepared for future use)
│
├── App.vue                # Root component
└── main.js                # App entry point

```

## Additional Files
- `index.html` (project root): Main HTML entry point
- `vite.config.js` (project root): Vite configuration
- `package.json`, `package-lock.json`: Project dependencies
- `docs/`: Project documentation (e.g., `component-creation-guide.md`)

---

## Implementation Details

### Components
- **Auth Components** (`components/Auth/`)
  - `SignInForm.vue`: Handles authentication with validation, loading states, error handling, Vuex integration
  - `SignUpForm.vue`: Handles registration with validation, loading states, error handling
- **Common Components** (`components/common/`)
  - `ActionButton.vue`: A versatile button component handling various types, styles, sizes, and states.
  - `UserTable.vue`: Displays a list of users in a table. Receives user data as a prop and emits events for actions (edit, delete, toggle activation). Does not handle modals or data fetching itself.
- **Navigation** (`components/`)
  - `MainNavigation.vue`: Main navigation, routing, active states, responsive design

### Pages
- **Home.vue**: Landing page, uses MainNavigation, background styling
- **SignIn.vue**: Dedicated sign-in page, uses SignInForm, matches home styling
- **SignUp.vue**: Dedicated sign-up page, uses SignUpForm
- **AdminDashboard.vue**: Protected admin dashboard. Displays user statistics and quick actions. Uses the `UserTable.vue` component to show an overview of users and handles user actions (e.g., opening modals or navigating) in its own context.
- **ManagerDashboard.vue**: Protected manager dashboard, manager-specific features

### Views
- **admin/Users.vue** (Consider renaming to `UserManagementView.vue` for clarity): Dedicated full-page view for comprehensive user management. Manages its own layout, modals (create/edit/confirm), search/filters, and data fetching. Uses the `UserTable.vue` component to display the list of users and handles actions from it.

### Store Structure
- **index.js**: Vuex store config, global state, auth state, persistent storage
- **modules/users.js**: User management Vuex module (fetch, create, update, delete users)

### Services
- **api.js**: Axios instance, request/response interceptors, token handling
- **authService.js**: Auth API calls (login, getMe)

### Router
- **index.js**: Route definitions, navigation guards, role-based redirects

### Styles
- **assets/styles/**: SCSS variables, dashboard styles, main styles
- **assets/facebook-icon.svg**, **assets/google-icon.svg**: Social login icons

### Layouts & Utils
- **layouts/**: (empty, for future layout components)
- **utils/**: (empty, for future utility functions)

### Documentation
- **docs/component-creation-guide.md**: Guide for creating new components

---

## Best Practices (Current Implementation)

1. **Authentication Flow**
   - Token-based authentication
   - Secure storage in localStorage
   - Protected routes with navigation guards

2. **Component Organization**
   - Single responsibility components, promoting better separation of concerns (e.g., `UserTable.vue` focuses solely on table rendering).
   - Props validation.
   - Event handling patterns for child-to-parent communication.
   - Reusability: Creating generic components like `UserTable.vue` and `ActionButton.vue` to be used in multiple places, reducing code duplication (DRY).

3. **State Management**
   - Centralized Vuex store
   - Local state when appropriate
   - Persistent auth state

4. **API Integration**
   - Axios for HTTP requests
   - Centralized service files
   - Error handling patterns

5. **Styling**
   - Global SCSS variables and resets
   - Scoped component styles
   - BEM naming convention
   - Responsive design

---

## Next Steps

1. **Immediate Priorities**
   - Implement remaining CRUD operations
   - Add error boundaries
   - Enhance form validation
   - Add loading states

2. **Future Enhancements**
   - Add user management features
   - Implement customer management
   - Add profile settings
   - Enhance dashboard features
   - Populate layouts/ and utils/ with reusable code

## Style Guidelines

Current styling implementation:

1. **Global Styles** (`assets/styles/`)
   - Variables for consistent theming
   - Global reset and base styles
   - Utility classes

2. **Component Styles**
   - Scoped SCSS in components
   - BEM naming convention
   - Responsive design patterns

## Planned Extensions

1. **Layouts Directory**
   - Prepared for implementing different layout templates
   - Will include admin, auth, and default layouts

2. **Utils Directory**
   - Will contain helper functions
   - Form validators
   - Date formatters
   - Common utilities

3. **Future Components**
   - User management components
   - Customer management components
   - Profile components
   - Settings components

## Best Practices (Current Implementation)

1. **Authentication Flow**
   - Token-based authentication
   - Secure storage in localStorage
   - Protected routes with navigation guards

2. **Component Organization**
   - Single responsibility components, promoting better separation of concerns (e.g., `UserTable.vue` focuses solely on table rendering).
   - Props validation.
   - Event handling patterns for child-to-parent communication.
   - Reusability: Creating generic components like `UserTable.vue` and `ActionButton.vue` to be used in multiple places, reducing code duplication (DRY).

3. **State Management**
   - Centralized Vuex store
   - Local state when appropriate
   - Persistent auth state

4. **API Integration**
   - Axios for HTTP requests
   - Centralized service files
   - Error handling patterns

## Next Steps

1. **Immediate Priorities**
   - Implement remaining CRUD operations
   - Add error boundaries
   - Enhance form validation
   - Add loading states

2. **Future Enhancements**
   - Add user management features
   - Implement customer management
   - Add profile settings
   - Enhance dashboard features 