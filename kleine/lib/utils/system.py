import platform, ifcfg, subprocess, os, psutil, sys, logging
from contextlib import contextmanager

from pyxavi import Config, Dictionary
from kleine.lib.abstract.pyxavi import PyXavi

class System(PyXavi):

    def __init__(self, config: Config = None, params: Dictionary = None):
        super(System, self).init_pyxavi(config=config, params=params)

    @staticmethod
    def get_os_info():
        info = platform.uname()
        return {
            "system": info.system,
            "node": info.node,
            "release": info.release,
            "version": info.version,
            "machine": info.machine,
            "processor": info.processor,
        }

    @staticmethod
    def get_network_interfaces():
        # (dict[2]){
        # "en0": (dict[4]){"ip": (str[12])"192.168.0.36", "netmask": (str[13])"255.255.255.0", "broadcast": (str[13])"192.168.0.255", "mac": (str[17])"5c:e9:1e:b4:15:cf"},
        # "bridge100": (dict[4]){"ip": (str[12])"192.168.64.1", "netmask": (str[13])"255.255.255.0", "broadcast": (str[14])"192.168.64.255", "mac": (str[17])"5e:e9:1e:4b:9e:64"}
        # }
        interfaces = ifcfg.interfaces()
        info: dict = {}
        for name, data in interfaces.items():
            if data.get("status", None) == "active" and data.get("inet", None) is not None:
                info[name] = {
                    "ip": data.get("inet"),
                    "netmask": data.get("netmask"),
                    "broadcast": data.get("broadcast"),
                    "mac": data.get("ether"),
                }
        return info

    @staticmethod
    def get_default_network_interface():
        data = ifcfg.default_interface()
        return {
            "name": data.get("name"),
            "ip": data.get("inet"),
            "netmask": data.get("netmask"),
            "broadcast": data.get("broadcast"),
            "mac": data.get("ether"),
        }

    @staticmethod
    def get_connected_wifi_info():
        """
        Get the list of available WiFi networks
        """
        os = platform.system()
        networks = []

        if os.lower() == "linux":
            # Use nmcli to get WiFi networks
            result = subprocess.run(['nmcli', '-t', '-f', 'SSID,SECURITY,SIGNAL', 'dev', 'wifi'], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE, 
                                    text=True)
            lines = result.stdout.strip().split('\n')
            for line in lines:
                parts = line.split(':')
                if len(parts) >= 3:
                    ssid = parts[0]
                    security = parts[1]
                    signal = parts[2]
                    networks.append({
                        "ssid": ssid,
                        "security": security,
                        "signal": signal
                    })
        elif os.lower() == "windows":
            # Use netsh to get WiFi networks
            wifi = subprocess.check_output(['netsh', 'WLAN', 'show', 'interfaces'])
            data = wifi.decode('utf-8')
            lines = data.split('\n')
            for line in lines:
                if "SSID" in line:
                    ssid = line.split(':')[1].strip()
                    networks.append({
                        "ssid": ssid
                    })
        elif os.lower() == "darwin":
            import macwifi

            data = macwifi.get_wifi_info()
            lines = data.split('\n')
            info = {}
            for line in lines:
                if "SSID" in line and "BSSID" not in line:
                    ssid = line.split(':')[1].strip()
                    info["ssid"] = ssid
                if "link auth" in line:
                    security = line.split(':')[1].strip()
                    info["security"] = security

            if info:
                networks.append(info)
                info = {}
        else:
            # Unsupported OS for WiFi scanning
            pass
        return networks

    @staticmethod
    def power_off_system():
        os = platform.system()
        try:
            if os.lower() == "linux":
                subprocess.run(['sudo', 'poweroff'])
            elif os.lower() == "windows":
                subprocess.run(['shutdown', '/s', '/t', '0'])
            elif os.lower() == "darwin":
                subprocess.run(['sudo', 'shutdown', '-h', 'now'])
            else:
                raise NotImplementedError(f"Power off not implemented for OS: {os}")
        except Exception as e:
            print(f"Error powering off system: {e}")
    
    @staticmethod
    def reboot_system():
        os = platform.system()
        try:
            if os.lower() == "linux":
                subprocess.run(['sudo', 'reboot'])
            elif os.lower() == "windows":
                subprocess.run(['shutdown', '/r', '/t', '0'])
            elif os.lower() == "darwin":
                subprocess.run(['sudo', 'shutdown', '-r', 'now'])
            else:
                raise NotImplementedError(f"Reboot not implemented for OS: {os}")
        except Exception as e:
            print(f"Error rebooting system: {e}")
    
    def restart_program():
        """
        Restarts the current program, with file objects and descriptors cleanup
        https://stackoverflow.com/a/54445517
        """

        try:
            p = psutil.Process(os.getpid())
            for handler in p.open_files() + p.net_connections():
                os.close(handler.fd)
        except Exception as e:
            logging.error(e)

        python = sys.executable
        os.execl(python, python, "\"{}\"".format(sys.argv[0]))
    
    @contextmanager
    def change_directory(directory: str):
        original_cwd = os.getcwd()
        os.chdir(directory)
        try:
            yield
        finally:
            os.chdir(original_cwd)
    
    def update_and_restart_system(self) -> bool:
        try:
            with System.change_directory(os.getcwd()):

                # First we pull the changes from git in the current branch.
                completed_process = subprocess.run(['git', 'pull'], capture_output=True)

                if completed_process.returncode == 0:
                    self._xlog.info("Git pull successful.")
                else:
                    self._xlog.error(f"Git pull failed: {completed_process.stderr.decode()}")
                    self._xlog.debug(completed_process.stdout.decode())
                    return False
            
            # Now we run the possible update of the python packages
            completed_process = subprocess.run(['make', 'update'], capture_output=True)

            if completed_process.returncode == 0:
                self._xlog.info("Python packages updated successfully.")
            else:
                self._xlog.error(f"Python packages update failed: {completed_process.stderr.decode()}")
                self._xlog.debug(completed_process.stdout.decode())
                return False

            # Finally, we restart the program.
            self._xlog.info("Restarting the program...")
            System.restart_program()
        except Exception as e:
            print(f"Error updating and restarting system: {e}")