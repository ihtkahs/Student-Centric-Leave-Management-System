from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

image_path = "media\leave_form.jpg"

def generate_leave_pdf(leave_request, pdf_path):
    # Create a canvas with A4 size (width, height)
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # Draw the leave form image as the full page background
    c.drawImage(image_path, 0, 0, width=width, height=height)

    # Set the font and size for overlaying text
    c.setFont("Times-Bold", 13)

    # Insert the leave details at specific coordinates
    # Adjust the coordinates (x, y) to perfectly align with your form fields
    c.drawString(280, 579, leave_request.student.name)            # Name field
    c.drawString(280, 556, leave_request.student.reg_no)       # Roll number field
    c.drawString(280, 534, "UG")             # UG/PG field
    c.drawString(429, 535, "B.Tech")            # Course field
    c.drawString(280, 514, f"{leave_request.student.year} ADS")       # Year/Branch field
    c.drawString(280, 498, leave_request.student.section)           # Section field

    c.drawString(350, 482, "3")       # Total leave taken so far

    c.drawString(350, 385, "5")        # Total days of leave

    # Insert leave reason and relevant dates
    c.drawString(230, 368, leave_request.reason)            # Reason for leave
    if(leave_request.duration=='single'):
        c.drawString(280, 333, f"{leave_request.date}")              # Form filling date
    else:
        c.drawString(280, 316, f"{leave_request.start_date}")         # Leave start date
        c.drawString(368, 316, f"{leave_request.end_date}")           # Leave end date

    # Finalize and save the PDF
    c.save()
