#!/usr/bin/env python3
"""
Generate a PDF book from markdown chapter files.
Modern React: A Complete Guide - PDF Generator
"""

import os
import re
import textwrap
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white, gray
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Preformatted, Table, TableStyle, KeepTogether,
    Flowable, BaseDocTemplate, Frame, PageTemplate,
    NextPageTemplate
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus.tableofcontents import TableOfContents

# ─── Register Unicode-capable fonts ───
# Arial Unicode MS has broad Unicode coverage (box-drawing, arrows, symbols)
ARIAL_UNICODE = '/Library/Fonts/Arial Unicode.ttf'
pdfmetrics.registerFont(TTFont('ArialUnicode', ARIAL_UNICODE))

# We need bold/italic variants - use Arial Unicode for all since it has good coverage
# ReportLab needs separate registrations for bold/italic even if same file
pdfmetrics.registerFont(TTFont('ArialUnicode-Bold', ARIAL_UNICODE))
pdfmetrics.registerFont(TTFont('ArialUnicode-Italic', ARIAL_UNICODE))
pdfmetrics.registerFont(TTFont('ArialUnicode-BoldItalic', ARIAL_UNICODE))

from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily('ArialUnicode',
    normal='ArialUnicode',
    bold='ArialUnicode-Bold',
    italic='ArialUnicode-Italic',
    boldItalic='ArialUnicode-BoldItalic',
)

# Use Menlo for monospace code (good Unicode support)
# Menlo is a .ttc (collection), try to register it
try:
    pdfmetrics.registerFont(TTFont('Menlo', '/System/Library/Fonts/Menlo.ttc', subfontIndex=0))
    CODE_FONT = 'Menlo'
except:
    CODE_FONT = 'Courier'

# Font name constants
BODY_FONT = 'ArialUnicode'
BODY_FONT_BOLD = 'ArialUnicode-Bold'
BODY_FONT_ITALIC = 'ArialUnicode-Italic'

# ─── Colors ───
DARK_BLUE = HexColor('#1a365d')
MEDIUM_BLUE = HexColor('#2b6cb0')
LIGHT_BLUE = HexColor('#ebf8ff')
CODE_BG = HexColor('#f7fafc')
CODE_BORDER = HexColor('#e2e8f0')
ACCENT = HexColor('#3182ce')
DARK_GRAY = HexColor('#2d3748')
MEDIUM_GRAY = HexColor('#4a5568')
LIGHT_GRAY = HexColor('#edf2f7')
WARNING_BG = HexColor('#fffbeb')
WARNING_BORDER = HexColor('#f6ad55')
TIP_BG = HexColor('#f0fff4')
TIP_BORDER = HexColor('#48bb78')

