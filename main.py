import requests
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct

# Файл с приватными ключами
private_keys_file = "private_keys.txt"

# Чтение приватных ключей из файла
with open(private_keys_file, "r") as f:
    private_keys = f.read().splitlines()

# URL для получения nonce
nonce_url_template = "https://api.mail3.me/api/v1/address_nonces/{address}"

# URL для создания сессии
session_url = "https://api.mail3.me/api/v1/sessions"

# URL для регистрации
registration_url = "https://api.mail3.me/api/v1/registrations"

# Обрабатываем каждый приватный ключ
for private_key in private_keys:
    # Извлекаем адрес из приватного ключа
    account = Account.from_key(private_key)
    address = account.address

    # Получаем nonce
    nonce_url = nonce_url_template.format(address=address)
    response = requests.get(nonce_url)

    if response.status_code == 404:
        # Если адрес не найден, начинаем регистрацию
        response_json = response.json()
        nonce = response_json.get("metadata", {}).get("nonce")
        if nonce:
            print(f" nonce из ошибки 404 для адреса {address}: {nonce}")
        else:
            print(f"Ошибка: не удалось извлечь nonce из ответа для адреса {address}.")
            continue

        # Формируем сообщение для подписания
        message = f"I authorize sending and checking my emails on mail3 from this device. This doesn't cost anything.\n\nNonce: {nonce}"

        # Кодируем сообщение для подписи
        message_obj = encode_defunct(text=message)

        # Подписываем сообщение с использованием приватного ключа
        signed_message = account.sign_message(message_obj)

        # Преобразуем подпись в формат с префиксом '0x'
        signature = "0x" + signed_message.signature.hex()

        print(f"Подпись для {address}: {signature}")

        # Данные для регистрации
        registration_data = {
            "address": address,
            "message": message,
            "signature": signature
        }

        # Отправляем запрос на регистрацию
        registration_response = requests.post(registration_url, json=registration_data)

        # Проверяем ответ от сервера
        if registration_response.status_code == 200:
            print(f"Регистрация успешна для {address}!")
            print(registration_response.json())  # Печать ответа, если он есть
        elif registration_response.status_code == 204:
            print(f"Регистрация прошла успешно для {address}, но без дополнительного контента в ответе.")
        else:
            print(f"Ошибка при регистрации для {address}: {registration_response.status_code}")
            print(registration_response.text)  # Печать текста ошибки для диагностики

        # После успешной регистрации продолжаем с запросом на сессию
        # Формируем сообщение для подписания с новым nonce
        message = f"I authorize sending and checking my emails on mail3 from this device. This doesn't cost anything.\n\nNonce: {nonce}"

        # Кодируем сообщение для подписи
        message_obj = encode_defunct(text=message)

        # Подписываем сообщение с использованием приватного ключа
        signed_message = account.sign_message(message_obj)

        # Преобразуем подпись в формат с префиксом '0x'
        signature = "0x" + signed_message.signature.hex()

        # Данные для создания сессии
        session_data = {
            "address": address,
            "message": message,
            "signature": signature
        }

        # Отправляем запрос для создания сессии
        session_response = requests.post(session_url, json=session_data)

        # Проверяем ответ от сервера
        if session_response.status_code == 200:
            print(f"Авторизация успешна для {address}!")
        else:
            print(f"Ошибка при создании сессии для {address}: {session_response.status_code}")
            print(session_response.text)  # Печать текста ошибки для диагностики

    elif response.status_code == 200:
        # Если nonce получен без ошибки
        nonce = response.json().get("nonce")
        if nonce is None:
            print(f"Ошибка: не удалось получить nonce для адреса {address}.")
            continue
        print(f"Nonce для {address}: {nonce}")

        # Формируем сообщение для подписания
        message = f"I authorize sending and checking my emails on mail3 from this device. This doesn't cost anything.\n\nNonce: {nonce}"

        # Кодируем сообщение для подписи
        message_obj = encode_defunct(text=message)

        # Подписываем сообщение с использованием приватного ключа
        signed_message = account.sign_message(message_obj)

        # Преобразуем подпись в формат с префиксом '0x'
        signature = "0x" + signed_message.signature.hex()

        # Данные для создания сессии
        session_data = {
            "address": address,
            "message": message,
            "signature": signature
        }

        # Отправляем запрос для создания сессии
        session_response = requests.post(session_url, json=session_data)

        # Проверяем ответ от сервера
        if session_response.status_code == 200:
            print(f"Авторизация успешна для {address}!")
        else:
            print(f"Ошибка при создании сессии для {address}: {session_response.status_code}")
            print(session_response.text)  # Печать текста ошибки для диагностики
