# Development Environment Configuration

# Environment
ENVIRONMENT=development

# Database Configuration
DB_HOST=vskorik-mysql.mysql.database.azure.com
DB_PORT=3306
DB_USER=vskorik32
DB_PASSWORD=Brat1978
DB_NAME=orderme_test

# JWT Configuration
SECRET_KEY=dev_8x#mP9$kL2@nQ5vR7*jW4yH1
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# SSL Configuration
SSL_VERIFY_IDENTITY=false
SSL_CA_CERT_PATH=

# API Configuration
API_V1_PREFIX=/api/v1

# Admin Configuration
ADMIN_EMAIL=admin@orderme.com
ADMIN_PASSWORD=Admin@123 

# Production Environment Configuration

# Environment
ENVIRONMENT=production

# Database Configuration
DB_HOST=vskorik-mysql.mysql.database.azure.com
DB_PORT=3306
DB_USER=vskorik32
DB_PASSWORD=Brat1978
DB_NAME=orderme

# JWT Configuration
SECRET_KEY=prod_8x#mP9$kL2@nQ5vR7*jW4yH1
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# SSL Configuration
SSL_VERIFY_IDENTITY=true

# API Configuration
API_V1_PREFIX=/api/v1

# Admin Configuration
ADMIN_EMAIL=admin@orderme.com
ADMIN_PASSWORD=Admin@123 