from logit import Logit
import time

def main():
	log = Logit("my-project-tag","my-app-tag-A")
	for i in range(0,1000):
		log.debug("my-tag-A", "this is is a debug message this is is a debug message ")

	print("logged data A...")

	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		log.stop()
		
	log.join()
	


if __name__ == "__main__":
	main()

    
