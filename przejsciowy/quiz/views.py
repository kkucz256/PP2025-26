import os
import re
import pdfplumber
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage

def upload_pdf_view(request):
    context = {}

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'extract':
            if 'pdf_file' not in request.FILES:
                context['error'] = "Nie wybrano pliku."
                return render(request, "quiz/upload_pdf.html", context)

            uploaded_file = request.FILES['pdf_file']

            if not uploaded_file.name.endswith('.pdf'):
                context['error'] = "To nie jest plik PDF."
                return render(request, "quiz/upload_pdf.html", context)

            try:
                fs = FileSystemStorage()
                old_filename = request.session.get('last_uploaded_pdf')
                
                if old_filename:
                    old_file_path = os.path.join(settings.MEDIA_ROOT, old_filename)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                        print(f"DEBUG: Usunięto poprzedni plik usera: {old_filename}")

                filename = fs.save(uploaded_file.name, uploaded_file)
                file_url = fs.url(filename)
                
                request.session['last_uploaded_pdf'] = filename
                
                context['file_url'] = file_url
                context['filename'] = filename

                extracted_text = ""
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text(x_tolerance=1, y_tolerance=3)
                        if text:
                            text = text.replace('\r', '')
                            text = text.replace('-\n', '')
                            text = text.replace('\n', ' ')
                            extracted_text += text + " "
                
                extracted_text = re.sub(r'\s+', ' ', extracted_text).strip()

                if not extracted_text:
                    context['error'] = "Nie udało się odczytać tekstu."
                else:
                    context['extracted_text'] = extracted_text

            except Exception as e:
                context['error'] = f"Błąd: {str(e)}"

        elif action == 'generate':
            final_text = request.POST.get('final_text')
            filename_to_delete = request.POST.get('filename_to_delete')

            if not final_text:
                context['error'] = "Pole tekstowe jest puste."
            else:
                print(f"DEBUG: Otrzymano tekst o długości {len(final_text)} znaków.")
                context['success'] = "Pytania generują się w tle (symulacja)."

                if filename_to_delete:
                    file_path = os.path.join(settings.MEDIA_ROOT, filename_to_delete)
                    if os.path.exists(file_path):
                        os.remove(file_path)

    return render(request, "quiz/upload_pdf.html", context)