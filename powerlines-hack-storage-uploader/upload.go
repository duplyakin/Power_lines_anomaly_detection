package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/ioutil"
	"mime/multipart"
	"net/http"
	"os"
	"strings"
)

// https://www.reddit.com/r/golang/comments/apf6l5/multiple_files_upload_using_gos_standard_library/eg94vaa/?context=8&depth=9

var (
	// here the pattern of index page
	// because it does not contain host and port of upload action (see below).
	// The host and port will be added in createUploadServer() function.
	indexPage = `
<html>
	<body>
		<form enctype="multipart/form-data" action="http://%s:%d/upload" method="post">
			<input type="file" name="files" multiple />
			<input type="submit" value="upload" />
		</form>
	</body>
</html>`
)

type UploadServer struct {
	server         *http.Server
	serverCfg      *ServerCfg
	serviceClients *AuxServiceClients
}

// auxiliary service clients (RabbitMq, Database)
// thar are used by server to serve incoming requests
type AuxServiceClients struct {
	rabbitMqClient *RabbitMqClient
	pgClient       *PgClient
}

func createUploadServer(serverCfg *ServerCfg, rabbitMqClient *RabbitMqClient, pgClient *PgClient) (*UploadServer, error) {
	serviceClients := &AuxServiceClients{
		rabbitMqClient: rabbitMqClient,
		pgClient:       pgClient,
	}
	serveMux := http.NewServeMux()
	serveMux.HandleFunc("/upload", serveUpload(serverCfg, serviceClients))

	indexPage = fmt.Sprintf(indexPage, serverCfg.ServerUploadCfg.Host, serverCfg.ServerUploadCfg.Port)
	serveMux.HandleFunc("/", serveIndex)

	us := UploadServer{
		server: &http.Server{
			Addr:     fmt.Sprintf(":%d", serverCfg.ServerUploadCfg.Port),
			Handler:  serveMux,
			ErrorLog: logger,
		},
		serverCfg:      serverCfg,
		serviceClients: serviceClients,
	}

	return &us, nil
}

func processFile(filepath string, serverCfg *ServerCfg, serviceClients *AuxServiceClients) (*CvMessage, error) {
	// 1. Prepare a message to CV service
	baseTransferAddr := fmt.Sprintf("http://%s:%d", serverCfg.ServerTransferCfg.Host,
		serverCfg.ServerTransferCfg.Port)
	link := fmt.Sprintf("%s/%s", baseTransferAddr, filepath) // TODO: maybe, something better here to generate link?

	// 2. Write task to database
	task := &DbTask{
		Type: "classification",
	}
	image := &DbImage{
		Path: filepath,
	}
	err := serviceClients.pgClient.Insert(task, image, baseTransferAddr)
	if err != nil {
		return nil, err
	} else {
		logger.Println("Insert task to db SUCCESSFULLY")
	}

	// 3. Send the message to RabbitMq
	cvMessage := &CvMessage{
		TaskId: task.Id,
		Link:   link,
	}
	err = serviceClients.rabbitMqClient.SendMsg(cvMessage)
	if err != nil {
		return nil, err
	} else {
		logger.Printf("Send message to RabbitMq successfully: %+v\n", *cvMessage)
	}

	return cvMessage, nil
}

func serveIndex(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(indexPage))
}

func extractFilepathRelativeToStorage(filePath, storageDir string) (string, error) {
	if !strings.HasPrefix(filePath, storageDir) {
		return "", errors.New(fmt.Sprintf("file path (%s) does NOT has prefix of storageDir (%s)",
			filePath, storageDir))
	}
	// For example, storageDir=="storageDir" (it can be not abs, but RECOMMEND to be abs!)
	// filePath="storageDir/137834764_IMG_2285.jpg".
	// We should get just a part "137834764_IMG_2285.jpg",
	// so get slice starting index from: len(storageDir)+1
	// +1, because of "/" between storage dir and filename.
	pathRelativeToStorageDir := filePath[len(storageDir)+1:]
	return pathRelativeToStorageDir, nil
}

func onUploadError(w http.ResponseWriter, logErrorMsg string, tempfile *os.File) {
	logger.Printf(logErrorMsg)
	w.WriteHeader(500)
	fmt.Fprintf(w, "Error occured during upload")
	if tempfile != nil {
		os.Remove(tempfile.Name())
	}
}

