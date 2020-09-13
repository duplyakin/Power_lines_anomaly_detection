package main

import (
	"encoding/json"
	"fmt"
	"github.com/streadway/amqp"
)

type RabbitMqClient struct {
	Connection *amqp.Connection
	Channel    *amqp.Channel
	Cfg        *RabbitMqCfg
}

type CvMessage struct {
	TaskId int64
	Link   string
}

func newRabbitMqClient(cfg *RabbitMqCfg) (*RabbitMqClient, error) {
	connUrl := fmt.Sprintf("amqp://%s:%s@%s:%d/",
		cfg.User,
		cfg.Password,
		cfg.Host,
		cfg.Port)
	conn, err := amqp.Dial(connUrl)
	if err != nil {
		return nil, err
	}
	channel, err := conn.Channel()
	if err != nil {
		conn.Close()
		return nil, err
	}

	return &RabbitMqClient{
		Connection: conn,
		Channel:    channel,
		Cfg:        cfg,
	}, nil
}

func (rc *RabbitMqClient) Close() {
	// channel should be closed at first (before connection)
	rc.Channel.Close()
	rc.Connection.Close()
}

func (rc *RabbitMqClient) SendMsg(msg *CvMessage) error {
	body, err := json.Marshal(msg)
	if err != nil {
		return err
	}

	err = rc.Channel.Publish(
		rc.Cfg.Exchange,
		rc.Cfg.RoutingKey,
		false,
		false,
		amqp.Publishing{
			DeliveryMode: amqp.Persistent,
			ContentType:  "application/json",
			Body:         body,
		})
	if err != nil {
		return err
	}

	return nil
}
