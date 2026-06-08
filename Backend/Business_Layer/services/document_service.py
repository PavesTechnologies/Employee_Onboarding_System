from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os
from datetime import datetime


class DocumentService:

    def generate_offer_pdf(self, offer_data):

        # Load template
        env = Environment(loader=FileSystemLoader("Backend/templates"))
        template = env.get_template("offer_letter.html")

        # Render HTML
        # html_content = template.render(offer_data)
        html_content = template.render(
            {**offer_data, "current_date": datetime.today().strftime("%d %B %Y")}
        )

        # Ensure folder exists
        os.makedirs("generated_pdfs", exist_ok=True)

        output_path = f"generated_pdfs/offer_{offer_data['user_uuid']}.pdf"

        # Generate PDF
        HTML(string=html_content).write_pdf(output_path)

        return output_path

    def generate_joining_pdf(self, joining_data):

        env = Environment(loader=FileSystemLoader("Backend/templates"))
        template = env.get_template("joining_letter.html")

        logo_path = os.path.abspath(
            os.path.join("Backend", "static", "images", "paves_logo.jpg")
        )

        html_content = template.render(
            {
                **joining_data,
                "current_date": datetime.today().strftime("%d %B %Y"),
                "logo_path": logo_path,
            }
        )

        os.makedirs("generated_pdfs", exist_ok=True)

        output_path = f"generated_pdfs/joining_{joining_data['user_uuid']}.pdf"

        HTML(string=html_content, base_url=os.getcwd()).write_pdf(output_path)

        return output_path
