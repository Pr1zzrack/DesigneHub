import requests

# URL вашего API
url = 'http://127.0.0.1:8000/designs/13/reviews/'  # Замените 1 на ID вашего design

# Токен JWT, который нужно передать в заголовке
jwt_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIzNjQ2NjIyLCJpYXQiOjE3MjM2NDYzMjIsImp0aSI6IjM2MjVlNzczYzYwZDQ5NDdhMjg4N2MwOTZhNzVmMzhkIiwidXNlcl9pZCI6MTl9.NmSiapXn5MMHJ8o5uAkzh1sBuJVoPScmC7jUoozf83E'

# Данные для создания комментария
data = {
    'content': 'Test 1'  # Текст отзыва
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
