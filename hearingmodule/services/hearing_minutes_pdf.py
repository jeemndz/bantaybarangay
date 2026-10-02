import hashlib
import os

from xml.sax.saxutils import escape

from django.conf import settings
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.enums import (
    TA_CENTER,
    TA_LEFT,
    TA_JUSTIFY,
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
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

from hearingmodule.models import (
    Hearing,
    HearingMinutesDocument,
)


# =========================================================
# BARANGAY INFORMATION
# =========================================================

BARANGAY_NAME = "BARANGAY ULINGAO"
MUNICIPALITY_NAME = "MUNICIPALITY OF SAN RAFAEL"
PROVINCE_NAME = "PROVINCE OF BULACAN"

OFFICE_NAME = "OFFICE OF THE LUPONG TAGAPAMAYAPA"


# =========================================================
# FILE HASH
# =========================================================

def calculate_file_hash(file_path):
    """
    Calculate the SHA-256 hash of the final PDF file.
    """

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        for chunk in iter(
            lambda: file.read(8192),
            b""
        ):
            sha256.update(chunk)

    return sha256.hexdigest()


# =========================================================
# SAFE TEXT
# =========================================================

def safe_value(value):
    """
    Convert empty values to N/A and escape content so it
    does not break ReportLab markup.
    """

    if value is None or value == "":
        return "N/A"

    return escape(str(value))


# =========================================================
# FORMAT ROLE
# =========================================================

def format_role(role):
    """
    Convert stored role values into a formal display value.
    """

    if not role:
        return "N/A"

    role_text = str(role).strip()

    role_mapping = {
        "admin": "Administrator",
        "official": "Barangay Official",
        "resident": "Resident",
    }

    return role_mapping.get(
        role_text.lower(),
        role_text.title(),
    )


# =========================================================
# PAGE FOOTER
# =========================================================

def add_page_footer(canvas, doc):
    """
    Add formal Barangay Ulingao footer and page number.
    """

    canvas.saveState()

    page_width, _ = A4

    # Footer separator
    canvas.setStrokeColor(
        colors.HexColor("#808080")
    )
    canvas.setLineWidth(0.4)

    canvas.line(
        22 * mm,
        15 * mm,
        page_width - 22 * mm,
        15 * mm,
    )

    # Footer text
    canvas.setFont(
        "Helvetica",
        7.5,
    )

    canvas.setFillColor(
        colors.HexColor("#4A4A4A")
    )

    canvas.drawString(
        22 * mm,
        10 * mm,
        (
            "Barangay Ulingao | "
            "San Rafael, Bulacan | "
            "Official Hearing Record"
        ),
    )

    canvas.drawRightString(
        page_width - 22 * mm,
        10 * mm,
        f"Page {doc.page}",
    )

    canvas.restoreState()


# =========================================================
# FORMAL HEADER
# =========================================================

def add_official_header(
    story,
    styles,
    document_title,
):
    """
    Add the formal Barangay Ulingao government header.
    """

    story.append(
        Paragraph(
            "REPUBLIC OF THE PHILIPPINES",
            styles["header_small"],
        )
    )

    story.append(
        Paragraph(
            PROVINCE_NAME,
            styles["header_small"],
        )
    )

    story.append(
        Paragraph(
            MUNICIPALITY_NAME,
            styles["header_small"],
        )
    )

    story.append(
        Paragraph(
            BARANGAY_NAME,
            styles["barangay_name"],
        )
    )

    story.append(
        Paragraph(
            OFFICE_NAME,
            styles["office_name"],
        )
    )

    story.append(
        Spacer(
            1,
            3 * mm,
        )
    )

    # Double-line effect
    line_top = Table(
        [[""]],
        colWidths=[166 * mm],
        rowHeights=[1],
    )

    line_top.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.black,
                ),
            ]
        )
    )

    story.append(line_top)

    story.append(
        Spacer(
            1,
            1.2 * mm,
        )
    )

    line_bottom = Table(
        [[""]],
        colWidths=[166 * mm],
        rowHeights=[0.4],
    )

    line_bottom.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.black,
                ),
            ]
        )
    )

    story.append(line_bottom)

    story.append(
        Spacer(
            1,
            6 * mm,
        )
    )

    story.append(
        Paragraph(
            document_title,
            styles["document_title"],
        )
    )

    story.append(
        Spacer(
            1,
            5 * mm,
        )
    )


