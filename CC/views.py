from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import *
from CC.models import InstituteInfo  
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, ProfileUpdateForm, InstituteForm, CircularForm
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect
from django.db import transaction

# ------------------ Basic Views ------------------

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
    InstituteName = InstituteInfo.objects.filter(category__name='University')
    categories = Category.objects.all()
    context = {
        'InstituteName': InstituteName,
        'categories': categories,
    }
    return render(request, 'CC/universities.html', context)

def institute_detail(request, institute_id):
    institute = get_object_or_404(InstituteInfo, pk=institute_id)
    comments = institute.comments.all().select_related('user', 'user__profile')
    nearby_hostels = institute.nearby_hostels.all().prefetch_related('images')
    
    # Check if user has bookmarked this institute
    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(
            user=request.user, 
            institute=institute
        ).exists()
    
    if request.method == 'POST':
        if 'action' in request.POST:
            if request.POST['action'] == 'update' and request.user.is_staff:
                institute.title = request.POST.get('title')
                institute.description = request.POST.get('description')
                institute.location = request.POST.get('location')
                institute.rank = request.POST.get('rank')
                institute.department = request.POST.get('department')
                institute.contact = request.POST.get('contact')
                institute.status = request.POST.get('status')
                
                try:
                    institute.save()
                    messages.success(request, 'Institute updated successfully!')
                    return redirect('institute_detail', institute_id=institute.pk)
                except Exception as e:
                    messages.error(request, f'Error updating institute: {str(e)}')
                    return redirect('institute_detail', institute_id=institute.pk)
                
            elif request.POST['action'] == 'delete' and request.user.is_staff:
                try:
                    institute_name = institute.title
                    institute.delete()
                    messages.success(request, f'Institute "{institute_name}" deleted successfully!')
                    return redirect('Home')
                except Exception as e:
                    messages.error(request, f'Error deleting institute: {str(e)}')
                    return redirect('institute_detail', institute_id=institute.pk)
    
    return render(request, 'CC/institute_detail.html', {
        'institute': institute,
        'comments': comments,
        'nearby_hostels': nearby_hostels,
        'is_bookmarked': is_bookmarked
    })

def Colleges(request):
    college_category = Category.objects.get(name="College")
    InstituteName = InstituteInfo.objects.filter(category= college_category).prefetch_related('images')
    context = {'InstituteName': InstituteName}
    return render(request, 'CC/Colleges.html', context)    

def circulars(request):
    if request.method == 'POST' and request.user.is_staff:
        if 'action' in request.POST:
            circular_id = request.POST.get('circular_id')
            circular = get_object_or_404(Circular, pk=circular_id)
            
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

    has_is_active = hasattr(Circular, 'is_active')
    try:
        if has_is_active:
            institutes = InstituteInfo.objects.filter(circulars__is_active=True).distinct().prefetch_related('circulars')
        else:
            institutes = InstituteInfo.objects.filter(circulars__isnull=False).distinct().prefetch_related('circulars')
    except Exception as e:
        institutes = InstituteInfo.objects.filter(circulars__isnull=False).distinct().prefetch_related('circulars')
    
    return render(request, 'CC/circulars.html', {
        'institutes': institutes,
        'user': request.user,
        'has_is_active': has_is_active
    })


# ------------------ Signup & Login ------------------



