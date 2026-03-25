# Используем официальный образ Node.js LTS (Alpine для минимального размера)
FROM node:18-alpine

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем package.json (package-lock.json не обязателен)
COPY app/package*.json ./

# Устанавливаем зависимости (только production)
RUN npm install --omit=dev

# Копируем исходный код
COPY app/ .

# Открываем порт, на котором работает приложение
EXPOSE 5000

# Запускаем сервер
CMD ["node", "server.js"]