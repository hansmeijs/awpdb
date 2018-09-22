"""awpdb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
# PR2018-08-31 see https://docs.djangoproject.com/en/2.0/ref/urls/#path
from django.urls import include, path, re_path
# PR2018-03-16; PR2018-03-31 don't add doubledot, gives error 'attempted relative import beyond top-level package'
from accounts import views as account_views
from importing import views as import_views
from schools import views as school_views
from subjects import views as subject_views
from students import views as student_views


urlpatterns = [
# PR2018-03-20
    url(r'^login/$', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
# PR2018-03-19
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
# PR2018-03-27
    url(r'^reset/$',
        auth_views.PasswordResetView.as_view(
            template_name='password_reset.html',
            email_template_name='password_reset_email.html',
            subject_template_name='password_reset_subject.txt'
        ),
        name='password_reset'),
    url(r'^reset/done/$',
        auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
        name='password_reset_confirm'),
    url(r'^reset/complete/$',
        auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
        name='password_reset_complete'),
    url(r'^settings/password/$', auth_views.PasswordChangeView.as_view(template_name='password_change.html'),
        name='password_change'),
    url(r'^settings/password/done/$', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'),
        name='password_change_done'),

# PR2018-04-24
    url(r'^account_activation_sent/$', account_views.account_activation_sent, name='account_activation_sent_url'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', account_views.UserActivate, name='activate_url'),
    #url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', account_views.UserActivateView.as_view(), name='activate_url'),
    url(r'^users/(?P<pk>\d+)/activated$', account_views.UserActivatedSuccess.as_view(), name='account_activation_success_url'),
    # PR2018-03-09 path is new in django2.0 See: https://docs.djangoproject.com/en/2.0/releases/2.0/#whats-new-2-0
    path('admin/', admin.site.urls, name='admin_url'),
# PR2018-03-21
    # PR2018-04-21 debug: don't forget the .as_view() with brackets in the urlpattern!!!
    url(r'^users/$', account_views.UserListView.as_view(), name='user_list_url'),
    url(r'^users/add$', account_views.UserAddView.as_view(), name='user_add_url'),
    url(r'^users/(?P<pk>\d+)/edit$', account_views.UserEditView.as_view(), name='user_edit_url'),
    url(r'^users/(?P<pk>\d+)/delete$', account_views.UserDeleteView.as_view(), name='user_delete_url'),
    url(r'^users/(?P<pk>\d+)/log$', account_views.UserLogView.as_view(), name='user_log_url'),

    url(r'session_security/', include('session_security.urls')),
# PR2018-05-11
    url(r'^users/(?P<pk>\d+)/language/(?P<lang>[A-Za-z]{2})/$', account_views.UserLanguageView.as_view(), name='language_set_url'),

# PR2018-03-11
    url('^$', school_views.home, name='home'),
# countries
    # PR2018-04-17 debug: don't forget the brackets at the end of as_view() !!
    url(r'^country/$', school_views.CountryListView.as_view(), name='country_list_url'),
    url(r'^country/add/$', school_views.CountryAddView.as_view(), name='country_add_url'),
    url(r'^country/(?P<pk>\d+)/selected/$', school_views.CountrySelectView.as_view(), name='country_selected_url'),
    url(r'^country/(?P<pk>\d+)/edit$', school_views.CountryEditView.as_view(), name='country_edit_url'),
    url(r'^country/(?P<pk>\d+)/log$', school_views.CountryLogView.as_view(), name='country_log_url'),
    url(r'^country/(?P<pk>\d+)/delete$', school_views.CountryDeleteView.as_view(), name='country_delete_url'),
    # url(r'^country/logdeleted$', school_views.CountryLogDeletedView.as_view(), name='country_log_deleted_url'),
    # url(r'^country/(?P<pk>\d+)/lock$', school_views.CountryLockView.as_view(), name='country_lock_url'),

# PR2018-03-14
    # PR2018-04-17 debug: don't forget the brackets at the end of as_view() !!\

    url(r'^examyear/$', school_views.ExamyearListView.as_view(), name='examyear_list_url'),
    url(r'^examyear/add/$', school_views.ExamyearAddView.as_view(), name='examyear_add_url'),
    url(r'^examyear/(?P<pk>\d+)/selected/$', school_views.ExamyearSelectView.as_view(), name='examyear_selected_url'),
    url(r'^examyear/(?P<pk>\d+)/edit/$', school_views.ExamyearEditView.as_view(), name='examyear_edit_url'),
    url(r'^examyear/(?P<pk>\d+)/delete/$', school_views.ExamyearDeleteView.as_view(), name='examyear_delete_url'),
    url(r'^examyear/(?P<pk>\d+)/log/$', school_views.ExamyearLogView.as_view(), name='examyear_log_url'),

# department PR2018-08-11
    url(r'^department/$', school_views.DepartmentListView.as_view(), name='department_list_url'),
    url(r'^department/add/$', school_views.DepartmentAddView.as_view(), name='department_add_url'),
    url(r'^department/(?P<pk>\d+)/selected/$', school_views.DepartmentSelectView.as_view(), name='department_selected_url'),
    url(r'^department/(?P<pk>\d+)/edit$', school_views.DepartmentEditView.as_view(), name='department_edit_url'),
    url(r'^department/(?P<pk>\d+)/delete/$', school_views.DepartmentDeleteView.as_view(), name='department_delete_url'),
    url(r'^department/(?P<pk>\d+)/log$', school_views.DepartmentLogView.as_view(), name='department_log_url'),

# schooldefault  PR2018-04-20
    url(r'^schooldefault/$', school_views.SchooldefaultListView.as_view(), name='schooldefault_list_url'),
    url(r'^schooldefault/add/$', school_views.SchooldefaultAddView.as_view(), name='schooldefault_add_url'),
    url(r'^schooldefault/(?P<pk>\d+)/selected/$', school_views.SchooldefaultSelectView.as_view(), name='schooldefault_selected_url'),
    url(r'^schooldefault/(?P<pk>\d+)/edit$', school_views.SchooldefaultEditView.as_view(), name='schooldefault_edit_url'),
    url(r'^schooldefault/(?P<pk>\d+)/delete/$', school_views.SchooldefaultDeleteView.as_view(), name='schooldefault_delete_url'),
    url(r'^schooldefault/(?P<pk>\d+)/log$', school_views.SchooldefaultLogView.as_view(), name='schooldefault_log_url'),

# school  PR2018-08-25
    url(r'^school/$', school_views.SchoolListView.as_view(), name='school_list_url'),
    url(r'^school/add/$', school_views.SchoolAddView.as_view(), name='school_add_url'),
    url(r'^school/(?P<pk>\d+)/selected/$', school_views.SchoolSelectView.as_view(), name='school_selected_url'),
    url(r'^school/(?P<pk>\d+)/edit$', school_views.SchoolEditView.as_view(), name='school_edit_url'),
    url(r'^school/(?P<pk>\d+)/delete/$', school_views.SchoolDeleteView.as_view(), name='school_delete_url'),
    url(r'^school/(?P<pk>\d+)/log$', school_views.SchoolLogView.as_view(), name='school_log_url'),

# level PR2018-08-12
    url(r'^level/$', subject_views.LevelListView.as_view(), name='level_list_url'),
    url(r'^level/add/$', subject_views.LevelAddView.as_view(), name='level_add_url'),
    url(r'^level/(?P<pk>\d+)/edit$', subject_views.LevelEditView.as_view(), name='level_edit_url'),
    url(r'^level/(?P<pk>\d+)/delete/$', subject_views.LevelDeleteView.as_view(), name='level_delete_url'),
    url(r'^level/(?P<pk>\d+)/log$', subject_views.LevelLogView.as_view(), name='level_log_url'),

    # PR 2018-08-31 from https://simpleisbetterthancomplex.com/tutorial/2018/01/29/how-to-implement-dependent-or-chained-dropdown-list-with-django.html
    # re_path(r'^ajax/load-levels/$', subject_views.load_levels, name='ajax_load_levels'),


# sector PR2018-08-23
    url(r'^sector/$', subject_views.SectorListView.as_view(), name='sector_list_url'),
    url(r'^sector/add/$', subject_views.SectorAddView.as_view(), name='sector_add_url'),
    url(r'^sector/(?P<pk>\d+)/edit$', subject_views.SectorEditView.as_view(), name='sector_edit_url'),
    url(r'^sector/(?P<pk>\d+)/delete/$', subject_views.SectorDeleteView.as_view(), name='sector_delete_url'),
    url(r'^sector/(?P<pk>\d+)/log$', subject_views.SectorLogView.as_view(), name='sector_log_url'),

# scheme PR2018-08-23
    url(r'^scheme/$', subject_views.SchemeListView.as_view(), name='scheme_list_url'),
    url(r'^scheme/add/$', subject_views.SchemeAddView.as_view(), name='scheme_add_url'),
    #url(r'^scheme/(?P<pk>\d+)/edit$', subject_views.SchemeEditView.as_view(), name='scheme_edit_url'),
    #url(r'^scheme/(?P<pk>\d+)/delete/$', subject_views.SchemeDeleteView.as_view(), name='scheme_delete_url'),
    #url(r'^scheme/(?P<pk>\d+)/log$', subject_views.SchemeLogView.as_view(), name='scheme_log_url'),

# subjectdefault PR2018-07-18
    url(r'^subjectdefault/$', subject_views.SubjectdefaultListView.as_view(), name='subjectdefault_list_url'),
    url(r'^subjectdefault/add/$', subject_views.SubjectdefaultAddView.as_view(), name='subjectdefault_add_url'),
    url(r'^subjectdefault/(?P<pk>\d+)/edit$', subject_views.SubjectdefaultEditView.as_view(), name='subjectdefault_edit_url'),
    url(r'^subjectdefault/(?P<pk>\d+)/delete/$', subject_views.SubjectdefaultDeleteView.as_view(), name='subjectdefault_delete_url'),
    url(r'^subjectdefault/(?P<pk>\d+)/log$', subject_views.SubjectdefaultLogView.as_view(), name='subjectdefault_log_url'),

# subject # PR2018-08-23
    url(r'^subject/$', subject_views.SubjectListView.as_view(), name='subject_list_url'),
    url(r'^subject/add/$', subject_views.SubjectAddView.as_view(), name='subject_add_url'),
    #url(r'^subject/(?P<pk>\d+)/edit$', subject_views.SubjectEditView.as_view(), name='subject_edit_url'),
    #url(r'^subject/(?P<pk>\d+)/delete/$', subject_views.SubjectDeleteView.as_view(), name='subject_delete_url'),
    #url(r'^subject/(?P<pk>\d+)/log$', subject_views.SubjectLogView.as_view(), name='subject_log_url'),

# student  PR2018-09-02
    url(r'^student/$', student_views.StudentListView.as_view(), name='student_list_url'),
    url(r'^student/add/$', student_views.StudentAddView.as_view(), name='student_add_url'),

    path('student/ajax/load_cities/', student_views.load_cities, name='ajax_load_cities'),  # PR2018-09-03

    # PR2018-05-06 debug: don't forget the brackets at the end of as_view() !!
    url(r'^import/schooldefault/$', import_views.ImportSchooldefaultView.as_view(), name='import_schooldefault_url'),
    url(r'^import/subjectdefault/$', import_views.ImportSubjectdefaultView.as_view(), name='import_subjectdefault_url'),
    url(r'^import/department/$', import_views.ImportDepartmentView.as_view(), name='import_department_url'),
    url(r'^import/level/$', import_views.ImportLevelView.as_view(), name='import_level_url'),
    path('import/sector/', import_views.ImportSectorView.as_view(), name='import_sector_url'),  # PR2018-09-04
    url(r'^import/birthcountry/$', import_views.ImportBirthcountryView.as_view(), name='import_birthcountry_url'),
    url(r'^import/birthcity/$', import_views.ImportBirthcityView.as_view(), name='import_birthcity_url'),

]