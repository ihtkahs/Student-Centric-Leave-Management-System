from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Define paths for the image and the output PDF
image_path = "media\leave_form.jpg"
output_pdf_path = "media\leave_form.pdf"

# Data to be filled in on the form.
leave_data = {
    "name": "John Doe",               # Name of the student
    "roll_number": "12345678",        # Roll number
    "ug_pg": "UG",                    # UG/PG status
    "course": "B.E. CSE",             # Course details
    "year_branch": "III / CSE",       # Year and branch
    "section": "A",                   # Section
    "leave_taken": "5",               # Total leave taken so far
    "leave_with_letter": "2",         # Leave with letter
    "medical_leave": "1",             # Medical leave
    "absent": "1",                    # Absent days
    "privilege_leave": "1",           # Privilege leave
    "relationship": "Father",         # Relationship (if required)
    "student_name": "John Doe",       # Student name (again, if separately required)
    "total_days": "2",                # Total days for this leave period
    "reason": "Medical Appointment",  # Reason for leave
    "date": "08-04-2025",             # Date when the form is filled
    "from_date": "10-04-2025",        # Leave start date
    "to_date": "11-04-2025"           # Leave end date
}

# Create a canvas with A4 size (width, height)
c = canvas.Canvas(output_pdf_path, pagesize=A4)
width, height = A4

# Draw the leave form image as the full page background
c.drawImage(image_path, 0, 0, width=width, height=height)

# Set the font and size for overlaying text
c.setFont("Times-Bold", 13)

# Insert the leave details at specific coordinates
# Adjust the coordinates (x, y) to perfectly align with your form fields
c.drawString(280, 579, leave_data["name"])            # Name field
c.drawString(280, 556, leave_data["roll_number"])       # Roll number field
c.drawString(280, 534, leave_data["ug_pg"])             # UG/PG field
c.drawString(429, 535, leave_data["course"])            # Course field
c.drawString(280, 514, leave_data["year_branch"])       # Year/Branch field
c.drawString(280, 498, leave_data["section"])           # Section field

c.drawString(350, 482, leave_data["leave_taken"])       # Total leave taken so far

c.drawString(350, 385, leave_data["total_days"])        # Total days of leave

# Insert leave reason and relevant dates
c.drawString(230, 368, leave_data["reason"])            # Reason for leave
c.drawString(280, 333, leave_data["date"])              # Form filling date
c.drawString(280, 316, leave_data["from_date"])         # Leave start date
c.drawString(368, 316, leave_data["to_date"])           # Leave end date

# Finalize and save the PDF
c.save()

print("PDF generated at:", output_pdf_path)
