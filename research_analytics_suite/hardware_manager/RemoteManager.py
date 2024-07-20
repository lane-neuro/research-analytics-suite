"""
RemoteManager

This module contains the RemoteManager class, which manages remote servers for GPU and CPU tasks.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import paramiko


class RemoteManager:
    def __init__(self, logger, known_hosts_file, remote_servers=None):
        """Initialize RemoteManager with logger, known hosts file, and optional remote servers list.

        Args:
            logger (Logger): The logger instance for logging messages.
            known_hosts_file (str): Path to the known hosts file.
            remote_servers (list, optional): List of remote servers. Defaults to None.
        """
        self.logger = logger
        self.known_hosts_file = known_hosts_file
        self.remote_servers = remote_servers or []

    def connect_to_remote_server(self, hostname, username, password):
        """Connect to a remote server via SSH and execute commands.

        Args:
            hostname (str): The hostname of the remote server.
            username (str): The username for SSH login.
            password (str): The password for SSH login.

        Returns:
            paramiko.SSHClient: The SSH client connection or None if connection fails.
        """
        self.logger.info(f"Connecting to remote server {hostname}...")
        try:
            ssh = paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.load_host_keys(self.known_hosts_file)
            ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
            ssh.connect(hostname, username=username, password=password)
            self.logger.info(f"Connected to {hostname}")
            return ssh
        except paramiko.ssh_exception.SSHException as e:
            self.logger.error(f"Failed to connect to {hostname}: {e}")
            return None

    def manage_remote_server(self, server, command):
        """Manage tasks on a remote server.

        Args:
            server (dict): Information about the remote server.
            command (str): The command to execute on the remote server.
        """
        ssh = self.connect_to_remote_server(server['hostname'], server['username'], server['password'])
        if not ssh:
            self.logger.error(f"Failed to connect to {server['hostname']}: Connection error")
            return

        try:
            self.logger.info(f"Managing tasks on remote server {server['hostname']}...")
            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode()
            self.logger.info(f"Output from remote server {server['hostname']}: {output}")
        except Exception as e:
            self.logger.error(f"Error managing tasks on remote server {server['hostname']}: {e}")
        finally:
            ssh.close()
