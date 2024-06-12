from passlib.context import CryptContext

# setup the password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# function to hash the password
def hash_password(password):
    return pwd_context.hash(password)

# print the hashed password
print(hash_password('*?Cheery209'))
