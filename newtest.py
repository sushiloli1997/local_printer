import platform
import subprocess

class PrinterManager:
    @staticmethod
    def get_printers():
        printers = []
        if platform.system() == "Windows":
            try:
                # Query all printers
                command = 'wmic printer get name, printerstatus, workoffline'
                result = subprocess.run(command, capture_output=True, text=True, shell=True)
                
                if result.returncode == 0:
                    print("Printer Statuses:\n")
                    lines = result.stdout.splitlines()
                    headers = lines[0].split()
                    printers_status = lines[1:]

                    for printer in printers_status:
                        if printer.strip():  # Avoid empty lines
                            printer_info = printer.split()
                            printer_name = ' '.join(printer_info[:-2])  # Printer name might have spaces
                            printer_status = printer_info[-2]
                            printer_offline = printer_info[-1]

                            # Map status code to human-readable status
                            status_str = "Unknown"
                            if printer_status == "3":
                                status_str = "Idle"
                            elif printer_status == "4":
                                status_str = "Printing"
                            elif printer_status == "5":
                                status_str = "Warming Up"
                            elif printer_offline.lower() == "true":
                                status_str = "Offline"
                            else:
                                status_str = "Ready"

                            printers.append((printer_name, status_str))
                else:
                    print(f"Failed to get printers status: {result.stderr}")
            except Exception as e:
                print(f"Error checking printers status: {e}")
        return printers
