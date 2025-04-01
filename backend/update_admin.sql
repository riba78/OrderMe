USE orderme;

-- Update admin user's password hash
UPDATE users 
SET password_hash = 'pbkdf2:sha256:1000000$1VWiDFjgXyjtfMKA$81cc2096aceaba939ec945e7e8270142c10b8a9cc32e63b4a4bdb5637cc413e9'
WHERE email = 'admin@orderme.com'; 