import requests

url = "https://vip3.activeusers.ru/app.php?act=item&id=13739&sign=iAY3p4eqbqFtFlmx3gMMbYJQ9p8juXRh11xIdg8kuUI&vk_access_token_settings=&vk_app_id=6987489&vk_are_notifications_enabled=0&vk_is_app_user=1&vk_is_favorite=0&vk_language=ru&vk_platform=desktop_web&vk_ref=other&vk_ts=1743599720&vk_user_id=569154671&back=act:user"

try:
    # Выполняем GET-запрос
    response = requests.get(url, timeout=10)

    # Проверяем статус ответа
    if response.status_code == 200:
        print("HTML-содержимое:\n")
        print(response.text)
    else:
        print(f"Ошибка: Сервер вернул код {response.status_code}")

except requests.exceptions.RequestException as e:
    print(f"Ошибка при выполнении запроса: {e}")