# Vue Frontend Project Structure

## Current Directory Structure

```
src/
│
├── assets/                  # Static assets
│   ├── styles/             # Global styles
│   │   ├── _variables.scss # SCSS variables
│   │   └── main.scss      # Main styles
│   ├── facebook-icon.svg   # Social login icons
│   └── google-icon.svg
│
├── components/             # Reusable UI components
│   ├── Auth/              # Authentication components
│   │   └── SignInForm.vue # Sign in form with validation
│   └── MainNavigation.vue # Main navigation component
│
├── pages/                 # Route-level views
│   ├── Home.vue          # Landing page
│   ├── SignIn.vue        # Sign in page
│   └── AdminDashboard.vue # Admin dashboard
│
├── router/               # Vue Router setup
│   └── index.js         # Routes and navigation guards
│
├── store/               # Vuex store
│   └── index.js        # Store configuration with auth module
│
├── services/           # API and business logic
│   └── authService.js  # Authentication service
│
├── layouts/            # Layout components (prepared for future use)
│
├── utils/             # Utility functions (prepared for future use)
│
├── App.vue            # Root component
└── main.js           # App entry point

```

## Implementation Details

### Components
Currently implemented components follow these patterns:

1. **Auth Components** (`components/Auth/`)
   - `SignInForm.vue`: Handles authentication with validation
   - Implements loading states and error handling
   - Uses Vuex for state management

2. **Navigation** (`components/`)
   - `MainNavigation.vue`: Main navigation component
   - Handles routing and active states
   - Responsive design implementation

### Pages
Current page implementations:

1. **Home.vue**
   - Landing page with sign-in functionality
   - Uses MainNavigation component
   - Implements background styling

2. **SignIn.vue**
   - Dedicated sign-in page
   - Uses SignInForm component
   - Matches home page styling

3. **AdminDashboard.vue**
   - Protected admin dashboard
   - Displays user statistics
   - Implements user management features

### Store Structure
Current Vuex implementation:

```javascript
// store/index.js
export default createStore({
  state: {
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null'),
  },
  getters: {
    userRole: state => state.user?.role || '',
    isAuthenticated: state => !!state.token,
  },
  mutations: {
    setToken(state, token) {
      state.token = token
      localStorage.setItem('token', token)
    },
    setUser(state, user) {
      state.user = user
      localStorage.setItem('user', JSON.stringify(user))
    },
    logout(state) {
      state.token = ''
      state.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})
```

### Services
Current API service implementation:

```javascript
// services/authService.js
import axios from 'axios'

export async function login(email, password) {
  return axios.post('/api/auth/signin', { email, password })
}

export async function getMe(token) {
  return axios.get('/api/users/me', {
    headers: {
      Authorization: `Bearer ${token}`
    }
  })
}
```

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

## Best Practices (Current Implementation)

1. **Authentication Flow**
   - Token-based authentication
   - Secure storage in localStorage
   - Protected routes with navigation guards

2. **Component Organization**
   - Single responsibility components
   - Props validation
   - Event handling patterns

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