# Overview

Бот создан в рамках хакатона "Цифровой Прорыв" для отправки уведомлений об аномальных случаях ЛЭП для кейса от Россети.
Ссылка на бота: http://t.me/DevlabsRossetiBot. Надо подписаться, чтобы получать уведомления.

# Docker

Сборка образа:

`docker build . -t devlabs-tgbot-img`

При запуске контейнера надо указать переменную окружения `BOT_TOKEN` (токен Телеграм бота):
либо через env файл передать, либо передать прямо в самой команде:

`docker run -d --name devlabs-tgbot --restart unless-stopped -e BOT_TOKEN=<here bot token> devlabs-tgbot-img`