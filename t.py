import requests

# URL вашего API
url = 'http://127.0.0.1:8000/designs/13/reviews/1'  # Замените 1 на ID вашего design

# Токен JWT, который нужно передать в заголовке
jwt_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIzNzA0MTgwLCJpYXQiOjE3MjM3MDM4ODAsImp0aSI6IjM2Y2M1NWY1YmU0NTQ3ZjM4YjMzMmM3MGZhMjc3ODMwIiwidXNlcl9pZCI6MTl9.MFj2nHnTLrKwmEO0kCDtEPBeew8NkG8THnrRwMzB9uI'

# Данные для создания комментария
data = {
    'content': 'This is a sample review content.'  # Текст отзыва
}

# Заголовки запроса
headers = {
    'Authorization': f'Bearer {jwt_token}',
    'Content-Type': 'application/json'
}

# Выполнение POST-запроса
response = requests.get(url, headers=headers)

# Проверка ответа
if response.status_code == 200:
    print('Review created successfully:', response.json())
else:
    print('Failed to create review:', response.status_code)
