from django.shortcuts import render,redirect,get_object_or_404
from django.conf import settings
from .models import Membership_plan, User_membership
from .form import MembershipplanForm, UserMembershipForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
from django.http import Http404
from django.utils.timezone import now
from django.urls import reverse
from datetime import timedelta
from account.models import CustomUser
from django.core.paginator import Paginator


def is_admin_user(user):
    return user.is_staff



def home(request):
    print(settings.TEMPLATES[0]['DIRS'])
    return render(request, 'Ecommerce/base.html')




# Create your views here.
@login_required
@user_passes_test(is_admin_user) 
def membership_plan_list(request):
    plans = Membership_plan.objects.all()
    paginator = Paginator(plans, 10)  # Show 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin_dashboard/membership_plan_list.html', {'page_obj': page_obj})





@login_required
@user_passes_test(is_admin_user) 
def membership_plan_add(request):
    
    context = {
        'model_name' : "Membership Plan",
        'list':'membership:membership_plan_list',
    }
    
    if request.method == 'POST':
        form = MembershipplanForm(request.POST)
        if form.is_valid():
            plan_name = form.cleaned_data['plan_name']
            if Membership_plan.objects.filter(plan_name = plan_name).exists():
                messages.error(request, "Membership Plan already exists.")
            else:
                form.save()
                messages.success(request, "Membership Plan added successfully.")
                return redirect('membership:membership_plan_list')
    else:
        form = MembershipplanForm()
       
    context['form'] = form 
    return render(request,'admin_dashboard/add_form.html',context)






@login_required
@user_passes_test(is_admin_user) 
def membership_view_details(request, pk):
    
    context = {
        'model_name': 'Membership Plan'
    }
    
    try:
        plan = get_object_or_404(Membership_plan, pk = pk)
    except Http404:
        return render(request, '404.html', status=404)
    
    form = MembershipplanForm(instance=plan)
    
    if request.method == 'POST':
        if 'update' in request.POST:
            form = MembershipplanForm(request.POST, instance=plan)
            
            if form.is_valid():
                form.save()
                messages.success(request, "Membership plan updated successfully!")
                return redirect('membership:membership_plan_list')
            else:
                messages.error(request, "Membership plan update failed. Please correct the errors.")

        elif 'delete' in request.POST:  # Delete action
            plan.delete()
            messages.success(request, "Membership plan deleted successfully!")
            return redirect('membership:membership_plan_list')
        
        elif 'cancel' in request.POST:
            return redirect('membership:membership_plan_list')
        
    context['form'] = form
    context['plan'] = plan
    return render(request, 'admin_dashboard/view_details.html',context)





@login_required
@user_passes_test(is_admin_user) 
def user_membership(request):
    memberships = User_membership.objects.all()
    paginator = Paginator(memberships, 10)  # Show 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin_dashboard/user_membership.html', {'page_obj': page_obj})





@login_required
@user_passes_test(is_admin_user)  
def add_user_membership(request):
    context = {
        'model_name': "User Member",
        'list':'membership:user_membership', 
    }
    
    if request.method == "POST" and 'plan' in request.POST:
        form = UserMembershipForm(request.POST)
        if form.is_valid():
            plan_id = form.cleaned_data.get('plan')  
            existing_membership = User_membership.objects.filter(user=request.user, plan=plan_id).exists()
            
            if existing_membership:
                messages.error(request, "You already have an active membership for this plan.")
                return render(request, 'admin_dashboard/add_form.html', {'form': form})
            
            membership = form.save(commit=False)
            membership.user = request.user  
            membership.plan = plan_id  
            membership.membership_end_date = membership.membership_start_date + timedelta(days=365)
            membership.save()
            
            messages.success(request, "User membership added successfully!")
            return redirect(reverse('membership:user_membership'))  # ✅ Fixed
        else:
            messages.error(request, "Error adding user membership. Please check the form.")
    else:
        form = UserMembershipForm()

    context['form'] = form
    return render(request, 'admin_dashboard/add_form.html', context)



    
    
def user_membership_details(request, pk):
    
    context = {
        'model_name': 'User Membership'
    }
    
    try:
        # Fetch the category or raise Http404 if not found
        membership = get_object_or_404(User_membership, pk=pk)
    except Http404:
        # Render the custom 404 page
        return render(request, '404.html', status=404)
    
    form = UserMembershipForm(instance=membership)
    
    if request.method == 'POST':
        if 'update' in request.POST:  # Update action
            form = UserMembershipForm(request.POST, instance=membership)
            if form.is_valid():
                form.save()
                messages.success(request, "Membership updated successfully!")
                return redirect('membership:user_membership')
            else:
                messages.error(request, "Membership update failed. Please correct the errors.")
        if 'delete' in request.POST:  # Delete action
            membership.delete()
            messages.success(request, "Membership deleted successfully!")
            return redirect('membership:user_membership')

        elif 'cancel' in request.POST:  # Cancel action
            return redirect('membership:user_membership')

    context['form'] = form
    context['membership'] = membership
    return render(request, 'admin_dashboard/view_details.html', context)


def show_membership_gold(request):
    return render(request, "Ecommerce/membership/membership.html")
  
        