import platform
import subprocess


class EthernetDetector:
    def __init__(self, logger):
        self.logger = logger
        self.os_info = platform.system().lower()

    def detect_ethernet(self):
        """Detect Ethernet connections.

        Returns:
            list: Information about detected Ethernet connections.
        """
        self.logger.info("Detecting Ethernet connections...")

        if self.os_info == 'linux':
            return self._detect_ethernet_linux()
        elif self.os_info == 'windows':
            return self._detect_ethernet_windows()
        elif self.os_info == 'darwin':
            return self._detect_ethernet_macos()
        else:
            self.logger.error(f"Ethernet detection not supported on {self.os_info} platform.")
            return []

    def _detect_ethernet_linux(self):
        """Detect Ethernet connections on Linux."""
        try:
            output = self._read_ethernet_output_linux()
            ethernet_connections = self._parse_ethernet_output_linux(output)
            self.logger.info(f"Detected Ethernet connections: {ethernet_connections}")
            return ethernet_connections
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect Ethernet connections: {e}")
            return []

    def _read_ethernet_output_linux(self):
        """Read Ethernet connection information on Linux."""
        result = subprocess.run(['ip link show'], capture_output=True, text=True, shell=True, check=True)
        return result.stdout

    def _parse_ethernet_output_linux(self, output):
        """Parse the output to find Ethernet connections on Linux."""
        return [line.split(" qdisc")[0] for line in output.split('\n') if 'state UP' in line]

    def _detect_ethernet_windows(self):
        """Detect Ethernet connections on Windows."""
        try:
            output = self._read_ethernet_output_windows()
            ethernet_connections = self._parse_ethernet_output_windows(output)
            self.logger.info(f"Detected Ethernet connections: {ethernet_connections}")
            return ethernet_connections
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect Ethernet connections: {e}")
            return []

    def _read_ethernet_output_windows(self):
        """Read Ethernet connection information on Windows."""
        result = subprocess.run(['powershell', 'Get-NetAdapter -Physical | Where-Object { $_.Status -eq "Up" }'],
                                capture_output=True, text=True, shell=True, check=True)
        return result.stdout

    def _parse_ethernet_output_windows(self, output):
        """Parse the output to find Ethernet connections on Windows."""
        lines = output.split('\n')
        adapters = []
        for i in range(0, len(lines), 2):
            if i+1 < len(lines) and "Name" in lines[i] and "Status" in lines[i+1]:
                adapters.append(lines[i].strip())
                adapters.append(lines[i+1].strip())
        return adapters

    def _detect_ethernet_macos(self):
        """Detect Ethernet connections on macOS."""
        try:
            output = self._read_ethernet_output_macos()
            ethernet_connections = self._parse_ethernet_output_macos(output)
            self.logger.info(f"Detected Ethernet connections: {ethernet_connections}")
            return ethernet_connections
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect Ethernet connections: {e}")
            return []

    def _read_ethernet_output_macos(self):
        """Read Ethernet connection information on macOS."""
        result = subprocess.run(['ifconfig'], capture_output=True, text=True, check=True)
        return result.stdout

    def _parse_ethernet_output_macos(self, output):
        """Parse the output to find Ethernet connections on macOS."""
        lines = output.split('\n')
        active_connections = []
        for i in range(len(lines)):
            if 'status: active' in lines[i]:
                active_connections.append(lines[i-1].strip())
        return active_connections

    def read_ethernet_data(self):
        """Read data from Ethernet connection.

        Returns:
            str: Data read from Ethernet connection.
        """
        self.logger.info("Reading data from Ethernet connection...")

        if self.os_info == 'linux':
            return self._read_data_linux()
        elif self.os_info == 'windows':
            return self._read_data_windows()
        elif self.os_info == 'darwin':
            return self._read_data_macos()
        else:
            self.logger.error(f"Ethernet data reading not supported on {self.os_info} platform.")
            return ""

    def _read_data_linux(self):
        """Read data from Ethernet connection on Linux."""
        try:
            output = subprocess.run(['cat', '/proc/net/dev'], capture_output=True, text=True, check=True)
            self.logger.info("Data read from Ethernet connection.")
            return output.stdout
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to read data from Ethernet connection: {e}")
            return ""

    def _read_data_windows(self):
        """Read data from Ethernet connection on Windows."""
        try:
            output = subprocess.run(['powershell', 'Get-NetAdapterStatistics'], capture_output=True, text=True, shell=True, check=True)
            self.logger.info("Data read from Ethernet connection.")
            return output.stdout
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to read data from Ethernet connection: {e}")
            return ""

    def _read_data_macos(self):
        """Read data from Ethernet connection on macOS."""
        try:
            output = subprocess.run(['netstat', '-ib'], capture_output=True, text=True, check=True)
            self.logger.info("Data read from Ethernet connection.")
            return output.stdout
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to read data from Ethernet connection: {e}")
            return ""

    def transmit_ethernet_data(self, data):
        """Transmit data over Ethernet connection.

        Args:
            data (str): Data to be transmitted.

        Returns:
            bool: True if data transmission was successful, False otherwise.
        """
        self.logger.info("Transmitting data over Ethernet connection...")

        if self.os_info == 'linux':
            return self._transmit_data_linux(data)
        elif self.os_info == 'windows':
            return self._transmit_data_windows(data)
        elif self.os_info == 'darwin':
            return self._transmit_data_macos(data)
        else:
            self.logger.error(f"Ethernet data transmission not supported on {self.os_info} platform.")
            return False

    def _transmit_data_linux(self, data):
        """Transmit data over Ethernet connection on Linux."""
        try:
            # Example command to simulate data transmission
            subprocess.run(['echo', data, '|', 'nc', 'localhost', '12345'], check=True, shell=True)
            self.logger.info("Data transmitted over Ethernet connection.")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to transmit data over Ethernet connection: {e}")
            return False

    def _transmit_data_windows(self, data):
        """Transmit data over Ethernet connection on Windows."""
        try:
            # Example command to simulate data transmission
            subprocess.run(['powershell', f'echo {data} | Out-File -FilePath C:\\Temp\\output.txt'], check=True, shell=True)
            self.logger.info("Data transmitted over Ethernet connection.")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to transmit data over Ethernet connection: {e}")
            return False

    def _transmit_data_macos(self, data):
        """Transmit data over Ethernet connection on macOS."""
        try:
            # Example command to simulate data transmission
            subprocess.run(['echo', data, '|', 'nc', 'localhost', '12345'], check=True, shell=True)
            self.logger.info("Data transmitted over Ethernet connection.")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to transmit data over Ethernet connection: {e}")
            return False
