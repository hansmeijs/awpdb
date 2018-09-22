from django.forms import ModelForm, CharField, IntegerField, ChoiceField, EmailField, MultipleChoiceField, CheckboxSelectMultiple, SelectMultiple
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _


from awpdb import constants as c
from awpdb import functions as f
from schools.models import Schooldefault
from subjects.models import Department

from django.forms.widgets import PasswordInput

from django.core.exceptions import ValidationError

# PR2018-05-04
import logging
logger = logging.getLogger(__name__)


# PR2018-04-23
class UserAddForm(UserCreationForm):
    # only request.users with permit=Admin can add user
    class Meta:
        User = get_user_model()
        model = User
        fields = ('username', 'last_name', 'email')
        # PR2018-04-23 exclude doesn't work, use pop instead in __int__. Was: exclude = ('first_name','last_name')
        labels = {
            'last_name': _('Full name'),
            'role': _('Organization'),
        }
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)  # pop() removes and returns an element from a dictionary, second argument is default when not found
        super(UserAddForm, self).__init__(*args, **kwargs)

        request_user = request.user
        # logger.debug('UserAddForm: __init__ request_user: ' + str(request_user))
        request_user_schooldefault = None
        if request_user.schooldefault:
            request_user_schooldefault = request_user.schooldefault
        logger.debug('UserAddForm request_user_schooldefault: ' + str(request_user_schooldefault))

    # ======= field 'username' ============

    # ======= field 'last_name' ============
        # field 'first_name' is not in use
        self.fields['last_name'] = CharField(
            max_length=50,
            required=True,
            label= _('Full name'),
            help_text=_('Required. 50 characters or fewer.'),
        )

    # ======= field 'email' ============

    # ======= field 'Role_list' ============
        # request.user with role=School: role = request.user.role, field is disabled
        # request.user with role=Insp can set role=Insp and role=School
        # request.user with role=System can set all roles
        # PR2018-08-04
        _choices = [(c.ROLE_00_SCHOOL, _('School')),]
        if request_user.is_role_insp_or_system:
            _choices.append((c.ROLE_01_INSP, _('Inspection')))
        if request_user.is_role_system:
            _choices.append((c.ROLE_02_SYSTEM, _('System')))

        self.fields['role_list'] = ChoiceField(
            required=True,
            # choises must be tuple or list, dictionary gives error: 'int' object is not iterable
            choices=_choices,
            label=_('Organization'),
            initial=request_user.role
        )
        self.fields['role_list'].disabled = request_user.is_role_school

    # ======= field 'Schooldefault_list' ============
        # request.user with role=School: school = request.user.school, field is disabled
        # request.user with role=Insp: choices: schools from request.user.country
        # request.user with role=System: choices: schools from request.user.country
        # TODO: finish choicelist
        # request.user with role=System school = blank, field is disabled
        if request_user.is_role_insp_or_system:
            # PR2018-09-15 system must have request_user.country. Was for system users: Schooldefault.objects.all():
            _choices = [c.CHOICE_NONE]  # CHOICE_NONE = (0, _('None'))
            schooldefaults = Schooldefault.objects.filter(country=request_user.country)
        else:
            _choices = [] # role_school cannot have blank schooldefault
            schooldefaults = Schooldefault.objects.filter(id=request_user.schooldefault.id)
        # logger.debug('UserAddForm schooldefaults: ' + str(schooldefaults))

        for item in schooldefaults:
            item_str = ''
            if item.code is not None:
                item_str = str(item.code) + ' - '
            if item.name is not None:
                item_str = item_str + str(item.name)
            _choices.append((item.id, item_str))
        # logger.debug('UserAddForm _choices: ' + str(_choices))

        self.fields['schooldefault_list'] = ChoiceField(
            choices=_choices,
            label=_('School')
        )

        if not request_user.is_role_insp_or_system:
            # when role = school: initial value of field schooldefault is request_user_schooldefault.id
            if request_user_schooldefault:
                self.fields['schooldefault_list'].initial = request_user_schooldefault.id
            # when role = school: field schooldefault is disables
            self.fields['schooldefault_list'].disabled = True

    # ======= field 'Permits' ============
        # permits_choices_tuple: ((1, 'Read'), (2, 'Write'), (4, 'Authorize'), (8, 'Admin'))
        self.fields['permit_list'] = MultipleChoiceField(
            required=False,
            widget=SelectMultiple,
            choices=request_user.permits_choices,  # choises must be tuple or list, dictionary gives error: 'int' object is not iterable
            label='Permissions',
            help_text=_('Select one or more permissions from the list. '
                        'Press the Ctrl button to select multiple permissions.'),
            initial= c.PERMIT_01_READ
        )

        """
    # ======= field 'Country_list' ============
    # request.user with role=Insp or role=School: country = request.user.country, field is disabled
    # only request.user with role=System kan choose country
        self.fields['country_list'] = ChoiceField(
            required=True,
            choices=f.get_country_choices_all(),
            label=_('Country')
        )
        self.fields['country_list'].initial = request.user.country.id
        self.fields['country_list'].disabled = True
        """

    # remove fields 'password1'
        self.fields.pop('password1')
        self.fields.pop('password2')

    """
    def clean_country_choice_NOT_IN_USE(self):
        country_choice = self.cleaned_data['country_choice']
        # Always return a value to use as the new cleaned data, even if this method didn't change it.
        return country_choice

    def clean_role_choice_NOT_IN_USE(self):
        role_choice = self.cleaned_data['role_choice']
        #raise ValidationError(" ValidationError role " + str(role_choice))
        if role_choice is None:
            role_choice = [str(c.ROLE_00_SCHOOL)]
        logger.debug('UserAddForm  def clean_role(self) clean_role_choice = ' + str(role_choice))

        # Always return a value to use as the new cleaned data, even if this method didn't change it.
        return role_choice

    def clean_permit_list_NOT_IN_USE(self):
        permit_list = self.cleaned_data['permit_list']
        #raise ValidationError(" ValidationError role " + str(data))
        if permit_list is None:
            permit_list = [str(c.PERMIT_00_NONE)]
        # logger.debug('UserAddForm  def clean_permit_list = ' + str(permit_list))

        # Always return a value to use as the new cleaned data, even if this method didn't change it.
        return permit_list
    """


