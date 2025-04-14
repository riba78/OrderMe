this is inital frontend structure template that will be extended with new features and pages

frontend/
├── public/
│   └── index.html
├── src/
│   ├── assets/                  # Static assets: images, fonts, etc.
│   ├── components/              # Reusable UI components
│   │   ├── Navigation.vue       # Top-level navigation bar
│   │   ├── Footer.vue           # Optional: reusable footer component
│   │   └── common/              # Shared UI elements (buttons, modals, etc.)
│   ├── views/                   # Page-level components (views)
│   │   ├── Admin/
│   │   │   ├── AdminDashboard.vue
│   │   │   ├── UsersManagement.vue
│   │   │   └── ProductsManagement.vue   # Suggested additional page
│   │   ├── Manager/
│   │   │   ├── ManagerDashboard.vue
│   │   │   └── OrderManagement.vue       # Suggested additional page
│   │   ├── Auth/
│   │   │   ├── SignIn.vue
│   │   │   └── SignUp.vue
│   │   └── Shared/
│   │       └── NotFound.vue      # Optional: 404 error page
│   ├── router/                  # Vue Router configuration
│   │   └── index.js
│   ├── store/                   # Vuex store (or other state management)
│   │   ├── modules/
│   │   │   ├── auth.js          # Authentication related state/actions
│   │   │   ├── users.js         # User management related state/actions
│   │   │   ├── products.js      # Products module
│   │   │   └── orders.js        # Orders module
│   │   └── index.js
│   ├── services/                # API calls and business logic
│   │   ├── authService.js       # Handles SignIn/SignUp API calls
│   │   ├── userService.js       # CRUD for users and customers
│   │   ├── productService.js    # CRUD for products
│   │   └── orderService.js      # CRUD for orders
│   ├── utils/                   # Utility functions & helpers
│   │   └── validation.js        # Form validation helpers, etc.
│   ├── App.vue                  # Main Vue component
│   └── main.js                  # Application entry point
└── package.json
