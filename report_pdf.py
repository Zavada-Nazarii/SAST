import requests
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, Frame, PageTemplate
from reportlab.platypus.flowables import KeepTogether, AnchorFlowable
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT

def get_engagements(auth_token):
    headers = {'Authorization': f'Token {auth_token}'}
    response = requests.get("https://defectdojo/api/v2/engagements/", headers=headers)
    engagements = response.json()['results']
    return [e for e in engagements if e['status'] == 'In Progress']

def get_tests(auth_token, engagement_id):
    headers = {'Authorization': f'Token {auth_token}'}
    response = requests.get(f"https://defectdojo/api/v2/tests/?engagement={engagement_id}&limit=10000", headers=headers)
    tests = response.json()['results']
    if tests:
        latest_test = max(tests, key=lambda x: x['id'])
        return latest_test
    return None

def get_findings(auth_token, test_id):
    headers = {'Authorization': f'Token {auth_token}'}
    response = requests.get(f"https://defectdojo/api/v2/findings/?test={test_id}&limit=1000", headers=headers)
    findings = response.json()['results']
    return [f for f in findings if f['severity'] in ['Critical', 'High', 'Medium']]

def get_tests_with_tags(auth_token, engagement_id):
    headers = {'Authorization': f'Token {auth_token}'}
    response = requests.get(f"https://defectdojo/api/v2/tests/?engagement={engagement_id}&limit=10000", headers=headers)
    tests = response.json()['results']
    tags_dict = {}
    for test in tests:
        tags = tuple(test.get('tags', []))
        if tags not in tags_dict or test['id'] > tags_dict[tags]['id']:
            tags_dict[tags] = {'id': test['id'], 'tags': test['tags'], 'created': test['created']}
    return [(info['id'], info['tags'], info['created']) for info in tags_dict.values()]

def sanitize_filename(filename):
    # Заміна пробілів та слешів на нижнє підкреслення із назв, видалення інших неприпустимих символів
    filename = re.sub(r'[ /]', '_', filename)
    filename = re.sub(r'[^\w\s.-]', '_', filename)
    return filename

def safe_paragraph(text, style):
    try:
        return Paragraph(text, style)
    except ValueError as e:
        print(f"Error creating paragraph: {e}\nText: {text}")
        return Paragraph("ERROR: Invalid paragraph content", style)

def trim_text_to_fit(paragraph, width, height, max_chars):
    if len(paragraph.text) > max_chars:
        paragraph.text = paragraph.text[:max_chars] + "..."
    while paragraph.wrap(width, height)[1] > height:
        paragraph.text = paragraph.text[:-10] + "..."
    return paragraph

