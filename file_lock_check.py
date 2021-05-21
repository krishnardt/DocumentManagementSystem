from lockfile import LockFile, LockTimeout
import CONSTANTS
filename= CONSTANTS.FILE_DIR+"/password.txt"
lock = LockFile(filename)

print(lock.is_locked())