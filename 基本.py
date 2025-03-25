from PIL import Image
import pyzbar.pyzbar as pyzbar

img_path = 'qrcode.png'
img = Image.open(img_path)

# Use pyzbar to decode the QR code image
barcodes = pyzbar.decode(img)

# Print the total number of barcodes detected
print(f"Total barcodes detected: {len(barcodes)}")

# Loop through each barcode and print its details
for index, barcode in enumerate(barcodes, start=1):
    barcode_content = barcode.data.decode('utf-8')  # Decode the QR code content
    barcode_type = barcode.type  # Type of the barcode
    barcode_rect = barcode.rect  # Position of the barcode in the image
    qr_size = list(barcode_rect)  # Size of the QR code

    # Print details of each barcode
    print(f"Barcode {index}:")
    print(f"  Content: {barcode_content}")
    print(f"  Type: {barcode_type}")
    print(f"  Position: {barcode_rect}")
    print(f"  Size: {qr_size}")

    # Print a separator for clarity between different barcodes
    print("-" * 30)
