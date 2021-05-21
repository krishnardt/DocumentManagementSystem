from lockfile import LockFile, LockTimeout
import CONSTANTS
filename= CONSTANTS.FILE_DIR+"/password.txt"
lock = LockFile(filename)
#lock.break_lock()
print(lock.i_am_locking())
# lock.break_lock()
print(lock.is_locked())
# lock.release()
lock.acquire()
while lock.i_am_locking():
	try:
	    
	    print(lock.is_locked())    # wait up to 60 seconds
	    print(lock.i_am_locking())
	    fb = open(filename, 'r')
	    da = fb.readlines()
	    for d in da[:1000000]:
	    	print(d)
	    fb.close()
	    lock.release()
	except LockTimeout:
	    print("enterd into exception")
	    lock.break_lock()
	    lock.acquire()
	print(lock.is_locked())
	print(lock.i_am_locking())
	print("I locked", lock.path)
if lock.is_locked():
	lock.release()


# while not lock.i_am_locking():
# 	try:
# 		lock.acquire(timeout=5)
# 		print(lock.is_locked())    # wait up to 60 seconds
# 		print(lock.i_am_locking())

# 		with open(filename, 'a') as fb:
# 			print(fb.write("hello "))

# 		print(lock.is_locked())    # wait up to 60 seconds
# 		print(lock.i_am_locking())
# 	except:
# 		lock.break_lock()
# 		lock.release()
# lock.release()
