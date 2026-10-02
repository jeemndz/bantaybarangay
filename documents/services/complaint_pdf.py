import hashlib
import os

from xml.sax.saxutils import escape

from django.conf import settings

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    PageBreak,
)

from complaints.models import Complaint
from registration.models import Resident
from documents.models import ComplaintDocument


# =========================================================
# FILE HASH
# =========================================================

def calculate_file_hash(file_path):
    """
    Calculate the SHA-256 hash of the final PDF file.
    """

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


# =========================================================
# SAFE TEXT
# =========================================================

def safe_value(value):
    """
    Convert empty values to N/A and escape user-entered
    content so it does not break ReportLab markup.
    """

    if value is None or value == "":
        return "N/A"

    return escape(str(value))


# =========================================================
# RESIDENT FULL NAME
# =========================================================

def get_resident_full_name(resident):
    """
    Build the resident's complete name.
    """

    parts = [
        resident.first_name,
        resident.middle_name,
        resident.last_name,
        resident.suffix,
    ]

    return " ".join(
        str(part).strip()
        for part in parts
        if part and str(part).strip()
    )


# =========================================================
# RESIDENT ADDRESS
# =========================================================

def get_resident_address(resident):
    """
    Build the most complete available resident address.
    """

    address_parts = [
        resident.house_block_lot,
        resident.street_purok_sitio,
        resident.barangay,
        resident.municipality_city,
        resident.province,
        resident.zip_code,
    ]

    address = ", ".join(
        str(part).strip()
        for part in address_parts
        if part and str(part).strip()
    )

    if not address and resident.address:
        address = resident.address

    return address or "N/A"


# =========================================================
# PAGE HEADER / FOOTER
# =========================================================

def add_page_number(canvas, doc):
    """
    Add the BantayBarangay footer and page number
    to every page of the PDF.
    """

    canvas.saveState()

    page_width, _ = A4

    canvas.setStrokeColor(
        colors.HexColor("#D1D5DB")
    )
    canvas.setLineWidth(0.5)

    canvas.line(
        20 * mm,
        15 * mm,
        page_width - 20 * mm,
        15 * mm,
    )

    canvas.setFont(
        "Helvetica",
        7.5
    )

    canvas.setFillColor(
        colors.HexColor("#6B7280")
    )

    canvas.drawString(
        20 * mm,
        10 * mm,
        "BantayBarangay Complaint Management System",
    )

    canvas.drawRightString(
        page_width - 20 * mm,
        10 * mm,
        f"Page {doc.page}",
    )

    canvas.restoreState()


# =========================================================
# SECTION TITLE
# =========================================================

def section_title(number, title, style):
    return Paragraph(
        f"{number}. {title.upper()}",
        style,
    )


# =========================================================
# INFORMATION TABLE
# =========================================================

def create_information_table(rows, styles):
    """
    Create a standardized two-column information table.
    """

    formatted_rows = []

    for label, value in rows:
        formatted_rows.append(
            [
                Paragraph(
                    f"<b>{escape(str(label))}</b>",
                    styles["table_label"],
                ),
                Paragraph(
                    safe_value(value),
                    styles["table_value"],
                ),
            ]
        )

    table = Table(
        formatted_rows,
        colWidths=[
            48 * mm,
            112 * mm,
        ],
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#F3F4F6"),
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#CBD5E1"),
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.35,
                    colors.HexColor("#E2E8F0"),
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    return table


# =========================================================
# OFFICIAL HEADER
# =========================================================

def add_official_header(
    story,
    styles,
    document_title,
):
    """
    Add the official BantayBarangay document header.
    """

    story.append(
        Paragraph(
            "REPUBLIC OF THE PHILIPPINES",
            styles["republic"],
        )
    )

    story.append(
        Paragraph(
            "BANTAYBARANGAY",
            styles["system_name"],
        )
    )

    story.append(
        Paragraph(
            document_title,
            styles["document_title"],
        )
    )

    header_line = Table(
        [[""]],
        colWidths=[160 * mm],
        rowHeights=[1],
    )

    header_line.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#1F2937"),
                ),
            ]
        )
    )

    story.append(header_line)

    story.append(
        Spacer(
            1,
            7 * mm
        )
    )


