import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import platform
import cgi
from fpdf import FPDF
from PIL import Image

# import cups  # For Linux/Mac
# import win32print  # For Windows

if platform.system() == "Windows":
    import win32print
    import win32api

else:
    import cups
# Global variables
UPLOAD_FOLDER = "generated_cards"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
selected_printer = None



class FileUploadHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        global selected_printer

        # Determine the type of request (JSON or file upload)
        ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
        
        if ctype == "application/json":
            # Handle JSON card data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            card_data = json.loads(post_data)

            masterId = card_data.get('masterId')
            name= card_data.get('name')
            father_name = card_data.get('fatherName')
            date_of_birth = card_data.get('dateOfBirth')
            birth_place = card_data.get('birthPlace')
            district = card_data.get('district')
            local_level = card_data.get('localLevel')
            ward_no = card_data.get('wardNo')
            issue_office = card_data.get('issueOffice')
            card_holder_photo = card_data.get('cardHolderPhoto')
            card_holder_signature = card_data.get('cardHolderSignature')
            gender = card_data.get('gender')

            officer_name = card_data.get('officerName')
            designation = card_data.get('designation')
            issued_date = card_data.get('issueDate')
            issuerSignature = card_data.get('issuerSignature')
            card_data = card_data.get('cardNo')


            # Generate QR code for the card
            from frontbackdesign import CardData, create_back_card, create_front_card

            card_data = CardData(card_no=str(card_data), 
                                masterId = masterId,
                                full_name=name, 
                                father_name=father_name, 
                                place_of_birth= birth_place, 
                                # address="Mugu District,  10 ward", 
                                ward= str(ward_no),
                                sex= gender, 
                                district=district, 
                                officer_name=officer_name, 
                                designation=designation, 
                                localLevel=local_level, 
                                issued_date=str(issued_date),
                                issueOffice=issue_office,
                                cardHolderPhoto = card_holder_photo,
                                cardHolderSignature=card_holder_signature,
                                issuerSignature=issuerSignature
                                )
            




def print_file(file_path, printer_name):
    if platform.system() == "Linux" or platform.system() == "Darwin":
        try:
            conn = cups.Connection()
            job_id = conn.printFile(printer_name, file_path, "ID Card Print Job", {})
            print(f"Job submitted successfully. Job ID: {job_id}")
        except Exception as e:
            print(f"Error printing file: {e}")
    elif platform.system() == "Windows":
        try:
            win32print.SetDefaultPrinter(printer_name)
            win32api.ShellExecute(0, "print", file_path, None, ".", 0)
        except Exception as e:
            print(f"Error printing file: {e}")



class PrinterManager:
    @staticmethod
    def get_printers():
        printers = []
        if platform.system() == "Windows":
            try:
                for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS):
                    printer_name = printer[2]
                    p_handle = win32print.OpenPrinter(printer_name)
                    printer_info = win32print.GetPrinter(p_handle, 2)
                    status = printer_info[18]
                    win32print.ClosePrinter(p_handle)
                    
                    status_str = "Ready"
                    if status & win32print.PRINTER_STATUS_OFFLINE:
                        status_str = "Offline"
                    elif status & win32print.PRINTER_STATUS_ERROR:
                        status_str = "Error"
                    elif status & win32print.PRINTER_STATUS_BUSY:
                        status_str = "Busy"
                    
                    printers.append((printer_name, status_str))
            except Exception as e:
                print(f"Error getting Windows printers: {e}")
        else:
            try:
                conn = cups.Connection()
                printers_dict = conn.getPrinters()
                for printer_name, printer_info in printers_dict.items():
                    status = printer_info.get('printer-state', 'unknown')
                    status_str = {
                        3: "Idle",
                        4: "Processing",
                        5: "Stopped"
                    }.get(status, "Unknown")
                    printers.append((printer_name, status_str))
            except Exception as e:
                print(f"Error getting CUPS printers: {e}")
        
        return printers

class PrinterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Localhost File Printer")
        self.root.geometry("700x400")
        
        # Create main frame with padding
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Server status label
        self.status_label = ttk.Label(
            main_frame, 
            text="Server Status: Running on http://localhost:9101",
            font=("Arial", 10)
        )
        self.status_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Printer selection frame
        printer_frame = ttk.LabelFrame(main_frame, text="Printer Selection", padding="10")
        printer_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        # Printer dropdown
        self.printer_var = tk.StringVar()
        self.printer_dropdown = ttk.Combobox(
            printer_frame, 
            textvariable=self.printer_var,
            state="readonly",
            width=40
        )
        self.printer_dropdown.grid(row=0, column=0, padx=5, pady=5)
        
        # Refresh button
        refresh_btn = ttk.Button(
            printer_frame,
            text="⟳",
            width=3,
            command=self.refresh_printers
        )
        refresh_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # Select printer button
        select_btn = ttk.Button(
            printer_frame,
            text="Select Printer",
            command=self.select_printer
        )
        select_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Currently selected printer frame
        selected_frame = ttk.LabelFrame(main_frame, text="Current Printer", padding="10")
        selected_frame.grid(row=2, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        # Selected printer label
        self.selected_label = ttk.Label(
            selected_frame,
            text="No printer selected",
            font=("Arial", 10, "bold")
        )
        self.selected_label.grid(row=0, column=0, pady=5)
        
        # Printer status label
        self.printer_status = ttk.Label(selected_frame, text="Status: Not Selected")
        self.printer_status.grid(row=1, column=0, pady=5)
        
        # Exit button
        exit_btn = ttk.Button(
            main_frame,
            text="Exit",
            command=root.quit,
            style="Accent.TButton"
        )
        exit_btn.grid(row=3, column=0, columnspan=3, pady=20)
        
        # Initialize printers
        self.refresh_printers()
        
        # Set up periodic refresh
        self.root.after(5000, self.periodic_refresh)



    def refresh_printers(self):
        printers = PrinterManager.get_printers()
        self.printers_dict = {f"{name} ({status})": name for name, status in printers}
        self.printer_dropdown['values'] = list(self.printers_dict.keys())
            
        if self.printer_var.get() not in self.printer_dropdown['values']:
            self.printer_var.set('')


    def select_printer(self):
        global selected_printer
        selection = self.printer_var.get()
        
        if not selection:
            messagebox.showwarning("Warning", "Please select a printer first!")
            return
            
        selected_printer = self.printers_dict[selection]
        status = selection.split('(')[1].rstrip(')')
        
        # Update UI
        self.selected_label.config(text=f"Selected Printer: {selected_printer}")
        self.printer_status.config(text=f"Status: {status}")
        
        # Show success message
        messagebox.showinfo("Success", f"Printer '{selected_printer}' has been selected!")
        print(f"Selected printer: {selected_printer}")

    def periodic_refresh(self):
        self.refresh_printers()
        # Update status of selected printer if one is selected
        if selected_printer:
            for printer_info in self.printer_dropdown['values']:
                if selected_printer in printer_info:
                    status = printer_info.split('(')[1].rstrip(')')
                    self.printer_status.config(text=f"Status: {status}")
                    break
        self.root.after(5000, self.periodic_refresh)




def start_server():
    server_address = ('localhost', 9101)
    httpd = HTTPServer(server_address, FileUploadHandler)
    print("Server running on http://localhost:9101")
    httpd.serve_forever()

if __name__ == "__main__":
    # Start server thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Start GUI
    root = tk.Tk()
    app = PrinterApp(root)  # Using the PrinterApp class from previous code
    root.mainloop()