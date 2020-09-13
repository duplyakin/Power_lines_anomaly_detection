package main

import (
	"context"
	"github.com/jackc/pgx/v4/pgxpool"
)

type PgClient struct {
	pool *pgxpool.Pool
}

func newPgClient(dbConnString string) (*PgClient, error) {
	pool, err := pgxpool.Connect(context.Background(), dbConnString)
	if err != nil {
		return nil, err
	}

	pgClient := &PgClient{
		pool: pool,
	}
	return pgClient, nil
}

func (pg *PgClient) Close() {
	pg.pool.Close()
}

// TaskType enum
type TaskType string

const (
	// value ("classification") must match to value in the DB
	Classification TaskType = "classification"
)

// TaskResult enum
type TaskResult string

const (
	// values ("ok", "not_ok") must match to value in the DB
	Ok    TaskType = "ok"
	NotOk TaskType = "not_ok"
)

type DbTask struct {
	Id      int64
	ImageId int64
	Type    TaskType
	Result  TaskResult
}

type DbImage struct {
	Id              int64
	StorageServerId int64
	Path            string
}

type DbStorageServer struct {
	Id               int64
	BaseTransferAddr string
}

func (pg *PgClient) Insert(task *DbTask, image *DbImage, baseTransferAddr string) error {
	var err error
	// 1. Read the storage server id
	image.StorageServerId, err = pg.readStorageServerId(baseTransferAddr) // should be OK
	if err != nil {
		return err
	}

	// 2.
	conn, err := pg.pool.Acquire(context.Background())
	if err != nil {
		return err
	}
	defer conn.Release()

	tx, err := conn.Begin(context.Background())
	/*
		tx, err := conn.BeginTx(context.Background(),
			pgx.TxOptions{
				DeferrableMode: pgx.Deferrable,
			})
	*/

	if err != nil {
		return err
	}
	// Rollback is safe to call even if the tx is already closed, so if
	// the tx commits successfully, this is a no-op
	defer tx.Rollback(context.Background())

	// 3.
	err = tx.QueryRow(context.Background(),
		"INSERT INTO images (storage_server_id, path) VALUES ($1, $2) RETURNING id",
		image.StorageServerId, image.Path).Scan(&image.Id)
	if err != nil {
		return err
	}

	// 4.
	task.ImageId = image.Id
	err = tx.QueryRow(context.Background(),
		"INSERT INTO tasks (image_id, type) VALUES ($1, $2) RETURNING id",
		task.ImageId, task.Type).Scan(&task.Id)
	if err != nil {
		return err
	}

	// 5.
	err = tx.Commit(context.Background())
	if err != nil {
		return err
	}

	return nil
}

func (pgClient *PgClient) readStorageServerId(baseTransferAddr string) (int64, error) {
	conn, err := pgClient.pool.Acquire(context.Background())
	if err != nil {
		return 0, err
	}
	defer conn.Release()

	var id int64
	err = conn.QueryRow(context.Background(),
		"SELECT id FROM storage_servers WHERE base_transfer_address=$1",
		baseTransferAddr).Scan(&id)
	if err != nil {
		return 0, err
	}
	return id, nil
}

func testInsert(pgClient *PgClient) {
	task := &DbTask{
		Type: "classification",
	}
	image := &DbImage{
		Path: "/home/ondar/images/example.jpg",
	}
	err := pgClient.Insert(task, image, "http://89.223.95.49:8888")
	if err != nil {
		logger.Println(err)
	} else {
		logger.Println("SUCCESS")
	}
}
