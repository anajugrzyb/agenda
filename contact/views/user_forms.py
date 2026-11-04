from django.shortcuts import render, redirect
from contact.forms import LoginForm, RegisterForm, RegisterUpdateForm
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

def register(request):
    form = RegisterForm()
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário registrado')
            return redirect('contact:login')
            
    return render(
        request,
        'contact/register.html',
        {
            'form': form 
        }
    )

@login_required(login_url='contact:login')    
def user_update(request):
    form = RegisterUpdateForm(instance=request.user)
    
    if request.method != 'POST':
        return render(
            request,
            'contact/user_update.html',
            {
                'form': form 
            }
        )
        
    form = RegisterUpdateForm(data=request.POST, instance=request.user)
    
    if not form.is_valid():
        return render(
            request,
            'contact/user_update.html',
            {
                'form': form 
            }
        )
        
    user = form.save()
    auth.update_session_auth_hash(request, user)
    messages.success(request, 'Perfil atualizado com sucesso')
    return redirect('contact:user_update')
        
    
def login_view(request):  
    form = LoginForm(request)
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            messages.success(request, 'Logado com sucesso')
            return redirect('contact:index')
        messages.error(request, 'Usuário ou senha inválidos')
        
     
    return render(
        request,
        'contact/login.html',
        {
            'form': form 
        }
    )
    
@login_required(login_url='contact:login')
@require_POST
def logout_view(request):
    auth.logout(request)
    return redirect('contact:login')
