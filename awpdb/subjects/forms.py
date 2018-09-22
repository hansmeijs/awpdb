# PR2018-07-20
from django.core.exceptions import ValidationError
from django.forms import Form, ModelForm, CharField, ChoiceField, MultipleChoiceField, SelectMultiple
from django.forms import TextInput, URLField, URLInput
from django.forms.formsets import BaseFormSet


from django.utils.translation import ugettext_lazy as _
from awpdb import constants as c
from schools.models import Country, Department
from subjects.models import Level, Sector, Scheme, Subjectdefault, Subject

# PR2018-04-20 from: https://experiencehq.net/articles/better-django-modelform-html
#class BaseModelForm(ModelForm):
#    def __init__(self, *args, **kwargs):
#        kwargs.setdefault('auto_id', '%s')
#        kwargs.setdefault('label_suffix', '')
#        super().__init__(*args, **kwargs)
#        for field_name in self.fields:
#            field = self.fields.get(field_name)
#            if field:
#                field.widget.attrs.update({
#                    'placeholder': field.help_text
#                })

# PR2018-05-04
import logging
logger = logging.getLogger(__name__)


# === Level =====================================
class LevelAddForm(ModelForm):
    class Meta:
        model = Level
        fields = ('country', 'name', 'abbrev', 'sequence')
        labels = {'country': _('Country'), 'name': _('Name'), 'abbrev': _('Abbreviation'), 'sequence': _('Sequence')}

    # PR2018-06-09 from https://stackoverflow.com/questions/16205908/django-modelform-not-required-field/30403969?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    # called by SubjectdefaultAddForm(request=request) in SubjectdefaultAddView.get and -.post
    def __init__(self, *args, **kwargs):
        # request is added as parameter in ExamyearAddView by form = ExamyearAddForm(request=request)
        # pop() removes and returns an element from a dictionary, second argument is default when not foundrequest = kwargs.pop('request', None)  # pop() removes and returns an element from a dictionary, second argument is default when not found
        self.request = kwargs.pop('request', None)
        super(LevelAddForm, self).__init__(*args, **kwargs)

        # ======= field 'Country' ============
        # PR2018-08-04 should use self.initial['country'] instead of self.fields['country'].initial =  'override'
        # see https://avilpage.com/2015/03/django-form-gotchas-dynamic-initial.html
        self.initial['country'] = self.request.user.country.id
        self.fields['country'].disabled = True

        # ======= field 'name' ============
        self.fields['name'] = CharField(
            max_length = 50,
            required = True,
            validators=[validate_unique_level_name(self.request.user.country)]
        )
        self.fields['name'].widget.attrs.update({'autofocus': 'autofocus'}) # , 'placeholder': 'Default subject name'

        # ======= field 'abbrev' ============
        self.fields['abbrev'] = CharField(
            max_length = 6,
            required = True,
            validators=[validate_unique_level_abbrev(self.request.user.country)]
        )

        # ======= field 'dep_list' ============
        _choices = Department.dep_list_choices(
            user_country=self.request.user.country,
            skip_none = True)
        self.fields['dep_list_field'] = MultipleChoiceField(
            required=False,
            widget=SelectMultiple,
            choices=_choices,
            label='Departments',
            help_text=_('Select the departments where this level is available. '
                        'Press the Ctrl button to select multiple departments.')
        )

        # ======= field 'is_active' ============
        # boolean, required, default=True
        # PR2018-08-09 value in is_active is stored as str: '0'=False, '1'=True
        self.fields['is_active_field'] = ChoiceField(
            choices=c.IS_ACTIVE_CHOICES,
            label=_('Active'),
            initial=1)

