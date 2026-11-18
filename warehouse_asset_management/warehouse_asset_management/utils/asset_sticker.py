import base64
import io
import json
import os

import frappe


def _save_image_file(buf, prefix, asset_name):
    """Save PNG buffer to public/files and return an absolute URL (so wkhtmltopdf can embed it)."""
    try:
        files_dir = frappe.get_site_path("public", "files")
        os.makedirs(files_dir, exist_ok=True)
        fname = f"{prefix}_{frappe.scrub(asset_name or 'asset')}.png"
        fpath = os.path.join(files_dir, fname)
        buf.seek(0)
        with open(fpath, "wb") as f:
            f.write(buf.read())
        # absolute URL (http://host/files/...) so wkhtmltopdf can fetch it from the running server
        return frappe.utils.get_url(f"/files/{fname}")
    except Exception:
        return _get_placeholder_data_uri()


@frappe.whitelist()
def get_asset_sticker_qr_png_data_uri(doc):
    """Generate QR code PNG and return a served URL (not base64) so it renders in PDF."""
    try:
        import qrcode
    except ImportError:
        return _get_placeholder_data_uri()

    data = {
        "name": doc.get("name", ""),
        "asset_name": doc.get("asset_name", ""),
        "category": doc.get("asset_category", ""),
        "location": doc.get("location", ""),
        "company": doc.get("company", ""),
        "status": doc.get("status", ""),
    }

    qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=2)
    qr.add_data(json.dumps(data, ensure_ascii=False))
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")

    return _save_image_file(buf, "sticker_qr", doc.get("name", ""))


@frappe.whitelist()
def get_asset_sticker_barcode_png_data_uri(doc):
    """Generate Code128 barcode PNG and return a served URL (not base64)."""
    asset_name = doc.get("name", "")

    try:
        import barcode
        from barcode.writer import ImageWriter

        code128 = barcode.get_barcode_class("code128")
        barcode_obj = code128(asset_name, writer=ImageWriter())

        buf = io.BytesIO()
        barcode_obj.write(
            buf,
            options={
                "module_width": 0.3,
                "module_height": 8,
                "font_size": 8,
                "text_distance": 2,
                "quiet_zone": 2,
            },
        )
        return _save_image_file(buf, "sticker_bc", asset_name)
    except ImportError:
        return _generate_simple_barcode(asset_name)


def _generate_simple_barcode(text):
    """Simple barcode-like rendering as fallback, saved as a file."""
    try:
        from PIL import Image, ImageDraw

        width = 200
        height = 60
        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)

        x = 10
        for char in text:
            for i in range(8):
                if hash(char + str(i)) % 3 == 0:
                    draw.rectangle([x, 10, x + 2, 50], fill="black")
                x += 3

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return _save_image_file(buf, "sticker_bc", text)
    except ImportError:
        return _get_placeholder_data_uri()


def _get_placeholder_data_uri():
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
