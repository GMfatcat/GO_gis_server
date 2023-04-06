package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"sync"
	"time"
)

// define json struct
// float32 to save some memory
// Captial First Letter for json parsing
type json_data struct {
	UserID      string  `json:"user_id"`
	RecieveTime string  `json:"time"`
	Latitude    float32 `json:"latitude"`
	Longitude   float32 `json:"longitude"`
}

func read_json_data(filePath string) ([]byte, error) {
	// read json file
	file, err := os.Open(filePath)
	// error handling if file cannot be opened
	if err != nil {
		return nil, fmt.Errorf("File Error: %v", err)
	}
	// make sure to close file
	defer file.Close()

	// read data in json file
	content, err := ioutil.ReadAll(file)
	// error handling if data cannot be read
	if err != nil {
		return nil, fmt.Errorf("Content Error: %v", err)
	}
	// data and file all good -> return content
	return content, nil
}

func show_json_data(file_content []byte) {

	var data json_data
	err := json.Unmarshal([]byte(file_content), &data)
	if err != nil {
		fmt.Println("Decode Error:", err)
		return
	}
	fmt.Println(string(file_content))

}

// ///normal version of parse_json : 8.197 sec for batch_1//////
func batch_processing(directoryPath string) {
	// start time
	startTime := time.Now()

	// read al json file
	files, err := os.ReadDir(directoryPath)
	if err != nil {
		fmt.Println("ReadDir Error:", err)
		return
	}

	// count number of json files in directory
	count := 0

	// iterate all files
	for _, file := range files {
		// json file fullpath
		json_filePath := filepath.Join(directoryPath, file.Name())

		// only process "JSON Files"
		if filepath.Ext(json_filePath) == ".json" {

			// record json number
			count++
			// read json and show, error message use "_", same as python
			content, _ := read_json_data(json_filePath)
			show_json_data(content)
		}
	}

	fmt.Println("Total JSON Files in", directoryPath, ":", count)
	elapsedTime := time.Since(startTime)
	fmt.Println("Elapsed Time (sec):", elapsedTime.Seconds())
}

// ///goroutine version of parse_json : 2.33 sec for batch_1//////
func processJSONFile(json_filePath string, wg *sync.WaitGroup) {
	defer wg.Done() // 標記goroutine處理完成

	content, _ := read_json_data(json_filePath)
	show_json_data(content)
}

func goroutine_batch_processing(directoryPath string) {
	// start time
	startTime := time.Now()

	// read al json file
	files, err := os.ReadDir(directoryPath)
	if err != nil {
		fmt.Println("ReadDir Error:", err)
		return
	}

	// count number of json files in directory
	count := 0
	// create goruoutine collection
	var wg sync.WaitGroup // 用於等待goroutine完成

	// iterate all files
	for _, file := range files {
		// json file fullpath
		json_filePath := filepath.Join(directoryPath, file.Name())

		// only process "JSON Files"
		if filepath.Ext(json_filePath) == ".json" {

			// record json number
			count++
			wg.Add(1)                              // 新增一個goroutine到等待組
			go processJSONFile(json_filePath, &wg) // 啟動goroutine進行處理
		}
	}

	wg.Wait() // 等待所有goroutine完成
	fmt.Println("Total JSON Files in", directoryPath, ":", count)
	elapsedTime := time.Since(startTime)
	fmt.Println("Elapsed Time (sec):", elapsedTime.Seconds())
}

func main() {

	fmt.Printf("Starting...\n")
	//var file_path string = `D:/Fake_Data/Data_multiprocess/batch_1/data_2023-04-01_10-10-05_00a20d9f-fdd2-4483-97c9-65c833b99c5a.json`
	var directoryPath string = `D:/Fake_Data/Data_multiprocess/batch_1/`
	// batch processing
	// batch_processing(directoryPath)
	// goroutines batch processing
	goroutine_batch_processing(directoryPath)

}