# ─── Custom Styles ───
def create_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        'BookTitle',
        parent=styles['Title'],
        fontSize=36,
        leading=44,
        textColor=DARK_BLUE,
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName=BODY_FONT_BOLD,
    ))

    styles.add(ParagraphStyle(
        'BookSubtitle',
        parent=styles['Normal'],
        fontSize=18,
        leading=24,
        textColor=MEDIUM_BLUE,
        alignment=TA_CENTER,
        spaceAfter=40,
        fontName=BODY_FONT,
    ))

    styles.add(ParagraphStyle(
        'ChapterTitle',
        parent=styles['Heading1'],
        fontSize=28,
        leading=34,
        textColor=DARK_BLUE,
        spaceBefore=0,
        spaceAfter=24,
        fontName=BODY_FONT_BOLD,
    ))

    styles.add(ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=20,
        leading=26,
        textColor=DARK_BLUE,
        spaceBefore=20,
        spaceAfter=12,
        fontName=BODY_FONT_BOLD,
    ))

    styles.add(ParagraphStyle(
        'SubSection',
        parent=styles['Heading3'],
        fontSize=16,
        leading=22,
        textColor=MEDIUM_BLUE,
        spaceBefore=16,
        spaceAfter=8,
        fontName=BODY_FONT_BOLD,
    ))

    styles.add(ParagraphStyle(
        'SubSubSection',
        parent=styles['Heading4'],
        fontSize=13,
        leading=18,
        textColor=MEDIUM_GRAY,
        spaceBefore=12,
        spaceAfter=6,
        fontName=BODY_FONT_BOLD,
    ))

    styles.add(ParagraphStyle(
        'BodyText2',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        textColor=DARK_GRAY,
        spaceBefore=4,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        fontName=BODY_FONT,
    ))

    styles.add(ParagraphStyle(
        'BulletItem',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        textColor=DARK_GRAY,
        leftIndent=24,
        bulletIndent=12,
        spaceBefore=2,
        spaceAfter=2,
        fontName=BODY_FONT,
    ))

    styles.add(ParagraphStyle(
        'NumberedItem',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        textColor=DARK_GRAY,
        leftIndent=24,
        bulletIndent=12,
        spaceBefore=2,
        spaceAfter=2,
        fontName=BODY_FONT,
    ))

    styles.add(ParagraphStyle(
        'CodeBlock',
        parent=styles['Code'],
        fontSize=9,
        leading=12,
        textColor=DARK_GRAY,
        backColor=CODE_BG,
        borderColor=CODE_BORDER,
        borderWidth=0.5,
        borderPadding=8,
        leftIndent=8,
        rightIndent=8,
        spaceBefore=8,
        spaceAfter=8,
        fontName=CODE_FONT,
        wordWrap='CJK',
    ))

    styles.add(ParagraphStyle(
        'InlineCode',
        parent=styles['Normal'],
        fontSize=10,
        fontName=CODE_FONT,
        textColor=MEDIUM_BLUE,
    ))

    styles.add(ParagraphStyle(
        'BlockQuote',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        textColor=MEDIUM_GRAY,
        leftIndent=24,
        borderColor=ACCENT,
        borderWidth=2,
        borderPadding=8,
        spaceBefore=8,
        spaceAfter=8,
        fontName=BODY_FONT_ITALIC,
    ))

    styles.add(ParagraphStyle(
        'TOCEntry',
        parent=styles['Normal'],
        fontSize=14,
        leading=22,
        textColor=DARK_BLUE,
        spaceBefore=4,
        spaceAfter=4,
        fontName=BODY_FONT,
    ))

    styles.add(ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=MEDIUM_GRAY,
        alignment=TA_CENTER,
    ))

    return styles


class HorizontalRule(Flowable):
    """A horizontal line separator."""
    def __init__(self, width_pct=100, color=CODE_BORDER, thickness=1):
        Flowable.__init__(self)
        self.width_pct = width_pct
        self.color = color
        self.thickness = thickness

    def draw(self):
        w = self.canv._pagesize[0] * self.width_pct / 100 - 2 * inch
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 0, w, 0)

    def wrap(self, availWidth, availHeight):
        return (availWidth, self.thickness + 4)


