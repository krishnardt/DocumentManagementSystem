from lockfile import LockFile, LockTimeout
filename= "/home/spyder/Documents/DocumentManagementService/BLOBS/password.txt"
lock = LockFile(filename)

print(lock.is_locked())