# PR2018-04-23
class UserActivateForm(ModelForm):

    class Meta:
        User = get_user_model()
        model = User
        fields = ('last_name', 'email') # , 'password1', 'password2',)

    def __init__(self, *args, **kwargs):
        logger.debug('UserActivateForm __init__  kwargs: ' + str(kwargs))
        self.request = kwargs.pop('request', None)  # pop() removes and returns an element from a dictionary, second argument is default when not found
        logger.debug('UserActivateForm __init__ request: ' + str(self.request))
        super(UserActivateForm, self).__init__(*args, **kwargs)

        self.fields['password1'] = CharField(max_length=32, label='Password') # label -='' works, but appears again after formerror
        self.fields['password2'] = CharField(max_length=32, label='Repeat password')

        self.fields['password1'].widget = PasswordInput # this is not working
        self.fields['password2'].widget = PasswordInput # this is not working
        # self.fields['password1'].widget = HiddenInput() # this works, but label stays
        # self.fields['password2'].widget = HiddenInput() # this works, but label stays


class UserEditForm(ModelForm):
    class Meta:
        User = get_user_model()
        model = User
        fields = ('username', 'last_name', 'email', 'country', 'role')
        # PR2018-04-23 exclude doen't work, use pop instead in __int__
        # was: exclude = ('first_name','last_name')
        labels = {
            'last_name': _('Full name'),
            'role': _('Organization'),
        }

    # PR2018-08-19 VULNERABILITY: User Insp / School can access other users by entering: http://127.0.0.1:8000/users/6/edit
    # must check if country is same as countr of insp OR selected_school is same as school of role_school

    # PR2018-05-20 from https://stackoverflow.com/questions/16205908/django-modelform-not-required-field/30403969?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    def __init__(self, *args, **kwargs):
        # kwargs: {'initial': {}, 'prefix': None, 'instance': <User: Truus>, 'request': <WSGIRequest: GET '/users/7/'>}
        self.request = kwargs.pop('request')  # To get request.user. Do not use kwargs.pop('user', None) due to potential security hole
        super(UserEditForm, self).__init__(*args, **kwargs)

        self.request_user = self.request.user
        # logger.debug('UserEditForm __init__ request_user ' + str(self.request_user))

        self.requestuser_countryid = 0
        if self.request_user.country:
            self.requestuser_countryid = self.request_user.country.id
        # logger.debug('UserEditForm __init__ self.requestuser_countryid ' + str(self.requestuser_countryid))

        self.this_instance = kwargs.get('instance')
        # logger.debug('UserEditForm __init__ instance ' + str(self.this_instance))

        kwargs.update({'selected_username': self.this_instance.username})
        # logger.debug('UserEditForm __init__ self.kwargs ' + str(kwargs))

        self.selecteduser_countryid = 0
        if self.this_instance.country:
            self.selecteduser_countryid = self.this_instance.country.id
        # logger.debug('UserEditForm __init__ self.selecteduser_countryid ' + str(self.selecteduser_countryid))