@csrf_protect
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)      
                messages.success(request, "Account created successfully!")
                
                # Check if it's an AJAX request
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True, 
                        'redirect_url': reverse('Home')
                    })
                else:
                    return redirect('Home')
                    
            except Exception as e:
                error_msg = f"Error creating account: {str(e)}"
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False, 
                        'errors': [error_msg]
                    })
                else:
                    messages.error(request, error_msg)
        else:
            # Form is invalid
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(f"{field}: {error}")
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False, 
                    'errors': errors
                })
            else:
                for error in errors:
                    messages.error(request, error)
    
    # If GET request or regular form submission with errors
    form = CustomUserCreationForm()
    return render(request, 'CC/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome, {username}!')
                return redirect('Home')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Invalid username or password')
    else:
        form = AuthenticationForm()
    return render(request, 'CC/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# ------------------ Profile Views ------------------

@login_required
def profile_view(request):
    profile = request.user.profile  # ✅ signal ensures profile exists

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


@login_required
def update_profile_pic(request):
    if request.method == 'POST' and request.FILES.get('profile_pic'):
        profile = request.user.profile  # ✅ use existing profile
        if profile.profile_pic:
            profile.profile_pic.delete()  # delete old pic if exists
        profile.profile_pic = request.FILES['profile_pic']
        profile.save()
        return JsonResponse({'success': True, 'url': profile.profile_pic.url})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


# ------------------ Other Views (unchanged) ------------------

def clear_signup_session(request):
    if 'signup_form_data' in request.session:
        del request.session['signup_form_data']
    return JsonResponse({'status': 'success'})


def search_results(request):
    query = request.GET.get('q', '')
    if query:
        institute_results = InstituteInfo.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(rank__icontains=query) |
            Q(department__icontains=query) |
            Q(contact__icontains=query)
        ).distinct().prefetch_related('images')
        circular_results = Circular.objects.filter(
            Q(title__icontains=query) |
            Q(admission_period__icontains=query) |
            Q(programs__icontains=query) |
            Q(details__icontains=query)
        ).distinct()
    else:
        institute_results = InstituteInfo.objects.none()
        circular_results = Circular.objects.none()
    
    categories = Category.objects.all()
    context = {
        'query': query,
        'institute_results': institute_results,
        'circular_results': circular_results,
        'categories': categories,
        'results_count': institute_results.count() + circular_results.count()
    }
    return render(request, 'CC/search_results.html', context)


def upload_institute(request):
    form = InstituteForm()
    if request.method == 'POST':
        form = InstituteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('Universities')
    return render(request, template_name='CC/createuniversity.html', context={'form': form})


def upload_circular(request):
    form = CircularForm()
    if request.method == 'POST':
        form = CircularForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('circulars')
    return render(request, template_name='CC/createcircular.html', context={'form': form})


def institute_comparison(request):
    all_institutes = InstituteInfo.objects.all().prefetch_related('images')
    categories = Category.objects.all()
    context = {
        'all_institutes': all_institutes,
        'categories': categories,
    }
    return render(request, 'CC/Comparison.html', context)


@login_required
def add_comment(request, institute_id):
    institute = get_object_or_404(InstituteInfo, pk=institute_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                institute=institute,
                user=request.user,
                content=content
            )
            messages.success(request, 'Comment added successfully!')
        return redirect('institute_detail', institute_id=institute_id)

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, user=request.user)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            comment.content = content
            comment.is_edited = True
            comment.save()
            messages.success(request, 'Comment updated successfully!')
        return redirect('institute_detail', institute_id=comment.institute.id)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, user=request.user)
    institute_id = comment.institute.id
    comment.delete()
    messages.success(request, 'Comment deleted successfully!')
    return redirect('institute_detail', institute_id=institute_id)



# Add these imports at the top
from django.views.decorators.http import require_POST
from django.http import JsonResponse

# Add these views after the existing views
@login_required
@require_POST
def toggle_bookmark(request, institute_id):
    institute = get_object_or_404(InstituteInfo, pk=institute_id)
    bookmark, created = Bookmark.objects.get_or_create(
        user=request.user,
        institute=institute
    )
    
    if not created:
        # If bookmark already exists, remove it (toggle off)
        bookmark.delete()
        is_bookmarked = False
        message = 'Institute removed from bookmarks'
    else:
        is_bookmarked = True
        message = 'Institute added to bookmarks'
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_bookmarked': is_bookmarked,
            'message': message
        })
    
    messages.success(request, message)
    return redirect('institute_detail', institute_id=institute_id)