class CodeBlockFlowable(Flowable):
    """A code block with background color and border."""
    def __init__(self, code_text, language=''):
        Flowable.__init__(self)
        self.code_text = code_text
        self.language = language
        self.padding = 10
        self.font_size = 8.5
        self.leading = 11.5

    def wrap(self, availWidth, availHeight):
        self.availWidth = availWidth
        lines = self.code_text.split('\n')
        self.height = len(lines) * self.leading + 2 * self.padding
        self.width = availWidth
        return (self.width, self.height)

    def split(self, availWidth, availHeight):
        """Split code block across pages if too tall."""
        lines = self.code_text.split('\n')
        header_space = 14 if self.language else 0
        usable = availHeight - 2 * self.padding - header_space
        if usable < self.leading * 2:
            return []  # Not enough space for even 2 lines, move to next page

        max_lines = int(usable / self.leading)
        if max_lines >= len(lines):
            return [self]

        first_text = '\n'.join(lines[:max_lines])
        second_text = '\n'.join(lines[max_lines:])
        return [
            CodeBlockFlowable(first_text, self.language),
            CodeBlockFlowable(second_text, ''),
        ]

    def draw(self):
        # Background
        self.canv.setFillColor(HexColor('#f8f9fa'))
        self.canv.setStrokeColor(HexColor('#dee2e6'))
        self.canv.setLineWidth(0.5)
        self.canv.roundRect(0, 0, self.width, self.height, 4, fill=1, stroke=1)

        # Language label
        if self.language:
            self.canv.setFillColor(HexColor('#868e96'))
            self.canv.setFont(BODY_FONT, 7)
            self.canv.drawString(self.padding, self.height - 12, self.language)
            y_start = self.height - self.padding - 14
        else:
            y_start = self.height - self.padding - 2

        # Code text
        self.canv.setFillColor(DARK_GRAY)
        self.canv.setFont(CODE_FONT, self.font_size)
        lines = self.code_text.split('\n')
        y = y_start
        for line in lines:
            # Truncate long lines
            if len(line) > 90:
                line = line[:87] + '...'
            self.canv.drawString(self.padding, y, line)
            y -= self.leading


def escape_xml(text):
    """Escape XML special characters for reportlab Paragraph."""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text


def format_inline(text):
    """Convert inline markdown to reportlab XML tags."""
    # Escape XML first
    text = escape_xml(text)

    # Step 1: Extract inline code spans and protect them from further processing
    code_placeholders = {}
    counter = [0]

    def replace_code(m):
        key = f'\x00CODE{counter[0]}\x00'
        code_placeholders[key] = '<font name="' + CODE_FONT + '" size="9" color="#2b6cb0">' + m.group(1) + '</font>'
        counter[0] += 1
        return key

    text = re.sub(r'`([^`]+?)`', replace_code, text)

    # Step 2: Extract links and protect them
    link_placeholders = {}

    def replace_link(m):
        key = f'\x00LINK{counter[0]}\x00'
        link_placeholders[key] = f'<u>{m.group(1)}</u>'
        counter[0] += 1
        return key

    text = re.sub(r'\[([^\]]+?)\]\([^\)]+?\)', replace_link, text)

    # Step 3: Bold + italic (***text*** or ___text___)
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)

    # Step 4: Bold (**text** or __text__)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)

    # Step 5: Italic (*text* or _text_) - careful not to match inside words
    text = re.sub(r'(?<!\w)\*([^\*]+?)\*(?!\w)', r'<i>\1</i>', text)
    text = re.sub(r'(?<!\w)_([^_]+?)_(?!\w)', r'<i>\1</i>', text)

    # Step 6: Restore protected spans
    for key, val in code_placeholders.items():
        text = text.replace(key, val)
    for key, val in link_placeholders.items():
        text = text.replace(key, val)

    return text


