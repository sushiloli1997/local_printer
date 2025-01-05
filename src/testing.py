import threading 
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import win32print
from fpdf import FPDF
import subprocess
import time
import logging
import sys

#fastapi
from fastapi import FastAPI, Request, Response, HTTPException

from fastapi.responses import HTMLResponse, JSONResponse

from dataclasses import dataclass, field
from datetime import datetime



import uvicorn

from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
import qrcode
import os



selected_printer = None

app = FastAPI()

log_file = "printer_log.txt"
current_dir = os.path.dirname(os.path.abspath(__file__))






# Set up logging
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()





def show_error_message(message):
    messagebox.showerror("Error", message)



def show_info_message(message):
    messagebox.showinfo("Info", message)



def show_warning_message(message):
    messagebox.showwarning("Warning", message)



def resource_path(relative_path):
    """ Get the path to the resource in the bundled executable. """
    try:
        # PyInstaller stores bundled files in a temporary folder when running the .exe
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)







@dataclass
class CardData:
    masterId: int
    name: str
    fatherName: str
    dateOfBirth: str
    cardExpiryDate: str
    birthPlace: str
    district: str
    localLevel: str
    wardNo: int
    issueOffice: str
    cardHolderSignature: str
    officerName: str
    gender: str
    slug: str
    designation: str
    issueDate: str
    issuerSignature: str
    cardNo: str
    cardId: int
    submissionNumber: str
    cardHolderPhoto: str
    accessToken: str
    refreshToken: str

    

    @staticmethod
    def qr_code_image(slug: str) -> str:
        """
        Generate a QR code as a Base64-encoded PNG image.
        :param master_id: Unique identifier to encode in the QR code.
        :return: Base64-encoded PNG image string.
        """
        # Data to encode
        data = f"https://borderpass.immigration.gov.np/china-nepal-entry-pass/qr/{slug}"
        
        # Create a QRCode object
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # Generate the image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert the image to Base64
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

def __str__(self):
    """
    Return a human-readable string representation of the card data.
    """
    return (f"Card No: {self.cardNo}\n"
            f"Full Name: {self.name}\n"
            f"Father's Name: {self.fatherName}\n"
            f"Date of Birth: {self.dateOfBirth}\n"
            f"Place of Birth: {self.birthPlace}\n"
            f"Ward No: {self.wardNo}\n"
            f"Gender: {self.gender}\n"
            f"Local Level: {self.localLevel}\n"
            f"District: {self.district}\n"
            f"Issue Office: {self.issueOffice}\n"
            f"Officer's Name: {self.officerName}\n"
            f"Designation: {self.designation}\n"
            f"Issue Date: {self.issueDate}\n"
            f"Card Expiry Date: {self.cardExpiryDate}\n"
            f"Submission Number: {self.submissionNumber}")





@app.get("/")
async def home():
    logger.info("Root endpoint accessed")
    return HTMLResponse(content="Hello, Application is Running on port 9010")




@app.options("/api/v1/china-pass-card-printer-app/")
async def options_handler():
    return JSONResponse(
        content="",
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
    )



