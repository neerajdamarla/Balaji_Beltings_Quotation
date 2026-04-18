from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import ImageReader

def generate_pdf(filename, company_info, quote_meta, customer, items, terms, my_name, intro_line):
    c = canvas.Canvas(filename, pagesize=A4)
    w, h = A4
    left_margin, right_margin = 18*mm, w - 18*mm
    current_y = h - 20*mm

    # ---------------- Header ----------------
    logo = ImageReader("logo.jpg")
    logo_width = 60
    logo_height = 60
    c.drawImage(logo, 50, h - 100, width=logo_width, height=logo_height, mask='auto')


    c.setFont("Helvetica-Bold", 25)
    c.drawCentredString(w/2, current_y, company_info['name'])
    current_y -= 10*mm
    c.setFont("Helvetica", 8)
    c.drawCentredString(w/2, current_y, company_info['address'])
    current_y -= 5*mm
    c.drawCentredString(w/2, current_y, f"{company_info['email']} | {company_info['phone']}")
    current_y -= 10*mm

    # Quotation heading
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(w/2, current_y, "QUOTATION")
    current_y -= 15*mm


    # Quotation/Customer details
    c.setFont("Helvetica", 10)
    c.drawString(left_margin, current_y, f"Quotation No: BB/Q/ {quote_meta['quotation_no']}")
    c.drawString(right_margin-120, current_y, f"Date: {quote_meta['quotation_date']}")

    c.drawString(left_margin, current_y-30, "To:")
    c.drawString(left_margin+10, current_y-45, customer['company_name'])
    c.drawString(left_margin+10, current_y-60, f"Email: {customer['email']}")
    c.drawString(left_margin+10, current_y-75, f"Phone: {customer['phone']}")


    current_y -= 100

    #c.setFont("Helvetica-Bold", 8)
    #c.drawCentredString(w/2, current_y, intro_line)
    #current_y -= 
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontName = "Helvetica"
    style.fontSize = 10
    style.alignment = 1  # 0=left, 1=center, 2=right

    para = Paragraph(intro_line, style)
    w, h = para.wrap(500, 100)   # 500 = max width, 100 = max height
    para.drawOn(c, (c._pagesize[0] - w) / 2, current_y - h)
    current_y -= h + 20

    # ---------------- Table ----------------
    col_widths = [15*mm, 50*mm, 25*mm, 25*mm, 15*mm, 20*mm, 24*mm]
    col_x = [left_margin]
    for wcol in col_widths:
        col_x.append(col_x[-1] + wcol)
    table_width = sum(col_widths)

    headers = ["SNo","Item Name","HSN","Make","Qty","UOM","Price"]
    row_height = 14
    start_y = current_y

    # Calculate total rows (header + items + total row)
    num_rows = len(items) + 2
    table_height = row_height * num_rows

    # Draw outer border
    c.rect(left_margin, start_y - table_height, table_width, table_height)

    # Horizontal lines
    for i in range(num_rows + 1):  
        y = start_y - i * row_height
        c.line(left_margin, y, left_margin + table_width, y)

    # Vertical lines
    for x in col_x:
        c.line(x, start_y, x, start_y - table_height)

    # Fill header background
    c.setFillGray(0.9, 1)
    c.rect(left_margin, start_y - row_height, table_width, row_height, fill=1, stroke=0)
    c.setFillGray(0, 1)

    # Print headers (centered)
    c.setFont("Helvetica-Bold", 9)
    for i, hdr in enumerate(headers):
        col_center = (col_x[i] + col_x[i+1]) / 2
        c.drawCentredString(col_center, start_y - row_height + 4, hdr)

    # Print items
    c.setFont("Helvetica", 9)
    y = start_y - row_height
    total = 0
    for idx, it in enumerate(items, start=1):
        y -= row_height
        # Columns centered/aligned depending on type
        c.drawCentredString((col_x[0]+col_x[1])/2, y+4, str(idx))
        c.drawString(col_x[1]+2, y+4, it['name'])  # Item left-aligned
        c.drawCentredString((col_x[2]+col_x[3])/2, y+4, it['hsn'])
        c.drawCentredString((col_x[3]+col_x[4])/2, y+4, it['make'])
        c.drawCentredString((col_x[4]+col_x[5])/2, y+4, str(it['qty']))
        c.drawCentredString((col_x[5]+col_x[6])/2, y+4, it['uom'])
        c.drawRightString(col_x[6+1]-2, y+4, f"{float(it['price']):.2f}")  # Price right-aligned

        total += float(it['qty']) * float(it['price'])

    # Total row
    y -= row_height
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(left_margin + table_width - 4, y+4, f"Total: {total:.2f}")

    current_y = y - 30

    # ---------------- Terms ----------------
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin, current_y, "Terms & Conditions:")
    current_y -= 14
    c.setFont("Helvetica", 9)
    for i, t in enumerate(terms, start=1):
        c.drawString(left_margin+5, current_y, f"{i}. {t}")
        current_y -= 12

    # Closing lines
    current_y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(left_margin, current_y, "We are awaiting for your purchase order.")
    current_y -= 20
    c.drawString(left_margin, current_y, "Thanking you,")

    c.drawString(right_margin-120, current_y-20, "Yours faithfully,")
    c.drawString(right_margin-120, current_y-35, f"For {company_info['name']}")
    c.drawString(right_margin-120, current_y-50, my_name)

    c.save()