# ++++++++++++ VALIDATION !!! +++++++++++++++++++++++++++++++++++++++
        # PR2018-08-19
        # VULNERABILITY: User Insp / School can access other users by entering: http://127.0.0.1:8000/users/6/edit
        # must check if country is same as country of insp OR selected_school is same as school of role_school
        # gives error: '__init__() should return None, not 'HttpResponse', but at least it doesn't show page
        if self.request_user.is_role_insp:
            if self.request_user.country and self.this_instance.country:
                if self.request_user.country != self.this_instance.country:
                    return render(self.request, 'home.html')
            else:
                return render(self.request, 'home.html')
        elif self.request_user.is_role_school:
            if self.request_user.schooldefault and self.this_instance.schooldefault:
                if self.request_user.schooldefault != self.this_instance.schooldefault:
                    return render(self.request, 'home.html')
            else:
                return render(self.request, 'home.html')

    # ======= field 'Role' ============
        # Field 'Role' can only be modified by system + admin users.
        _enabled = self.request_user.is_role_system
        self.fields['role'].disabled = not self.request_user.is_role_system_perm_admin

    # ======= field 'Country' ============
        # RequestUser cannot change SelectedUser's country (request_user != selected_user)
        # SelectedUser can only change his own country if SelectedUser is_role_system: (request_user == selected_user)
        country_disabled = True
        if self.request_user == self.this_instance:
            if self.this_instance.is_role_system:
                country_disabled = False
        self.fields['country'].disabled = country_disabled
        """
        Not in use, Country field does the job PR2018-08-01
        self.fields['country_list'] = ChoiceField(
            required=False,
            # choises must be tuple or list, dictionary gives error: 'int' object is not iterable
            choices=self.request.user.country_choices,
            label=_('CountryLIST')
        )
        # PR2018-07-26 debug: use .id instead of country. This showed always first item in choices: initial=self.this_instance.country
        # PR2018-08-01 debug: 'NoneType' object has no attribute 'id'. Check first if country is not None
        if self.this_instance.country is not None:
            self.fields['country_list'].initial = self.this_instance.country.id
        """

    # ======= field 'examyear' ============
        self.fields['examyear_field'] = ChoiceField(
            required=False,
            # choises must be tuple or list, dictionary gives error: 'int' object is not iterable
            choices=self.request.user.examyear_choices(self.this_instance),
            label=_('Examyear'),
            # PR2018-07-31 debug: use schooldefault.id instead of schooldefault.
            # This showed always first item in choices: initial=self.this_instance.schooldefault
        )
        self.is_disabled = True
        if self.request_user.is_role_insp_or_system:
            if self.request_user == self.this_instance:
                self.is_disabled = False
        # self.fields['examyear_field'].disabled = self.is_disabled

    # ======= field 'Schooldefault_list' ============
        # request.user with role=School: school field 'Schooldefault' is disabled
        # request.user with role=System or Insp: can only change their own Schooldefault, otherwise field is disabled
        # Show only schools from selected_user.country. Filter is in schooldefault_choices

        self.selected_user_schooldefault_id = 0
        if self.this_instance.schooldefault:
            self.selected_user_schooldefault_id = self.this_instance.schooldefault.id

        self.fields['schooldefault_list'] = ChoiceField(
            required=False,
            # choises must be tuple or list, dictionary gives error: 'int' object is not iterable
            choices=self.request.user.schooldefault_choices(self.this_instance),
            label=_('School'),
            # PR2018-07-31 debug: use schooldefault.id instead of schooldefault.
            # This showed always first item in choices: initial=self.this_instance.schooldefault
            initial=self.selected_user_schooldefault_id
        )
        self.is_disabled = True
        if self.request_user.is_role_insp_or_system:
            if self.request_user == self.this_instance:
                self.is_disabled = False

        # self.fields['schooldefault_list'].disabled = self.is_disabled

    # ======= field 'department_field' ============
        # get value of selected_user_department_id
        self.selected_user_department_id = 0
        if self.this_instance.department:
            self.selected_user_department_id = self.this_instance.department.id
        # give value to _choices
        # TODO: Show only departments of selected school / examyear
        _choices = Department.dep_list_choices(
            user_country=self.this_instance.country,
            # init_list_str=self.this_instance.dep_list
            )
        self.fields['department_field'] = ChoiceField(
            required=False,
            # choises must be tuple or list, dictionary gives error: 'int' object is not iterable
            choices=_choices,
            label=_('Department'),
            # PR2018-07-31 debug: use schooldefault.id instead of schooldefault.
            # This showed always first item in choices: initial=self.this_instance.schooldefault
            initial=self.selected_user_department_id
        )


    # ======= field 'Permits' ============
        self.permits_tuple = self.this_instance.permits_tuple
        self.fields['permit_list'] = MultipleChoiceField(
            required=False,
            widget=SelectMultiple,
            # choises must be tuple or list, dictionary gives error: 'int' object is not iterable
            choices= self.request.user.permits_choices,
            label='Permissions',
            help_text=_('Select one or more permissions from the list. '
                        'Press the Ctrl button to select multiple permissions.'),
            initial=self.permits_tuple
        )

    # ======= field 'is_active' ============
        # PR2018-06-22, value in is_active is stored as str: '0'=False, '1'=True
        __initial_is_active = 0
        if self.this_instance.is_active is not None:
            __initial_is_active = int(self.this_instance.is_active)
        # logger.debug('UserEditForm __init__ instance ' + str(self.this_instance) + ' __initial_is_active: ' + str(__initial_is_active) + ' type : ' + str(type(__initial_is_active)))
        self.fields['field_is_active'] = ChoiceField(
            choices=c.IS_ACTIVE_CHOICES,
            label=_('Active'),
            initial=__initial_is_active
        )
