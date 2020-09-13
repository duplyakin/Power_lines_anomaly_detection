# Overview

Все разрабатывалось на видеокарте 1080 Ti, 12Gb с использованием 
detectron2 (https://github.com/facebookresearch/detectron2) и Pytorch 1.6.

Код обрабатывает поступающие сообщения из RabbitMq, обрабатывает фото,
сохраняет результаты в базу и отправляет дальше в очереди Notifications API.
В качестве примера Notification API сервиса реализован Telegram бот.
