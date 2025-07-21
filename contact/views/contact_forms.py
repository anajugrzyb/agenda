from django.shortcuts import render
from contact.forms import ContactForm

def create(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
  
    else:
        form = ContactForm()

    return render(request, 'contact/create.html', {'form': form})