def parse_markdown_to_flowables(md_text, styles, chapter_num=None):
    """Parse markdown text and return a list of reportlab flowables."""
    flowables = []
    lines = md_text.split('\n')
    i = 0
    in_code_block = False
    code_lines = []
    code_language = ''
    in_table = False
    table_rows = []

    while i < len(lines):
        line = lines[i]

        # Code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                # End code block
                code_text = '\n'.join(code_lines)
                if code_text.strip():
                    flowables.append(Spacer(1, 6))
                    flowables.append(CodeBlockFlowable(code_text, code_language))
                    flowables.append(Spacer(1, 6))
                code_lines = []
                code_language = ''
                in_code_block = False
            else:
                # Start code block
                in_code_block = True
                lang_match = re.match(r'```(\w+)', line.strip())
                code_language = lang_match.group(1) if lang_match else ''
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Table detection
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                in_table = True
                table_rows = []
            # Skip separator rows (|---|---|)
            if re.match(r'^\s*\|[\s\-:|]+\|\s*$', line):
                i += 1
                continue
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            table_rows.append(cells)
            i += 1
            continue
        elif in_table:
            # End of table
            in_table = False
            if table_rows:
                flowables.extend(create_table(table_rows, styles))
            table_rows = []

        stripped = line.strip()

        # Empty line
        if not stripped:
            i += 1
            continue

        # Horizontal rule
        if re.match(r'^(\-{3,}|\*{3,}|_{3,})$', stripped):
            flowables.append(Spacer(1, 6))
            flowables.append(HorizontalRule())
            flowables.append(Spacer(1, 6))
            i += 1
            continue

        # Headers
        if stripped.startswith('#'):
            header_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
            if header_match:
                level = len(header_match.group(1))
                text = header_match.group(2).strip()
                text = format_inline(text)

                if level == 1:
                    flowables.append(Spacer(1, 40))
                    flowables.append(Paragraph(text, styles['ChapterTitle']))
                    flowables.append(HorizontalRule(color=DARK_BLUE, thickness=2))
                    flowables.append(Spacer(1, 16))
                elif level == 2:
                    flowables.append(Spacer(1, 12))
                    flowables.append(Paragraph(text, styles['SectionTitle']))
                elif level == 3:
                    flowables.append(Paragraph(text, styles['SubSection']))
                elif level >= 4:
                    flowables.append(Paragraph(text, styles['SubSubSection']))
            i += 1
            continue

        # Blockquote
        if stripped.startswith('>'):
            quote_text = stripped.lstrip('> ').strip()
            quote_text = format_inline(quote_text)
            flowables.append(Paragraph(quote_text, styles['BlockQuote']))
            i += 1
            continue

        # Unordered list items
        list_match = re.match(r'^(\s*)([-*+])\s+(.+)$', stripped)
        if list_match:
            indent_level = len(line) - len(line.lstrip())
            text = format_inline(list_match.group(3))
            bullet_style = ParagraphStyle(
                'DynBullet',
                parent=styles['BulletItem'],
                leftIndent=24 + indent_level * 12,
                bulletIndent=12 + indent_level * 12,
            )
            flowables.append(Paragraph(text, bullet_style, bulletText='\u2022'))
            i += 1
            continue

        # Ordered list items
        num_match = re.match(r'^(\s*)(\d+)\.\s+(.+)$', stripped)
        if num_match:
            num = num_match.group(2)
            text = format_inline(num_match.group(3))
            flowables.append(Paragraph(text, styles['NumberedItem'], bulletText=f'{num}.'))
            i += 1
            continue

        # Regular paragraph - collect continuation lines
        para_lines = [stripped]
        i += 1
        while i < len(lines):
            next_line = lines[i].strip()
            if (not next_line or next_line.startswith('#') or
                next_line.startswith('```') or next_line.startswith('>') or
                next_line.startswith('- ') or next_line.startswith('* ') or
                next_line.startswith('+ ') or re.match(r'^\d+\.\s', next_line) or
                (next_line.startswith('|') and '|' in next_line)):
                break
            para_lines.append(next_line)
            i += 1

        para_text = ' '.join(para_lines)
        para_text = format_inline(para_text)
        flowables.append(Paragraph(para_text, styles['BodyText2']))

    # Handle any remaining table
    if in_table and table_rows:
        flowables.extend(create_table(table_rows, styles))

    # Handle any remaining code block
    if in_code_block and code_lines:
        code_text = '\n'.join(code_lines)
        if code_text.strip():
            flowables.append(CodeBlockFlowable(code_text, code_language))

    return flowables


