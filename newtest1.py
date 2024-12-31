import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import platform
import cgi
from fpdf import FPDF
import logging

logging.basicConfig(level=logging.INFO)



def show_error_message(message):
    messagebox.showerror("Error", message)

def show_info_message(message):
    messagebox.showinfo("Info", message)


def delete_card_files(file_path):
    try: 
        os.remove(file_path)
        print(f"{file_path}deleted Successfully.")
    except FileNotFoundError:
        print(f"Requested file not found: {file_path}")



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
            
            front_elements = [
            # Header Section
            {"type": "text", "text": "Government of Nepal", "position": (340, 10), "color": (255, 0, 0), "size": 34},
            {"type": "text", "text": "Ministry of Home Affairs", "position": (300, 50), "color": (255, 0, 0), "size": 40},
            {"type": "text", "text": "China Entry/Exit Pass for Nepalese Citizen", "position": (200, 90), "color": (255, 0, 0), "size": 34},
            
            # Details Section
            {"type": "text", "text": "Card No", "position": (50, 190), "color": (0, 0, 0), "size": 30},
            {"type": "text", "text": f": {card_data.card_no}", "position": (260, 190), "color": (0, 0, 0), "size": 30},
            {"type": "text", "text": "Full Name", "position": (50, 235), "color": (0, 0, 0), "size": 30},
            {"type": "text", "text": f": {card_data.full_name}", "position": (260, 235), "color": (0, 0, 0), "size": 30},
            {"type": "text", "text": "Father's Name", "position": (50, 280), "color": (0, 0, 0), "size": 30},
            {"type": "text", "text": f": {card_data.father_name}", "position": (260, 280), "color": (0, 0, 0), "size": 30},
            {"type": "text", "text": "Place of Birth", "position": (50, 325), "color": (0, 0, 0), "size": 30},
            {"type": "text", "text": f": {card_data.place_of_birth}", "position": (260, 325), "color": (0, 0, 0), "size": 30},

            # Address Section
            {"type": "text", "text": "Address", "position": (50, 370), "color": (0, 0, 0), "size": 30},
            {"type": "text", "text": f": {card_data.district} District", "position": (260, 370), "color": (0, 0, 0), "size": 30},
            {"type": "text", "text": f"{card_data.localLevel}", "position": (280, 415), "color": (0, 0, 0), "size": 30},
            {"type": "text", "text": f"{card_data.ward} Ward", "position": (280, 460), "color": (0, 0, 0), "size": 30},

            # Additional Information
            {"type": "text", "text": "Sex", "position": (640, 325), "color": (0, 0, 0), "size": 30},
            {"type": "text", "text": f": {card_data.sex}", "position": (700, 325), "color": (0, 0, 0), "size": 30},

            {"type": "text", "text": "Issue Office", "position": (50, 505), "color": (0, 0, 0), "size": 30},
            {"type": "text", "text": f": {card_data.issueOffice}", "position": (260, 505), "color": (0, 0, 0), "size": 30},
            #Profile Image
            {"type": "image", "data": card_data.get_cardHolderPhoto(), "position": (760, 208), "size": (225, 225)},
            
            ]


            back_elements = [
                {"type": "text", "text": "If found please return to nearest District Administration Office", "position": (30, 450), "color": (0, 0, 0), "size": 30},
                {"type": "text", "text": "Valid only for entry/exit purpose to china through land border", "position": (30, 480), "color": (0, 0, 0), "size": 30},
                {"type": "text", "text": "This pass shall be valid for five years and will be renewed if necessary", "position": (30, 510), "color": (0, 0, 0), "size": 30},
                {"type": "text", "text": "For more information about validity period please scan QR code", "position": (30, 540), "color": (0, 0, 0), "size": 30},

                {"type": "text", "text": "Card Holder's", "position": (50, 75), "color": (0, 0, 0), "size": 30},
                {"type": "text", "text": "Signature:", "position": (50, 130), "color": (0, 0, 0), "size": 30},

                {"type": "text", "text": "Officer's Name:", "position": (490, 120), "color": (0, 0, 0), "size": 30},
                {"type": "text", "text": card_data.officer_name, "position": (710, 120), "color": (0, 0, 0), "size": 30},
                {"type": "text", "text": "Designation:", "position": (490, 155), "color": (0, 0, 0), "size": 30},
                {"type": "text", "text": card_data.designation, "position": (710, 155), "color": (0, 0, 0), "size": 30},
                {"type": "text", "text": "Issued Date:", "position": (490, 190), "color": (0, 0, 0), "size": 30},
                {"type": "text", "text": card_data.issued_date, "position": (710, 190), "color": (0, 0, 0), "size": 30},

                # Add an image element (e.g., profile image)
                {"type": "image", "data": card_data.get_cardHolderSignature(), "position": (160, 140), "size": (125, 125)},
                {"type": "image", "data": card_data.get_issueSignature(), "position": (660, 230), "size": (125, 125)},
                
                {"type": "image", "data": card_data.qr_code_image(), "position": (2, 237), "size": (197, 197)},

                {"type": "text", "text": "Signature:", "position": (490, 225), "color": (0, 0, 0), "size": 30},
                {"type": "text", "text": "Card Issuing Authority:", "position": (550, 75), "color": (0, 0, 0), "size": 30},
            ]
            
            create_back_card(card_data, back_elements, 'generated_cards/back.png')
            create_front_card(card_data, front_elements,  'generated_cards/front.png')

            # Merge the front and back card images to pdf
            logging.info("Merging front and back card images to PDF...")
            try:
                create_card_pdf(
                    front_path='generated_cards/front.png',
                    back_path='generated_cards/back.png',
                    output_path='generated_cards/card.pdf'
                )
            except Exception as e:
                print(f"Error creating PDF: {e}")
                self.send_response(500)
                self.end_headers()
                return