# =========================================================
# SECTION HEADING
# =========================================================

def section_heading(title, styles):

    return Paragraph(
        title.upper(),
        styles["section"],
    )


# =========================================================
# INFORMATION TABLE
# =========================================================

def create_information_table(
    rows,
    styles,
):
    """
    Create a clean formal two-column information table.
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
            118 * mm,
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
                    "LINEBELOW",
                    (0, 0),
                    (-1, -1),
                    0.3,
                    colors.HexColor("#B8B8B8"),
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    return table


# =========================================================
# SIGNATURE BLOCK
# =========================================================

def create_signature_block(
    processed_by_name,
    formatted_role,
    processed_at,
    styles,
):
    """
    Create the formal Prepared / Processed By section.
    """

    signature_table = Table(
        [
            [
                Paragraph(
                    "Prepared / Processed By:",
                    styles["signature_label"],
                )
            ],
            [Spacer(1, 10 * mm)],
            [
                Paragraph(
                    (
                        "<u><b>"
                        f"{safe_value(processed_by_name)}"
                        "</b></u>"
                    ),
                    styles["signature_name"],
                )
            ],
            [
                Paragraph(
                    safe_value(formatted_role),
                    styles["signature_role"],
                )
            ],
            [
                Paragraph(
                    (
                        "Date Prepared: "
                        f"{safe_value(processed_at)}"
                    ),
                    styles["signature_date"],
                )
            ],
        ],
        colWidths=[75 * mm],
        hAlign="LEFT",
    )

    signature_table.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
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
                    2,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    2,
                ),
            ]
        )
    )

    return signature_table


# =========================================================
# MINUTES PARAGRAPHS
# =========================================================

def add_minutes_content(
    story,
    notes,
    styles,
):
    """
    Add hearing notes as normal flowing paragraphs.

    This avoids placing all hearing minutes inside one large
    table cell and allows long minutes to continue naturally
    to Page 3, Page 4, and later pages.
    """

    if not notes or not str(notes).strip():

        story.append(
            Paragraph(
                "No hearing minutes were recorded.",
                styles["minutes"],
            )
        )

        return

    normalized_notes = (
        str(notes)
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )

    paragraphs = normalized_notes.split("\n")

    for paragraph_text in paragraphs:

        paragraph_text = paragraph_text.strip()

        if not paragraph_text:

            story.append(
                Spacer(
                    1,
                    3 * mm,
                )
            )

            continue

        story.append(
            Paragraph(
                safe_value(paragraph_text),
                styles["minutes"],
            )
        )


# =========================================================
# GENERATE OFFICIAL HEARING MINUTES PDF
# =========================================================

def generate_hearing_minutes_pdf(
    hearing_id,
    processed_by,
    processed_by_name,
    processed_by_role,
):
    """
    Generate the formal Official Hearing Minutes of
    Barangay Ulingao, San Rafael, Bulacan.

    Page 1:
        Official hearing record and case information.

    Page 2 onward:
        Minutes of the hearing.

    SHA-256 is calculated only after the final PDF has
    been completely generated.
    """

    # =====================================================
    # GET HEARING
    # =====================================================

    hearing = Hearing.objects.get(
        hearing_id=hearing_id
    )

    if hearing.status != "Completed":

        raise ValueError(
            "The official Hearing Minutes PDF can only be "
            "generated after the hearing is completed."
        )

    if not hearing.notes or not hearing.notes.strip():

        raise ValueError(
            "The official Hearing Minutes PDF cannot be "
            "generated because no hearing notes were recorded."
        )

    # =====================================================
    # DOCUMENT IDENTIFIER
    # =====================================================

    document_identifier = (
        f"HRG-{hearing.hearing_id}"
    )

    # =====================================================
    # PREVENT OVERWRITING REGISTERED DOCUMENT
    # =====================================================

    existing_document = (
        HearingMinutesDocument.objects
        .filter(
            hearing_id=hearing.hearing_id,
            document_type="HEARING_MINUTES",
        )
        .first()
    )

    if (
        existing_document
        and
        existing_document.blockchain_status
        == "Registered"
    ):

        raise ValueError(
            "The Hearing Minutes document has already been "
            "registered on the blockchain and cannot be "
            "regenerated or overwritten."
        )

    # =====================================================
    # FILE DIRECTORY
    # =====================================================

    relative_directory = os.path.join(
        "hearing_minutes",
        f"hearing_{hearing.hearing_id}",
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

    file_name = (
        f"official_hearing_minutes_"
        f"{document_identifier}.pdf"
    )

    absolute_path = os.path.join(
        absolute_directory,
        file_name,
    )

    relative_path = (
        f"{settings.MEDIA_URL}"
        f"hearing_minutes/"
        f"hearing_{hearing.hearing_id}/"
        f"{file_name}"
    )

    # =====================================================
    # FORMATTED VALUES
    # =====================================================

    hearing_date = (
        hearing.hearing_date.strftime(
            "%B %d, %Y"
        )
        if hearing.hearing_date
        else "N/A"
    )

    start_time = (
        hearing.start_time.strftime(
            "%I:%M %p"
        )
        if hearing.start_time
        else "N/A"
    )

    end_time = (
        hearing.end_time.strftime(
            "%I:%M %p"
        )
        if hearing.end_time
        else "N/A"
    )

    generated_time = timezone.localtime(
        timezone.now()
    )

    processed_at = generated_time.strftime(
        "%B %d, %Y - %I:%M %p"
    )

    formatted_role = format_role(
        processed_by_role
    )

    # =====================================================
    # STYLES
    # =====================================================

    base_styles = getSampleStyleSheet()

    styles = {}

    styles["header_small"] = ParagraphStyle(
        "HeaderSmall",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.black,
        spaceAfter=1,
    )

    styles["barangay_name"] = ParagraphStyle(
        "BarangayName",
        parent=base_styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=17,
        alignment=TA_CENTER,
        textColor=colors.black,
        spaceBefore=2,
        spaceAfter=1,
    )

    styles["office_name"] = ParagraphStyle(
        "OfficeName",
        parent=base_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.black,
        spaceAfter=2,
    )

    styles["document_title"] = ParagraphStyle(
        "DocumentTitle",
        parent=base_styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=17,
        alignment=TA_CENTER,
        textColor=colors.black,
        spaceAfter=3,
    )

    styles["reference"] = ParagraphStyle(
        "Reference",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        alignment=TA_LEFT,
        textColor=colors.black,
    )

    styles["section"] = ParagraphStyle(
        "Section",
        parent=base_styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.black,
        spaceBefore=10,
        spaceAfter=5,
    )

    styles["table_label"] = ParagraphStyle(
        "TableLabel",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.black,
    )

    styles["table_value"] = ParagraphStyle(
        "TableValue",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.black,
    )

    styles["minutes_intro"] = ParagraphStyle(
        "MinutesIntro",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=15,
        alignment=TA_JUSTIFY,
        textColor=colors.black,
        spaceAfter=8,
    )

    styles["minutes"] = ParagraphStyle(
        "Minutes",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=16,
        alignment=TA_JUSTIFY,
        textColor=colors.black,
        firstLineIndent=8 * mm,
        spaceAfter=5,
    )

    styles["certification"] = ParagraphStyle(
        "Certification",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=13,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor("#303030"),
        spaceAfter=5,
    )

    styles["signature_label"] = ParagraphStyle(
        "SignatureLabel",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.black,
    )

    styles["signature_name"] = ParagraphStyle(
        "SignatureName",
        parent=base_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.black,
    )

    styles["signature_role"] = ParagraphStyle(
        "SignatureRole",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.black,
    )

    styles["signature_date"] = ParagraphStyle(
        "SignatureDate",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#404040"),
    )

    styles["notice"] = ParagraphStyle(
        "Notice",
        parent=base_styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#555555"),
    )

    # =====================================================
    # PDF DOCUMENT
    # =====================================================

    pdf = SimpleDocTemplate(
        absolute_path,
        pagesize=A4,
        rightMargin=22 * mm,
        leftMargin=22 * mm,
        topMargin=17 * mm,
        bottomMargin=23 * mm,
        title=(
            "Official Hearing Minutes - "
            f"{hearing.case_number}"
        ),
        author=(
            "Barangay Ulingao, "
            "San Rafael, Bulacan"
        ),
        subject=(
            "Official Barangay Hearing Minutes"
        ),
    )

    story = []

    # =====================================================
    # PAGE 1
    # OFFICIAL HEARING RECORD
    # =====================================================

    add_official_header(
        story,
        styles,
        "OFFICIAL HEARING RECORD",
    )

    # =====================================================
    # REFERENCE INFORMATION
    # =====================================================

    reference_table = Table(
        [
            [
                Paragraph(
                    (
                        "<b>Document No.:</b> "
                        f"{safe_value(document_identifier)}"
                    ),
                    styles["reference"],
                ),
                Paragraph(
                    (
                        "<b>Case No.:</b> "
                        f"{safe_value(hearing.case_number)}"
                    ),
                    styles["reference"],
                ),
            ]
        ],
        colWidths=[
            83 * mm,
            83 * mm,
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

    story.append(
        Spacer(
            1,
            5 * mm,
        )
    )

    # =====================================================
    # I. CASE INFORMATION
    # =====================================================

    case_section = [
        section_heading(
            "I. CASE INFORMATION",
            styles,
        ),
        create_information_table(
            [
                (
                    "Case Number",
                    hearing.case_number,
                ),
                (
                    "Complaint Reference",
                    f"CP-{hearing.complaint_id:04d}",
                ),
                (
                    "Complainant",
                    hearing.complainant_name,
                ),
                (
                    "Respondent",
                    hearing.respondent_name,
                ),
                (
                    "Nature of Dispute",
                    hearing.dispute_nature,
                ),
            ],
            styles,
        ),
    ]

    story.append(
        KeepTogether(case_section)
    )

    # =====================================================
    # II. HEARING PARTICULARS
    # =====================================================

    hearing_section = [
        section_heading(
            "II. HEARING PARTICULARS",
            styles,
        ),
        create_information_table(
            [
                (
                    "Date of Hearing",
                    hearing_date,
                ),
                (
                    "Time",
                    (
                        f"{start_time} - "
                        f"{end_time}"
                    ),
                ),
                (
                    "Stage of Proceedings",
                    hearing.hearing_stage,
                ),
                (
                    "Venue / Chamber",
                    hearing.chamber,
                ),
                (
                    "Mediator / Presiding Official",
                    hearing.mediator,
                ),
                (
                    "Summons Status",
                    hearing.summons_status,
                ),
                (
                    "Hearing Status",
                    hearing.status,
                ),
            ],
            styles,
        ),
    ]

    story.append(
        KeepTogether(hearing_section)
    )

    # =====================================================
    # III. DOCUMENT PREPARATION
    # =====================================================

    processing_section = [
        section_heading(
            "III. DOCUMENT PREPARATION",
            styles,
        ),
        create_information_table(
            [
                (
                    "Prepared / Processed By",
                    processed_by_name,
                ),
                (
                    "Position / Role",
                    formatted_role,
                ),
                (
                    "Date and Time Prepared",
                    processed_at,
                ),
            ],
            styles,
        ),
    ]

    story.append(
        KeepTogether(processing_section)
    )

    # =====================================================
    # IV. DOCUMENT INTEGRITY
    # =====================================================

    integrity_section = [
        section_heading(
            "IV. DOCUMENT INTEGRITY",
            styles,
        ),
        create_information_table(
            [
                (
                    "Document Identifier",
                    document_identifier,
                ),
                (
                    "Document Classification",
                    "Official Hearing Minutes",
                ),
                (
                    "Integrity Protection",
                    (
                        "SHA-256 Cryptographic Hash / "
                        "Hyperledger Fabric"
                    ),
                ),
            ],
            styles,
        ),
        Spacer(
            1,
            3 * mm,
        ),
        Paragraph(
            (
                "This electronic hearing record is prepared "
                "for document integrity verification. Upon "
                "registration, its SHA-256 cryptographic hash "
                "may be recorded through the barangay's "
                "blockchain-based document integrity system. "
                "Any subsequent modification to the generated "
                "PDF will result in a different cryptographic "
                "hash."
            ),
            styles["certification"],
        ),
    ]

    story.append(
        KeepTogether(integrity_section)
    )

    # =====================================================
    # PAGE BREAK
    # =====================================================

    story.append(
        PageBreak()
    )

    # =====================================================
    # PAGE 2+
    # MINUTES OF THE HEARING
    # =====================================================

    add_official_header(
        story,
        styles,
        "MINUTES OF THE HEARING",
    )

    # =====================================================
    # HEARING REFERENCE
    # =====================================================

    minutes_reference = create_information_table(
        [
            (
                "Case Number",
                hearing.case_number,
            ),
            (
                "Date of Hearing",
                hearing_date,
            ),
            (
                "Time",
                (
                    f"{start_time} - "
                    f"{end_time}"
                ),
            ),
            (
                "Venue / Chamber",
                hearing.chamber,
            ),
            (
                "Complainant",
                hearing.complainant_name,
            ),
            (
                "Respondent",
                hearing.respondent_name,
            ),
            (
                "Mediator / Presiding Official",
                hearing.mediator,
            ),
        ],
        styles,
    )

    story.append(
        minutes_reference
    )

    story.append(
        Spacer(
            1,
            8 * mm,
        )
    )

    # =====================================================
    # OFFICIAL PROCEEDINGS
    # =====================================================

    story.append(
        section_heading(
            "OFFICIAL PROCEEDINGS",
            styles,
        )
    )

    story.append(
        Paragraph(
            (
                "The following constitutes the official "
                "record of the proceedings, discussions, "
                "statements, and other matters recorded "
                "during the hearing:"
            ),
            styles["minutes_intro"],
        )
    )

    story.append(
        Spacer(
            1,
            2 * mm,
        )
    )

    # Long notes can naturally continue to later pages.
    add_minutes_content(
        story,
        hearing.notes,
        styles,
    )

    # =====================================================
    # PREPARED / PROCESSED BY
    # =====================================================

    story.append(
        Spacer(
            1,
            12 * mm,
        )
    )

    story.append(
        create_signature_block(
            processed_by_name,
            formatted_role,
            processed_at,
            styles,
        )
    )

    # =====================================================
    # CERTIFICATION / ELECTRONIC RECORD NOTICE
    # =====================================================

    story.append(
        Spacer(
            1,
            10 * mm,
        )
    )

    certification = Table(
        [
            [
                Paragraph(
                    (
                        "<b>ELECTRONIC RECORD NOTICE</b><br/><br/>"
                        "This document is an electronically "
                        "generated official hearing record of "
                        "Barangay Ulingao, San Rafael, Bulacan. "
                        "Document integrity is protected through "
                        "SHA-256 cryptographic hashing and "
                        "blockchain-based verification. "
                        "Alteration of the finalized document "
                        "after blockchain registration will "
                        "produce a different cryptographic hash."
                    ),
                    styles["certification"],
                )
            ]
        ],
        colWidths=[166 * mm],
    )

    certification.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#808080"),
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

    story.append(certification)

    story.append(
        Spacer(
            1,
            6 * mm,
        )
    )

    story.append(
        Paragraph(
            (
                "Barangay Ulingao, Municipality of San Rafael, "
                "Province of Bulacan"
            ),
            styles["notice"],
        )
    )

    # =====================================================
    # BUILD FINAL PDF
    # =====================================================

    pdf.build(
        story,
        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer,
    )

    # =====================================================
    # CALCULATE SHA-256 AFTER FINAL PDF
    # =====================================================

    file_hash = calculate_file_hash(
        absolute_path
    )

    # =====================================================
    # CREATE / UPDATE HEARING MINUTES DOCUMENT
    # =====================================================

    hearing_document, created = (
        HearingMinutesDocument.objects.update_or_create(
            hearing_id=hearing.hearing_id,
            document_type="HEARING_MINUTES",
            defaults={
                "complaint_id":
                    hearing.complaint_id,

                "file_name":
                    file_name,

                "file_path":
                    relative_path,

                "file_hash":
                    file_hash,

                "blockchain_status":
                    "Pending",

                "blockchain_tx_id":
                    None,

                "blockchain_registered_at":
                    None,

                "integrity_status":
                    "Not Verified",

                "last_verified_at":
                    None,

                "processed_by":
                    processed_by,

                "processed_by_name":
                    processed_by_name,

                "processed_by_role":
                    formatted_role,
            },
        )
    )

    return hearing_document