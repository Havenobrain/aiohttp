import aiohttp
import aiohttp.web as web
import asyncio

# Список подключенных клиентов
clients = []

# Обработчик подключения через веб-сокеты
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    clients.append(ws)
    print("Клиент подключился")

    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                print(f"Получено сообщение от клиента: {msg.data}")
                # Рассылка сообщения всем подключенным клиентам
                for client in clients:
                    if not client.closed:
                        await client.send_str(msg.data)
                        print(f"Сообщение отправлено клиенту: {msg.data}")
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f"Ошибка веб-сокета: {ws.exception()}")

    finally:
        clients.remove(ws)
        print("Клиент отключился")

    return ws

# Обработчик для приема новостей через POST-запросы
async def news_handler(request):
    try:
        data = await request.json()
        news_message = data.get('message', 'Новость без содержания')
        print(f"Получена новость: {news_message}")

        # Рассылка новостей всем подключенным клиентам
        for ws in clients:
            if ws.closed:
                continue
            await ws.send_str(news_message)
            print(f"Новость отправлена клиенту: {news_message}")

        return web.Response(text="Новость разослана клиентам.")
    
    except Exception as e:
        print(f"Ошибка при обработке новостей: {e}")
        return web.Response(status=400, text=f"Ошибка: {e}")

# Функция для периодической проверки соединений
async def check_connections():
    while True:
        await asyncio.sleep(30)  # Периодичность проверки, например каждые 30 секунд
        for ws in clients:
            try:
                if not ws.closed:
                    await ws.send_str("ping")  # Отправляем 'ping' для проверки соединения
                    print(f"ping отправлен клиенту")
            except Exception as e:
                print(f"Ошибка при проверке соединения: {e}")

# Создание приложения и маршрутов
app = web.Application()

# Маршруты
app.add_routes([
    web.get('/', lambda request: web.FileResponse('./static/index.html')),
    web.get('/ws', websocket_handler),
    web.post('/news', news_handler),
    web.static('/', './static'),  # Указываем путь к папке static
])

# Запуск сервера и задачи по проверке соединений
async def main():
    loop = asyncio.get_event_loop()
    loop.create_task(check_connections())
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    print("Сервер запущен на http://localhost:8080")
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