def create_card_pdf(front_path: str,back_path: str,output_path: str):
    try:
        # Verify input files exist
        if not os.path.exists(front_path):
            raise FileNotFoundError(f"Front image not found: {front_path}")
        if not os.path.exists(back_path):
            raise FileNotFoundError(f"Back image not found: {back_path}")
        
        page_height = 85.6 
        page_width = 54
        # Create PDF object with A4 Landscape
        pdf = FPDF(orientation='L', unit='mm', format=(page_width, page_height))
        pdf.set_auto_page_break(auto=False)  # Disable auto page break
        pdf.add_page()
        pdf.image(front_path, x=0, y=0, w=page_height, h=page_width)
        
        # Process back page
        pdf.add_page()
        # Add back image to full page
        pdf.image(back_path, x=0, y=0, w=page_height, h=page_width)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # # Save PDF
        pdf_file=pdf.output(output_path)
        print(f"Landscape full-page PDF successfully created at: {output_path}")
        print_file(output_path, selected_printer)

    except Exception as e:
        print(f"Error creating PDF: {str(e)}")
        raise


def print_file(file_path, printer_name):
    if platform.system() == "Linux" or platform.system() == "Darwin":
        try:
            if not printer_name:
                show_error_message("No printer selected")
            conn = cups.Connection()
            job_id = conn.printFile(printer_name, file_path, "ID Card Print Job", {})
            print(f"Job submitted successfully. Job ID: {job_id}")
        except Exception as e:
            print(f"Error printing file: {e}")
    elif platform.system() == "Windows":
        try:
            if not printer_name:
                show_error_message("No printer selected")
            # win32print.SetDefaultPrinter(printer_name)
            win32api.ShellExecute(0, "printto", file_path, f'"{printer_name}', ".", 0)
            print(f"Printing file on {printer_name}...")
            # win32api.ShellExecute(0, "print", file_path, None, ".", 0)

        except Exception as e:
            print(f"Error printing file hai ta: {e}")

    else:
        print("Unsupported OS")

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
                    elif status & win32print.PRINTER_STATUS_PAPER_JAM:
                        status_str = "Paper Jam"
                    elif status & win32print.PRINTER_STATUS_PAPER_OUT:
                        status_str = "Paper Out"
                    elif status & win32print.PRINTER_STATUS_OUTPUT_BIN_FULL:
                        status_str = "Output Bin Full"
                    elif status & win32print.PRINTER_STATUS_NOT_AVAILABLE:
                        status_str = "Not Available"
                    elif status & win32print.PRINTER_STATUS_NO_TONER:
                        status_str = "No Toner"
                    elif status & win32print.PRINTER_STATUS_PAGE_PUNT:
                        status_str = "Page Punt"
                    elif status & win32print.PRINTER_STATUS_USER_INTERVENTION:
                        status_str = "User Intervention Required"
                    elif status & win32print.PRINTER_STATUS_POWER_SAVE:
                        status_str = "Power Save"
                    elif status & win32print.PRINTER_STATUS_SERVER_UNKNOWN:
                        status_str = "Server Unknown"
                    elif status & win32print.PRINTER_STATUS_SERVER_OFFLINE:
                        status_str = "Server Offline"
                    elif status & win32print.PRINTER_STATUS_SERVER_UNAVAILABLE:
                        status_str = "Server Unavailable"
                    elif status & win32print.PRINTER_STATUS_WARMING_UP:
                        status_str = "Warming Up"
                    elif status & win32print.PRINTER_STATUS_TONER_LOW:
                        status_str = "Toner Low"
                    elif status & win32print.PRINTER_STATUS_NO_TONER:
                        status_str = "No Toner"
                    elif status & win32print.PRINTER_STATUS_PAGE_PUNT:
                        status_str = "Page Punt"
                    elif status & win32print.PRINTER_STATUS_USER_INTERVENTION:
                        status_str = "User Intervention Required"
                    elif status & win32print.PRINTER_STATUS_OUTPUT_BIN_FULL:
                        status_str = "Output Bin Full"
                    elif status & win32print.PRINTER_STATUS_NOT_AVAILABLE:
                        status_str = "Not Available"
                    elif status & win32print.PRINTER_STATUS_DOOR_OPEN:
                        status_str = "Door Open"
                    elif status & win32print.PRINTER_STATUS_ERROR:
                        status_str = "Error"
                    elif status & win32print.PRINTER_STATUS_INITIALIZING:
                        status_str = "Initializing"
                    elif status & win32print.PRINTER_STATUS_IO_ACTIVE:
                        status_str = "IO Active"
                    
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
                        5: "Stopped",
                        6: "Canceled",
                        7: "Aborted",
                        9: "Completed",
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