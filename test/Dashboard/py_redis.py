import redis
import numpy as np

# check
def check_data(Grid):
	print(Grid[100][100])
	print(np.sum(Grid))

def get_redis_data():
	redis_conn = connect_to_redis()
	if redis_conn is not None:
		data = fetch_data(redis_conn)
		return data if np.sum(data) > 0 else None
	else:
		return None

def connect_to_redis(host='localhost', port = 6379):
	try:
		r = redis.Redis(host = host, port = port, db=0)
		return r
	except Exception as e:
		print(e)
		return None

def fetch_data(redis_connection):
	# 讀取所有鍵
	keys = redis_connection.keys('GridSum:*')
	# 初始化二維矩陣 row = 240, cols = 220
	num_rows = 240
	num_cols = 220
	Grid = np.zeros((num_rows, num_cols), dtype=np.int32)
	# fill in data
	# 遍歷所有鍵，從Redis中讀取對應的值並填充到矩陣中
	for key in keys:
		# 解析鍵以獲取行和列
		row, col = map(int, key.decode().split(':')[1:])
		# 從Redis中讀取值
		value = int(redis_connection.get(key))
		# 將值填充到矩陣中
		Grid[row][col] = value

	# check_data(Grid)
	return Grid

# if __name__ == '__main__':
# 	# connect and get data
# 	data = get_redis_data()