def create_pdf(engagement, tests_with_tags, output_filename):
    def header(canvas, doc):
        canvas.saveState()
        header_image_path = "./Report/header.png"
        canvas.drawImage(header_image_path, 0, A4[1] - 1*inch, width=A4[0], height=1*inch)
        
        logo_path = "./Report/SAST.png"
        logo = Image(logo_path, width=1*inch, height=1*inch)
        canvas.drawImage(logo_path, doc.leftMargin, A4[1] - 1.5*inch - 1*inch, width=1*inch, height=1*inch)
        
        canvas.restoreState()

    doc = SimpleDocTemplate(output_filename, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    block_style = ParagraphStyle(name='BlockStyle', fontSize=10, leading=12)
    table_style = ParagraphStyle(name='TableStyle', fontSize=10, leading=12, wordWrap='CJK')

    # Головна назва 
    title = f"{engagement['name']} - {tests_with_tags[0][2][:10]}"
    elements.append(Spacer(1, 1*inch))  
    elements.append(safe_paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))

    # Список сервісів
    service_title_style = ParagraphStyle(name='ServiceTitleStyle', fontSize=14, leading=16, alignment=TA_LEFT, spaceAfter=12)
    service_item_style = ParagraphStyle(name='ServiceItemStyle', fontSize=14, leading=16, alignment=TA_LEFT)

    elements.append(safe_paragraph("SERVICES:", service_title_style))

    for test_id, tags, created in tests_with_tags:
        for tag in tags:
            elements.append(safe_paragraph(f'<a href="#{tag}">- {tag}</a>', service_item_style))
    elements.append(Spacer(1, 24))

    severity_colors = {
        'Critical': colors.red,
        'High': colors.orange,
        'Medium': colors.yellow
    }

    for test_id, tags, created in tests_with_tags:
        findings = get_findings(auth_token, test_id)

        for tag in tags:
            elements.append(AnchorFlowable(tag))
            tag_title = f"<b>SERVICE:</b> {tag}"
            tag_title_paragraph = safe_paragraph(tag_title, styles['Title'])
            tag_title_table = Table([[tag_title_paragraph]], colWidths=[7.5*inch])
            tag_title_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ]))
            elements.append(tag_title_table)
            elements.append(Spacer(1, 12))

            # Пошук унікальних тегів для усіх тегів та знахідок
            unique_findings = {}
            for finding in findings:
                title = finding['title']
                if title not in unique_findings:
                    unique_findings[title] = {
                        'severity': finding['severity'],
                        'description': finding['description'],
                        'count': 0
                    }
                unique_findings[title]['count'] += 1

            table_data = [['Title', 'Severity', 'Description', 'Count']]
            for title, data in unique_findings.items():
                description_paragraph = safe_paragraph(data['description'], table_style)
                trimmed_paragraph = trim_text_to_fit(description_paragraph, 439.27559055118115, 685.8897637795277, max_chars=300)
                table_data.append([
                    safe_paragraph(title, table_style),
                    data['severity'],
                    trimmed_paragraph,
                    str(data['count'])
                ])

            table = Table(table_data, colWidths=[2.5*inch, 1.5*inch, 3.0*inch, 0.5*inch])
            table_styles = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]

            for row_num, row_data in enumerate(table_data[1:], start=1):
                severity = row_data[1]
                if severity in severity_colors:
                    table_styles.append(('BACKGROUND', (1, row_num), (1, row_num), severity_colors[severity]))

            table.setStyle(TableStyle(table_styles))
            elements.append(table)
            elements.append(Spacer(1, 24))

            # Findings blocks for each tag
            for finding in findings:
                severity_color = severity_colors.get(finding['severity'], colors.white)
                block_content = f"""
                <b>Title:</b> {finding['title']}<br/>
                <b>Severity:</b> {finding['severity']}<br/>
                <b>Description:</b> {finding['description']}<br/>
                <b>Line:</b> {finding.get('line', 'N/A')}<br/>
                <b>File Path:</b> {finding.get('file_path', 'N/A')}<br/>
                """
                block_paragraph = safe_paragraph(block_content, block_style)
                trimmed_paragraph = trim_text_to_fit(block_paragraph, 439.27559055118115, 685.8897637795277, max_chars=300)
                block_table = Table([[trimmed_paragraph]], colWidths=[7.5*inch])
                block_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), severity_color),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('LEFTPADDING', (0, 0), (-1, -1), 12),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                    ('TOPPADDING', (0, 0), (-1, -1), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ]))
                elements.append(KeepTogether(block_table))
                elements.append(Spacer(1, 12))

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
    template = PageTemplate(id='test', frames=[frame], onPage=header)
    doc.addPageTemplates([template])

    doc.build(elements)


def main(auth_token):
    engagements = get_engagements(auth_token)
    for engagement in engagements:
        tests_with_tags = get_tests_with_tags(auth_token, engagement['id'])
        if tests_with_tags:
            output_filename = sanitize_filename(f"{engagement['name']}.pdf")
            create_pdf(engagement, tests_with_tags, output_filename)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python report_pdf.py <Authorization Token>")
    else:
        auth_token = sys.argv[1]
        main(auth_token)

