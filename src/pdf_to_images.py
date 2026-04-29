from pdf2image import convert_from_path
import os

def convert_pdf_to_images(pdf_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    images = convert_from_path(
        pdf_path,
        dpi=300,
        poppler_path=r"C:\Users\Prajwal\Desktop\Release-25.12.0-0\poppler-25.12.0\Library\bin"
    )

    image_paths = []
    for i, image in enumerate(images):
        path = os.path.join(output_dir, f"page_{i+1}.png")
        image.save(path, "PNG")
        image_paths.append(path)

    return image_paths