package main

import (
	"encoding/json"
	"fmt"
	"gis_server/test/DB"  //import db module
	"gis_server/test/GIS" //import gis module
	"io/ioutil"
	"os"
	"path/filepath"
	"sync"
	"time"
)

// define root & saving directory
var RootDir = `D:/Fake_Data/Data_multiprocess/`
var SaveGridDir = `D:/binary_grids/`

// define json struct
// Captial First Letter for json parsing
type json_data struct {
	UserID      string  `json:"user_id"`
	RecieveTime string  `json:"time"`
	Latitude    float64 `json:"latitude"`
	Longitude   float64 `json:"longitude"`
}

// Gids Max Rows and Cols
var (
	MaxRows int
	MaxCols int
)

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

func show_json_data(file_content []byte, show_coord bool) (float64, float64) {

	var data json_data
	err := json.Unmarshal([]byte(file_content), &data)
	if err != nil {
		fmt.Println("Decode Error:", err)
		// return -1.0 --> pass GIS if return is nil
		return -1.0, -1.0
	}

	// only show when needed, save some time
	if show_coord {
		fmt.Println(string(file_content))
	}
	//return coordinate
	lat := data.Latitude
	lon := data.Longitude
	return lat, lon

}

// ///goroutine version of parse_json : 2.33 sec for batch_1//////
func processJSONFile(json_filePath string, wg *sync.WaitGroup, grid *gis.Grid) {
	defer wg.Done() // 標記goroutine處理完成

	content, _ := read_json_data(json_filePath)
	// show and return coordinate for GIS
	lat, lon := show_json_data(content, false)
	// 做GIS Index計算
	if lat != -1.0 {
		gis_grid_calculate(lat, lon, grid)
	}

}

func gis_prepare() (int, int, *gis.Grid) {
	// Prepare for GIS Calculation
	all_rows, all_cols := gis.GetRowsCols(-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0)
	// fmt.Printf("TOTAL col=%d, row=%d\n", all_cols, all_rows)
	// 初始化Grid
	grid := gis.NewGrid(all_rows, all_cols)
	return all_rows, all_cols, grid
}

func gis_grid_calculate(user_lat float64, user_lon float64, grid *gis.Grid) {
	row, col := gis.GetRowsCols(user_lat, user_lon, -1.0, -1.0, -1.0, -1.0, -1.0)
	// safety check --> use = not := to change row
	if row >= MaxRows {
		row = row - 1
	}
	if col >= MaxCols {
		col = col - 1
	}
	// 建立這組座標結構
	coord := gis.Coordinate{
		Lon: user_lon,
		Lat: user_lat}
	//add to grid
	grid.AddCoordinate(row, col, coord)

}

func test_gis(row int, col int, grid *gis.Grid) {
	// see how many coords store in this grid
	this_grid_coordinates := grid.GetCoordinates(row, col)
	count := len(this_grid_coordinates)
	fmt.Printf("row=%d, col=%d 中共有 %d 組座標資訊:\n", row, col, count)

	for i, coord := range this_grid_coordinates {
		fmt.Printf("座標 %d: Lon=%f, Lat=%f\n", i+1, coord.Lon, coord.Lat)
	}
}

func save_grid(grid *gis.Grid, filename string) {
	err := gis.SaveGrid(grid, filename)
	if err != nil {
		fmt.Println("Error:", err)
	}
}

func convert_grid_to_gridsum(grid *gis.Grid) *db.GridSum {

	gridSum := &db.GridSum{
		Rows:    grid.Rows,
		Cols:    grid.Cols,
		GridSum: make([][]int, grid.Rows),
	}
	// record sum to gridSum
	for i := 0; i < grid.Rows; i++ {
		gridSum.GridSum[i] = make([]int, grid.Cols)
		for j := 0; j < grid.Cols; j++ {
			gridSum.GridSum[i][j] = len(grid.Grid[i][j])
		}
	}

	return gridSum

}

func save_to_redis(gridSum *db.GridSum, expire_time int) {
	// make connection with redis
	client, err := db.RedisConnection()
	if err != nil {
		fmt.Println("Redis Error:", err)
	}

	// save gridSum to redis server
	db.SaveGridSum(gridSum.GridSum, client, expire_time)
	fmt.Println("Save to Redis!! Expire time:", expire_time, "sec")

	// check value after 5 and 21 seconds
	// QueryGridSum in row = 100 col = 100
	// time.Sleep(5 * time.Second) // 讓程式睡 5 秒
	// fmt.Println("After 5 seconds..")
	db.QueryGridSum(100, 100, client)
	// time.Sleep(16 * time.Second) // 讓程式睡 6 秒
	// fmt.Println("After 16 seconds..")
	// db.QueryGridSum(100, 100, client)
}

// ///////////////////////////////////

func goroutine_batch_processing(directoryPath string) {
	// start time
	startTime := time.Now()

	// read al json file
	files, err := os.ReadDir(directoryPath)
	// _, err := os.ReadDir(directoryPath)
	if err != nil {
		fmt.Println("ReadDir Error:", err)
		return
	}

	// count number of json files in directory
	count := 0
	// create goruoutine collection
	var wg sync.WaitGroup

	// Prepare for GIS Calculation
	MaxRows, MaxCols, grid := gis_prepare()
	// iterate all files
	for _, file := range files {
		// json file fullpath
		json_filePath := filepath.Join(directoryPath, file.Name())

		// only process "JSON Files"
		if filepath.Ext(json_filePath) == ".json" {

			// record json number
			count++
			wg.Add(1)                                    // 新增一個goroutine到等待組
			go processJSONFile(json_filePath, &wg, grid) // 啟動goroutine進行處理
		}
	}

	wg.Wait() // 等待所有goroutine完成
	elapsedTime := time.Since(startTime)
	fmt.Println("Elapsed Time (sec):", elapsedTime.Seconds())
	fmt.Println("Total JSON Files in", directoryPath, ":", count)
	//save & test GIS output
	fmt.Printf("Grid cols=%d, rows=%d\n", MaxCols, MaxRows)
	test_gis(100, 100, grid) //test Grid(100,100)
	// save grid
	cuurent_dir_name := filepath.Base(directoryPath)
	gridpath := filepath.Join(SaveGridDir, cuurent_dir_name)
	save_grid(grid, gridpath)
	// test Redis
	gridsum := convert_grid_to_gridsum(grid)
	// expire time = 10 sec
	save_to_redis(gridsum, 15)
}

func main() {

	fmt.Printf("Starting...\n")
	// test import gis_package
	// fmt.Printf("Lat : %f %f\n", gis.MinLat, gis.MaxLat)
	// fmt.Printf("Lon : %f %f\n", gis.MinLon, gis.MaxLon)
	// Walk every directory under root directory
	filepath.Walk(RootDir, ProcessEveryDirectory)

}

func ProcessEveryDirectory(path string, info os.FileInfo, err error) error {
	if err != nil {
		return err
	}
	if info.IsDir() {
		// Skip root directory
		if path == RootDir {
			return nil
		}
		// Call goroutine_batch_processing on each subdirectory
		// goroutines batch processing
		goroutine_batch_processing(path)
		// Stop for 9 seconds
		time.Sleep(15 * time.Second)
	}
	return nil
}
