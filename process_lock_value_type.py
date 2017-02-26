

# This class encapsulates the parameters to uniquely identify a process and the port it is listening on.
# 1. The type of the class
# 2. The fully qualified domain name
# 3. The process's PID
# 4. The port the process in listening on
class ProcessLockValueType:
    def __init__(self, fqdn, pid, port):
        self.type = 'ProcessLockValueType'
        self.fqdn = fqdn
        self.pid = pid
        self.port = port
