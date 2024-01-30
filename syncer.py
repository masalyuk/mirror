import paramiko
from scp import SCPClient

# SSH/SCP Parameters @

KEY_PATH = 'rem2'

class Syncer:
    def __init__(self, ip, port, local_in=None, local_out=None, remote_in=None, remote_out=None, user=None):
        self.ip = ip
        self.port = port
        self.user = user
        self.local_in = local_in
        self.local_out = local_out

        self.remote_in = remote_in
        self.remote_out = remote_out

        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(self.ip, self.port, username=user, pkey=paramiko.RSAKey.from_private_key_file(KEY_PATH))

    def send_to_remote(self):
        with SCPClient(self.ssh_client.get_transport()) as scp:
            scp.put(self.local_in, self.remote_in)
    
    def copy_to_local(self):
        try:
            with SCPClient(self.ssh_client.get_transport()) as scp:
                scp.get(self.remote_out, self.local_out)
        except:
            pass