@login_required
def bookmarked_institutes(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('institute')
    bookmarked_institutes = [bookmark.institute for bookmark in bookmarks]
    
    return render(request, 'CC/bookmarks.html', {
        'bookmarked_institutes': bookmarked_institutes
    })


from django.views.generic import DetailView
from .forms import HostelForm
@login_required
def create_hostel(request, institute_id):
    institute = get_object_or_404(InstituteInfo, pk=institute_id)
    
    if not request.user.is_staff:
        messages.error(request, 'Only staff members can create hostels.')
        return redirect('institute_detail', institute_id=institute_id)
    
    if request.method == 'POST':
        hostel_form = HostelForm(request.POST)
        
        if hostel_form.is_valid():
            # Create hostel instance but don't save to DB yet
            hostel = hostel_form.save(commit=False)
            hostel.institute = institute
            hostel.save()
            
            # Debug: Check what files are being received
            print("FILES received:", dict(request.FILES))
            images = request.FILES.getlist('images')
            print(f"Number of images received: {len(images)}")
            
            # Handle multiple image uploads
            for i, image in enumerate(images):
                print(f"Processing image {i+1}: {image.name}, size: {image.size}")
                try:
                    hostel_image = HostelImage.objects.create(hostel=hostel, image=image)
                    print(f"Successfully created HostelImage: {hostel_image}")
                except Exception as e:
                    print(f"Error creating HostelImage: {e}")
            
            messages.success(request, f'Hostel "{hostel.name}" created successfully with {len(images)} images!')
            return redirect('institute_detail', institute_id=institute_id)
        else:
            print("Form errors:", hostel_form.errors)
            messages.error(request, 'Please correct the errors below.')
    else:
        hostel_form = HostelForm()
    
    return render(request, 'CC/create_hostel.html', {
        'form': hostel_form,
        'institute': institute
    })

class HostelDetailView(DetailView):
    model = Hostel
    template_name = 'CC/hostel_detail.html'
    context_object_name = 'hostel'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['similar_hostels'] = Hostel.objects.filter(
            institute=self.object.institute
        ).exclude(pk=self.object.pk)[:3]
        return context

@login_required
def delete_hostel(request, hostel_id):
    hostel = get_object_or_404(Hostel, pk=hostel_id)
    institute_id = hostel.institute.id
    
    if not request.user.is_staff:
        messages.error(request, 'Only staff members can delete hostels.')
        return redirect('institute_detail', institute_id=institute_id)
    
    if request.method == 'POST':
        hostel_name = hostel.name
        hostel.delete()
        messages.success(request, f'Hostel "{hostel_name}" deleted successfully!')
    
    return redirect('institute_detail', institute_id=institute_id)


@login_required
def update_hostel(request, hostel_id):
    hostel = get_object_or_404(Hostel, pk=hostel_id)
    
    if not request.user.is_staff:
        messages.error(request, 'Only staff members can update hostels.')
        return redirect('hostel_detail', pk=hostel_id)
    
    if request.method == 'POST':
        form = HostelForm(request.POST, instance=hostel)
        if form.is_valid():
            form.save()
            
            # Handle new image uploads
            new_images = request.FILES.getlist('images')
            for image in new_images:
                HostelImage.objects.create(hostel=hostel, image=image)
            
            messages.success(request, f'Hostel "{hostel.name}" updated successfully!')
            return redirect('hostel_detail', pk=hostel_id)
    else:
        form = HostelForm(instance=hostel)
    
    return render(request, 'CC/update_hostel.html', {
        'form': form,
        'hostel': hostel
    })


from django.http import JsonResponse

@login_required
def delete_hostel_image(request, image_id):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    image = get_object_or_404(HostelImage, pk=image_id)
    image.delete()
    
    return JsonResponse({'success': True})