class LevelEditForm(ModelForm):  # PR2018-08-11
    class Meta:
        model = Level
        fields = ('country', 'name', 'abbrev', 'sequence')
        labels = {'country': _('Country'),  'name': _('Name'), 'abbrev': _('Abbreviation'), 'sequence': _('Sequence')}

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # To get request.user. Do not use kwargs.pop('user', None) due to potential security hole
        super(LevelEditForm, self).__init__(*args, **kwargs)

        self.this_instance = kwargs.get('instance')

        # ======= field 'Country' ============
        self.fields['country'].disabled = True

        # ======= field 'name' ============
        self.fields['name'] = CharField(
            max_length = 50,
            required = True,
            validators=[validate_unique_level_name(self.request.user.country, self.this_instance)])
        self.fields['name'].widget.attrs.update({'autofocus': 'autofocus'})

        # ======= field 'abbrev' ============
        self.fields['abbrev'] = CharField(
            max_length = 8,
            required = True,
            validators=[validate_unique_level_abbrev(self.request.user.country, self.this_instance)])

        # ======= field 'dep_list' ============
        _choices = Department.dep_list_choices(
            user_country=self.request.user.country,
            init_list_str=self.this_instance.dep_list,
            skip_none = True)

        self.fields['dep_list_field'] = MultipleChoiceField(
            required=False,
            widget=SelectMultiple,
            choices=_choices,
            label='Departments',
            help_text=_('Select the departments where this level is available. '
                        'Press the Ctrl button to select multiple departments.'),
            initial=self.this_instance.dep_list_tuple
        )

        # ======= field 'is_active' ============
        # PR2018-08-09 value in is_active is stored as str: '0'=False, '1'=True, default=True
        __initial_is_active = 1
        if self.this_instance is not None:
            __initial_is_active = int(self.this_instance.is_active)
        self.fields['is_active_field'] = ChoiceField(
            choices=c.IS_ACTIVE_CHOICES,
            label=_('Active'),
            initial=__initial_is_active)


# === Sector =====================================
class SectorAddForm(ModelForm): # PR2018-08-24
    class Meta:
        model = Sector
        fields = ('country', 'name', 'abbrev', 'sequence')
        labels = {'country': _('Country'), 'name': _('Name'), 'abbrev': _('Abbreviation'), 'sequence': _('Sequence')}

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SectorAddForm, self).__init__(*args, **kwargs)

        # ======= field 'Country' ============
        self.initial['country'] = self.request.user.country.id
        self.fields['country'].disabled = True

        # ======= field 'name' ============
        self.fields['name'] = CharField(
            max_length = 50,
            required = True,
            validators=[validate_unique_sector_name(self.request.user.country)]
        )
        self.fields['name'].widget.attrs.update({'autofocus': 'autofocus'}) # , 'placeholder': 'Default subject name'

        # ======= field 'abbrev' ============
        self.fields['abbrev'] = CharField(
            max_length = 6,
            required = True,
            validators=[validate_unique_sector_abbrev(self.request.user.country)]
        )

        # ======= field 'dep_list' ============
        _choices = Department.dep_list_choices(
            user_country=self.request.user.country,
            skip_none = True)
        self.fields['dep_list_field'] = MultipleChoiceField(
            required=False,
            widget=SelectMultiple,
            choices=_choices,
            label='Departments',
            help_text=_('Select the departments where this sector is available. '
                        'Press the Ctrl button to select multiple departments.')
        )

        # ======= field 'is_active' ============
        # boolean, required, default=True
        # PR2018-08-09 value in is_active is stored as str: '0'=False, '1'=True
        self.fields['is_active_field'] = ChoiceField(
            choices=c.IS_ACTIVE_CHOICES,
            label=_('Active'),
            initial=1)


class SectorEditForm(ModelForm):  # PR2018-08-24
    class Meta:
        model = Sector
        fields = ('country', 'name', 'abbrev', 'sequence')
        labels = {'country': _('Country'),  'name': _('Name'), 'abbrev': _('Abbreviation'), 'sequence': _('Sequence')}

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # To get request.user. Do not use kwargs.pop('user', None) due to potential security hole
        super(SectorEditForm, self).__init__(*args, **kwargs)

        self.this_instance = kwargs.get('instance')

        # ======= field 'Country' ============
        self.fields['country'].disabled = True

        # ======= field 'name' ============
        self.fields['name'] = CharField(
            max_length = 50,
            required = True,
            validators=[validate_unique_sector_name(self.request.user.country, self.this_instance)])
        self.fields['name'].widget.attrs.update({'autofocus': 'autofocus'})

        # ======= field 'abbrev' ============
        self.fields['abbrev'] = CharField(
            max_length = 8,
            required = True,
            validators=[validate_unique_sector_abbrev(self.request.user.country, self.this_instance)])

        # ======= field 'dep_list' ============
        _choices = Department.dep_list_choices(
            user_country=self.request.user.country,
            init_list_str=self.this_instance.dep_list,
            skip_none = True)

        self.fields['dep_list_field'] = MultipleChoiceField(
            required=False,
            widget=SelectMultiple,
            choices=_choices,
            label='Departments',
            help_text=_('Select the departments where this sector is available. '
                        'Press the Ctrl button to select multiple departments.'),
            initial=self.this_instance.dep_list_tuple
        )

        # ======= field 'is_active' ============
        # PR2018-08-09 value in is_active is stored as str: '0'=False, '1'=True, default=True
        __initial_is_active = 1
        if self.this_instance is not None:
            __initial_is_active = int(self.this_instance.is_active)

        self.fields['is_active_field'] = ChoiceField(
            choices=c.IS_ACTIVE_CHOICES,
            label=_('Active'),
            initial=__initial_is_active)