def create_table(rows, styles):
    """Create a reportlab Table from parsed rows."""
    flowables = []
    if not rows:
        return flowables

    # Convert cells to Paragraphs
    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=DARK_GRAY,
        fontName=BODY_FONT,
    )
    header_style = ParagraphStyle(
        'TableHeader',
        parent=cell_style,
        fontName=BODY_FONT_BOLD,
        textColor=white,
    )

    # Determine column count
    max_cols = max(len(r) for r in rows)

    # Normalize rows
    table_data = []
    for idx, row in enumerate(rows):
        while len(row) < max_cols:
            row.append('')
        if idx == 0:
            table_data.append([Paragraph(format_inline(c), header_style) for c in row])
        else:
            table_data.append([Paragraph(format_inline(c), cell_style) for c in row])

    # Calculate column widths
    avail = 6.5 * inch
    col_width = avail / max_cols if max_cols > 0 else avail

    t = Table(table_data, colWidths=[col_width] * max_cols)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), BODY_FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ('FONTNAME', (0, 1), (-1, -1), BODY_FONT),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, CODE_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    flowables.append(Spacer(1, 8))
    flowables.append(t)
    flowables.append(Spacer(1, 8))
    return flowables


# Chapter files in order
CHAPTER_DIR = '/Users/e141057/Desktop/work/clade_play_area/books/react/manuscript'
CHAPTER_FOLDERS = [
    '01-welcome-to-react-19',
    '02-development-environment',
    '03-jsx-in-depth',
    '04-components-and-props',
    '05-state-and-usestate',
    '06-event-handling',
    '07-conditional-rendering-and-lists',
    '08-useeffect-and-lifecycle',
    '09-forms',
    '10-useref-and-dom',
    '11-performance-optimization',
    '12-custom-hooks',
    '13-context-api',
    '14-usereducer',
    '15-react-router',
    '16-api-and-data-fetching',
    '17-styling',
    '18-state-management',
    '19-error-boundaries',
    '20-accessibility',
    '21-testing',
    '22-debugging',
    '23-authentication',
    '24-deployment',
    '25-architecture',
    '26-assets-and-env',
    '27-best-practices',
    '28-interview-prep',
    '29-real-world-project',
    '30-glossary',
]


def add_page_number(canvas, doc):
    """Add page number and footer to each page."""
    page_num = canvas.getPageNumber()
    if page_num > 2:  # Skip cover and TOC first page
        canvas.saveState()
        canvas.setFont(BODY_FONT, 9)
        canvas.setFillColor(MEDIUM_GRAY)
        canvas.drawCentredString(
            letter[0] / 2, 0.5 * inch,
            f"- {page_num} -"
        )
        # Header line
        canvas.setStrokeColor(CODE_BORDER)
        canvas.setLineWidth(0.5)
        canvas.line(inch, letter[1] - 0.6 * inch, letter[0] - inch, letter[1] - 0.6 * inch)
        canvas.setFont(BODY_FONT_ITALIC, 8)
        canvas.setFillColor(HexColor('#a0aec0'))
        canvas.drawString(inch, letter[1] - 0.55 * inch, 'Modern React: A Complete Guide')
        canvas.restoreState()


def build_cover_page(styles):
    """Create the cover page flowables."""
    flowables = []
    flowables.append(Spacer(1, 2.5 * inch))
    flowables.append(Paragraph('Modern React', styles['BookTitle']))
    flowables.append(Paragraph('A Complete Guide', styles['BookSubtitle']))
    flowables.append(Spacer(1, 0.5 * inch))
    flowables.append(HorizontalRule(width_pct=40, color=ACCENT, thickness=2))
    flowables.append(Spacer(1, 0.3 * inch))

    subtitle_style = ParagraphStyle(
        'CoverDesc',
        parent=styles['Normal'],
        fontSize=13,
        leading=20,
        textColor=MEDIUM_GRAY,
        alignment=TA_CENTER,
        fontName=BODY_FONT,
    )
    flowables.append(Paragraph(
        'From Fundamentals to Production-Ready Applications',
        subtitle_style
    ))
    flowables.append(Spacer(1, 0.3 * inch))
    flowables.append(Paragraph(
        'Functional Components &bull; Hooks &bull; Modern Patterns',
        subtitle_style
    ))
    flowables.append(Spacer(1, 2 * inch))

    edition_style = ParagraphStyle(
        'Edition',
        parent=styles['Normal'],
        fontSize=11,
        textColor=MEDIUM_GRAY,
        alignment=TA_CENTER,
        fontName=BODY_FONT,
    )
    flowables.append(Paragraph('2025 Edition &bull; 30 Chapters', edition_style))
    flowables.append(PageBreak())
    return flowables


