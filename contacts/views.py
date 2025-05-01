# contacts/views.py
from django.views.generic import FormView
from django.urls import reverse_lazy
from .models import ContactRequest
from .forms import ContactForm
from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
import json

class ContactView(FormView):
    template_name = 'contacts/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contacts')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

def contact_view(request):
    return render(request, 'contacts/contact.html')

def send_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            subject = data.get('subject')
            message = data.get('message')

            # Send email
            email_subject = f'Contact Form: {subject}'
            email_message = f"""
New message from {name} ({email})

Subject: {subject}

Message:
{message}
"""
            try:
                send_mail(
                    email_subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.CONTACT_EMAIL],
                    fail_silently=False,
                )
                return JsonResponse({'status': 'success'})
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Failed to send email. Please try again later.'
                })
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid request format'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })