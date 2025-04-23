from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from .models import CrewMember, CrewQualification, CrewSchedule, CrewLeave

def index(

    return render(request, 'crew/index.html', {
        'title': 'Crew Portal'
    })

@login_required

def crew_dashboard(

    try:
        crew_member = request.user.crew_profile
    except:
        messages.error(request, "You don't have a crew profile.")
        return redirect('home')

    today = timezone.now().date()
    upcoming_schedules = CrewSchedule.objects.filter(
        crew_member=crew_member,
        start_time__date__gte=today,
        status__in=['tentative', 'assigned', 'confirmed']
    ).order_by('start_time')[:5]

    active_leaves = CrewLeave.objects.filter(
        crew_member=crew_member,
        start_date__lte=today,
        end_date__gte=today,
        status='approved'
    )

    expiring_date = today + timezone.timedelta(days=90)
    expiring_qualifications = CrewQualification.objects.filter(
        crew_member=crew_member,
        is_active=True,
        expiry_date__isnull=False,
        expiry_date__lte=expiring_date,
        expiry_date__gte=today
    )

    start_of_month = today.replace(day=1)
    flight_hours_month = crew_member.get_flight_hours(start_of_month, today)

    context = {
        'crew_member': crew_member,
        'upcoming_schedules': upcoming_schedules,
        'active_leaves': active_leaves,
        'expiring_qualifications': expiring_qualifications,
        'flight_hours_month': flight_hours_month,
        'max_flight_hours_month': crew_member.max_flight_hours_month
    }

    return render(request, 'crew/dashboard.html', context)

@login_required

def schedule_list(

    try:
        crew_member = request.user.crew_profile
    except:
        messages.error(request, "You don't have a crew profile.")
        return redirect('home')

    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)

    schedules = CrewSchedule.objects.filter(crew_member=crew_member)

    if start_date:
        schedules = schedules.filter(start_time__date__gte=start_date)

    if end_date:
        schedules = schedules.filter(end_time__date__lte=end_date)

    schedules = schedules.order_by('start_time')

    context = {
        'crew_member': crew_member,
        'schedules': schedules,
        'start_date': start_date,
        'end_date': end_date
    }

    return render(request, 'crew/schedule_list.html', context)

@login_required

def schedule_detail(

    try:
        crew_member = request.user.crew_profile
    except:
        messages.error(request, "You don't have a crew profile.")
        return redirect('home')

    schedule = get_object_or_404(CrewSchedule, pk=pk)

    if schedule.crew_member != crew_member and not request.user.is_staff:
        messages.error(request, "You don't have permission to view this schedule.")
        return redirect('crew_dashboard')

    context = {
        'schedule': schedule
    }

    return render(request, 'crew/schedule_detail.html', context)

@login_required
@require_POST

def schedule_check_in(

    try:
        crew_member = request.user.crew_profile
    except:
        messages.error(request, "You don't have a crew profile.")
        return redirect('home')

    schedule = get_object_or_404(CrewSchedule, pk=pk)

    if schedule.crew_member != crew_member:
        messages.error(request, "You don't have permission to check in for this schedule.")
        return redirect('crew_dashboard')

    if schedule.status not in ['confirmed', 'assigned']:
        messages.error(request, "This schedule cannot be checked in with its current status.")
        return redirect('crew_schedule_detail', pk=schedule.id)

    now = timezone.now()
    check_in_window = timezone.timedelta(hours=3)  

    if schedule.start_time > (now + check_in_window):
        messages.error(request, "It's too early to check in for this duty.")
        return redirect('crew_schedule_detail', pk=schedule.id)

    schedule.check_in()

    messages.success(request, "Successfully checked in for your duty.")
    return redirect('crew_schedule_detail', pk=schedule.id)

@login_required
@require_POST

def schedule_check_out(

    try:
        crew_member = request.user.crew_profile
    except:
        messages.error(request, "You don't have a crew profile.")
        return redirect('home')

    schedule = get_object_or_404(CrewSchedule, pk=pk)

    if schedule.crew_member != crew_member:
        messages.error(request, "You don't have permission to check out from this schedule.")
        return redirect('crew_dashboard')

    if schedule.status != 'checked_in':
        messages.error(request, "You must be checked in to check out from this duty.")
        return redirect('crew_schedule_detail', pk=schedule.id)

    schedule.check_out()

    messages.success(request, "Successfully checked out from your duty.")
    return redirect('crew_schedule_detail', pk=schedule.id)

@login_required

def qualification_list(

    try:
        crew_member = request.user.crew_profile
    except:
        messages.error(request, "You don't have a crew profile.")
        return redirect('home')

    qualifications = CrewQualification.objects.filter(
        crew_member=crew_member
    ).order_by('qualification_type', '-issue_date')

    show_inactive = request.GET.get('show_inactive', False)
    if not show_inactive:
        qualifications = qualifications.filter(is_active=True)

    context = {
        'crew_member': crew_member,
        'qualifications': qualifications,
        'show_inactive': show_inactive
    }

    return render(request, 'crew/qualification_list.html', context)

@login_required

def leave_list(

    try:
        crew_member = request.user.crew_profile
    except:
        messages.error(request, "You don't have a crew profile.")
        return redirect('home')

    leaves = CrewLeave.objects.filter(
        crew_member=crew_member
    ).order_by('-start_date')

    context = {
        'crew_member': crew_member,
        'leaves': leaves
    }

    return render(request, 'crew/leave_list.html', context)

@login_required

def leave_request(

    try:
        crew_member = request.user.crew_profile
    except:
        messages.error(request, "You don't have a crew profile.")
        return redirect('home')

    if request.method == 'POST':

        leave_type = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')

        leave = CrewLeave.objects.create(
            crew_member=crew_member,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status='pending'
        )

        messages.success(request, "Leave request submitted successfully.")
        return redirect('crew_leave_list')

    context = {
        'crew_member': crew_member,
        'leave_types': CrewLeave.LEAVE_TYPES
    }

    return render(request, 'crew/leave_request.html', context)

@login_required
@permission_required('crew.change_crewleave')

def leave_approval(

    pending_leaves = CrewLeave.objects.filter(
        status='pending'
    ).order_by('start_date')

    if request.method == 'POST':
        leave_id = request.POST.get('leave_id')
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')

        leave = get_object_or_404(CrewLeave, pk=leave_id)

        if action == 'approve':
            leave.approve(request.user, notes)
            messages.success(request, f"Leave request for {leave.crew_member} approved.")
        elif action == 'deny':
            leave.deny(request.user, notes)
            messages.success(request, f"Leave request for {leave.crew_member} denied.")

        return redirect('crew_leave_approval')

    context = {
        'pending_leaves': pending_leaves
    }

    return render(request, 'crew/leave_approval.html', context)

@login_required
@permission_required('crew.view_crewmember')

def crew_list(

    search_term = request.GET.get('search', '')
    crew_type = request.GET.get('crew_type', '')
    base_airport = request.GET.get('base_airport', '')

    crew_members = CrewMember.objects.all()

    if search_term:
        crew_members = crew_members.filter(
            Q(crew_id__icontains=search_term) | 
            Q(user__first_name__icontains=search_term) | 
            Q(user__last_name__icontains=search_term)
        )

    if crew_type:
        crew_members = crew_members.filter(crew_type=crew_type)

    if base_airport:
        crew_members = crew_members.filter(base_airport__code=base_airport)

    crew_members = crew_members.order_by('crew_type', 'user__last_name', 'user__first_name')

    context = {
        'crew_members': crew_members,
        'search_term': search_term,
        'crew_type': crew_type,
        'base_airport': base_airport,
        'crew_types': CrewMember.CREW_TYPES
    }

    return render(request, 'crew/crew_list.html', context)

@login_required

def profile_view(

    crew_member = get_object_or_404(CrewMember, user=request.user)
    return render(request, 'crew/profile.html', {'crew_member': crew_member})

@login_required

    crew_member = get_object_or_404(CrewMember, user=request.user)

    if request.method == 'POST':

        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()

        crew_member.phone = request.POST.get('phone')
        crew_member.address = request.POST.get('address')
        crew_member.emergency_contact_name = request.POST.get('emergency_contact_name')
        crew_member.emergency_contact_phone = request.POST.get('emergency_contact_phone')
        crew_member.save()

        messages.success(request, 'Your profile has been updated successfully.')
        return redirect('crew:profile')

    return redirect('crew:profile')

@login_required

    crew_member = get_object_or_404(CrewMember, user=request.user)

    if request.method == 'POST' and request.FILES.get('profile_image'):

        crew_member.profile_image = request.FILES['profile_image']
        crew_member.save()

        messages.success(request, 'Your profile photo has been updated successfully.')

    return redirect('crew:profile')

@login_required

def change_password(

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()

            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('crew:profile')
        else:
            for error in form.errors.values():
                messages.error(request, error)

    return redirect('crew:profile') 