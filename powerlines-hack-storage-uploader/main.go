package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"time"
)

const (
	cfgTypeEnvName = "DEVLABS_UPLOAD_CFG_TYPE"
)

var logger = log.New(os.Stdout, "devlabs-upload-service ", log.LstdFlags|log.Lshortfile)

func main() {
	logger.Println("Start the upload service")

	// 1. Read config
	cfg, err := readConfig(cfgTypeEnvName)
	if err != nil {
		logger.Fatal(err.Error())
	}
	logger.Println("Config:", *cfg)

	// 2.
	rabbitmq, err := newRabbitMqClient(&cfg.RabbitMq)
	if err != nil {
		logger.Fatal(err.Error())
	}
	defer rabbitmq.Close()

	// 3. DB
	pgClient, err := newPgClient(cfg.DbUrl)
	if err != nil {
		logger.Fatal(err.Error())
	}
	defer pgClient.Close()

	// 4. Server
	uploadServer, err := createUploadServer(&cfg.Server, rabbitmq, pgClient)
	if err != nil {
		logger.Fatal(err.Error())
	}
	go func() {
		// service connections
		if err := uploadServer.server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Fatalf("LISTEN ERROR: %s", err.Error())
		}
	}()

	// Wait for interrupt signal to gracefully shutdown the server with
	// a timeout of 10 seconds.
	quit := make(chan os.Signal)
	signal.Notify(quit, os.Interrupt)
	<-quit
	close(quit)
	logger.Println("Shutting down the server...")

	// Shut down the server here
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := uploadServer.server.Shutdown(ctx); err != nil {
		logger.Fatalf("SERVER SHUTDOWN ERROR: %s", err)
	}
	logger.Println("Server exiting.")
}
