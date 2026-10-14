# pdf_generator.py
from xhtml2pdf import pisa
import markdown

def create_pdf(markdown_text, output_filename="Representment_Packet.pdf"):
    # First, convert the raw Markdown string into HTML tags
    html_body = markdown.markdown(markdown_text)
    
    # Next, inject that HTML body into a styled template
    html_content = f"""
    <html>
    <head>
        <style>
            @page {{
                size: a4 portrait;
                margin: 2.5cm;
            }}
            body {{
                font-family: Helvetica, Arial, sans-serif;
                font-size: 14px;
                color: #333333;
                line-height: 1.5;
            }}
            h1 {{
                color: #1a365d;
                font-size: 20px;
                border-bottom: 2px solid #1a365d;
                padding-bottom: 8px;
                margin-bottom: 20px;
                text-align: center;
            }}
            h2, h3 {{
                color: #2b6cb0;
                font-size: 16px;
                margin-top: 25px;
                margin-bottom: 10px;
            }}
            p {{
                margin-bottom: 12px;
            }}
            ul, ol {{
                margin-bottom: 15px;
                margin-left: 20px;
            }}
            li {{
                margin-bottom: 6px;
            }}
            blockquote {{
                background-color: #f7fafc;
                border-left: 4px solid #4299e1;
                padding: 10px 15px;
                margin: 15px 0;
                font-style: italic;
                color: #4a5568;
            }}
            hr {{
                border: 0;
                border-top: 1px solid #e2e8f0;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                font-size: 10px;
                color: #a0aec0;
                margin-top: 40px;
                border-top: 1px solid #e2e8f0;
                padding-top: 10px;
            }}
        </style>
    </head>
    <body>
        <h1>FORMAL CHARGEBACK REPRESENTMENT PACKET</h1>
        {html_body}
        <div class="footer">Generated automatically by ChargeGuard AI Sentinel on August 22, 2026</div>
    </body>
    </html>
    """
    
    # Create the PDF
    with open(output_filename, "wb") as pdf_file:
        pisa.CreatePDF(html_content, dest=pdf_file)
        
    return output_filename