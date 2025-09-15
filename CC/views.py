from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import *
from CC.models import InstituteInfo  
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile
from django.contrib.auth import get_user_model
from django.db.models import Q
from .forms import ProfileUpdateForm
from django.views.decorators.csrf import csrf_protect
from .forms import*
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.views import View
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from .forms import*
from django.db import transaction

# Create your views here.

def home_redirect(request):
    return redirect('Home')


def Home(request):
    university_category = Category.objects.get(name="University")
    college_category = Category.objects.get(name="College")
    
    universities = InstituteInfo.objects.filter(category=university_category)
    colleges = InstituteInfo.objects.filter(category=college_category)
    
    context = {
        'universities': universities,
        'colleges': colleges
    }
    return render(request, 'CC/home.html', context)

def Login(request):
    return render(request,template_name='CC/Login.html')

def Universities(request):
    InstituteName = InstituteInfo.objects.filter(category__name='University')  # or whatever filter you're using
    categories = Category.objects.all()
    context = {
        'InstituteName': InstituteName,
        'categories': categories,
    }
    return render(request, 'CC/universities.html', context)

from django.shortcuts import render, get_object_or_404
from .models import InstituteInfo  

def institute_detail(request, institute_id):
    institute = get_object_or_404(InstituteInfo, pk=institute_id)
    
    if request.method == 'POST':
        if 'action' in request.POST:
            if request.POST['action'] == 'update' and request.user.is_staff:
                # Update the institute
                institute.title = request.POST.get('title')
                institute.description = request.POST.get('description')
                institute.location = request.POST.get('location')
                institute.nearby_hostels = request.POST.get('nearby_hostels')
                institute.rank = request.POST.get('rank')
                institute.department = request.POST.get('department')
                institute.contact = request.POST.get('contact')
                institute.status = request.POST.get('status')
                institute.save()
                messages.success(request, 'Institute updated successfully!')
                return redirect('institute_detail', institute_id=institute.pk)
                
            elif request.POST['action'] == 'delete' and request.user.is_staff:
                # Delete the institute
                institute.delete()
                messages.success(request, 'Institute deleted successfully!')
                return redirect('Home')  # Change 'home' to your desired redirect URL
    
    return render(request, 'CC/institute_detail.html', {'institute': institute})

def Colleges(request):
    college_category = Category.objects.get(name="College")
    InstituteName = InstituteInfo.objects.filter(category= college_category).prefetch_related('images')
    context = {'InstituteName': InstituteName}
    return render(request, 'CC/Colleges.html', context)    


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from .models import InstituteInfo, Circular

def circulars(request):
    # Handle POST requests for circular updates/deletions
    if request.method == 'POST' and request.user.is_staff:
        if 'action' in request.POST:
            circular_id = request.POST.get('circular_id')
            circular = get_object_or_404(Circular, pk=circular_id)
            institute_id = circular.institute.id
            
            if request.POST['action'] == 'update_circular':
                circular.title = request.POST.get('title')
                circular.admission_period = request.POST.get('admission_period')
                circular.programs = request.POST.get('programs')
                circular.details = request.POST.get('details')
                
                if hasattr(Circular, 'is_active'):
                    circular.is_active = request.POST.get('is_active') == 'true'
                
                circular.save()
                messages.success(request, 'Circular updated successfully!')
                return redirect('circulars')
                
            elif request.POST['action'] == 'delete_circular':
                circular.delete()
                messages.success(request, 'Circular deleted successfully!')
                return redirect('circulars')

    # Get active circulars and check if is_active field exists
    has_is_active = hasattr(Circular, 'is_active')
    try:
        if has_is_active:
            institutes = InstituteInfo.objects.filter(
                circulars__is_active=True
            ).distinct().prefetch_related('circulars')
        else:
            institutes = InstituteInfo.objects.filter(
                circulars__isnull=False
            ).distinct().prefetch_related('circulars')
    except Exception as e:
        institutes = InstituteInfo.objects.filter(
            circulars__isnull=False
        ).distinct().prefetch_related('circulars')
    
    return render(request, 'CC/circulars.html', {
        'institutes': institutes,
        'user': request.user,
        'has_is_active': has_is_active  # Pass this to template
    })

@csrf_protect
@transaction.atomic
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            print(f"Created user ID: {user.id}")  # Debug
            
            # Verify user exists in database
            from django.contrib.auth import get_user_model
            User = get_user_model()
            print(f"Total users: {User.objects.count()}")  # Debug
            
            login(request, user)
            return redirect('Home')


from django.contrib.auth import get_user_model
User = get_user_model()

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Debug: Print which user model is being used
        print(f"Authenticating against: {User.__name__}")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('Home')
        else:
            # Debug: Check if user exists but password is wrong
            try:
                user_exists = User.objects.get(username=username)
                messages.error(request, 'Password is incorrect')
            except User.DoesNotExist:
                messages.error(request, 'Username does not exist')
    
    return render(request, 'CC/Login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('home_redirect')

def clear_signup_session(request):
    if 'signup_form_data' in request.session:
        del request.session['signup_form_data']
    return JsonResponse({'status': 'success'})

@login_required
def update_profile_pic(request):
    if request.method == 'POST' and request.FILES.get('profile_pic'):
        # Get or create profile for the user
        profile, created = Profile.objects.get_or_create(user=request.user)
        
        # Delete old profile pic if exists
        if profile.profile_pic:
            profile.profile_pic.delete()
        
        # Save new profile pic
        profile.profile_pic = request.FILES['profile_pic']
        profile.save()
        
        return JsonResponse({
            'success': True,
            'url': profile.profile_pic.url
        })
    return JsonResponse({
        'success': False,
        'error': 'Invalid request'
    })



def search_results(request):
    query = request.GET.get('q', '')
    
    if query:
        # Search across all relevant fields in InstituteInfo
        institute_results = InstituteInfo.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(rank__icontains=query) |
            Q(department__icontains=query) |
            Q(contact__icontains=query)
        ).distinct()
        
        # Search across all relevant fields in Circular
        circular_results = Circular.objects.filter(
            Q(title__icontains=query) |
            Q(admission_period__icontains=query) |
            Q(programs__icontains=query) |
            Q(details__icontains=query)
        ).distinct()
    else:
        institute_results = InstituteInfo.objects.none()
        circular_results = Circular.objects.none()
    
    context = {
        'query': query,
        'institute_results': institute_results,
        'circular_results': circular_results,
        'results_count': institute_results.count() + circular_results.count()
    }
    
    return render(request, 'CC/search_results.html', context)

@login_required
def profile_view(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Error updating profile. Please check the form.')
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, 'CC/profile.html', {'form': form})



def upload_institute(request):
    form = InstituteForm()
    if request.method == 'POST':
        form = InstituteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('Universities')
    Context = {'form': form,}
    return render(request, template_name='CC/createuniversity.html', context=Context)

def upload_circular(request):
    form = CircularForm()
    if request.method == 'POST':
        form = CircularForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('circulars')
    Context = {'form': form,}
    return render(request, template_name='CC/createcircular.html', context=Context)