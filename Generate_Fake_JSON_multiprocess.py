import json
import uuid
import time
import datetime
import os
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool, cpu_count

################################################################
# TW lat & lon boundaries
tw_boundary = {
	"min_lat": 20.6833,
	"max_lat": 25.3005,
	"min_lon": 118.0669,
	"max_lon": 122.0201,
}
# save massive data there
data_path = r"D:\Fake_Data\Data_multiprocess"

BATCH_MAX_NUM = 120

DATA_MIN = 1e4
DATA_MAX = 5 * 1e4
################################################################

def progress_bar(width: int, iters: int):
    for i in range(1, width + 1):
        # time.sleep(duration) :.2f
        strbarwidth = f"[{'#' * iters}{'-' * (width - iters)}] - {round((iters) * (100/width))}%\r"
        print(strbarwidth, end='')

def generate_coordinates() -> float:
	lon = np.random.uniform(tw_boundary["min_lon"], tw_boundary["max_lon"])
	lat = np.random.uniform(tw_boundary["min_lat"], tw_boundary["max_lat"])
	return lon, lat

# TODO: Consider that some users will be the same in different times -> UID may not always be different
def generate_userid() -> str:
	return str(uuid.uuid4())

def generate_time(current_batch : int) -> str:
	year = 2023
	month = 4
	day = 1
	hour = 10
	minute = 10 + (current_batch * 5) // 60
	second = (current_batch * 5) % 60 + np.random.randint(0, 5)

	if minute >= 60:
		hour += minute // 60
		minute %= 60
	if hour >= 24:
		day += hour // 24
		hour %= 24

	# return a datetime string
	dt = datetime.datetime(year, month, day, hour, minute, second)
	return dt.strftime("%Y-%m-%d %H:%M:%S")

def save_data(user_id, lon, lat, time, folder_path):
	data = {
	"user_id": user_id,
	"longitude": lon,
	"latitude": lat,
	"time": time
	}
	# set filename
	time_str = time.replace(":", "-").replace(" ", "_")
	filename = f"data_{time_str}_{user_id}.json"
	with open(os.path.join(folder_path, filename), "w") as file:
		json.dump(data, file)

def process_data(user_id, lon, lat, time, full_folder_path):
    save_data(user_id, lon, lat, time, full_folder_path)

def batch_generate(batch_num : int) -> int:
	# make a dir
	dir_name = f"batch_{batch_num}"
	full_folder_path = os.path.join(data_path,dir_name)
	os.makedirs(full_folder_path, exist_ok=True)

	# random decide how many data to generate in this batch
	data_num = np.random.randint(DATA_MIN,DATA_MAX)

	# generate data in generator style to save memory
	def generate_data(full_folder_path = full_folder_path):
		# Generate data
		for _ in range(data_num):
			lon, lat = generate_coordinates()
			user_id = generate_userid()
			time = generate_time(current_batch = batch_num)
			yield user_id, lon, lat, time, full_folder_path

	# multi process
	with Pool(cpu_count()) as pool:
		pool.starmap(process_data, generate_data())

	# return data_num for visualization
	return data_num

def draw_data(data:list) -> None:
	plt.title("Fake Data Distribution (Multi-Process)")
	plt.xlabel("Batch")
	plt.ylabel("Data")
	plt.bar(range(len(data)), data)
	plt.tight_layout()
	# save plot with the same directory as code -> not convinent to enter data storage directory
	plt.savefig("Fake_Data_Distribution_multi_process.png",dpi = 300)

def main():
	# start
	BATCH_NUM = []
	print("START GENERATING FAKE DATA....")
	st = time.time()
	for batch_num in range(1,BATCH_MAX_NUM + 1):
		data_num = batch_generate(batch_num)
		BATCH_NUM.append(data_num)
		# show progress
		progress_bar(BATCH_MAX_NUM,batch_num)

	print("")
	draw_data(BATCH_NUM)
	end = time.time()
	print(f"FINISH GENERATING FAKE DATA in {(end-st)/60:.2f} min")

if __name__ == '__main__':
	main()