def build_toc_page(styles):
    """Create a table of contents page."""
    flowables = []
    flowables.append(Spacer(1, 0.5 * inch))
    flowables.append(Paragraph('Table of Contents', styles['ChapterTitle']))
    flowables.append(HorizontalRule(color=DARK_BLUE, thickness=2))
    flowables.append(Spacer(1, 16))

    chapter_names = [
        ('1', 'Welcome to React'),
        ('2', 'Development Environment'),
        ('3', 'JSX in Depth'),
        ('4', 'Components and Props'),
        ('5', 'State and useState'),
        ('6', 'Event Handling'),
        ('7', 'Conditional Rendering and Lists'),
        ('8', 'useEffect and Component Lifecycle'),
        ('9', 'Forms'),
        ('10', 'useRef and DOM Manipulation'),
        ('11', 'Performance Optimization'),
        ('12', 'Custom Hooks'),
        ('13', 'Context API'),
        ('14', 'useReducer'),
        ('15', 'React Router'),
        ('16', 'API and Data Fetching'),
        ('17', 'Styling in React'),
        ('18', 'State Management at Scale'),
        ('19', 'Error Boundaries'),
        ('20', 'Accessibility'),
        ('21', 'Testing'),
        ('22', 'Debugging'),
        ('23', 'Authentication'),
        ('24', 'Deployment and Production'),
        ('25', 'App Architecture and Folder Structure'),
        ('26', 'Images, Assets, and Environment Variables'),
        ('27', 'Best Practices and Common Mistakes'),
        ('28', 'Interview Preparation'),
        ('29', 'Building a Real-World Project'),
        ('30', 'Glossary of React Terms'),
    ]

    for num, name in chapter_names:
        toc_style = ParagraphStyle(
            f'TOC_{num}',
            parent=styles['Normal'],
            fontSize=12,
            leading=20,
            textColor=DARK_GRAY,
            leftIndent=20,
            fontName=BODY_FONT,
        )
        flowables.append(Paragraph(
            f'<b>Chapter {num}</b> &mdash; {name}',
            toc_style
        ))

    flowables.append(PageBreak())
    return flowables


def main():
    output_path = os.path.join(
        '/Users/e141057/Desktop/work/clade_play_area/books/react/build',
        'Modern_React_Complete_Guide.pdf'
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    styles = create_styles()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        topMargin=0.85 * inch,
        bottomMargin=0.85 * inch,
        leftMargin=1 * inch,
        rightMargin=1 * inch,
        title='Modern React: A Complete Guide',
        author='Modern React Book',
        subject='React Development',
    )

    story = []

    # Cover page
    print("Building cover page...")
    story.extend(build_cover_page(styles))

    # Table of contents
    print("Building table of contents...")
    story.extend(build_toc_page(styles))

    # Chapters
    for idx, folder in enumerate(CHAPTER_FOLDERS):
        chapter_path = os.path.join(CHAPTER_DIR, folder, 'chapter.md')
        if not os.path.exists(chapter_path):
            print(f"  Skipping {folder} (no chapter.md)")
            continue

        print(f"Processing chapter {idx + 1}/30: {folder}...")
        with open(chapter_path, 'r', encoding='utf-8') as f:
            md_text = f.read()

        # Each chapter starts on a new page
        if idx > 0:
            story.append(PageBreak())

        chapter_flowables = parse_markdown_to_flowables(md_text, styles, chapter_num=idx + 1)
        story.extend(chapter_flowables)

    # Build the PDF
    print("\nGenerating PDF... (this may take a minute)")
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)

    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\nPDF generated successfully!")
    print(f"  Location: {output_path}")
    print(f"  Size: {file_size_mb:.1f} MB")


if __name__ == '__main__':
    main()