@app.post("/api/v1/china-pass-card-printer-app/")
async def handle_post(request: Request):
    content_type = request.headers.get("Content-Type")
    if content_type == "application/json":
        try:
            # Parse JSON data
            card_data = await request.json()
            logger.info(f"Received card data.")

            # Create the card data model
            card_data = CardData(**card_data)

            front_elements = [
                # Header Section
                {"type": "text", "text": "Government of Nepal", "position": (340, 10), "color": (255, 0, 0), "size": 34},
                {"type": "text", "text": "Ministry of Home Affairs", "position": (300, 50), "color": (255, 0, 0), "size": 40},
                {"type": "text", "text": "China Entry/Exit Pass for Nepalese Citizen", "position": (200, 90), "color": (255, 0, 0), "size": 34},
                
                # Details Section
                {"type": "text", "text": "Card No", "position": (50, 190), "color": (0, 0, 0), "size": 30},
                {"type": "text", "text": f": {card_data.cardNo}", "position": (260, 190), "color": (0, 0, 0), "size": 30},
                {"type": "text", "text": "Full Name", "position": (50, 235), "color": (0, 0, 0), "size": 30},
                {"type": "text", "text": f": {card_data.name}", "position": (260, 235), "color": (0, 0, 0), "size": 30},
                {"type": "text", "text": "Father's Name", "position": (50, 280), "color": (0, 0, 0), "size": 30},
                {"type": "text", "text": f": {card_data.fatherName}", "position": (260, 280), "color": (0, 0, 0), "size": 30},
                {"type": "text", "text": "Place of Birth", "position": (50, 325), "color": (0, 0, 0), "size": 30},
                {"type": "text", "text": f": {card_data.birthPlace}", "position": (260, 325), "color": (0, 0, 0), "size": 30},

                # Address Section
                {"type": "text", "text": "Address", "position": (50, 370), "color": (0, 0, 0), "size": 30},
                {"type": "text", "text": f": {card_data.district} District", "position": (260, 370), "color": (0, 0, 0), "size": 30},
                {"type": "text", "text": f"{card_data.localLevel}", "position": (280, 415), "color": (0, 0, 0), "size": 30},
                {"type": "text", "text": f"{card_data.wardNo} Ward", "position": (280, 460), "color": (0, 0, 0), "size": 30},

                # Additional Information
                {"type": "text", "text": "Sex", "position": (640, 325), "color": (0, 0, 0), "size": 30},
                {"type": "text", "text": f": {card_data.gender}", "position": (700, 325), "color": (0, 0, 0), "size": 30},

                {"type": "text", "text": "Issue Office", "position": (50, 505), "color": (0, 0, 0), "size": 30},
                {"type": "text", "text": f": {card_data.issueOffice}", "position": (260, 505), "color": (0, 0, 0), "size": 30},
                #Profile Image
                {"type": "image", "data": card_data.cardHolderPhoto, "position": (760, 208), "size": (225, 225)},
                
                ]
            back_elements = [
                    {"type": "text", "text": "If found please return to nearest District Administration Office", "position": (30, 450), "color": (0, 0, 0), "size": 30},
                    {"type": "text", "text": "Valid only for entry/exit purpose to china through land border", "position": (30, 480), "color": (0, 0, 0), "size": 30},
                    {"type": "text", "text": "This pass shall be valid for five years and will be renewed if necessary", "position": (30, 510), "color": (0, 0, 0), "size": 30},
                    {"type": "text", "text": "For more information about validity period please scan QR code", "position": (30, 540), "color": (0, 0, 0), "size": 30},

                    {"type": "text", "text": "Card Holder's", "position": (50, 75), "color": (0, 0, 0), "size": 30},
                    {"type": "text", "text": "Signature:", "position": (50, 130), "color": (0, 0, 0), "size": 30},

                    {"type": "text", "text": "Officer's Name:", "position": (490, 120), "color": (0, 0, 0), "size": 30},
                    {"type": "text", "text": card_data.officerName, "position": (710, 120), "color": (0, 0, 0), "size": 30},
                    {"type": "text", "text": "Designation:", "position": (490, 155), "color": (0, 0, 0), "size": 30},
                    {"type": "text", "text": card_data.designation, "position": (710, 155), "color": (0, 0, 0), "size": 30},
                    {"type": "text", "text": "Issued Date:", "position": (490, 190), "color": (0, 0, 0), "size": 30},
                    {"type": "text", "text": card_data.issueDate, "position": (710, 190), "color": (0, 0, 0), "size": 30},

                    # Add an image element (e.g., profile image)
                    {"type": "image", "data": card_data.cardHolderSignature, "position": (160, 140), "size": (125, 125)},
                    {"type": "image", "data": card_data.issuerSignature, "position": (660, 230), "size": (125, 125)},
                    
                    {"type": "image", "data": card_data.qr_code_image(card_data.slug), "position": (2, 237), "size": (197, 197)},

                    {"type": "text", "text": "Signature:", "position": (490, 225), "color": (0, 0, 0), "size": 30},
                    {"type": "text", "text": "Card Issuing Authority:", "position": (550, 75), "color": (0, 0, 0), "size": 30},
                ]
                
            logger.info("Creating card images...")

            # Create front and back card images
            # front_file = os.path.join(current_dir, 'front.png')
            # back_file = os.path.join(current_dir, 'back.png')
            if selected_printer is None or selected_printer == "":
                messagebox.showerror("Error", "Please select a printer first!")
                logger.error("Printer Not Selected")

                return JSONResponse(
                content={
                    "message": "Printer Not Selected",
                    "status": "Error",
                },
                status_code=400,
            )

            card_front=create_front=create_front_card(card_data, front_elements, 'front.png')
            card_back=create_back=create_back_card(card_data, back_elements, 'back.png')

            logger.info(f"Card images front: {create_front} and back: {create_back} created successfully")


            # Merge the images to create a PDF
            logger.info("Merging front and back card images to PDF...")
            create_card_pdf(
                front_path=card_front,
                back_path=card_back,
                output_path='card.pdf'
            )

            # Return success response
            logger.info("Card successfully created and printed")
            return JSONResponse(
                content={
                    "message": "Card successfully created and printed",
                    "status": "success",
                },
                status_code=200,
            )

        except Exception as e:
            logger.error(f"Error processing card data: {e}")
            raise HTTPException(
                status_code=500,
                detail="An error occurred while creating the card"
            )
    else:
        logger.error("Invalid content type")
        raise HTTPException(
            status_code=400,
            detail="Unsupported Content-Type. Expected 'application/json'."
        )