# === Scheme =====================================
class SchemeAddForm(ModelForm): # PR2018-08-24
    class Meta:
        model = Scheme
        fields = ('examyear', 'department', 'level', 'sector', 'name')
        labels = {'examyear': _('Exam year'), 'department': _('Department'), 'level': _('Level'), 'sector': _('Sector'), 'name': _('Name')}

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SchemeAddForm, self).__init__(*args, **kwargs)

        # ======= field 'Examyear' ============
        self.initial['examyear'] = self.request.user.examyear.id
        self.fields['examyear'].disabled = True

        # ======= field 'department' ============
        _dep_choices = Department.dep_list_choices(
            user_country=self.request.user.country,
            skip_none = False)
        self.fields['department'].choices = _dep_choices

        # ======= field 'level' ============
        logger.debug('SchemeAddForm __init__ request.user.country: ' + str(self.request.user.country))
        logger.debug('SchemeAddForm __init__ request.user.department: ' + str(self.request.user.department))

        #_level_choices = Level.level_list_choices(self.request.user.country, self.request.user.department, None, False)  # cur_dep_id = None, skip_none=False
        _level_choices = Level.level_list_choices(
            user_country=self.request.user.country,
            skip_none = True)
        self.fields['level'].choices = _level_choices
        #self.fields['level'].queryset = Level.objects.none()

        # ======= field 'sector' ============
        sector_choices = Sector.sector_list_choices(self.request.user.country, self.request.user.department, None, False)  # cur_dep_id = None, skip_none=False
        self.fields['sector'].choices = sector_choices

        # ======= field 'is_active' ============
        # boolean, required, default=True
        # PR2018-08-09 value in is_active is stored as str: '0'=False, '1'=True
        self.fields['is_active_field'] = ChoiceField(
            choices=c.IS_ACTIVE_CHOICES,
            label=_('Active'),
            initial=1)


class SchemeEditForm(ModelForm):  # PR2018-08-11
    class Meta:
        model = Scheme
        fields = ('department', 'level', 'sector', 'examyear')
        labels = {"department": _('Department'), "level": _('Level'), "sector": _('Sector'), "examyear": _('Exam year')}

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # To get request.user. Do not use kwargs.pop('user', None) due to potential security hole
        super(SchemeEditForm, self).__init__(*args, **kwargs)
        self.this_instance = kwargs.get('instance')

        # ======= field 'Department' ============
        _choices = Department.dep_list_choices(
            user_country=self.request.user.country,
            init_list_str=self.this_instance.dep_list)

        self.fields['department_list'] = ChoiceField(
            required=True,
            choices=_choices,
            label=_('Department')
        )
        # PR2018-08-04 should use self.initial['country'] instead of self.fields['country'].initial =  'override'
        self.initial['department_list'] = self.this_instance.department

        # ======= field 'is_active' ============
        # boolean, required, default=True
        # PR2018-08-09 value in is_active is stored as str: '0'=False, '1'=True
        __initial_is_active = 1
        if self.this_instance is not None:
            __initial_is_active = int(self.this_instance.is_active)

        self.fields['is_active_field'] = ChoiceField(
            choices=c.IS_ACTIVE_CHOICES,
            label=_('Active'),
            initial=__initial_is_active)

        # ======= field 'Examyear' ============
        # PR2018-08-04 should use self.initial['country'] instead of self.fields['country'].initial =  'override'
        # see https://avilpage.com/2015/03/django-form-gotchas-dynamic-initial.html
        # self.initial['examyear'] = self.request.user.examyear.id
        self.fields['examyear'].disabled = True


