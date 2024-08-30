// Находим элементы формы, поля ввода и списка сообщений
const form = document.getElementById('form');
const messageInput = document.getElementById('messageInput');
const messages = document.getElementById('messages');

// Подключение к WebSocket серверу по указанному URL
const ws = new WebSocket('ws://localhost:8080/ws');

ws.onopen = () => {
    console.log("WebSocket соединение установлено");
};

// Обработка входящих сообщений от сервера
ws.onmessage = function(event) {
    console.log("Получено сообщение от сервера: ", event.data);  // Логируем полученные сообщения
    // Фильтруем сообщения "ping"
    if (event.data === 'ping') {
        return;  // Игнорируем сообщения "ping"
    }
    const li = document.createElement('li');  // Создаем новый элемент списка
    li.textContent = event.data;  // Устанавливаем текстом полученное сообщение
    messages.appendChild(li);  // Добавляем элемент в список сообщений
    messages.scrollTop = messages.scrollHeight;  // Прокручиваем список к последнему сообщению
};

ws.onerror = (error) => {
    console.error("WebSocket ошибка: ", error);
};

// Отправка сообщения на сервер при отправке формы
form.addEventListener('submit', function(event) {
    event.preventDefault();  // Предотвращаем стандартное поведение формы (перезагрузку страницы)
    if (messageInput.value.trim() !== "") {  // Проверяем, что поле ввода не пустое
        console.log("Отправка сообщения на сервер: ", messageInput.value);
        ws.send(messageInput.value);  // Отправляем введенное сообщение на сервер
        messageInput.value = '';  // Очищаем поле ввода после отправки
    }
});