# Function to decode base64 images and return a list of images with positions and sizes
def convert_and_add_base64_images(base64_strings_positions_sizes, tolerance=30):
    images_positions = []
    for base64_string, position, size in base64_strings_positions_sizes:
        # Handle padding
        missing_padding = len(base64_string) % 4
        if missing_padding != 0:
            base64_string += '=' * (4 - missing_padding)
        else:
            base64_string = base64_string
                        
        # Decode and open image
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data)).convert('RGBA')
        
        # Remove background with tolerance
        datas = image.getdata()
        new_data = []
        for item in datas:
            # Get average of RGB values
            avg = sum(item[:3]) / 3
            # If color is close to white within tolerance
            if all(abs(x - avg) < tolerance for x in item[:3]) and avg > 255 - tolerance:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        
        image.putdata(new_data)
        
        # Resize if needed
        if size:
            image = image.resize(size, Image.LANCZOS)
            
        # Save
        output_path = f"image_{len(images_positions)}.png"
        image.save(output_path, 'PNG')
        images_positions.append((image, position))
        
    return images_positions



def create_front_card(card_data, elements, filename):
    try:
        file_path = os.path.join(current_dir, 'front.jpg')
        watermark = Image.open(file_path).convert("RGBA")

        # Create a new image with the same size as the watermark
        width, height = watermark.size
        image = Image.new('RGBA', (width, height))
        image.paste(watermark, (0, 0), watermark)

        draw = ImageDraw.Draw(image)
        arial_font = 'font.ttf'

        for element in elements:
            if element["type"] == "text":
                # Draw text on the card
                font = ImageFont.truetype(arial_font, element["size"])
                draw.text(element["position"], element["text"], fill=element["color"], font=font)

            elif element["type"] == "image":
                # Decode the base64 image and remove the background
                img_data = base64.b64decode(element["data"])
                img = Image.open(BytesIO(img_data)).convert("RGBA")

                # Remove background
                datas = img.getdata()
                new_data = []
                for item in datas:
                    avg = sum(item[:3]) / 3
                    if all(abs(x - avg) < 30 for x in item[:3]) and avg > 255 - 30:
                        new_data.append((255, 255, 255, 0))
                    else:
                        new_data.append(item)

                img.putdata(new_data)

                # Resize the image if size is provided
                if "size" in element:
                    img = img.resize(element["size"], Image.LANCZOS)

                # Paste the image at the specified position
                image.paste(img, element["position"], img)

        # Save the final card
        image.convert('RGB').save(filename)
        logger.info(f"Back card saved at {filename}")
        logger.info(f"Front card saved at {filename}")
        return filename

    except Exception as e:
        logger.info(f"Error creating Front card: {e}") 



