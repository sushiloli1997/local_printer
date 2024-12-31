import qrcode
import base64
from io import BytesIO

def generate_qr_base64(data):
    """
    Generates a QR code for the given data and returns it as a Base64 string.
    
    Args:
        data (str): The text or URL to encode in the QR code.
    
    Returns:
        str: The QR code image in Base64 format with a 'data:image/png;base64,' prefix.
    """
    # Generate the QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create an image
    img = qr.make_image(fill_color="black", back_color="white")

    # Save the image to a BytesIO object
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # Convert the image to Base64
    base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # Return the Base64 string with the data URI prefix
    return f"data:image/png;base64,{base64_image}"

# Example usage
if __name__ == "__main__":
    test= '41242131212'
    qr_base64 = generate_qr_base64(f"https://example.com/{test}")
    print(qr_base64)
