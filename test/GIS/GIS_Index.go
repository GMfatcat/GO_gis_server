package gis

import (
	"fmt"
	"math"
	"os"
	"encoding/gob"
)

// ------------------ Config ----------------- //
// Coordinate 為自定義的座標資訊結構
type Coordinate struct {
	Lon float64
	Lat float64
}

// Grid 為自定義的網格結構
type Grid struct {
	Rows int
	Cols int
	Grid [][][]Coordinate
}

var (
	MinLat   float64 = 20.6833
	MaxLat   float64 = 25.3005
	MinLon   float64 = 118.0669
	MaxLon   float64 = 122.0201
	GridSize float64 = 2.0 // 網格大小，單位為公里
)

// ------------------ Function ----------------- //
// register struct to save gob binary data of Grid
func init() {
	gob.Register(Grid{})
	gob.Register(Coordinate{})
}
// -1 = undefined
func GetRowsCols(
	lat float64,
	lon float64,
	minLat float64,
	maxLat float64,
	minLon float64,
	maxLon float64,
	gridSize float64,
) (
	rows int,
	cols int,
) {

	// if no assign use the global value
	if minLat == -1.0 {
		minLat = MinLat
	}
	if maxLat == -1.0 {
		maxLat = MaxLat
	}
	if minLon == -1.0 {
		minLon = MinLon
	}
	if maxLon == -1.0 {
		maxLon = MaxLon
	}
	if gridSize == -1.0 {
		gridSize = GridSize
	}

	// lat & lon = 0 --> calculate (all_rows & all_cols) --> remain same
	// if calculate certain lat and lon --> maxLon & maxLat replace by lat and lon
	if lat != -1.0 && lon != -1.0 {
		maxLon = lon
		maxLat = lat
	}

	// 換算經度方向上的網格數
	cols = int(math.Ceil((maxLon - minLon) / (gridSize / 111)))
	// 換算緯度方向上的網格數
	cosLat := math.Cos(minLat * math.Pi / 180) // 轉換為弧度
	rows = int(math.Ceil((maxLat - minLat) / (gridSize / (111 * cosLat))))
	// return
	return rows, cols
}

// 初始化 Grid
func NewGrid(rows int, cols int) *Grid {
	g := &Grid{
		Rows: rows,
		Cols: cols,
		Grid: make([][][]Coordinate, rows),
	}
	for i := 0; i < rows; i++ {
		g.Grid[i] = make([][]Coordinate, cols)
		for j := 0; j < cols; j++ {
			g.Grid[i][j] = make([]Coordinate, 0)
		}
	}
	return g
}

// 將座標資訊存入 Grid 中的指定 row 和 col
func (g *Grid) AddCoordinate(row, col int, coord Coordinate) {
	g.Grid[row][col] = append(g.Grid[row][col], coord)
}

// 從 Grid 中取得指定 row 和 col 對應的座標資訊
func (g *Grid) GetCoordinates(row, col int) []Coordinate {
	return g.Grid[row][col]
}

// 將 Grid 資料以二進制格式寫入檔案
func SaveGrid(grid *Grid, filename string) error {
	file, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer file.Close()

	encoder := gob.NewEncoder(file)
	err = encoder.Encode(grid)
	if err != nil {
		return err
	}

	fmt.Println("Grid data has been written to", filename)
	return nil
}

/*
func main() {

	// start time
	startTime := time.Now()
	// 計算所有網格的行數和列數 --> -1.0 as use GLOBAL
	all_rows, all_cols := GetRowsCols(-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0)
	fmt.Printf("TOTAL col=%d, row=%d\n", all_cols, all_rows)
	// 初始化Grid
	grid := NewGrid(all_rows, all_cols)

	// 計算獨立測資的行數和列數
	lat := 25.12345
	lon := 121.98765
	row, col := GetRowsCols(lat, lon, -1.0, -1.0, -1.0, -1.0, -1.0)
	fmt.Printf("Lon=%f, Lat=%f : col=%d, row=%d\n", lon, lat, col, row)

	// 建立這組座標結構
	coord := Coordinate{
		Lon: lon,
		Lat: lat}
	// add to grid
	grid.AddCoordinate(row, col, coord)
	// see how many coords store in this grid
	this_grid_coordinates := grid.GetCoordinates(row, col)
	count := len(this_grid_coordinates)
	fmt.Printf("row=%d, col=%d 中共有 %d 組座標資訊:\n", row, col, count)

	for i, coord := range this_grid_coordinates {
		fmt.Printf("座標 %d: Lon=%f, Lat=%f\n", i+1, coord.Lon, coord.Lat)
	}

	elapsedTime := time.Since(startTime)
	fmt.Println("Elapsed Time (sec):", elapsedTime.Seconds())

}
*/
