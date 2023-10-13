from io import BytesIO

from django.conf import settings
from django.utils import timezone
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def create_shopping_list_pdf(shopping_cart):

    buffer = BytesIO()
    page = canvas.Canvas(buffer)
    pdfmetrics.registerFont(
        TTFont('Ubuntu-Regular', 'data/fonts/Ubuntu-Regular.ttf', 'UTF-8')
    )
    page.setFont('Ubuntu-Regular', size=20)
    page.drawString(x=130, y=750, text='Список ингредиентов для рецептов')
    page.setFont('Ubuntu-Regular', size=14)
    down_param = 20
    for number, ingredient in enumerate(shopping_cart, start=1):
        page.drawString(
            10,
            down_param,
            f"{number}. {ingredient['ingredient__name']}, "
            f"{ingredient['ingredient_amount_sum']} "
            f"{ingredient['ingredient__measurement_unit']}.",
        )
        down_param += 20
        if down_param >= 780:
            down_param = 20
            page.showPage()
            page.setFont('Ubuntu-Regular', size=14)

    current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    site_address = settings.CSRF_TRUSTED_ORIGINS[0]
    page.setFont('Ubuntu-Regular', size=10)
    page.drawString(x=50, y=30, text=f'Адрес сайта: {site_address}')
    page.drawString(
        x=50, y=50, text=f'Дата и время скачивания: {current_time}'
    )

    page.showPage()
    page.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
