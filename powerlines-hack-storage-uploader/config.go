package main

import (
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"strconv"
)

const (
	SERVER_UPLOAD_HOST_ENV    = "SERVER_UPLOAD_HOST"
	SERVER_UPLOAD_PORT_ENV    = "SERVER_UPLOAD_PORT"
	SERVER_UPLOAD_STORAGE_ENV = "SERVER_UPLOAD_STORAGE"
)

type ServerUploadCfg struct {
	Host        string `json:"host"`
	Port        int64  `json:"port"`
	StoragePath string `json:"storage_path"`
}

type ServerTransferCfg struct {
	Host string `json:"host"`
	Port int64  `json:"port"`
}

type ServerCfg struct {
	ServerUploadCfg   `json:"upload"`
	ServerTransferCfg `json:"transfer"`
}

type RabbitMqCfg struct {
	Host       string `json:"host"`
	Port       int64  `json:"port"`
	User       string `json:"user"`
	Password   string `json:"password"`
	Exchange   string `json:"exchange"`
	RoutingKey string `json:"routing_key"`
}

type Config struct {
	Server   ServerCfg   `json:"server"`
	RabbitMq RabbitMqCfg `json:"rabbit_mq"`
	DbUrl    string      `json:"database_url"`
}

// env_type:
//     "dev" -- for "config/dev.json"
//     "prod" -- for "config/prod.json"
func readConfig(env_type string) (*Config, error) {
	service_type, ok := os.LookupEnv(env_type)
	if !ok || service_type == "" {
		return nil, errors.New(env_type + " is not set!")
	}
	config_path := form_config_file_path(service_type + ".json")
	cfg_file, err := os.Open(config_path)
	if err != nil {
		return nil, err
	}
	defer cfg_file.Close()

	var cfg Config
	if err := json.NewDecoder(cfg_file).Decode(&cfg); err != nil {
		return nil, err
	}

	replaceFromEnv(&cfg.Server.ServerUploadCfg.Host, SERVER_UPLOAD_HOST_ENV)
	replaceFromEnv(&cfg.Server.ServerUploadCfg.Port, SERVER_UPLOAD_PORT_ENV)
	replaceFromEnv(&cfg.Server.ServerUploadCfg.StoragePath, SERVER_UPLOAD_STORAGE_ENV)

	return &cfg, nil
}

// This function returns the relative path of config file.
// For example, "config/dev.json" (if config_file_name=="dev.json").
// Here very simple version, you can modify it to return path
// using automatic definition of the current source file dir.
func form_config_file_path(config_file_name string) string {
	return filepath.Join("config", config_file_name)
}

// replaceFromEnv replaces corresponding config parameter with value of environment variable.
func replaceFromEnv(cfgParam interface{}, env string) {
	envValue, found := os.LookupEnv(env)
	if !found {
		return
	}
	switch cfgParam.(type) {
	case *string:
		s := cfgParam.(*string)
		*s = envValue
	case *int64:
		i := cfgParam.(*int64)
		if v, err := strconv.ParseInt(envValue, 10, 64); err == nil {
			*i = v
		}
	default:
		return
	}
}