# === Subjectdefault =====================================
# PR2018-07-20
class SubjectdefaultAddForm(ModelForm):
    class Meta:
        model = Subjectdefault
        fields = ('name', 'abbrev', 'sequence')
        labels = {
            "name": _('Name'),
            "abbrev": _('Abbreviation'),
            "sequence": _('Sequence')}

    # PR2018-06-09 from https://stackoverflow.com/questions/16205908/django-modelform-not-required-field/30403969?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    # called by SubjectdefaultAddForm(request=request) in SubjectdefaultAddView.get and -.post
    def __init__(self, *args, **kwargs):
        # request is added as parameter in ExamyearAddView by form = ExamyearAddForm(request=request)
        # pop() removes and returns an element from a dictionary, second argument is default when not foundrequest = kwargs.pop('request', None)  # pop() removes and returns an element from a dictionary, second argument is default when not found
        self.request = kwargs.pop('request', None)
        super(SubjectdefaultAddForm, self).__init__(*args, **kwargs)
        # logger.debug('SubjectdefaultAddForm __init__ request: ' + str(self.request))

        if self.request.user.country is not None:

            # ======= field 'name' ============
            self.fields['name'] = CharField(
                max_length = 50,
                required = True,
                validators=[validate_unique_subjectdefault_name(self.request.user.country)])
            self.fields['name'].widget.attrs.update({'autofocus': 'autofocus'}) # , 'placeholder': 'Default subject name'

            # ======= field 'abbrev' ============
            self.fields['abbrev'] = CharField(
                max_length = 6,
                required = True,
                validators=[validate_unique_subjectdefault_abbrev(self.request.user.country)])

            # ======= field 'dep_list' ============
            _choices = Department.dep_list_choices(self.request.user.country, None, True)  # cu_dep_id = None, skip_none=True
            self.fields['dep_list_field'] = MultipleChoiceField(
                required=False,
                widget=SelectMultiple,
                choices=_choices,
                label='Departments',
                help_text=_('Select the departments where this default subject is available. '
                            'Press the Ctrl button to select multiple departments.'),
            )

            # ======= field 'level_list' ============
            # level_list_tuple: ((0, 'None'), (1, 'PBL'), (2, 'PKL'), (3, 'TKL')), filter by Country
            # choises must be tuple or list, dictionary gives error: 'int' object is not iterable
            # _choices = Level.level_list_choices(request.user.country, True) # skip_none=True
            self.fields['levl_list_field'] = MultipleChoiceField(
                required=False,
                widget=SelectMultiple,
                # choices=_choices,
                label='Levels',
                help_text=_('Select the levels where this default subject is available. '
                            'Press the Ctrl button to select multiple levels.'),
            )

            # ======= field 'sector_list' ============
            # sector_list_tuple: ((0, 'None'), (1, 'Ec'), (2, 'Z&W'), (3, 'Techn')), filter by Country
            # choises must be tuple or list, dictionary gives error: 'int' object is not iterable
            _choices = Sector.sector_list_choices(self.request.user.country, True) # skip_none=True
            self.fields['level_list_field'] = MultipleChoiceField(
                required=False,
                widget=SelectMultiple,
                choices=_choices,
                label='Sectors',
                help_text=_('Select the sectors where this default subject is available. '
                            'Press the Ctrl button to select multiple sectors.'),
            )

            # ======= field 'is_active' ============
            # boolean, required, default=True
            # PR2018-08-09 value in is_active is stored as str: '0'=False, '1'=True
            self.fields['is_active_field'] = ChoiceField(
                choices=c.IS_ACTIVE_CHOICES,
                label=_('Active'),
                initial=1)


            # ======= field 'Country_list' ============
            # value = request.user.country
            _country_choices = self.request.user.country_choices,
            logger.debug('SubjectdefaultAddForm __init__ request.user.country_choices: ' + str(_country_choices) + ' Type: ' + str(type(_country_choices)))
            _country_choices = []
            if self.request.user.is_role_system:
                countries = Country.objects.order_by('name')
            else:
                # PR2018-06-01 debug: objects.get gives error: 'Country' object is not iterable
                # use objects.filter instead
                countries = Country.objects.filter(id=self.request.user.country.id)
            for country in countries:
                if country.name is not None:
                    _country_choices.append((country.id, country.name))
            logger.debug('SubjectdefaultAddForm __init__ _country_choices: ' + str(_country_choices) + ' Type: ' + str(type(_country_choices)))

            self.fields['country_list'] = ChoiceField(
                required=True,
                choices=_country_choices,
                label=_('Country')
            )
            # PR2018-08-04 should use self.initial['country'] instead of self.fields['country'].initial =  'override'
            self.initial['country_list'] = self.request.user.country
            self.fields['country_list'].disabled = True

            logger.debug('SubjectdefaultAddForm __init__ field Country')

