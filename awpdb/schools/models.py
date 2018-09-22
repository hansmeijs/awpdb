#PR2018-04-13
from django.db.models import Model, Manager, ForeignKey, PROTECT, CASCADE
from django.db.models import CharField, IntegerField, PositiveSmallIntegerField, BooleanField, DateField, DateTimeField
from django.contrib.auth import get_user_model
from django.utils import timezone

# PR2018-05-05 use AUTH_USER_MODEL
#from django.contrib.auth.models import User
#from accounts.models import User
from awpdb.settings import AUTH_USER_MODEL
from django.utils.translation import ugettext_lazy as _
from awpdb import constants as c
# PR2018-09-15 Departmnet moved from Subjects to Schools; because this doesn/'t work, circular reference: from subjects.models import Department

import logging
logger = logging.getLogger(__name__)

# PR2018-04-22: backup: (venv) C:\dev\awpr\awpr>py -3 manage.py dumpdata schools --format json --indent 4 > schools/backup/schools.json
#               restore: (venv) C:\dev\awpr\awpr>py -3 manage.py loaddata schools/backup/schools.json

# The clean() method on a Field subclass is responsible for running to_python() , validate() , and run_validators()
# in the correct order and propagating their errors.
# If, at any time, any of the methods raise ValidationError, the validation stops and that error is raised.
# This method returns the clean data, which is then inserted into the cleaned_data dictionary of the form.

# PR2018-07-20 from https://stackoverflow.com/questions/3090302/how-do-i-get-the-object-if-it-exists-or-none-if-it-does-not-exist
# CustomManager adds function get_or_none. Used in  Subjectdefault to prevent DoesNotExist exception
class CustomManager(Manager):
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.DoesNotExist:
            return None


class Country(Model):
    # PR2018-07-20 from https://stackoverflow.com/questions/3090302/how-do-i-get-the-object-if-it-exists-or-none-if-it-does-not-exist
    objects = CustomManager()

    name = CharField(max_length=20, unique=True)
    abbrev = CharField(max_length=6, unique=True)
    locked = BooleanField(default=False)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    class Meta:
        ordering = ['name',]

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(Country, self).__init__(*args, **kwargs)
        # private variable __original checks if data_has_changed, to prevent update record when no changes are made.
        # otherwise a logrecord would be created every time the save button is clicked without changes
        self.original_name = self.name
        self.original_abbrev = self.abbrev
        self.original_locked = self.locked

    def save(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)

        # Override the save() method of the model to perform validation on every save.
        # https://stackoverflow.com/questions/14470585/how-to-validate-uniqueness-constraint-across-foreign-key-django?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
        # self.full_clean()

    # check if data has changed. If so: save object
        #logger.debug('original_name ' + str(self.original_name) + ' name ' + str(self.name))
        if self.data_has_changed():
            self.modified_by = self.request.user
            # timezone.now() is timezone aware, based on the USE_TZ setting; datetime.now() is timezone naive. PR2018-06-07
            self.modified_at = timezone.now()
            self.mode = ('c', 'u')[self.is_update]  # result = (on_false, on_true)[condition]
            # when adding record: self.id=None, set force_insert=True; otherwise: set force_update=True PR2018-06-09
            super(Country, self).save(force_insert = not self.is_update, force_update = self.is_update, **kwargs)
            # self.id gets its value in super(Country, self).save
            # save to logfile
            self.save_to_log()

    def delete(self, *args, **kwargs):
        self.modified_at = timezone.now()
        self.mode = 'd'
        self.data_has_changed()
        # First save to logfile
        self.save_to_log()
        # then delete record
        super(Country, self).delete(*args, **kwargs)

    def save_to_log(self):
        Country_log.objects.create(
            country_id=self.id,

            name=self.name,
            abbrev=self.abbrev,
            locked=self.locked,

            name_mod=self.name_mod,
            abbrev_mod=self.abbrev_mod,
            locked_mod=self.locked_mod,

            mode=self.mode,
            modified_by=self.modified_by,
            modified_at=self.modified_at
        )

    def data_has_changed(self):  # PR2018-08-31
        # returns True when the value of one or more fields has changed PR2018-08-26
        self.is_update = self.id is not None # self.id is None before new record is saved
        self.name_mod = self.original_name != self.name
        self.abbrev_mod = self.original_abbrev != self.abbrev
        self.locked_mod = self.original_locked != self.locked
        return not self.is_update or \
               self.name_mod or \
               self.abbrev_mod or \
               self.locked_mod

    @property # PR2018-06-22
    def has_no_linked_data(self):
        User = get_user_model()
        linked_users_count = User.objects.filter(country_id=self.pk).count()
        # logger.debug('Country(Model has_linked_data linked_users_count: ' + str(linked_users_count))
        # TODO add other dependencies: Subject, Schoolcode etc
        return not bool(linked_users_count)

    @property
    def locked_str(self):
        return c.LOCKED_DICT.get(self.locked, '')

