from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML
import os

TEMPLATE_DIR = os.path.join("Backend", "templates")


def generate_pdf(template_name, context):

    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml"]),
    )

    template = env.get_template(template_name)

    html = template.render(context)

    # Return PDF bytes instead of saving locally
    pdf_bytes = HTML(string=html).write_pdf()

    return pdf_bytes