class SubjectdefaultEditForm(ModelForm):  # PR2018-07-21
    class Meta:
        model = Subjectdefault
        fields = ('name', 'abbrev', 'sequence', 'is_active')
        labels = {
            "name": _('Name'),
            "abbrev": _('Abbreviation'),
            "sequence": _('Sequence'),
            "is_active": _('Active')}

    # PR2018-06-09 from https://stackoverflow.com/questions/16205908/django-modelform-not-required-field/30403969?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    def __init__(self, *args, **kwargs):
        # kwargs: {'initial': {}, 'prefix': None, 'instance': <User: Truus>, 'request': <WSGIRequest: GET '/users/7/'>}
        # pop() removes and returns an element from a dictionary, second argument is default when not found
        self.request = kwargs.pop('request', None)  # To get request.user. Do not use kwargs.pop('user', None) due to potential security hole
        super(SubjectdefaultEditForm, self).__init__(*args, **kwargs)

        self.this_instance = kwargs.get('instance')

        # ======= field 'dep_list' ============
        _choices = Department.dep_list_choices(self.request.user.country, None, True)  # cu_dep_id = None, skip_none=True
        self.fields['dep_list_field'] = MultipleChoiceField(
            required=False,
            widget=SelectMultiple,
            choices=_choices,
            label='Departments',
            help_text=_('Select the departments where this default subject is available. '
                        'Press the Ctrl button to select multiple departments.'),
            initial=self.this_instance.dep_list_tuple
        )

        # ======= field 'is_active' ============
        # boolean, required, default=True
        # PR2018-08-09 value in is_active is stored as str: '0'=False, '1'=True
        __initial_is_active = 1
        if self.this_instance is not None:
            __initial_is_active = int(self.this_instance.is_active)

        self.fields['is_active_field'] = ChoiceField(
            choices=c.IS_ACTIVE_CHOICES,
            label=_('Active'),
            initial=__initial_is_active)

    def clean_countries_list_NIU(self):
        countries_list = self.cleaned_data['countries_list']
        logger.debug('SubjectdefaultEditForm XXXclean_countries_listXXX countries_list: <' + str(countries_list)+ '>')

        if countries_list is not None:
            logger.debug('SubjectdefaultEditForm clean_countries_list countries_list: <' + str(countries_list)+ '>')
            has_none = False
            countrylist = ''
            for item in countries_list:
                index = int(item[0])
                if index == -1:
                    has_none == True
                else:
                    countrylist = '; ' + str(index)
            if countrylist: # means: if not countrylist == '':
                # cut off first 2 characters: '; '
                countrylist = countrylist[2:]
        logger.debug('SubjectdefaultEditForm  clean_countries_list countrylist = ' + str(countrylist))

        # Always return a value to use as the new cleaned data, even if this method didn't change it.
        return countrylist

    # add field is_active
        # PR2018-07-19 , value in is_active is stored as str: '0'=False, '1'=True
       # __initial_inactive = 0
        #if self.selected_subject.is_active is not None:
        #    __initial_inactive = int(self.selected_subject.is_active)
        ##logger.debug('CountryEditForm ' + str(self.selected_country) + '__initial_locked: ' + str(__initial_locked) + ' type : ' + str(type(__initial_locked)))
        #self.fields['field_inactive'] = ChoiceField(
        #    choices=c.INACTIVE_CHOICES,
        #    label=_('Inactive'),
        #    initial=__initial_inactive
        #)


