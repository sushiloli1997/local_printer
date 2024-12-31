from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
import qrcode


class CardData:
    def __init__(self, issued_date, card_no, full_name, masterId, localLevel, father_name,issueOffice, officer_name, place_of_birth, ward, sex, district, designation, cardHolderSignature, cardHolderPhoto, issuerSignature ):
        self.card_no = card_no
        self.full_name = full_name
        self.officer_name = officer_name
        self.father_name = father_name
        self.place_of_birth = place_of_birth
        self.ward = ward
        self.sex = sex
        self.issued_date = issued_date
        self.designation = designation
        self.district = district
        self.issueOffice = issueOffice
        self.localLevel = localLevel
        self.masterId = masterId
        self.cardHolderSignature = cardHolderSignature
        self.cardHolderPhoto = cardHolderPhoto
        self.issueSignature = issuerSignature



    def get_card_no(self):
        return self.card_no
    
    def get_cardHolderPhoto(self):
        return self.cardHolderPhoto
    
    def get_cardHolderSignature(self):
        return self.cardHolderSignature
    
    def get_localLevel(self):
        return self.localLevel
    
    def get_issueSignature(self):
        return self.issueSignature
    
    def get_profile_image(self):
        return self.cardHolderPhoto

    def get_issued_date(self):
        return self.issued_date
    
    def get_designation(self):
        return self.designation

    def get_full_name(self):
        return self.full_name
    
    def get_officer_name(self):
        return self.officer_name

    def get_father_name(self):
        return self.father_name

    def get_place_of_birth(self):
        return self.place_of_birth

    def get_ward(self):
        return self.ward

    def get_sex(self):
        return self.sex

    def get_district(self):
        return self.district

    def set_card_no(self, card_no):
        self.card_no = card_no

    def set_full_name(self, full_name):
        self.full_name = full_name

    def set_father_name(self, father_name):
        self.father_name = father_name

    def set_place_of_birth(self, place_of_birth):
        self.place_of_birth = place_of_birth

    def set_ward(self, ward):
        self.ward = ward

    def set_sex(self, sex):
        self.sex = sex

    def set_locallevel(self, localLevel):
        self.localLevel = localLevel

    def set_district(self, district):
        self.district = district
    
    def qr_code_image(masterId):
        # Data to encode
        data = f"www.example.com/{masterId}"
        
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
        return (f"Card No: {self.card_no}\n"
                f"Full Name: {self.full_name}\n"
                f"Father's Name: {self.father_name}\n"
                f"Place of Birth: {self.place_of_birth}\n"
                f"ward: {self.ward}\n"
                f"Sex: {self.sex}\n"
                f"Local Level: {self.localLevel}\n"
                f"District Administration Office: {self.district}")






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
        # Load the watermark image for the front
        watermark = Image.open('asset/front.jpg').convert("RGBA")

        # Create a new image with the same size as the watermark
        width, height = watermark.size
        image = Image.new('RGBA', (width, height))
        image.paste(watermark, (0, 0), watermark)

        draw = ImageDraw.Draw(image)
        arial_font = 'asset/font.ttf'

        for element in elements:
            if element["type"] == "text":
                # Draw text on the card
                font = ImageFont.truetype(arial_font, element["size"])
                draw.text(element["position"], element["text"], fill=element["color"], font=font)

            elif element["type"] == "image":
                # Decode the base64 image and remove the background
                img_data = base64.b64decode(element["data"])
                img = Image.open(BytesIO(img_data)).convert("RGBA")

                # Resize the image if size is provided
                if "size" in element:
                    img = img.resize(element["size"], Image.LANCZOS)

                # Paste the image at the specified position
                image.paste(img, element["position"], img)

        # Save the final card
        image.convert('RGB').save(filename)
        print(f"Front card saved at {filename}")

    except Exception as e:
        print(f"Error creating front card: {e}")



def create_back_card(card_data, elements, filename):
    try:
        # Load the watermark image for the back
        watermark = Image.open('asset/back.jpg').convert("RGBA")

        # Create a new image with the same size as the watermark
        width, height = watermark.size
        image = Image.new('RGBA', (width, height))
        image.paste(watermark, (0, 0), watermark)

        draw = ImageDraw.Draw(image)
        arial_font = 'asset/font.ttf'

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
        print(f"Back card saved at {filename}")

    except Exception as e:
        print(f"Error creating back card: {e}") 
