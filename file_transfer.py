import paramiko
from subprocess import call
from datetime import datetime



class SSHConnection(object):


    def __init__(self, host, username, password, port=22):
        # * Initialize and setup connection
        self.sftp = None
        self.sftp_open = False
        # * Open SSH Transport stream
        self.transport = paramiko.Transport((host, port))
        self.transport.connect(username=username, password=password)


    def _openSFTPConnection(self):
        # * Opens an SFTP connection if not already open
        if not self.sftp_open:
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            self.sftp_open = True


    def get(self, remote_path, local_path=None):
        # * Copies a file from the remote host to the local host.
        self._openSFTPConnection()
        self.sftp.get(remote_path, local_path)


    def put(self, local_path, remote_path=None):
        # * Copies a file from the local host to the remote host
        self._openSFTPConnection()
        self.sftp.put(local_path, remote_path)


    def close(self):
        # * Close SFTP connection and ssh connection
        if self.sftp_open:
            self.sftp.close()
            self.sftp_open = False
        self.transport.close()



def file_transfer(origin_direct, origin_file_name, dest_direct, dest_file_name, host, username, password, port):
    ### * File Transfer Any Server * ###
    try:
        ssh = SSHConnection(host, username, password, port)
        ssh.put(origin_direct + origin_file_name, dest_direct + dest_file_name)
        print('File Transfered At Backup Location - {}'.format(str(dest_direct + dest_file_name)))
    except Exception as e:
        print('File Not Transfered At Backup Location - {}'.format(str(e)))
    finally:
        ssh.close()


def cp_dir(source, target):
    ### * Copy Directory * ###
    try:
        call(['cp', '-a', source, target])
        print("Directory Copied To - {}".format(target))
    except Exception as e:
        print("Directory Not Copied - {}".format(target))


def cp_file(source, target):
    ### * Copy File * ###
    try:
        call(['cp', source, target])
        print("File Copied To - {}".format(target))
        print("Transfer Done  at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
    except Exception as e:
        print("File Not Copied - {}".format(target))


def mv_file(source, target):
    ### * Move File * ###
    try:
        call(['mv', source, target])
        print("File Moved To - {}".format(target))
        print("Transfer Done  at {} ".format(datetime.now().strftime(r'%d-%m-%Y %H:%M:%S')))
    except Exception as e:
        print("File Not Moved - {}".format(target))



if __name__ == "__main__":
    pass
    # ssh = SSHConnection(host= "192.168.1.205", username= "bechpsp", password="J6Hsaiuhw#1220")
    # ssh.get(remote_path="/home/bechpsp/DEV/static.zip", 
    # local_path="/home/compsan/DEV/static.zip")
    # ssh.close()
