package db

import (
	"context"
	"fmt"
	"github.com/redis/go-redis/v9"
	"time"
)

// GridSum紀錄所有網隔的總數
type GridSum struct {
	Rows    int
	Cols    int
	GridSum [][]int
}

// RedisConnection 連接到 Redis 伺服器並返回 Redis 客戶端
func RedisConnection() (*redis.Client, error) {
	// 連接到 Redis 伺服器
	client := redis.NewClient(&redis.Options{
		Addr:     "localhost:6379", // 你的 Redis 伺服器位址
		Password: "",               // Redis 伺服器密碼 (如果有的話)
		DB:       0,                // 選擇 Redis 資料庫
	})

	// 測試連線
	pong, err := client.Ping(context.Background()).Result()
	fmt.Println("Redis Connection Ping:", pong, err)

	return client, err
}

func SaveGridSum(Grid [][]int, client *redis.Client, expire_time int) {
	// 將二維矩陣的點總和存儲到 Redis 中
	for row := 0; row < len(Grid); row++ {
		for col := 0; col < len(Grid[row]); col++ {
			key := fmt.Sprintf("GridSum:%d:%d", row, col) // 生成 Redis 鍵
			value := Grid[row][col]                       // 對應位置的點總和
			// 設定鍵值對 10秒後過期
			err := client.Set(context.Background(), key, value, time.Duration(expire_time)*time.Second).Err()
			// err := client.Set(context.Background(), key, value, 0).Err()
			if err != nil {
				fmt.Println("Error:", err)
				return
			}
		}
	}
}

func QueryGridSum(row int, col int, client *redis.Client) {
	// 從 Redis 中查詢點總和資料
	r := row
	c := col
	key := fmt.Sprintf("GridSum:%d:%d", r, c)                 // 生成 Redis 鍵
	value, err := client.Get(context.Background(), key).Int() // 從 Redis 取得值
	if err == redis.Nil {
		fmt.Println("Key does not exist")
	} else if err != nil {
		fmt.Println("Error:", err)
	} else {
		fmt.Printf("GridSum[%d][%d] = %d\n", r, c, value)
	}
}