func serveUpload(serverCfg *ServerCfg, serviceClients *AuxServiceClients) func(w http.ResponseWriter, r *http.Request) {

	return func(w http.ResponseWriter, r *http.Request) {
		// define some variables used throughout the function
		// n: for keeping track of bytes read and written
		// err: for storing errors that need checking
		var n int
		var err error

		// define pointers for the multipart reader and its parts
		var mr *multipart.Reader
		var part *multipart.Part

		logger.Println("File Upload Endpoint Hit")

		if mr, err = r.MultipartReader(); err != nil {
			onUploadError(w,
				fmt.Sprintf("Hit error while opening multipart reader: %s", err.Error()),
				nil)
			return
		}

		// buffer to be used for reading bytes from files
		chunk := make([]byte, 4096)

		// messages
		var cvMessages []CvMessage

		// continue looping through all parts, *multipart.Reader.NextPart() will
		// return an End of File when all parts have been read.
		for {
			// variables used in this loop only
			// tempfile: filehandler for the temporary file
			// filesize: how many bytes where written to the tempfile
			// uploaded: boolean to flip when the end of a part is reached
			var tempfile *os.File
			var filesize int
			var uploaded bool

			if part, err = mr.NextPart(); err != nil {
				if err != io.EOF {
					onUploadError(w,
						fmt.Sprintf("Hit error while fetching next part: %s", err.Error()),
						nil)
				} else {
					logger.Println("Hit last part of multipart upload, cvMessages=", cvMessages)
					w.WriteHeader(http.StatusOK)
					w.Header().Set("Content-Type", "application/json")
					jData, err := json.Marshal(cvMessages)
					if err != nil {
						onUploadError(w,
							fmt.Sprintf("Hit error while jsoning cvMessages: %s", err.Error()),
							nil)
					}
					w.Write(jData)
				}
				return
			}
			// at this point the filename and the mimetype is known
			logger.Printf("Uploaded filename: %s", part.FileName())
			logger.Printf("Uploaded mimetype: %s", part.Header)

			tempfile, err = ioutil.TempFile(serverCfg.ServerUploadCfg.StoragePath,
				fmt.Sprintf("*_%s", part.FileName()))
			if err != nil {
				onUploadError(w,
					fmt.Sprintf("Hit error while reading chunk: %s", err.Error()),
					nil)
				return
			}
			// Не будем здесь использовать 'defer',
			// т.к. при возникновении ошибки в процессе обработки мы удаляем файл из ОС
			// (см. функцию onUploadError).
			// Если загрузка прошла успешно, то явно закроем файл (см. чуть ниже).
			//defer tempfile.Close()

			// here the temporary filename is known
			logger.Printf("Temporary filename: %s\n", tempfile.Name())

			// continue reading until the whole file is upload or an error is reached
			for !uploaded {
				if n, err = part.Read(chunk); err != nil {
					if err != io.EOF {
						onUploadError(w,
							fmt.Sprintf("Hit error while reading chunk: %s", err.Error()),
							tempfile)
						return
					}
					uploaded = true
				}

				if n, err = tempfile.Write(chunk[:n]); err != nil {
					onUploadError(w,
						fmt.Sprintf("Hit error while writing chunk: %s", err.Error()),
						tempfile)
					return
				}
				filesize += n
			}
			logger.Printf("Uploaded filesize: %d bytes", filesize)

			// close file explicitly
			tempfile.Close()
			// change the file mode
			if err = os.Chmod(tempfile.Name(), 0666); err != nil {
				onUploadError(w,
					fmt.Sprintf("Hit error while chmod file: %s", err.Error()),
					tempfile)
				return
			}

			// after uploading we can process this file
			pathRelativeToStorageDir, err := extractFilepathRelativeToStorage(tempfile.Name(),
				serverCfg.ServerUploadCfg.StoragePath)
			if err != nil {
				onUploadError(w,
					fmt.Sprintf("Hit error while extracing filepath relative to storage: %s", err.Error()),
					tempfile)
				return
			}

			cvMessage, err := processFile(pathRelativeToStorageDir, serverCfg, serviceClients)
			if err != nil {
				onUploadError(w,
					fmt.Sprintf("Hit error while processing uploaded file: %s", err.Error()),
					tempfile)
				return
			} else {
				cvMessages = append(cvMessages, *cvMessage)
			}
		}
	}
}