# =========================================================
# GENERATE OFFICIAL COMPLAINT PDF
# =========================================================

def generate_complaint_pdf(complaint_id):
    """
    Generate the official complaint record.

    Page 1:
        Official complaint and incident information.

    Page 2 onward:
        Full complaint details, respondent information,
        processing information, and document integrity.

    The SHA-256 hash is calculated only after the final
    PDF has been completely generated.
    """

    # =====================================================
    # GET COMPLAINT
    # =====================================================

    complaint = Complaint.objects.get(
        complaint_id=complaint_id
    )

    # =====================================================
    # GET COMPLAINANT / RESIDENT
    # =====================================================

    resident = Resident.objects.get(
        resident_id=complaint.resident_id
    )

    reference_number = complaint.reference_number

    document_identifier = (
        f"DOC-{reference_number}"
    )

    # =====================================================
    # FILE DIRECTORY
    # =====================================================

    relative_directory = os.path.join(
        "complaint_documents",
        f"complaint_{complaint.complaint_id}",
    )

    absolute_directory = os.path.join(
        settings.MEDIA_ROOT,
        relative_directory,
    )

    os.makedirs(
        absolute_directory,
        exist_ok=True,
    )

    # =====================================================
    # FILE NAME
    # =====================================================

    file_name = f"{reference_number}.pdf"

    absolute_path = os.path.join(
        absolute_directory,
        file_name,
    )

    relative_path = (
        f"{settings.MEDIA_URL}"
        f"complaint_documents/"
        f"complaint_{complaint.complaint_id}/"
        f"{file_name}"
    )

    # =====================================================
    # DATE / TIME VALUES
    # =====================================================

    date_filed = (
        complaint.submitted_at.strftime(
            "%B %d, %Y"
        )
        if complaint.submitted_at
        else "N/A"
    )

    submitted_at = (
        complaint.submitted_at.strftime(
            "%B %d, %Y - %I:%M %p"
        )
        if complaint.submitted_at
        else "N/A"
    )

    updated_at = (
        complaint.updated_at.strftime(
            "%B %d, %Y - %I:%M %p"
        )
        if complaint.updated_at
        else "N/A"
    )

    incident_date = (
        complaint.incident_date.strftime(
            "%B %d, %Y"
        )
        if complaint.incident_date
        else "N/A"
    )

    incident_time = (
        complaint.incident_time.strftime(
            "%I:%M %p"
        )
        if complaint.incident_time
        else "N/A"
    )

    complainant_name = get_resident_full_name(
        resident
    )

    complainant_address = get_resident_address(
        resident
    )

    # =====================================================
    # STYLES
    # =====================================================

    base_styles = getSampleStyleSheet()

    styles = {}

    styles["republic"] = ParagraphStyle(
        "Republic",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#374151"),
        spaceAfter=2,
    )

    styles["system_name"] = ParagraphStyle(
        "SystemName",
        parent=base_styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=21,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#111827"),
        spaceAfter=3,
    )

    styles["document_title"] = ParagraphStyle(
        "DocumentTitle",
        parent=base_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#374151"),
        spaceAfter=12,
    )

    styles["reference"] = ParagraphStyle(
        "Reference",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#111827"),
    )

    styles["section"] = ParagraphStyle(
        "Section",
        parent=base_styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor("#111827"),
        spaceBefore=12,
        spaceAfter=6,
    )

    styles["table_label"] = ParagraphStyle(
        "TableLabel",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#374151"),
    )

    styles["table_value"] = ParagraphStyle(
        "TableValue",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#111827"),
    )

    styles["details"] = ParagraphStyle(
        "Details",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=15,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#111827"),
        spaceAfter=6,
    )

    styles["details_label"] = ParagraphStyle(
        "DetailsLabel",
        parent=base_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#374151"),
        spaceAfter=6,
    )

    styles["integrity"] = ParagraphStyle(
        "Integrity",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=12,
        textColor=colors.HexColor("#4B5563"),
    )

    styles["footer_note"] = ParagraphStyle(
        "FooterNote",
        parent=base_styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#6B7280"),
    )

    # =====================================================
    # PDF DOCUMENT
    # =====================================================

    pdf = SimpleDocTemplate(
        absolute_path,
        pagesize=A4,
        rightMargin=25 * mm,
        leftMargin=25 * mm,
        topMargin=20 * mm,
        bottomMargin=23 * mm,
        title=(
            f"Complaint Record "
            f"{reference_number}"
        ),
        author="BantayBarangay",
        subject="Official Complaint Record",
    )

    story = []

    # =====================================================
    # PAGE 1
    # OFFICIAL COMPLAINT RECORD
    # =====================================================

    add_official_header(
        story,
        styles,
        "OFFICIAL COMPLAINT RECORD",
    )

    # =====================================================
    # REFERENCE INFORMATION
    # =====================================================

    reference_table = Table(
        [
            [
                Paragraph(
                    (
                        "<b>Reference No.:</b> "
                        f"{safe_value(reference_number)}"
                    ),
                    styles["reference"],
                ),
                Paragraph(
                    (
                        "<b>Date Filed:</b> "
                        f"{safe_value(date_filed)}"
                    ),
                    styles["reference"],
                ),
            ]
        ],
        colWidths=[
            80 * mm,
            80 * mm,
        ],
    )

    reference_table.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, 0),
                    "RIGHT",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
            ]
        )
    )

    story.append(reference_table)

    # =====================================================
    # I. COMPLAINANT INFORMATION
    # =====================================================

    complainant_section = [
        section_title(
            "I",
            "Complainant Information",
            styles["section"],
        ),

        create_information_table(
            [
                (
                    "Name",
                    complainant_name
                ),
                (
                    "Address",
                    complainant_address
                ),
                (
                    "Contact Number",
                    resident.contact_number
                ),
                (
                    "Sex",
                    resident.gender
                ),
            ],
            styles,
        ),
    ]

    story.append(
        KeepTogether(complainant_section)
    )

    # =====================================================
    # II. COMPLAINT INFORMATION
    # =====================================================

    complaint_section = [
        section_title(
            "II",
            "Complaint Information",
            styles["section"],
        ),

        create_information_table(
            [
                (
                    "Report Type",
                    complaint.report_type
                ),
                (
                    "Complaint Type",
                    complaint.complaint_type
                ),
                (
                    "Subject",
                    complaint.subject
                ),
                (
                    "Priority",
                    complaint.priority
                ),
                (
                    "Status",
                    complaint.status
                ),
            ],
            styles,
        ),
    ]

    story.append(
        KeepTogether(complaint_section)
    )

    # =====================================================
    # III. INCIDENT INFORMATION
    # =====================================================

    incident_section = [
        section_title(
            "III",
            "Incident Information",
            styles["section"],
        ),

        create_information_table(
            [
                (
                    "Date",
                    incident_date
                ),
                (
                    "Time",
                    incident_time
                ),
                (
                    "Location",
                    complaint.location
                ),
            ],
            styles,
        ),
    ]

    story.append(
        KeepTogether(incident_section)
    )

    # =====================================================
    # FORCE DETAILS TO NEW PAGE
    # =====================================================

    story.append(
        PageBreak()
    )

    # =====================================================
    # PAGE 2+
    # COMPLAINT DETAILS
    # =====================================================

    add_official_header(
        story,
        styles,
        "COMPLAINT DETAILS",
    )

    # =====================================================
    # COMPLAINT REFERENCE INFORMATION
    # =====================================================

    complaint_reference = create_information_table(
        [
            (
                "Reference Number",
                reference_number
            ),
            (
                "Date Filed",
                date_filed
            ),
            (
                "Complainant",
                complainant_name
            ),
            (
                "Respondent",
                complaint.respondent_name
            ),
            (
                "Complaint Type",
                complaint.complaint_type
            ),
            (
                "Status",
                complaint.status
            ),
        ],
        styles,
    )

    story.append(
        complaint_reference
    )

    story.append(
        Spacer(
            1,
            7 * mm
        )
    )

    # =====================================================
    # IV. COMPLAINT NARRATIVE
    # =====================================================

    story.append(
        section_title(
            "IV",
            "Complaint Narrative",
            styles["section"],
        )
    )

    story.append(
        Paragraph(
            "Official complaint description:",
            styles["details_label"],
        )
    )

    description_text = (
        safe_value(complaint.description)
        .replace("\r\n", "<br/>")
        .replace("\n", "<br/>")
        .replace("\r", "<br/>")
    )

    description_box = Table(
        [
            [
                Paragraph(
                    description_text,
                    styles["details"],
                )
            ]
        ],
        colWidths=[
            160 * mm
        ],
    )

    description_box.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#CBD5E1"),
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#FFFFFF"),
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
            ]
        )
    )

    story.append(
        description_box
    )

    # =====================================================
    # V. RESPONDENT INFORMATION
    # =====================================================

    respondent_section = [
        section_title(
            "V",
            "Respondent Information",
            styles["section"],
        ),

        create_information_table(
            [
                (
                    "Name",
                    complaint.respondent_name
                ),
                (
                    "Relationship",
                    complaint.respondent_relationship
                ),
                (
                    "Contact Number",
                    complaint.respondent_contact
                ),
                (
                    "Address",
                    complaint.respondent_address
                ),
            ],
            styles,
        ),
    ]

    story.append(
        KeepTogether(respondent_section)
    )

    # =====================================================
    # VI. PROCESSING INFORMATION
    # =====================================================

    processing_section = [
        section_title(
            "VI",
            "Processing Information",
            styles["section"],
        ),

        create_information_table(
            [
                (
                    "Assigned Official",
                    complaint.assigned_official
                ),
                (
                    "Resolution / Remarks",
                    complaint.resolution
                ),
                (
                    "Submitted At",
                    submitted_at
                ),
                (
                    "Last Updated",
                    updated_at
                ),
            ],
            styles,
        ),
    ]

    story.append(
        KeepTogether(processing_section)
    )

    # =====================================================
    # VII. DOCUMENT INTEGRITY
    # =====================================================

    integrity_section = [
        section_title(
            "VII",
            "Document Integrity Information",
            styles["section"],
        ),

        create_information_table(
            [
                (
                    "Document ID",
                    document_identifier
                ),
                (
                    "Document Type",
                    "Complaint Record"
                ),
                (
                    "Integrity Method",
                    "SHA-256 / Hyperledger Fabric"
                ),
            ],
            styles,
        ),

        Spacer(
            1,
            3 * mm
        ),

        Paragraph(
            (
                "This electronic complaint document is protected "
                "using SHA-256 cryptographic hashing and "
                "blockchain-based integrity verification. "
                "After registration, modification of the PDF "
                "will produce a different cryptographic hash."
            ),
            styles["integrity"],
        ),
    ]

    story.append(
        KeepTogether(integrity_section)
    )

    # =====================================================
    # FINAL NOTICE
    # =====================================================

    story.append(
        Spacer(
            1,
            10 * mm
        )
    )

    story.append(
        Paragraph(
            (
                "This document was generated electronically by "
                "the BantayBarangay Complaint Management System. "
                "Any modification to the generated file after "
                "blockchain registration will result in a "
                "different cryptographic hash."
            ),
            styles["footer_note"],
        )
    )

    # =====================================================
    # BUILD FINAL PDF
    # =====================================================

    pdf.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )

    # =====================================================
    # CALCULATE SHA-256 AFTER PDF IS FINAL
    # =====================================================

    file_hash = calculate_file_hash(
        absolute_path
    )

    # =====================================================
    # CREATE / UPDATE COMPLAINT DOCUMENT
    # =====================================================

    complaint_document, created = (
        ComplaintDocument.objects.update_or_create(
            complaint_id=complaint.complaint_id,
            document_type="COMPLAINT",
            defaults={
                "file_name": file_name,
                "file_path": relative_path,
                "file_hash": file_hash,

                # Regenerating the PDF means the current
                # version has not yet been registered.
                "blockchain_status": "Pending",
                "blockchain_tx_id": None,
                "blockchain_registered_at": None,

                "integrity_status": "Not Verified",
                "last_verified_at": None,
            },
        )
    )

    return complaint_document