# === Subject =====================================
# PR2018-08-09
class SubjectAddForm(ModelForm):
    class Meta:
        model = Subject
        fields = ('name', 'abbrev', 'sequence', 'dep_list', 'examyear')
        labels = {
            "name": _('Name'),
            "abbrev": _('Abbreviation'),
            "sequence": _('Sequence'),
            "dep_list": _('Departments'),
            "examyear": _('Examyear')}

    # PR2018-06-09 from https://stackoverflow.com/questions/16205908/django-modelform-not-required-field/30403969?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    # called by SubjectdefaultAddForm(request=request) in SubjectdefaultAddView.get and -.post
    def __init__(self, *args, **kwargs):
        # request is added as parameter in ExamyearAddView by form = ExamyearAddForm(request=request)
        # pop() removes and returns an element from a dictionary, second argument is default when not foundrequest = kwargs.pop('request', None)  # pop() removes and returns an element from a dictionary, second argument is default when not found
        request = kwargs.pop('request', None)
        super(SubjectAddForm, self).__init__(*args, **kwargs)
        # logger.debug('SubjectAddForm __init__ request: ' + str(request))

        self.selected_subject = kwargs.get('instance')

        # ======= field 'name' ============
        self.fields['name'] = CharField(
            max_length = 50,
            required = True,
            validators=[validate_unique_subject_name(request.user.country)])
        self.fields['name'].widget.attrs.update({'autofocus': 'autofocus'}) # , 'placeholder': 'Default subject name'

        # ======= field 'abbrev' ============
        self.fields['abbrev'] = CharField(
            max_length = 6,
            required = True,
            validators=[validate_unique_subject_abbrev(request.user.country)])

        # ======= field 'sequence' ============
        # ======= field 'dep_list' ============

        # ======= field 'is_active' ============
        # boolean, required, default=True
        # PR2018-08-09 value in is_active is stored as str: '0'=False, '1'=True
        self.fields['is_active_field'] = ChoiceField(
            choices=c.IS_ACTIVE_CHOICES,
            label=_('Active'),
            initial=1)

        # ======= field 'examyear' ============
        # PR2018-08-09 should use self.initial['examyear'] instead of self.fields['examyear'].initial =  'override'
        # see https://avilpage.com/2015/03/django-form-gotchas-dynamic-initial.html
        self.initial['examyear'] = request.user.examyear.id
        self.fields['examyear'].disabled = True


# +++++++++++++++++++++  VALIDATORS  ++++++++++++++++++++++++++++++

# ===  Level  =====================================
# PR2018-08-06:
class validate_unique_level_name(object):
    def __init__(self, country, instance=None):
        self.country = country
        if instance:
            self.instance_id = instance.id
        else:
            self.instance_id = None

    def __call__(self, value):
        # __iexact looks for the exact string, but case-insensitive. If value is None, it is interpreted as an SQL NULL
        if value is None:
            _value_exists = False
        elif self.instance_id is None:
            _value_exists = Level.objects.filter(name__iexact=value, country=self.country).exists()
        else:
            _value_exists = Level.objects.filter(name__iexact=value, country=self.country).exclude(pk=self.instance_id).exists()
        if _value_exists:
            raise ValidationError(_('Level name already exists.'))
        return value

# PR2018-08-11:
class validate_unique_level_abbrev(object):
    def __init__(self, country, instance=None):
        self.country = country
        if instance is None:
            # instance_id gets value=-1 when adding new record, to skip exclude
            self.instance_id = -1
        else:
            self.instance_id = instance.id

    def __call__(self, value):
        # logger.debug('validate_unique_level_abbrev __call__ value: ' + str(value))
        # __iexact looks for the exact string, but case-insensitive. If value is None, it is interpreted as an SQL NULL
        _value_exists = False
        if value is not None:
            _value_exists = Level.objects.filter(abbrev__iexact=value, country=self.country).exclude(pk=self.instance_id).exists()
        if _value_exists:
            raise ValidationError(_('Abbreviation of level already exists.'))
        # logger.debug('validate_unique_level_abbrev __init__ _value_exists: ' + str(_value_exists))
        return value

# ===  Sector  =====================================
class validate_unique_sector_name(object):  # PR2018-08-24
    def __init__(self, country, instance=None):
        self.country = country
        if instance:
            self.instance_id = instance.id
        else:
            self.instance_id = None

    def __call__(self, value):
        # __iexact looks for the exact string, but case-insensitive. If value is None, it is interpreted as an SQL NULL
        if value is None:
            _value_exists = False
        elif self.instance_id is None:
            _value_exists = Sector.objects.filter(name__iexact=value, country=self.country).exists()
        else:
            _value_exists = Sector.objects.filter(name__iexact=value, country=self.country).exclude(pk=self.instance_id).exists()
        if _value_exists:
            raise ValidationError(_('Sector name already exists.'))
        return value

