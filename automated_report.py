import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

DATA_FILE = "sample_news_data.json"
REPORT_FILE = "news_report.pdf"

def load_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def analyze_data(data):
    analysis = {}

    articles = data.get('articles', [])
    categories = data.get('categories', [])
    bookmarks = data.get('bookmarks', [])
    reading_list = data.get('readingList', [])
    user_preferences = data.get('userPreferences', {})
    reading_history = data.get('readingHistory', [])

    analysis['total_articles'] = len(articles)
    # Get top 5 viewed articles
    top_articles = sorted(articles, key=lambda x: x.get('views',0), reverse=True)[:5]
    analysis['top_articles'] = top_articles

    # Articles per category
    category_counts = {}
    for category in categories:
        category_counts[category['name']] = category.get('articleCount', 0)
    analysis['category_counts'] = category_counts

    # Bookmarks count
    analysis['total_bookmarks'] = len(bookmarks)

    # Reading list progress
    total_reading = len(reading_list)
    completed = sum(1 for rl in reading_list if rl.get('completedAt'))
    progress_percent = (completed / total_reading * 100) if total_reading > 0 else 0
    analysis['reading_list_progress'] = progress_percent

    # User preferences summary
    analysis['user_preferences'] = user_preferences

    # Reading history count & total time spent
    total_history = len(reading_history)
    total_time_spent = sum(rh.get('timeSpent', 0) for rh in reading_history)
    analysis['total_reading_history'] = total_history
    analysis['total_time_spent'] = total_time_spent

    return analysis

def build_pdf_report(analysis):
    # Setup PDF
    doc = SimpleDocTemplate(
        REPORT_FILE,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
        title="News Content Reader Report"
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='TitleStyle', fontSize=24, leading=28, spaceAfter=24, alignment=1))
    styles.add(ParagraphStyle(name='HeadingStyle', fontSize=18, leading=22, spaceAfter=12))
    styles.add(ParagraphStyle(name='BodyStyle', fontSize=12, leading=16, spaceAfter=12))
    styles.add(ParagraphStyle(name='SmallStyle', fontSize=10, leading=12, spaceAfter=8, textColor=colors.grey))

    elements = []

    # Title Page
    elements.append(Paragraph("Automated News Content Reader Report", styles['TitleStyle']))
    elements.append(Spacer(1, 12))

    # Logo with placeholder image
    logo_url = "https://storage.googleapis.com/workspace-0f70711f-8b4e-4d94-86f1-2a93ccde5887/image/47fa8e44-44af-4d68-9a3a-c26113e981f1.png"
    img = Image(logo_url, width=2.5*inch, height=1*inch)
    img.hAlign = "CENTER"
    elements.append(img)
    elements.append(Spacer(1, 24))

    report_date = datetime.now().strftime("%B %d, %Y %H:%M")
    elements.append(Paragraph(f"Report generated on: {report_date}", styles['SmallStyle']))
    elements.append(PageBreak())

    # Summary Section
    elements.append(Paragraph("Summary", styles['HeadingStyle']))

    summary_data = [
        ['Total Articles', analysis['total_articles']],
        ['Total Bookmarks', analysis['total_bookmarks']],
        ['Total Reading List Items', f"{len(analysis['user_preferences'].get('categories', []))} subscribed categories"],
        ['Reading List Completion', f"{analysis['reading_list_progress']:.1f}%"],
        ['Total Reading History Entries', analysis['total_reading_history']],
        ['Total Time Spent Reading (seconds)', analysis['total_time_spent']],
    ]
    table = Table(summary_data, colWidths=[200, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0891b2")),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND',(0,1),(-1,-1),colors.whitesmoke),
        ('GRID',(0,0),(-1,-1),0.5,colors.grey),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 24))

    # Articles Per Category
    elements.append(Paragraph("Articles Per Category", styles['HeadingStyle']))
    cat_data = [['Category','Article Count']]
    for cat, count in analysis['category_counts'].items():
        cat_data.append([cat, count])
    cat_table = Table(cat_data, colWidths=[250, 150])
    cat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0891b2")),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND',(0,1),(-1,-1),colors.whitesmoke),
        ('GRID',(0,0),(-1,-1),0.5,colors.grey),
    ]))
    elements.append(cat_table)
    elements.append(Spacer(1, 24))

    # Top Articles Section
    elements.append(Paragraph("Top 5 Articles by Views", styles['HeadingStyle']))

    top_articles_data = [['Title', 'Author', 'Category', 'Views', 'Read Time (mins)']]
    for article in analysis['top_articles']:
        title = article.get('title', 'N/A')
        author = article.get('author', 'N/A')
        cat = article.get('category', 'N/A')
        views = article.get('views', 0)
        read_time = article.get('readTime', 0)
        top_articles_data.append([title, author, cat, views, read_time])

    top_table = Table(top_articles_data, colWidths=[200, 100, 80, 50, 80])
    top_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0891b2")),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('ALIGN',(3,1),(-1,-1),'RIGHT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND',(0,1),(-1,-1),colors.whitesmoke),
        ('GRID',(0,0),(-1,-1),0.5,colors.grey),
    ]))
    elements.append(top_table)
    elements.append(Spacer(1, 24))

    # User Preferences Overview
    elements.append(Paragraph("User Preferences Overview", styles['HeadingStyle']))

    prefs = analysis.get('user_preferences', {})
    subscribed_categories = prefs.get('categories', [])
    subscribed_sources = prefs.get('sources', [])
    font_size = prefs.get('fontSize', 'Default')
    theme = prefs.get('theme', 'Not set')
    notifications = prefs.get('notifications', False)

    prefs_paragraph = (
        f"<b>Subscribed Categories:</b> {', '.join(subscribed_categories) if subscribed_categories else 'None'}<br/>"
        f"<b>Subscribed Sources:</b> {', '.join(subscribed_sources) if subscribed_sources else 'None'}<br/>"
        f"<b>Font Size:</b> {font_size}<br/>"
        f"<b>Theme:</b> {theme}<br/>"
        f"<b>Notifications Enabled:</b> {'Yes' if notifications else 'No'}<br/>"
    )
    elements.append(Paragraph(prefs_paragraph, styles['BodyStyle']))

    # Build PDF
    doc.build(elements)

def main():
    print("Loading data...")
    data = load_data(DATA_FILE)
    print("Analyzing data...")
    analysis = analyze_data(data)
    print("Generating PDF report...")
    build_pdf_report(analysis)
    print(f"Report generated successfully: {REPORT_FILE}")

if __name__ == "__main__":
    main()