def create_back_card(card_data, elements, filename):
    try:
        file_path = os.path.join(current_dir, 'back.jpg')
        watermark = Image.open(file_path).convert("RGBA")

        # Create a new image with the same size as the watermark
        width, height = watermark.size
        image = Image.new('RGBA', (width, height))
        image.paste(watermark, (0, 0), watermark)

        draw = ImageDraw.Draw(image)
        arial_font = 'font.ttf'

        for element in elements:
            if element["type"] == "text":
                # Draw text on the card
                font = ImageFont.truetype(arial_font, element["size"])
                draw.text(element["position"], element["text"], fill=element["color"], font=font)

            elif element["type"] == "image":
                # Decode the base64 image and remove the background
                img_data = base64.b64decode(element["data"])
                img = Image.open(BytesIO(img_data)).convert("RGBA")

                # Remove background
                datas = img.getdata()
                new_data = []
                for item in datas:
                    avg = sum(item[:3]) / 3
                    if all(abs(x - avg) < 30 for x in item[:3]) and avg > 255 - 30:
                        new_data.append((255, 255, 255, 0))
                    else:
                        new_data.append(item)

                img.putdata(new_data)

                # Resize the image if size is provided
                if "size" in element:
                    img = img.resize(element["size"], Image.LANCZOS)

                # Paste the image at the specified position
                image.paste(img, element["position"], img)

        # Save the final card
        image.convert('RGB').save(filename)
        logger.info(f"Back card saved at {filename}")
        return filename

    except Exception as e:
        logger.info(f"Error creating back card: {e}") 




def create_card_pdf(front_path: str,back_path: str,output_path: str):
    try:  
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
        
        
        # # Save PDF
        pdf_file=pdf.output(output_path)
        logger.info(f"Full-page PDF successfully created at: {output_path}")

            # return output_path
        print_file(output_path, selected_printer)
        # time.sleep(2)
        
        remove_file('front.png')
        remove_file('back.png')

        logger.info(f"Files removed: {a}, {b}")

        return output_path

    except Exception as e:
        logger.info(f"Error creating PDF: {str(e)}")
        raise



def remove_file(file_path):
    try:
        os.remove(file_path)
        logging.info(f"Successfully removed file: {file_path}")
    except FileNotFoundError:
        logging.warning(f"File not found: {file_path}")
    except Exception as e:
        logging.error(f"Error removing file: {e}")
        raise e  # Re-raise exception if needed


def check_adobe_acrobat():
    adobe_path = r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe"
    if not os.path.exists(adobe_path):
        logger.info("Adobe Acrobat DC is not installed or not found at the expected location.")
        sys.exit(1)
    return adobe_path


def print_file(file_path, printer_name):
    try:
        # Set the printer to the specified printer
        adobe_path = check_adobe_acrobat()
        win32print.SetDefaultPrinter(printer_name)

        # logger.info the file by invoking the default PDF viewer directly
        if os.path.exists(file_path):
            # Open the file using the default PDF viewer with the logger.info command
            subprocess.run([adobe_path, r"/t", file_path, printer_name])
            logger.info("File sent to printer successfully.")
            
            logger.info(f"File '{file_path}' has been sent to the printer '{printer_name}'.")

            time.sleep(15)
            
            remove_file('card.pdf')
            logger.info(f"File '{file_path}' has been removed.")
        else:
            logger.info(f"Error: The file '{file_path}' does not exist.")

    except Exception as e:
        logger.info(f"Error: {e}")
        raise e  # Re-raise exception if needed

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
        exit_btn.grid(row=4, column=0, columnspan=3, pady=20)
        
        # Initialize printers
        self.refresh_printers()
        
        # Set up periodic refresh
        self.root.after(5000, self.periodic_refresh)

    def refresh_printers(self):
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        self.printers_dict = {printer[2]: printer[2] for printer in printers}
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
        
        # Update UI
        self.selected_label.config(text=f"Selected Printer: {selected_printer}")
        self.printer_status.config(text=f"Status: Selected")
    
        # Show success message
        messagebox.showinfo("Success", f"Printer '{selected_printer}' has been selected!")
        logger.info(f"Selected printer: {selected_printer}")

    def periodic_refresh(self):
        self.refresh_printers()
        self.root.after(5000, self.periodic_refresh)
    
    def run(self):
        self.root.mainloop()


# Function to start the FastAPI server
def start_server():
    logger.info("Starting server on http://0.0.0.0:9010")
    uvicorn.run(app, host="0.0.0.0", port=9010)

if __name__ == "__main__":
    # Start the FastAPI server in a separate thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Start the Tkinter application in the main thread
    root = tk.Tk()
    printer_app = PrinterApp(root)
    printer_app.run()