class validate_unique_sector_abbrev(object):  # PR2018-08-24
    def __init__(self, country, instance=None):
        self.country = country
        if instance:
            self.instance_id = instance.id
        else:
            self.instance_id = None

    def __call__(self, value):
        # __iexact looks for the exact string, but case-insensitive. If value is None, it is interpreted as an SQL NULL
        if value is None:
            _value_exists = False
        elif self.instance_id is None:
            _value_exists = Sector.objects.filter(abbrev__iexact=value, country=self.country).exists()
        else:
            _value_exists = Sector.objects.filter(abbrev__iexact=value, country=self.country).exclude(pk=self.instance_id).exists()
        if _value_exists:
            raise ValidationError(_('Abbreviation of sector already exists.'))
        return value

# ===  Subjectdefault  =====================================

class validate_unique_subjectdefault_name(object):  # PR2018-08-16:
    def __init__(self, country, instance=None):
        self.country = country
        self.instance = instance
        # logger.debug('validate_unique_subjectdefault_name __init__ self.instance: ' + str(self.instance))

    def __call__(self, value):
        if self.country and value:
            # logger.debug('validate_unique_subjectdefault_name __call__ value: ' + str(value))
            # __iexact looks for case-insensitive string. If value is None, it is interpreted as an SQL NULL
            if self.instance:
                # exclude value of this instance
                subjectdefault = Subjectdefault.objects.filter(name__iexact=value, country=self.country).exclude(pk=self.instance.id).first()
            else:
                subjectdefault = Subjectdefault.objects.filter(name__iexact=value, country=self.country).first()
            if subjectdefault:
                raise ValidationError(_('Name "%s" already exists.' %subjectdefault.name))
        return value


class validate_unique_subjectdefault_abbrev(object):  # PR2018-08-16:
    def __init__(self, country, instance=None):
        self.country = country
        self.instance = instance

    def __call__(self, value):
        if self.country and value:
            # __iexact looks for case-insensitive string. If value is None, it is interpreted as an SQL NULL
            if self.instance:
                # exclude value of this instance
                subjectdefault = Subjectdefault.objects.filter(abbrev__iexact=value, country=self.country).exclude(pk=self.instance.id).first()
            else:
                subjectdefault = Subjectdefault.objects.filter(abbrev__iexact=value, country=self.country).first()
            if subjectdefault:
                raise ValidationError(_('Abbreviation "%s" already exists.' %subjectdefault.abbrev))
        return value


# === VALIDATORS =====================================
# PR2018-08-06:
class validate_unique_subject_name(object):
    def __init__(self, examyear):
        self.examyear = examyear
        # logger.debug('validate_unique_subject __init__ self.examyear: ' + str(self.examyear))

    def __call__(self, value):
        # logger.debug('validate_unique_subjec __call__ value: ' + str(value))
        # filter a Case-insensitive exact match.
        if Subject.objects.filter(name__iexact=value, examyear=self.examyear).exists():
            #logger.debug('validate_unique_subjectdefault ValidationError: Default subject exists')
            # raise ValidationError({'subjectdefault':[_('Subject already exists.'),]})
            raise ValidationError(_('Subject already exists.'))
        return value

# PR2018-08-09:
class validate_unique_subject_abbrev(object):
    def __init__(self, examyear):
        self.examyear = examyear
        # logger.debug('validate_unique_subject_abbrev __init__ self.examyear: ' + str(self.examyear))

    def __call__(self, value):
        # logger.debug('validate_unique_subject_abbrev __call__ value: ' + str(value))
        # filter a Case-insensitive exact match.
        if Subject.objects.filter(abbrev__iexact=value, examyear=self.examyear).exists():
            # logger.debug('validate_unique_subject_abbrev ValidationError: Default subject exists')
            # raise ValidationError({'subject':[_('Abbreviation of default subject already exists.'),]})
            raise ValidationError(_('Abbreviation of default subject already exists.'))
        return value