# PR2018-05-05
class Country_log(Model):
    objects = CustomManager()

    country_id = IntegerField(db_index=True)

    name = CharField(max_length=20, null=True)
    abbrev = CharField(max_length=6, null=True)
    locked = BooleanField(default=False)

    name_mod = BooleanField(default=False)
    abbrev_mod = BooleanField(default=False)
    locked_mod = BooleanField(default=False)

    mode = CharField(max_length=1, null=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    def __str__(self):
        return self.name

    @property
    def locked_str(self):
        return c.LOCKED_DICT.get(self.locked)

    @property
    def mode_str(self):
        mode_str = '-'
        if self.mode is not None:
            mode_str = c.MODE_DICT.get(str(self.mode))
        return mode_str


# ===  Examyear Model =====================================
class Examyear(Model):  # PR2018-06-06
    objects = CustomManager()

    country = ForeignKey(Country, related_name='examyears', on_delete=PROTECT)
    examyear = PositiveSmallIntegerField()
    published = BooleanField(default=False)
    locked = BooleanField(default=False)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    class Meta:
        ordering = ['-examyear',]

    def __str__(self):
        return str(self.examyear)

    def __init__(self, *args, **kwargs):
        super(Examyear, self).__init__(*args, **kwargs)
        # private variable __original checks if data_has_changed, to prevent update record when no changes are made.
        # Otherwise a logrecord would be created every time the save button is clicked without changes

        try: # PR2018-08-03 necessary, otherwise gives error 'Examyear has no country' because self = None.
            self._original_country = self.country
        except:
            self._original_country = None

        self._original_examyear = self.examyear
        self.__original_published = self.published
        self._original_locked = self.locked

    def save(self, *args, **kwargs):
        # country.save(request) in ExamyearAddView.post
        self.request = kwargs.pop('request', None)

        if self.data_has_changed():
            self.modified_by = self.request.user
            self.modified_at = timezone.now()  # timezone.now() is timezone aware, based on the USE_TZ setting; datetime.now() is timezone naive. PR2018-06-07
            self.mode = ('c', 'u')[self.is_update]  # result = (on_false, on_true)[condition]
            # when adding record: self.id=None, set force_insert=True; otherwise: set force_update=True PR2018-06-09
            super(Examyear, self).save(force_insert = not self.is_update, force_update = self.is_update, **kwargs)
            # self.id gets its value in super(Country, self).save
            self.save_to_log()

    def delete(self, *args, **kwargs):
        # first save to logfile
        self.modified_at = timezone.now()
        self.mode='d'
        self.save_to_log()
        # then delete record
        super(Examyear, self).delete(*args, **kwargs)

    def save_to_log(self, *args, **kwargs):
        _country_mod = self._original_country != self.country
        _examyear_mod = self._original_examyear != self.examyear
        _published_mod = bool(self.__original_published)!= bool(self.published)
        _locked_mod = bool(self._original_locked) != bool(self.locked)

        #Create method also saves record
        log_obj = Examyear_log.objects.create(
            examyear_id=self.id,

            country=self.country,
            examyear=self.examyear,
            published=self.published,
            locked=self.locked,

            country_mod=_country_mod,
            examyear_mod=_examyear_mod,
            published_mod=_published_mod,
            locked_mod=_locked_mod,

            mode=self.mode,
            modified_by=self.modified_by,
            modified_at=self.modified_at
        )
        log_obj.save()

    def data_has_changed(self):
        # returns True when the value of one or more fields has changed PR2018-08-26
        self.is_update = self.id is not None # self.id is None before new record is saved

        modified = False
        if self.id is None: # save new record
            modified = True
        elif self._original_country != self.country:
            modified = True
        elif self._original_examyear != self.examyear:
            modified = True
        elif bool(self.__original_published)!= bool(self.published):
            modified = True
        elif bool(self._original_locked)!= bool(self.locked):
            modified = True
        return modified

    @property
    def locked_str(self):
        return c.LOCKED_DICT.get(int(self.locked))

    @property
    def published_str(self):
        return c.PUBLISHED_DICT.get(int(self.published))

    @property
    def schoolyear(self):  # PR2018-05-18 calculates schoolyear from this_examyear
        schoolyear = '-'
        if self.examyear is not None:
            schoolyear = str(self.examyear -1) + '-' + str(self.examyear)
        return schoolyear

    @property
    def equals_this_examyear(self):
        # PR2018-05-18 this_examyear is from August 01 thru July 31
        # PR2018-05-18 returns True if selected_examyear is this_examyear
        examyear_equals_thisyear = False
        if self.examyear is not None:
            now = timezone.now()
            this_examyear = now.year
            selected_examyear = self.examyear

            if now.month > 7:
                this_examyear = now.year + 1
            if selected_examyear == this_examyear:
                examyear_equals_thisyear = True
        return examyear_equals_thisyear

    @classmethod
    def next_examyear(self, request):
        # PR2018-07-25
        # PR2018-04-20 debug: gives error: invalid literal for int() with base 10: 'None' when table is empty
        # year_count = self.objects.count()

        #logger.debug('class Examyear(Model) next_examyear request.user.country: ' + str(request.user.country))
        try:
            examyear_count = self.objects.filter(country=request.user.country).count()
            # logger.debug('class Examyear(Model) next_examyear year_count: ' + str(year_count))
            if examyear_count == 0:
                examyear_max = 2018
            else:
                examyear = self.objects.filter(country=request.user.country).order_by('-examyear').first()
                examyear_max = examyear.examyear
                # logger.debug('class Examyear(Model) next_examyear examyear_max: ' + str(examyear_max))
        except:
            examyear_max = 2018
        examyear_new = int(examyear_max) + 1
        return examyear_new

# PR2018-06-06
class Examyear_log(Model):
    objects = CustomManager()

    examyear_id = IntegerField(db_index=True)
    country = ForeignKey(Country, null=True, related_name='+', on_delete=PROTECT)
    country_mod = BooleanField(default=False)
    examyear = PositiveSmallIntegerField(null=True)
    examyear_mod = BooleanField(default=False)
    published = BooleanField(default=False)
    published_mod = BooleanField(default=False)
    locked = BooleanField(default=False)
    locked_mod = BooleanField(default=False)
    mode = CharField(max_length=1, null=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    @property
    def published_str(self):
        return c.PUBLISHED_DICT.get(int(self.published))

    @property
    def locked_str(self):
        return c.LOCKED_DICT.get(int(self.locked))

    @property
    def mode_str(self):
        mode_str = '-'
        if self.mode is not None:
            mode_str = c.MODE_DICT.get(str(self.mode))
        return mode_str


# === Department =====================================
# PR2018-09-15 moved from Subjects to School because of circulair refrence when trying to import subjects.Department
class Department(Model):# PR2018-08-10
    objects = CustomManager()

    country = ForeignKey(Country, related_name='dep_list', on_delete=PROTECT)
    name = CharField(max_length=50, # PR2018-08-06 set Unique per Country True. Was: unique=True,
        help_text=_('Required. {} characters or fewer.'.format('50')),)
    abbrev = CharField(max_length=8, # PR2018-08-06 set Unique per Country True. Was: unique=True,
        help_text=_('Required. {} characters or fewer.'.format('8')),)
    sequence = PositiveSmallIntegerField(default=1)
    is_active = BooleanField(default=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    class Meta:
        ordering = ['sequence',]

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(Department, self).__init__(*args, **kwargs)
        # private variable __original checks if data_has_changed, to prevent update record when no changes are made.
        # Otherwise a logrecord is created every time the save button is clicked without changes
        try:
            self.original_country = self.country  # result = (on_false, on_true)[condition]
            # logger.debug('class Department(Model) __init__ self.original_country: ' + str(self.original_country))
        except:
            self.original_country = None
        self.original_name = self.name
        self.original_abbrev = self.abbrev
        self.original_is_active = self.is_active
        self.original_sequence = self.sequence
        """
        # TODO iterate through field list PR2018-08-22
        see: https://www.caktusgroup.com/blog/2018/05/07/creating-dynamic-forms-django/
        for i in range(len(interests) + 1):
            field_name = 'interest_%s' % (i,)
            self.fields[field_name] = forms.CharField(required=False)
            try:
                self.initial[field_name] = interests[i].interest
            Except IndexError:
                self.initial[field_name] = “”
        field_name = 'interest_%s' % (i + 1,)
        self.fields[field_name] = forms.CharField(required=False)
        self.fields[field_name] = “”
        """

        # for k, v in vars(self).items():
        #     logger.debug('class Department(Model) __init__ for k, v in vars(self).items(): k: ' + str(k) + '_v: ' + str(v))

    def save(self, *args, **kwargs):  # called by subjectdefault.save(self.request) in SubjectdefaultEditView.form_valid
        self.request = kwargs.pop('request', None)

        # Override the save() method of the model to perform validation on every save.
        # https://stackoverflow.com/questions/14470585/how-to-validate-uniqueness-constraint-across-foreign-key-django?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
        # self.full_clean()

    # check if data has changed. If so: save object
        if self.data_has_changed():
            self.modified_by = self.request.user
            # timezone.now() is timezone aware, based on the USE_TZ setting; datetime.now() is timezone naive. PR2018-06-07
            self.modified_at = timezone.now()
            self.mode = ('c', 'u')[self.is_update]  # result = (on_false, on_true)[condition]

            # when adding record: self.id=None, set force_insert=True; otherwise: set force_update=True PR2018-06-09
            super(Department, self).save(force_insert = not self.is_update, force_update = self.is_update, **kwargs)
            # self.id gets its value in super(Country, self).save
            self.save_to_log()

    def delete(self, *args, **kwargs):
        self.modified_at = timezone.now()
        self.mode = 'd'
        self.data_has_changed()
        # First save to logfile
        self.save_to_log()
        # then delete record
        super(Department, self).delete(*args, **kwargs)

    def save_to_log(self):
        # Create method also saves record
        Department_log.objects.create(
            department_id=self.id, # self.id gets its value in super(School, self).save

            country=self.country,
            name=self.name,
            abbrev=self.abbrev,
            sequence = self.sequence,
            is_active = self.is_active,

            country_mod = self.country_mod,
            name_mod = self.name_mod,
            abbrev_mod = self.abbrev_mod,
            sequence_mod = self.sequence_mod,
            is_active_mod = self.is_active_mod,

            mode=self.mode,
            modified_by=self.modified_by,
            modified_at=self.modified_at
        )

    def data_has_changed(self):  # PR2018-07-21
        # returns True when the value of one or more fields has changed PR2018-08-26
        self.is_update = self.id is not None # self.id is None before new record is saved
        self.country_mod = self.original_country != self.country
        self.name_mod = self.original_name != self.name
        self.abbrev_mod = self.original_abbrev != self.abbrev
        self.sequence_mod = self.original_sequence != self.sequence
        self.is_active_mod = self.original_is_active != self.is_active

        return not self.is_update or \
               self.country_mod or \
               self.name_mod or \
               self.abbrev_mod or \
               self.sequence_mod or \
               self.is_active_mod

    # @property  # PR2018-08-11
    # def has_no_linked_data(self):
    #     linked_items_count = Scheme.objects.filter(department_id=self.pk).count()
    #     # logger.debug('SubjectDefault Model has_no_linked_data linked_items_count: ' + str(linked_items_count))
    #     return not bool(linked_items_count)

    @property
    def shortname(self):
        # PR2018-05-18 calculates 'Vsbo' from 'V.S.B.O.'
        _abbrev = ''
        if self.abbrev is not None:
            _abbrev = str(self.abbrev)
            _without_dots = _abbrev.replace('.', '')
            _without_spaces = _without_dots.replace(' ', '')
            _first_letter = _without_spaces[0:1]
            _other_letters = _without_spaces[1:]
            _abbrev = _first_letter.upper() + _other_letters.lower()
        return _abbrev

    @property
    def is_active_str(self): # PR108-08-09
        return c.IS_ACTIVE_DICT.get(self.is_active, '')


#  ++++++++++  Class methods  ++++++++++++++++++++++++
    @classmethod
    def dep_list_str(cls, dep_list):
        # PR2018-08-16 dep_list_str displays string of dep_list, level_list or sector_list.
        # e.g.: '1;2;3' becomes 'Vsbo, Havo, Vwo', '0' is skipped', empty is displayed as '-'
        list_str = '-'
        # logger.debug('DepartmentModel dep_list_str dep_list: <' + str(dep_list) + '> type: <' + str(type(dep_list)) + '>')
        if dep_list:
            list_split = dep_list.split(';')
            if bool(list_split):
                # logger.debug('DepartmentModel dep_list_str list_split: <' + str(list_split) + '> type: <' + str(type(list_split)) + '>')
                for id_str in list_split:
                    if id_str:
                        value = ''
                        try:
                            id_int = int(id_str)
                            # logger.debug('DepartmentModel dep_list_str _id_int: ' + str(id_int) + '> type: <' + str(type(id_int)) + '>')
                            # skip value 0 (None)
                            if id_int:
                                # logger.debug('DepartmentModel dep_list_str _id_int: ' + str(_id_int))
                                instance = cls.objects.filter(pk=id_int).first()
                                value = instance.shortname
                                # logger.debug('DepartmentModel dep_list_str value: ' + str(value) + '> type: <' + str(type(value)) + '>')
                        except:
                            value = ''
                        if value:
                            list_str = list_str + ', ' + value
                if list_str:  # means: if not list_str == '':
                    # slice off first 2 characters: ', '
                    list_str = list_str[2:]
        # logger.debug('DepartmentModel dep_list_str list_str: <' + str(list_str) + '>')
        return list_str

    @classmethod
    def dep_list_choices(cls, user_country=None, init_list_str=None, skip_none=False):
        # PR2018-08-12 function creates list of dep_list, used in LevelAddForm, LevelEditForm, SecctorAddForm, SectorEditForm
        # filter by user_country
        # add inactive records only when it is the current record (otherwise it will not display in field) PR2018-08-24
        # choises must be tuple or list, dictionary gives error: 'int' object is not iterable
        # dep_list_choices: [(0, 'None'), (1, 'Vsbo'), (2, 'Havo'), (3, 'Vwo')]
        # IN USE?? dep_list_choices_tuple: ((0, 'None'), (1, 'Vsbo'), (2, 'Havo'), (3, 'Vwo')), filter by Country
        #logger.debug('DepartmentModel dep_list_choices init_list_str: <' + str(init_list_str) + '> Type: ' + str(type(init_list_str)))

        choices = []
        if user_country:
            # add row 'None' at the start, only if not skip_none
            if not skip_none:
                choices = [(0, '---')]

            # PR2018-08-28 init_list is the dep_list of the current user. Inactive items that are in the init_list will still be shown
            init_list_tuple = ()
            if init_list_str:
                # This function converts init_list_str string into init_list_tuple,  e.g.: ';1;2;' will be converted to (,1,2,)
                init_list_list = init_list_str.split(';')
                init_list_tuple = tuple(init_list_list)

            # iterate through departments rows, filtered by country
            departments = cls.objects.filter(country=user_country)
            for item in departments:
                if item:
                    # check if item must be added to list:
                    # - all active items are added
                    # - inactive items are only added when they are in init_list_str
                    show_item = False
                    if item.is_active:
                        show_item = True
                    else:
                        # do show inactive items when they are in init_list
                        if init_list_tuple:
                            for list_item in init_list_tuple:
                                # PR2018-08-30 debug: skip empty element to prevent error:
                                # "invalid literal for int() with base 10: ''"
                                if list_item:
                                    if int(list_item) == item.id:
                                        show_item = True
                                        break
                    # add item to list
                    if show_item:
                        display = item.shortname + ' ' + item.country.name
                        # display INACTIVE when item is inactive
                        if not item.is_active:
                            display += ' (inactive)'
                        item = (item.id, display )
                        choices.append(item)
        #logger.debug('dep_list_choices choices = ' + str(choices))
        return choices


# PR2018-06-06
class Department_log(Model):
    objects = CustomManager()

    department_id = IntegerField(db_index=True)
    country = ForeignKey(Country, null=True, related_name='+', on_delete=PROTECT)
    name = CharField(max_length=50, null=True)
    abbrev = CharField(max_length=8, null=True)
    sequence = PositiveSmallIntegerField()
    is_active = BooleanField(default=True)

    country_mod = BooleanField(default=False)
    name_mod = BooleanField(default=False)
    abbrev_mod = BooleanField(default=False)
    sequence_mod = BooleanField(default=False)
    is_active_mod = BooleanField(default=False)

    mode = CharField(max_length=1, null=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    @property
    def is_active_str(self):
        return c.IS_ACTIVE_DICT.get(self.is_active, '')

    @property
    def mode_str(self):
        return c.MODE_DICT.get(str(self.mode),'-')


# PR2018-05-27
class Schooldefault(Model):
    # PR2018-07-20 from https://stackoverflow.com/questions/3090302/how-do-i-get-the-object-if-it-exists-or-none-if-it-does-not-exist
    objects = CustomManager()

    country = ForeignKey(Country, related_name='schooldefaults', on_delete=PROTECT)
    name = CharField(max_length=50, unique=True,
        help_text=_('Required. {} characters or fewer.'.format('50')),
        error_messages={'unique': _("A school with that name already exists."),})
    code = CharField(max_length=12,unique=True,
        help_text=_('Required. {} characters or fewer.'.format('12')),
        error_messages={'unique': _("A schoolcode with that name already exists."),})
    abbrev = CharField(max_length=20)
    article = CharField(max_length=3, null=True)
    dep_list = CharField(max_length=20, null=True)
    is_template = BooleanField(default=False)  # School 'Inspections' has default template settings for all schools of this country
    is_active = BooleanField(default=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    class Meta:
        ordering = ['code',]

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):  # PR2018-07-23
        super(Schooldefault, self).__init__(*args, **kwargs)
        # private variable __original checks if data_has_changed, to prevent update record when no changes are made.
        # Otherwise a logrecord is created every time the save button is clicked without changes
        try:
            self._original_country = self.country
        except:
            self._original_country = None
        self.original_name = self.name
        self.original_code = self.code
        self.original_abbrev = self.abbrev
        self.original_article = self.article
        self.original_dep_list = self.dep_list
        self.original_is_template = self.is_template
        self.original_is_active = self.is_active

    def save(self, *args, **kwargs):  # called by schooldefault.save(self.request) in SchooldefaultEditView.form_valid
        self.request = kwargs.pop('request', None)
        logger.debug('Schooldefault(Model) save: self.request: ' + str(self.request) + ' type: ' + str(type(self.request)))

        # Override the save() method of the model to perform validation on every save.
        # https://stackoverflow.com/questions/14470585/how-to-validate-uniqueness-constraint-across-foreign-key-django?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
        # self.full_clean()

    # check if data has changed. If so: save object
        if self.data_has_changed():
            self.modified_by = self.request.user
            # timezone.now() is timezone aware, based on the USE_TZ setting; datetime.now() is timezone naive. PR2018-06-07
            self.modified_at = timezone.now()
            self.mode = ('c', 'u')[self.is_update]  # result = (on_false, on_true)[condition]
            # when adding record: self.id=None, set force_insert=True; otherwise: set force_update=True PR2018-06-09
            super(Schooldefault, self).save(force_insert = not self.is_update, force_update = self.is_update, **kwargs)
            self.save_to_log()

    def delete(self, *args, **kwargs):
        self.data_has_changed()  # necessary to get _mod variables
        self.modified_at = timezone.now()
        self.mode='d'
        # First save to logfile
        self.save_to_log()
        # then delete record
        super(Schooldefault, self).delete(*args, **kwargs)

    def save_to_log(self): # PR2018-08-26
        # Create method also saves record
        Schooldefault_log.objects.create(
            schooldefault_id=self.id,  # self.id gets its value in super(Schooldefault, self).save

            country=self.country,
            name=self.name,
            code=self.code,
            abbrev=self.abbrev,
            article=self.article,
            dep_list=self.dep_list,
            is_template=self.is_template,
            is_active=self.is_active,

            country_mod=self.country_mod,
            name_mod=self.name_mod,
            code_mod=self.code_mod,
            abbrev_mod=self.abbrev_mod,
            article_mod=self.article_mod,
            dep_list_mod=self.dep_list_mod,
            is_template_mod=self.is_template_mod,
            is_active_mod=self.is_active_mod,

            mode=self.mode,
            modified_by=self.modified_by,
            modified_at=self.modified_at
        )

    def data_has_changed(self):
        # returns True when the value of one or more fields has changed PR2018-08-26
        self.is_update = self.id is not None # self.id is None before new record is saved

        self.country_mod = self._original_country != self.country
        self.name_mod = self.original_name != self.name
        self.code_mod = self.original_code != self.code
        self.abbrev_mod = self.original_abbrev != self.abbrev
        self.article_mod = self.original_article != self.article
        self.dep_list_mod = self.original_dep_list != self.dep_list
        self.is_template_mod = self.original_is_template != self.is_template
        self.is_active_mod = self.original_is_active != self.is_active

        return not self.is_update or \
               self.country_mod or \
               self.name_mod or \
               self.code_mod or \
               self.abbrev_mod or \
               self.article_mod or \
               self.dep_list_mod or \
               self.is_template_mod or \
               self.is_active_mod

    @property  # PR2018-07-23
    def has_no_linked_data(self):
        linked_items_count = School.objects.filter(schooldefault_id=self.pk).count()
        # logger.debug('SchooldefaultModel has_no_linked_data linked_items_count: ' + str(linked_items_count))
        return not bool(linked_items_count)


    # PR2018-06-03
    def code_schoolname(self):
        code_str = ''
        if self.code:
            code_str = str(self.code) + ' - '
        if self.name:
            code_str = code_str + str(self.name)
        return code_str

    @property
    def is_active_str(self):  # PR108-09-02
        return c.IS_ACTIVE_DICT.get(self.is_active, '')

    @property
    def is_active_choices(self):  # PR108-09-02
        return c.IS_ACTIVE_DICT.get(self.is_active, '')
# PR2018-05-05
class Schooldefault_log(Model):
    objects = CustomManager()

    schooldefault_id = IntegerField(db_index=True)

    country = ForeignKey(Country, null=True, related_name='+', on_delete=PROTECT)
    name = CharField(max_length=50, null=True)
    code = CharField(max_length=12,null=True)
    abbrev = CharField(max_length=20,null=True)
    article = CharField(max_length=3, null=True)
    dep_list = CharField(max_length=20, null=True)
    is_template = BooleanField(default=False)  # School 'Inspections' has default template settings for all schools of this country
    is_active = BooleanField(default=False)

    country_mod = BooleanField(default=False)
    name_mod = BooleanField(default=False)
    code_mod = BooleanField(default=False)
    abbrev_mod = BooleanField(default=False)
    article_mod = BooleanField(default=False)
    dep_list_mod = BooleanField(default=False)
    is_template_mod = BooleanField(default=False)  #
    is_active_mod = BooleanField(default=False)

    mode = CharField(max_length=1, null=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()


# ===  School Model =====================================
class School(Model):  # PR2018-08-20
    objects = CustomManager()

    examyear = ForeignKey(Examyear, related_name='schools', on_delete=PROTECT)
    schooldefault = ForeignKey(Schooldefault, related_name='schools', on_delete=PROTECT)
    is_template = BooleanField(default=False)  # is_template School of this country and examyear PR2018-08-23

    name = CharField(max_length=50)
    code = CharField(max_length=12)
    abbrev = CharField(max_length=20)
    article = CharField(max_length=3, null=True)
    dep_list = CharField(max_length=20, null=True)
    # president = CharField(max_length=50, null=True)
    # secretary = CharField(max_length=50, null=True)
    # diplomadate = DateField(null=True)
    locked =  BooleanField(default=False)

    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    class Meta:
        ordering = ['code',]

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):  # PR2018-08-20
        super(School, self).__init__(*args, **kwargs)
        # private variable __original checks if data_has_changed, to prevent update record when no changes are made.
        # Otherwise a logrecord is created every time the save button is clicked without changes
        try:
            self.original_examyear = self.examyear  # result = (on_false, on_true)[condition]
        except:
            self.original_examyear = None
        try:
            self.original_schooldefault = self.schooldefault  # result = (on_false, on_true)[condition]
        except:
            self.original_schooldefault = None
        self.original_name = self.name
        self.original_code = self.code
        self.original_abbrev = self.abbrev
        self.original_article = self.article
        self.original_dep_list = self.dep_list
        self.original_locked = self.locked

    def save(self, *args, **kwargs):  #PR2018-08-20 called by school.save(self.request) in SchoolEditView.form_valid
        self.request = kwargs.pop('request', None)

    # Check if data has changed. If so: save object
        if self.data_has_changed():
            self.modified_by = self.request.user
            self.modified_at = timezone.now()
            self.mode = ('c', 'u')[self.is_update]  # result = (on_false, on_true)[condition]
            # when adding record: self.id=None, set force_insert=True; otherwise: set force_update=True PR2018-06-09
            super(School, self).save(force_insert = not self.is_update, force_update = self.is_update, **kwargs)
            self.save_to_log()

    def delete(self, *args, **kwargs):
        self.modified_at = timezone.now()
        self.mode = 'd'
        # First save to logfile
        self.save_to_log()
        # then delete record
        super(School, self).delete(*args, **kwargs)

    def save_to_log(self):
        # Create method also saves record
        School_log.objects.create(
            school_id=self.id,  # self.id gets its value in super(School, self).save

            examyear=self.examyear,
            schooldefault=self.schooldefault,

            name=self.name,
            code=self.code,
            abbrev=self.abbrev,
            article=self.article,
            dep_list=self.dep_list,
            locked=self.locked,

            examyear_mod=self.examyear_mod,
            schooldefault_mod=self.schooldefault_mod,
            name_mod=self.name_mod,
            code_mod=self.code_mod,
            abbrev_mod=self.abbrev_mod,
            article_mod=self.article_mod,
            dep_list_mod=self.dep_list_mod,
            locked_mod=self.locked_mod,

            mode=self.mode,
            modified_by=self.modified_by,
            modified_at=self.modified_at
        )

    def data_has_changed(self):
        # returns True when the value of one or more fields has changed PR2018-08-26
        self.is_update = self.id is not None # self.id is None before new record is saved
        self.examyear_mod = self.original_examyear != self.examyear
        self.schooldefault_mod = self.original_schooldefault != self.schooldefault
        self.name_mod = self.original_name != self.name
        self.code_mod = self.original_code != self.code
        self.abbrev_mod = self.original_abbrev != self.abbrev
        self.article_mod = self.original_article != self.article
        self.dep_list_mod = self.original_dep_list != self.dep_list
        self.locked_mod = self.original_locked != self.locked

        return not self.is_update or \
               self.examyear_mod or \
               self.schooldefault_mod or \
               self.name_mod or \
               self.code_mod or \
               self.abbrev_mod  or \
               self.article_mod or \
               self.dep_list_mod or \
               self.locked_mod

    @property
    def dep_list_tuple(self):
        return get_list_tuple(self.dep_list)

    @property
    def locked_str(self):
        return c.LOCKED_DICT.get(int(self.locked))

class School_log(Model):
    objects = CustomManager()

    school_id = IntegerField(db_index=True)

    examyear = ForeignKey(Examyear, null=True, related_name='+', on_delete=PROTECT)
    schooldefault = ForeignKey(Schooldefault, null=True, related_name='+', on_delete=PROTECT)
    name = CharField(max_length=50,null=True)
    code = CharField(max_length=12,null=True)
    abbrev = CharField(max_length=20,null=True)
    article = CharField(max_length=3, null=True)
    dep_list = CharField(max_length=20, null=True)
    is_template = BooleanField(default=False)  # default School of this country and examyear PR2018-08-23
    locked =  BooleanField(default=False)

    examyear_mod = BooleanField(default=False)
    schooldefault_mod = BooleanField(default=False)
    name_mod = BooleanField(default=False)
    code_mod = BooleanField(default=False)
    abbrev_mod = BooleanField(default=False)
    article_mod = BooleanField(default=False)
    dep_list_mod = BooleanField(default=False)
    is_template_mod =  BooleanField(default=False)
    locked_mod =  BooleanField(default=False)

    mode = CharField(max_length=1, null=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    def __str__(self):
        return self.name

    @property
    def locked_str(self):
        return c.LOCKED_DICT.get(int(self.locked))

    @property
    def mode_str(self):
        mode_str = '-'
        if self.mode is not None:
            mode_str = c.MODE_DICT.get(str(self.mode))
        return mode_str


# PR2018-06-07
class Entrylist(Model):
    school = ForeignKey(School, related_name='+', on_delete=CASCADE)
    key_id = IntegerField(db_index=True, default=0)
    char01 = CharField(max_length=255, null=True)
    char02 = CharField(max_length=255, null=True)
    int01 = IntegerField(null=True)
    int02 = IntegerField(null=True)
    bool01 = BooleanField(default=False)
    bool02 = BooleanField(default=False)
    date01 = DateTimeField(null=True)
    date02 = DateTimeField(null=True)


# PR2018-05-06
class SchoolSettings(Model):
    school = ForeignKey(School, related_name='schoolsettings', on_delete=CASCADE)
    key_id = IntegerField(db_index=True, default=0)
    char01 = CharField(max_length=255, null=True)
    char02 = CharField(max_length=255, null=True)
    int01 = IntegerField(null=True)
    int02 = IntegerField(null=True)
    bool01 = BooleanField(default=False)
    bool02 = BooleanField(default=False)
    date01 = DateTimeField(null=True)
    date02 = DateTimeField(null=True)


