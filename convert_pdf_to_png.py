"""
Utility script to convert the Virpil PDF to PNG images
Run this on Windows where PDF conversion tools are available
"""

try:
    from pdf2image import convert_from_path

    pdf_path = 'images/Virpil Alpha Dual Fillable.pdf'
    output_folder = 'assets/images'

    print('Converting PDF to images...')
    images = convert_from_path(pdf_path, dpi=200)

    for i, image in enumerate(images):
        output_path = f'{output_folder}/virpil_alpha_page_{i+1}.png'
        image.save(output_path, 'PNG')
        print(f'Saved: {output_path}')

    print(f'\nSuccess! Converted {len(images)} pages')

except ImportError:
    print("pdf2image not installed. Install with: pip install pdf2image")
    print("Also requires poppler: https://github.com/oschwartz10612/poppler-windows/releases/")
except Exception as e:
    print(f"Error: {e}")
