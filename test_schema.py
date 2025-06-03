# from datetime import datetime
# from pydantic import ValidationError
# from app.schemas import UserCreate  # عدل 'your_schema_file' لاسم الملف اللي فيه السكيما بتاعتك

# # بيانات اختبار صحيحة
# data = {
#     "username": "ramif123",
#     "email": "rami@example.com",
#     "phone_number": "+201234567890",
#     "date_of_birth": "1995-05-15T00:00:00",
#     "password": "mypassword123",
#     "confirm_password": "mypassword123"
# }

# try:
#     user = UserCreate(**data)
#     print("Valid data:", user)
# except ValidationError as e:
#     print("Validation errors:", e)
