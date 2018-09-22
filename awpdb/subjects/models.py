# PR2018-07-20
from django.db.models import Model, Manager, ForeignKey, PROTECT, CASCADE, SET_NULL
from django.db.models import CharField, IntegerField, PositiveSmallIntegerField, BooleanField, DateTimeField, DateField
from django.core.validators import MaxValueValidator
from django.utils import timezone
# from django.core.exceptions import ObjectDoesNotExist, ValidationError, NON_FIELD_ERRORS
# PR2018-05-05 use AUTH_USER_MODEL
#from django.contrib.auth.models import User
#from accounts.models import User
from django.utils.translation import ugettext_lazy as _

from awpdb.settings import AUTH_USER_MODEL
from schools.models import Country, Examyear, Department, School
from awpdb import constants as c

import logging
logger = logging.getLogger(__name__)

# PR2018-04-22: backup: (venv) C:\dev\awpr\awpr>py -3 manage.py dumpdata schools --format json --indent 4 > schools/backup/schools.json
#               restore: (venv) C:\dev\awpr\awpr>py -3 manage.py loaddata schools/backup/schools.json

# clean() method rus to_python(), validate(), and run_validators() and propagates their errors.
# If, at any time, any of the methods raise ValidationError, the validation stops and that error is raised.
# This method returns the clean data, which is then inserted into the cleaned_data dictionary of the form.


# PR2018-07-20 from https://stackoverflow.com/questions/3090302/how-do-i-get-the-object-if-it-exists-or-none-if-it-does-not-exist
# CustomManager adds function get_or_none. Used in  Subjectdefault to prevent DoesNotExist exception
class CustomManager(Manager):
    def get_or_none(self, **kwargs):
        try:
            # logger.debug('get_or_none self=<' + str(self) + '>')
            return self.get(**kwargs)
        except self.DoesNotExist:
            # logger.debug('get_or_none self.DoesNotExist=<' + str(self.DoesNotExist) + '>')
            return None



# === Level =====================================
class Level(Model): # PR2018-08-12
    country = ForeignKey(Country, related_name='levels', on_delete=PROTECT)
    name = CharField(max_length=50, # PR2018-08-06 set Unique per Country True.
        help_text=_('Required. {} characters or fewer.'.format('50')),)
    abbrev = CharField(max_length=8, # PR2018-08-06 set Unique per Country True.
        help_text=_('Required. {} characters or fewer.'.format('8')),)
    sequence = PositiveSmallIntegerField(default=1)
    dep_list = CharField(max_length=20, null=True)
    is_active = BooleanField(default=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    class Meta:
        ordering = ['sequence',]

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(Level, self).__init__(*args, **kwargs)
        # private variable __original checks if data_has_changed, to prevent update record when no changes are made.
        # Otherwise a logrecord is created every time the save button is clicked without changes
        try:
            self.original_country = self.country  # result = (on_false, on_true)[condition]
            # logger.debug('class Level(Model) __init__ self.original_country: ' + str(self.original_country))
        except:
            self.original_country = None
        self.original_name = self.name
        self.original_abbrev = self.abbrev
        self.original_sequence = self.sequence
        self.original_dep_list = self.dep_list
        self.original_is_active = self.is_active

    def save(self, *args, **kwargs):  # called by subjectdefault.save(self.request) in SubjectdefaultEditView.form_valid
        self.request = kwargs.pop('request', None)
        # logger.debug('Level(Model) save self.request ' + str(self.request) + ' Type: ' + str(type(self.request)))

        # Override the save() method of the model to perform validation on every save.
        # https://stackoverflow.com/questions/14470585/how-to-validate-uniqueness-constraint-across-foreign-key-django?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
        # self.full_clean()

    # check if data has changed. If so: save object
        if self.data_has_changed():
            #logger.debug('Level(Model) save self.data_has_changed')
            self.modified_by = self.request.user
            # timezone.now() is timezone aware, based on the USE_TZ setting; datetime.now() is timezone naive. PR2018-06-07
            self.modified_at = timezone.now()
            self.mode = ('c', 'u')[self.is_update]  # result = (on_false, on_true)[condition]
            # logger.debug('Level(Model) save self.mode ' + str(self.mode) + ' Type: ' + str(type(self.mode)))

            # when adding record: self.id=None, set force_insert=True; otherwise: set force_update=True PR2018-06-09
            super(Level, self).save(force_insert = not self.is_update, force_update = self.is_update, **kwargs)
            # self.id gets its value in super(Country, self).save
            self.save_to_log()

    def delete(self, *args, **kwargs):
        self.modified_at = timezone.now()
        self.mode = 'd'
        self.data_has_changed()
        # First save to logfile
        self.save_to_log()
        # then delete record
        super(Level, self).delete(*args, **kwargs)

    def save_to_log(self):  # PR2018-08-27
        # Create method also saves record
        Level_log.objects.create(
            level_id=self.id,  # self.id gets its value in super(Level, self).save

            country=self.country,
            name=self.name,
            abbrev=self.abbrev,
            sequence=self.sequence,
            dep_list=self.dep_list,
            is_active=self.is_active,

            country_mod=self.country_mod,
            name_mod=self.name_mod,
            abbrev_mod=self.abbrev_mod,
            sequence_mod=self.sequence_mod,
            dep_list_mod=self.dep_list_mod,
            is_active_mod=self.is_active_mod,

            mode=self.mode,
            modified_by=self.modified_by,
            modified_at=self.modified_at
        )

    def data_has_changed(self):  # PR2018-07-21 # PR2018-08-24
        # returns True when the value of one or more fields has changed PR2018-08-26
        self.is_update = self.id is not None # self.id is None before new record is saved
        self.country_mod = self.original_country != self.country
        self.name_mod = self.original_name != self.name
        self.abbrev_mod = self.original_abbrev != self.abbrev
        self.sequence_mod = self.original_sequence != self.sequence
        self.dep_list_mod = self.original_dep_list != self.dep_list
        self.is_active_mod = self.original_is_active != self.is_active

        return not self.is_update or \
               self.country_mod or \
               self.name_mod or \
               self.abbrev_mod or \
               self.sequence_mod or \
               self.dep_list_mod or \
               self.is_active_mod

    @property  # PR2018-08-11
    def has_no_linked_data(self):
        linked_items_count = Scheme.objects.filter(level_id=self.pk).count()
        # logger.debug('SubjectDefault Model has_no_linked_data linked_items_count: ' + str(linked_items_count))
        return not bool(linked_items_count)

    @property
    def dep_list_str(self): # PR108-08-27
        return Department.dep_list_str(self.dep_list)

    @property
    def dep_list_tuple(self):
        # dep_list_tuple is called bij LevelEditForm, SectorEditForm, SchemeEditForm, SubjectdefaultEditForm
        return get_dep_list_tuple(self.dep_list)

    @property
    def is_active_str(self): # PR108-08-09
        return c.IS_ACTIVE_DICT.get(self.is_active, '')

    @property
    def is_active_choices(self): # PR108-06-22
        return c.IS_ACTIVE_DICT.get(self.is_active, '')

#  ++++++++++  Class methods  +++++++++++++++++++++++++++
    """
    @classmethod
    def level_list_choices(cls, user_country=None, skip_none=False):
        # PR2018-08-16 function creates list of level_list: [(0, 'None'), (1, 'PBL'), (2, 'PKL'), (3, 'TKL')], filter by Country

        # choises must be tuple or list, dictionary gives error: 'int' object is not iterable
        _choices = []
        if user_country:
            if not skip_none:
                _choices = [(0, 'None')]
            levels = cls.objects.filter(country=user_country)
            for level in levels:
                if level:
                    item = (level.id, level.abbrev)
                    _choices.append(item)
        return _choices


    @classmethod
    def level_list_choices(cls, user_country=None, cur_level_id = None, skip_none=False):
        # PR2018-08-16 function creates list of level_list: [(0, 'None'), (1, 'PBL'), (2, 'PKL'), (3, 'TKL')]
        # filter by user_country
        # add inactive records only when it is current record (otherwise it will not display in field) PR2018-08-24

        # choises must be tuple or list, dictionary gives error: 'int' object is not iterable
        # level_list_choices: [(0, 'None'), (1, 'PKL'), (2, 'PBL'), (3, 'TKL')]
        _choices = []
        if user_country:
            if not skip_none:
                _choices = [(None, '---')]
            levels = cls.objects.filter(country=user_country)
            for item in levels:
                if item:
                    if item.is_active:
                        display = item.name + ' - ' + item.country.name
                        item = (item.id, display )
                        _choices.append(item)
                    else:
                        display = item.name + ' - ' + item.country.name + ' - INACTIVE'
                        item = (item.id, display )
                        _choices.append(item)
        # logger.debug('Level(Model) level_list_choices = ' + str(_choices))
        return _choices
    """

    @classmethod
    def level_list_choices(cls, user_country=None, user_dep=None, init_list_str=None, skip_none=False):
        # PR2018-08-29 function is used in SchemeAddForm, SchemeEditForm
        # filter by user_dep (user_country is Foreignkey of user_dep)
        # add records not in user_dep only when it is current record (otherwise it will not display in field) PR2018-08-24
        # choises must be tuple or list, dictionary gives error: 'int' object is not iterable
        # dep_list_choices: [(0, 'None'), (1, 'Vsbo'), (2, 'Havo'), (3, 'Vwo')]
        # IN USE?? dep_list_choices_tuple: ((0, 'None'), (1, 'Vsbo'), (2, 'Havo'), (3, 'Vwo')), filter by Country
        #logger.debug('DepartmentModel dep_list_choices init_list_str: <' + str(init_list_str) + '> Type: ' + str(type(init_list_str)))

        logger.debug('Level(Model) level_list_choices user_country: ' + str(user_country))
        logger.debug('Level(Model) __init__ user_dep: ' + str(user_dep))

        choices = []
        if user_country:
            # add row 'None' at the start, only if not skip_none
            if not skip_none:
                choices = [(0, '---')]

            # PR2018-08-28 init_list is the dep_list of the current user. Inactive items that are in the init_list will still be shown
            init_list_tuple = ()
            if init_list_str:
                # This function converts init_list_str string into init_list_tuple,  e.g.: '1;2' will be converted to (1,2)
                init_list_list = init_list_str.split(';')
                init_list_tuple = tuple(init_list_list)

            # wrap dep_id in delimiters, so ';1;' can be searched in ";1;15;6;'
            if user_dep:
                user_dep_id_str = ';' + str(user_dep.id) + ";"
                # iterate through level rows, filtered by country
                # levels = cls.objects.filter(dep_list__contains=';12;')
                levels = cls.objects.filter(country=user_country, dep_list__contains=user_dep_id_str)
            else:
                levels = cls.objects.filter(country=user_country)

            for level in levels:
                if level:
                    # check if level must be added to list:
                    # - all active levels are added
                    # - inactive levels are only added when they are in init_list_str
                    show_item = False
                    if level.is_active:
                        show_item = True
                    else:
                        # do show inactive items when they are in init_list
                        if init_list_tuple:
                            for list_item in init_list_tuple:
                                #logger.debug(' dep_list_choices list_item: ' + str(list_item))
                                if int(list_item) == level.id:
                                    show_item = True
                                    break
                    # add level to list
                    if show_item:
                        # TODO  country.name is for testing only
                        display = level.abbrev + ' ' + level.country.name
                        # display INACTIVE when level is inactive
                        if not level.is_active:
                            display += ' (inactive)'
                        # TODO  level.dep_list is for testing only
                        if level.dep_list:  # for testing only
                            display += ' ' + level.dep_list
                        level = (level.id, display )
                        choices.append(level)
        #logger.debug('dep_list_choices choices = ' + str(choices))
        return choices

# PR2018-08-12
class Level_log(Model):
    level_id = IntegerField(db_index=True)

    country = ForeignKey(Country, null=True, related_name='+', on_delete=PROTECT)
    name = CharField(max_length=50, null=True)
    abbrev = CharField(max_length=8, null=True)
    sequence = PositiveSmallIntegerField(null=True)
    dep_list = CharField(max_length=20, null=True)
    is_active = BooleanField(default=True)

    country_mod = BooleanField(default=False)
    name_mod = BooleanField(default=False)
    abbrev_mod = BooleanField(default=False)
    sequence_mod = BooleanField(default=False)
    dep_list_mod = BooleanField(default=False)
    is_active_mod = BooleanField(default=False)

    mode = CharField(max_length=1, null=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    @property
    def dep_list_str(self): # PR108-08-27
        return Department.dep_list_str(self.dep_list)

    @property
    def mode_str(self):
        return c.MODE_DICT.get(str(self.mode),'-')

# PR2018-06-06
class Sector(Model):
    country = ForeignKey(Country, related_name='sectors', on_delete=PROTECT)
    name = CharField(max_length=50)
    abbrev = CharField(max_length=8)
    sequence = PositiveSmallIntegerField(default=1)
    dep_list = CharField(max_length=20, null=True)
    is_active = BooleanField(default=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    class Meta:
        ordering = ['sequence',]

    def __str__(self):
        return self.abbrev

    def __init__(self, *args, **kwargs):
        super(Sector, self).__init__(*args, **kwargs)

        # private variable __original checks if data_has_changed, to prevent update record when no changes are made.
        # Otherwise a logrecord is created every time the save button is clicked without changes
        try:
            self.original_country = self.country  # result = (on_false, on_true)[condition]
            # logger.debug('class Level(Model) __init__ self.original_country: ' + str(self.original_country))
        except:
            self.original_country = None
        self.original_name = self.name
        self.original_abbrev = self.abbrev
        self.original_sequence = self.sequence
        self.original_dep_list = self.dep_list
        self.original_is_active = self.is_active

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
            # logger.debug('Sector(Model) save self.mode ' + str(self.mode) + ' Type: ' + str(type(self.mode)))

            # when adding record: self.id=None, set force_insert=True; otherwise: set force_update=True PR2018-06-09
            super(Sector, self).save(force_insert = not self.is_update, force_update = self.is_update, **kwargs)
            # self.id gets its value in super(Country, self).save
            self.save_to_log()

    def delete(self, *args, **kwargs):
        self.modified_at = timezone.now()
        self.mode = 'd'
        self.data_has_changed()
        # First save to logfile
        self.save_to_log()
        # then delete record
        super(Sector, self).delete(*args, **kwargs)

    def save_to_log(self, *args, **kwargs):
        # Create method also saves record
        Sector_log.objects.create(
            sector_id=self.id,

            country=self.country,
            name=self.name,
            abbrev=self.abbrev,
            sequence=self.sequence,
            dep_list=self.dep_list,
            is_active=self.is_active,

            country_mod=self.country_mod,
            name_mod=self.name_mod,
            abbrev_mod=self.abbrev_mod,
            sequence_mod=self.sequence_mod,
            dep_list_mod=self.dep_list_mod,
            is_active_mod=self.is_active_mod,

            mode=self.mode,
            modified_by=self.modified_by,
            modified_at=self.modified_at
        )

    def data_has_changed(self): # PR2018-07-21
        # returns True when the value of one or more fields has changed PR2018-08-26
        self.is_update = self.id is not None # self.id is None before new record is saved
        self.country_mod = self.original_country != self.country
        self.name_mod = self.original_name != self.name
        self.abbrev_mod = self.original_abbrev != self.abbrev
        self.sequence_mod = self.original_sequence != self.sequence
        self.dep_list_mod = self.original_dep_list != self.dep_list
        self.is_active_mod = self.original_is_active != self.is_active
        return not self.is_update or \
               self.country_mod or \
               self.name_mod or \
               self.abbrev_mod or \
               self.sequence_mod or \
               self.dep_list_mod or \
               self.is_active_mod

    @property  # PR2018-08-11
    def has_no_linked_data(self):
        linked_items_count = Scheme.objects.filter(sector_id=self.pk).count()
        # logger.debug('SubjectDefault Model has_no_linked_data linked_items_count: ' + str(linked_items_count))
        return not bool(linked_items_count)

    @property
    def dep_list_str(self): # PR108-08-27
        return Department.dep_list_str(self.dep_list)

    @property
    def dep_list_tuple(self):
        # dep_list_tuple is called bij LevelEditForm, SectorEditForm, SchemeEditForm, SubjectdefaultEditForm
        return get_dep_list_tuple(self.dep_list)

    @property
    def is_active_str(self): # PR108-08-09
        return c.IS_ACTIVE_DICT.get(self.is_active, '')

    @property
    def is_active_choices(self): # PR108-06-22
        return c.IS_ACTIVE_DICT.get(self.is_active, '')

#  ++++++++++  Class methods  +++++++++++++++++++++++++++
    @classmethod
    def sector_list_choices(cls, user_country=None, user_dep=None, init_list_str=None, skip_none=False):
        # PR2018-08-29 function is used in SchemeAddForm, SchemeEditForm
        # filter by user_dep (user_country is Foreignkey of user_dep)
        # add records not in user_dep only when it is current record (otherwise it will not display in field) PR2018-08-24
        # choises must be tuple or list, dictionary gives error: 'int' object is not iterable
        # dep_list_choices: [(0, 'None'), (1, 'Vsbo'), (2, 'Havo'), (3, 'Vwo')]
        # IN USE?? dep_list_choices_tuple: ((0, 'None'), (1, 'Vsbo'), (2, 'Havo'), (3, 'Vwo')), filter by Country
        #logger.debug('DepartmentModel dep_list_choices init_list_str: <' + str(init_list_str) + '> Type: ' + str(type(init_list_str)))

        logger.debug('Sector(Model) level_list_choices user_country: ' + str(user_country))
        logger.debug('Sector(Model) __init__ user_dep: ' + str(user_dep))

        choices = []
        if user_country:
            # add row 'None' at the start, only if not skip_none
            if not skip_none:
                choices = [(0, '---')]

            # PR2018-08-28 init_list is the dep_list of the current user. Inactive items that are in the init_list will still be shown
            init_list_tuple = ()
            if init_list_str:
                # This function converts init_list_str string into init_list_tuple,  e.g.: '1;2' will be converted to (1,2)
                init_list_list = init_list_str.split(';')
                init_list_tuple = tuple(init_list_list)

            # wrap dep_id in delimiters, so ';1;' can be searched in ";1;15;6;'
            user_dep_id_str = ';' + str(user_dep.id) + ";"

            # iterate through sector rows, filtered by country
            # sectors = cls.objects.filter(dep_list__contains=';12;')
            sectors = cls.objects.filter(country=user_country, dep_list__contains=user_dep_id_str)
            for sector in sectors:
                if sector:
                    # check if sector must be added to list:
                    # - all active sectors are added
                    # - inactive sectors are only added when they are in init_list_str
                    show_item = False
                    if sector.is_active:
                        show_item = True
                    else:
                        # do show inactive items when they are in init_list
                        if init_list_tuple:
                            for list_item in init_list_tuple:
                                #logger.debug(' dep_list_choices list_item: ' + str(list_item))
                                if int(list_item) == sector.id:
                                    show_item = True
                                    break
                    # add sector to list
                    if show_item:
                        display = sector.abbrev + ' ' + sector.country.name + ' ' + sector.dep_list
                        # display INACTIVE when sector is inactive
                        if not sector.is_active:
                            display += ' (inactive)'
                        sector = (sector.id, display )
                        choices.append(sector)
        #logger.debug('dep_list_choices choices = ' + str(choices))
        return choices


# PR2018-06-06
class Sector_log(Model):
    sector_id = IntegerField(db_index=True)

    country = ForeignKey(Country, null=True, related_name='+', on_delete=PROTECT)
    name = CharField(max_length=50, null=True)
    abbrev = CharField(max_length=8, null=True)
    sequence = PositiveSmallIntegerField(null=True)
    dep_list = CharField(max_length=20, null=True)
    is_active = BooleanField(default=True)

    country_mod = BooleanField(default=False)
    name_mod = BooleanField(default=False)
    abbrev_mod = BooleanField(default=False)
    dep_list_mod = BooleanField(default=False)
    sequence_mod = BooleanField(default=False)
    is_active_mod = BooleanField(default=False)

    mode = CharField(max_length=1, null=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    @property
    def dep_list_str(self): # PR108-08-27
        return Department.dep_list_str(self.dep_list)

    @property
    def mode_str(self):
        return c.MODE_DICT.get(str(self.mode),'-')


# PR2018-06-06
class Character(Model):
    department = ForeignKey(Department, related_name='characters', on_delete=CASCADE)
    name = CharField(max_length=50)
    abbrev = CharField(db_index=True,max_length=8)
    short = CharField(max_length=20)
    is_active = BooleanField(default=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    def __str__(self):
        return self.abbrev

class Character_log(Model):
    character_id = IntegerField(db_index=True)
    department = ForeignKey(Department, null=True, related_name='+', on_delete=CASCADE)
    department_mod = BooleanField(default=False)
    name = CharField(max_length=50, null=True)
    name_mod = BooleanField(default=False)
    abbrev = CharField(max_length=8,null=True)
    abbrev_mod = BooleanField(default=False)
    short = CharField(max_length=20, null=True)
    short_mod = BooleanField(default=False)
    is_active = BooleanField(default=True)
    is_active_mod = BooleanField(default=False)
    mode = CharField(max_length=1, null=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()


# PR2018-06-06 There is one Scheme per department/level/sector per year per country
class Scheme(Model):  # PR2018-09-07
    examyear = ForeignKey(Examyear, related_name='schemes', on_delete=PROTECT)
    department = ForeignKey(Department, related_name='schemes', on_delete=PROTECT)
    level = ForeignKey(Level, related_name='schemes', on_delete=PROTECT)
    sector = ForeignKey(Sector, related_name='schemes', on_delete=PROTECT)
    name = CharField(max_length=50, # set Unique per examyear True.
        help_text=_('Required. {} characters or fewer.'.format('50')),)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    class Meta:
        ordering = ['name',]

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(Scheme, self).__init__(*args, **kwargs)
        try:
            self.original_examyear = self.examyear
            self.original_department = self.department
            self.original_level = self.level
            self.original_sector = self.sector
        except:
            self.original_examyear = None
            self.original_department = None
            self.original_level = None
            self.original_sector = None
        self.original_name = self.name

    def save(self, *args, **kwargs):  # called by subjectdefault.save(self.request) in SubjectdefaultEditView.form_valid
        self.request = kwargs.pop('request', None)

        if self.data_has_changed():
            self.modified_by = self.request.user
            self.modified_at = timezone.now()
            self.mode = ('c', 'u')[self.is_update]

            super(Scheme, self).save(force_insert = not self.is_update, force_update = self.is_update, **kwargs)
            self.save_to_log()

    def delete(self, *args, **kwargs):
        self.modified_at = timezone.now()
        self.mode = 'd'
        self.data_has_changed()
        # First save to logfile
        self.save_to_log()
        # then delete record
        super(Scheme, self).delete(*args, **kwargs)

    def save_to_log(self):  # PR2018-08-27
        # Create method also saves record
        Scheme_log.objects.create(
            scheme_id=self.id,  # self.id gets its value in super(Level, self).save

            examyear=self.examyear,
            department=self.department,
            level=self.level,
            sector=self.sector,
            name=self.name,

            examyear_mod=self.examyear_mod,
            department_mod=self.department_mod,
            level_mod=self.level_mod,
            sector_mod=self.sector_mod,
            name_mod=self.name_mod,

            mode=self.mode,
            modified_by=self.modified_by,
            modified_at=self.modified_at
        )

        def data_has_changed(self):  # PR2018-09-07
            # returns True when the value of one or more fields has changed
            self.is_update = self.id is not None  # self.id is None before new record is saved
            self.examyear_mod = self.original_examyear != self.examyear  # result = (on_false, on_true)[condition]
            self.department_mod = self.original_department != self.department
            self.level_mod = self.original_level != self.level
            self.sector_mod = self.original_sector != self.sector
            self.name_mod = self.original_name != self.name

            return not self.is_update or \
                   self.examyear_mod or \
                   self.department_mod or \
                   self.level_mod or \
                   self.sector_mod or \
                   self.name_mod

    @property  # PR2018-08-11
    def has_no_linked_data(self):
        linked_items_count = Scheme.objects.filter(level_id=self.pk).count()
        # logger.debug('SubjectDefault Model has_no_linked_data linked_items_count: ' + str(linked_items_count))
        return not bool(linked_items_count)

class Scheme_log(Model):
    scheme_id = IntegerField(db_index=True)

    examyear = ForeignKey(Examyear, related_name='+', on_delete=PROTECT)
    department = ForeignKey(Department, null=True, related_name='+', on_delete=PROTECT)
    level = ForeignKey(Level, null=True, related_name='+', on_delete=PROTECT)
    sector = ForeignKey(Sector, null=True, related_name='+', on_delete=PROTECT)
    name = CharField(max_length=50, null=True)

    examyear_mod = BooleanField(default=False)
    department_mod = BooleanField(default=False)
    level_mod = BooleanField(default=False)
    sector_mod = BooleanField(default=False)
    name_mod = BooleanField(default=False)

    mode = CharField(max_length=1, null=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()


# ===  Subjectdefault Model =====================================
# PR2018-06-05 Subject is the base Model of all subjects
class Subjectdefault(Model):
    # CustomManager adds function get_or_none. Used in  Subjectdefault to prevent DoesNotExist exception
    objects = CustomManager()

    country = ForeignKey(Country, related_name='subjectdefaults', on_delete=PROTECT)

    name = CharField(max_length=50, # PR2018-08-06 set Unique per Country True. Was: unique=True,
        help_text=_('Required. {} characters or fewer.'.format('50')),)
    abbrev = CharField(max_length=10, # PR2018-08-06 set Unique per Country True. Was: unique=True,
        help_text=_('Required. {} characters or fewer.'.format('10')),)
    sequence = PositiveSmallIntegerField(default=9999,
        help_text=_('Sets subject sequence in reports. Required. Maximum value is {}.'.format(9999)),
        validators=[MaxValueValidator(9999),],
        error_messages={'max_value': _('Value must be less or equal to {}.'.format(9999))})
    dep_list = CharField(max_length=20, null=True)
    is_active = BooleanField(default=True)

    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    class Meta:
        ordering = ['sequence',]

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(Subjectdefault, self).__init__(*args, **kwargs)

        # private variable __original checks if data_has_changed, to prevent update record when no changes are made.
        # Otherwise a logrecord is created every time the save button is clicked without changes
        try:
            self.original_country = self.country  # result = (on_false, on_true)[condition]
            # logger.debug('class Subjectdefault(Model) __init__ self.original_country: ' + str(self.original_country))
        except:
            self.original_country = None
        self.original_name = self.name
        self.original_abbrev = self.abbrev
        self.original_sequence = self.sequence
        self.original_dep_list = self.dep_list
        self.original_is_active = self.is_active

    def save(self, *args, **kwargs):  # called by subjectdefault.save(self.request) in SubjectdefaultEditView.form_valid
        self.request = kwargs.pop('request', None)

        # Override the save() method of the model to perform validation on every save.
        # https://stackoverflow.com/questions/14470585/how-to-validate-uniqueness-constraint-across-foreign-key-django?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
        # self.full_clean()

    # check if data has changed. If so: save object
        if self.data_has_changed():
            self.modified_by = self.request.user
            self.modified_at = timezone.now()  # timezone.now() is timezone aware; datetime.now() is timezone naive.
            self.mode = ('c', 'u')[self.is_update]  # result = (on_false, on_true)[condition]
            # when adding record: self.id=None, set force_insert=True; otherwise: set force_update=True PR2018-06-09
            super(Subjectdefault, self).save(force_insert = not self.is_update, force_update = self.is_update, **kwargs)
            # self.id gets its value in super(Country, self).save
            self.save_to_log()

    def delete(self, *args, **kwargs):
        self.modified_at = timezone.now()
        self.mode = 'd'
        self.data_has_changed()
        # First save to logfile
        self.save_to_log()
        # then delete record
        super(Subjectdefault, self).delete(*args, **kwargs)

    def save_to_log(self): # PR2018-08-29
        # Create method also saves record
        Subjectdefault_log.objects.create(
            subjectdefault_id=self.id,

            country=self.country,
            name=self.name,
            abbrev=self.abbrev,
            sequence=self.sequence,
            dep_list = self.dep_list,
            is_active = self.is_active,

            country_mod=self.country_mod,
            name_mod=self.name_mod,
            abbrev_mod=self.abbrev_mod,
            sequence_mod=self.sequence_mod,
            dep_list_mod=self.dep_list_mod,
            is_active_mod = self.is_active_mod,

            mode=self.mode,
            modified_by=self.modified_by,
            modified_at=self.modified_at
        )

    def data_has_changed(self): # PR2018-08-29
        # returns True when the value of one or more fields has changed PR2018-08-26
        self.is_update = self.id is not None # self.id is None before new record is saved
        self.country_mod = self.original_country != self.country
        self.name_mod = self.original_name != self.name
        self.abbrev_mod = self.original_abbrev != self.abbrev
        self.sequence_mod = self.original_sequence != self.sequence
        self.dep_list_mod = self.original_dep_list != self.dep_list
        self.is_active_mod = self.original_is_active != self.is_active

        return not self.is_update or \
               self.country_mod or \
               self.name_mod or \
               self.abbrev_mod or \
               self.sequence_mod or \
               self.dep_list_mod or \
               self.is_active_mod

    @property  # PR2018-07-19
    def has_no_linked_data(self):
        linked_items_count = Subject.objects.filter(subjectdefault_id=self.pk).count()
        # logger.debug('SubjectDefault Model has_no_linked_data linked_items_count: ' + str(linked_items_count))
        return not bool(linked_items_count)

    @property
    def dep_list_str(self): # PR108-08-16
        _list_str = get_list_str(self.dep_list, 'Department')
        return _list_str

    @property
    def dep_list_tuple(self):  # PR2018-08-15
        # e.g.: dep_list='1;2' will be converted to tuple=(1,2)
        # empty list = (0,), e.g: 'None'
        _list_str = str(self.dep_list)
        # logger.debug('Level(Model) dep_list_tuple _list_str=<' + str(_list_str) + '>')
        if _list_str:
            try:
                _list_split = _list_str.split(';')
                # logger.debug('Level(Model) dep_list_tuple dep_list_split=<' + str(dep_list_split) + '>')
                _list_tuple = tuple(_list_split)
                # logger.debug('Level(Model) dep_list_tuple _dep_list_tuple=<' + str(_dep_list_tuple) + '>')
            except:
                _list_tuple = ('0',)
            if not bool(_list_tuple):
                _list_tuple = ('0',)
        else:
            _list_tuple = ('0',)
        # logger.debug('Level(Model) dep_list_tuple _dep_list_tuple=#' + str(_dep_list_tuple) + '#')
        return _list_tuple

    @property
    def is_active_str(self): # PR108-08-09
        return c.IS_ACTIVE_DICT.get(self.is_active,'')

    @property
    def is_active_choices(self): # PR108-06-22
        return c.IS_ACTIVE_DICT.get(self.is_active, '')


# PR2018-06-05 Subject is the base Model of all subjects
class Subjectdefault_log(Model):
    subjectdefault_id = IntegerField(db_index=True)
    country = ForeignKey(Country, null=True, related_name='+', on_delete=PROTECT)
    name = CharField(max_length=50, null=True)
    abbrev = CharField(max_length=10, null=True)
    sequence = PositiveSmallIntegerField()
    dep_list = CharField(max_length=20, null=True)
    is_active = BooleanField(default=True)

    country_mod = BooleanField(default=False)
    name_mod = BooleanField(default=False)
    abbrev_mod = BooleanField(default=False)
    sequence_mod = BooleanField(default=False)
    dep_list_mod = BooleanField(default=False)
    is_active_mod = BooleanField(default=False)

    mode = CharField(max_length=1, null=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    @property
    def dep_list_str(self): # PR108-08-16
        return get_list_str(self.dep_list, 'Department')

    @property
    def is_active_str(self):
        return c.IS_ACTIVE_DICT.get(self.is_active,'')

    @property
    def mode_str(self):
        return c.MODE_DICT.get(str(self.mode),'-')

# =============  Subject Model  =====================================
class Subject(Model):
    # PR2018-06-05 Subject has one subject per examyear per country
    # Subject has no country field: country is a field in examyear

    examyear = ForeignKey(Examyear, related_name='subjects', on_delete=PROTECT)
    subjectdefault = ForeignKey(Subjectdefault, related_name='subjects', on_delete=PROTECT)

    name = CharField(max_length=50, # PR2018-08-08 set Unique per Examyear True.
        help_text=_('Required. {} characters or fewer.'.format('50')),)
    abbrev = CharField(max_length=10, # PR2018-08-08 set Unique per Examyear True. Was: unique=True,
        help_text=_('Required. {} characters or fewer.'.format('10')),)
    sequence = PositiveSmallIntegerField(default=9999,
        help_text=_('Sets subject sequence in reports. Required. Maximum value is {}.'.format(9999)),
        validators=[MaxValueValidator(9999),],
        error_messages={'max_value': _('Value must be less or equal to {}.'.format(9999))})
    dep_list = CharField(max_length=20, null=True)
    is_active = BooleanField(default=True)

    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    class Meta:
        ordering = ['sequence',]

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(Subject, self).__init__(*args, **kwargs)

        # private variable __original checks if data_has_changed, to prevent update record when no changes are made.
        # Otherwise a logrecord is created every time the save button is clicked without changes
        try:
            self.original_examyear = self.examyear  # result = (on_false, on_true)[condition]
        except:
            self.original_examyear = None
        try:
            self.original_subjectdefault = self.subjectdefault  # result = (on_false, on_true)[condition]
        except:
            self.original_subjectdefault = None
        self.original_name = self.name
        self.original_abbrev = self.abbrev
        self.original_sequence = (None, self.sequence)[bool(self.sequence)]  # result = (on_false, on_true)[condition]
        self.original_dep_list = self.dep_list
        self.original_is_active = self.is_active

    def save(self, *args, **kwargs):  # called by subject.save(self.request) in SubjectEditView.form_valid
        self.request = kwargs.pop('request', None)

    # check if data has changed. If so: save object
        if self.data_has_changed():
            self.modified_by = self.request.user
            self.modified_at = timezone.now()  # timezone.now() is timezone aware; datetime.now() is timezone naive.
            self.mode = ('c', 'u')[self.is_update]  # result = (on_false, on_true)[condition]
            # when adding record: self.id=None, set force_insert=True; otherwise: set force_update=True PR2018-06-09
            super(Subject, self).save(force_insert = not self.is_update, force_update = self.is_update, **kwargs)
            self.save_to_log()

    def delete(self, *args, **kwargs):
        self.modified_at = timezone.now()
        self.mode = 'd'
        self.data_has_changed()
        # First save to logfile
        self.save_to_log()
        # then delete record
        super(Subject, self).delete(*args, **kwargs)

    def save_to_log(self):  # PR2018-08-29
        Subject_log.objects.create(
            subject_id=self.id,

            examyear=self.examyear,
            subjectdefault=self.subjectdefault,
            name=self.name,
            abbrev=self.abbrev,
            sequence=self.sequence,
            dep_list=self.dep_list,
            is_active=self.is_active,

            examyear_mod=self.examyear_mod,
            subjectdefault_mod=self.subjectdefault_mod,
            country_mod=self.country_mod,
            name_mod=self.name_mod,
            abbrev_mod=self.abbrev_mod,
            sequence_mod=self.sequence_mod,
            dep_list_mod=self.dep_list_mod,
            is_active_mod=self.is_active_mod,

            mode=self.mode,
            modified_by=self.modified_by,
            modified_at=self.modified_at
        )

    def data_has_changed(self):  # PR2018-07-21
        # returns True when the value of one or more fields has changed PR2018-08-26
        self.is_update = self.id is not None # self.id is None before new record is saved

        self.examyear_mod = self.original_examyear != self.examyear
        self.subjectdefault_mod = self.original_subjectdefault != self.subjectdefault
        self.name_mod = self.original_name != self.name
        self.abbrev_mod = self.original_abbrev != self.abbrev
        self.sequence_mod = self.original_sequence != self.sequence
        self.dep_list_mod = self.original_dep_list != self.dep_list
        self.is_active_mod = self.original_is_active != self.is_active

        return not self.is_update or \
               self.examyear_mod or \
               self.subjectdefault_mod or \
               self.name_mod or \
               self.abbrev_mod or \
               self.sequence_mod or \
               self.dep_list_mod or \
               self.is_active_mod

    @property  # PR2018-07-19
    def has_no_linked_data(self):
        # TODO find records in linked tables
        linked_items_count = Subject.objects.filter(subject_id=self.pk).count()
        # logger.debug('SubjectDefault Model has_no_linked_data linked_items_count: ' + str(linked_items_count))
        return not bool(linked_items_count)

    @property
    def dep_list_str(self): # PR108-08-27
        return Department.dep_list_str(self.dep_list)

# PR2018-06-05 Subject is the base Model of all subjects
class Subject_log(Model):
    subject_id = IntegerField(db_index=True)

    examyear = ForeignKey(Examyear, null=True, related_name='+', on_delete=PROTECT)
    subjectdefault = ForeignKey(Subjectdefault, null=True, related_name='+', on_delete=PROTECT)
    name = CharField(max_length=50, null=True)
    abbrev = CharField(max_length=10, null=True)
    sequence = PositiveSmallIntegerField(null=True)
    dep_list = CharField(max_length=20, null=True)
    is_active = BooleanField(default=True)

    examyear_mod = BooleanField(default=False)
    subjectdefault_mod = BooleanField(default=False)
    name_mod = BooleanField(default=False)
    abbrev_mod = BooleanField(default=False)
    sequence_mod = BooleanField(default=False)
    dep_list_mod = BooleanField(default=False)
    is_active_mod = BooleanField(default=False)

    mode = CharField(max_length=1, null=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()


# PR2018-06-06
class Package(Model):
    school = ForeignKey(School, related_name='packages', on_delete=PROTECT)
    scheme = ForeignKey(Scheme, related_name='packages', on_delete=PROTECT)
    is_template = BooleanField(default=False)  # default is_template Package of this country and examyear PR2018-08-09
    name = CharField(max_length=50)
    abbrev = CharField(max_length=20)
    is_active = BooleanField(default=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    def __str__(self):
        return self.abbrev


# PR2018-06-06
class Package_log(Model):
    package_id = IntegerField(db_index=True)
    school = ForeignKey(School, null=True, related_name='+', on_delete=PROTECT)
    scheme = ForeignKey(Scheme, null=True, related_name='+', on_delete=PROTECT)
    is_template = BooleanField(default=False)  # default template Package of this country and examyear PR2018-08-09
    name = CharField(max_length=50, null=True)
    abbrev = CharField(max_length=20, null=True)
    is_active = BooleanField(default=True)
    mode = CharField(max_length=1, null=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()


# PR2018-06-05
class SubjectScheme(Model):
    school = ForeignKey(School, related_name='subjectschemes', on_delete=CASCADE)
    subject = ForeignKey(Subject, related_name='subjectschemes', on_delete=PROTECT)
    scheme = ForeignKey(Scheme, related_name='subjectschemes', on_delete=PROTECT)
    is_template = BooleanField(default=False)  # default template SubjectScheme of this country and examyear PR2018-08-09

    character = ForeignKey(Character, related_name='subjectschemes', on_delete=PROTECT)

    gradetype = PositiveSmallIntegerField(default=0, choices = c.GRADETYPE_CHOICES)

    weightSE = PositiveSmallIntegerField(default=1)
    weightCE = PositiveSmallIntegerField(default=1)

    is_mandatory = BooleanField(default=False)
    is_combination = BooleanField(default=False)

    is_combi = BooleanField(default=False)
    choicecombi_allowed = BooleanField(default=False)
    has_practexam = BooleanField(default=False)

    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    def __str__(self):
        subjectscheme_str = ''
        if self.subject:
            subjectscheme_str = self.subject
        if self.scheme:
            subjectscheme_str = subjectscheme_str + '-' + self.scheme
        return subjectscheme_str


# PR2018-06-08
class SubjectScheme_log(Model):
    subjectscheme_id = IntegerField(db_index=True)

    subject = ForeignKey(Subject, null=True, related_name='+', on_delete=PROTECT)
    scheme = ForeignKey(Scheme, null=True, related_name='+', on_delete=PROTECT)
    school = ForeignKey(School, related_name='+', on_delete=PROTECT)
    is_template = BooleanField(default=False)  # default SubjectScheme of this country and examyear PR2018-08-09

    character = ForeignKey(Character,null=True,  related_name='+', on_delete=PROTECT)

    gradetype = PositiveSmallIntegerField(null=True)

    weightSE = PositiveSmallIntegerField(null=True)
    weightCE = PositiveSmallIntegerField(null=True)

    is_mandatory = BooleanField(default=False)
    is_combination = BooleanField(default=False)

    is_combi = BooleanField(default=False)
    choicecombi_allowed = BooleanField(default=False)
    has_practexam = BooleanField(default=False)

    mode = CharField(max_length=1, null=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()



# PR2018-08-23
class Norm(Model):
    subject = ForeignKey(Subject, related_name='norms', on_delete=PROTECT)
    scheme = ForeignKey(Scheme, related_name='norms', on_delete=PROTECT)

    is_etenorm = BooleanField(default=False)
    is_primarynorm = BooleanField(default=False)
    scalelength_ce = CharField(max_length=10, null=True)
    norm_ce = CharField(max_length=10, null=True)
    scalelength_reex = CharField(max_length=10, null=True)
    norm_reex = CharField(max_length=10, null=True)
    scalelength_practex = CharField(max_length=10, null=True)
    norm_practex = CharField(max_length=10, null=True)

    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    def __str__(self):
        subjectscheme_str = ''
        if self.subject:
            subjectscheme_str = self.subject
        if self.scheme:
            subjectscheme_str = subjectscheme_str + '-' + self.scheme
        return subjectscheme_str


# PR2018-08-23
class Norm_log(Model):
    norm_id = IntegerField(db_index=True)

    subject = ForeignKey(Subject, null=True, related_name='+', on_delete=PROTECT)
    scheme = ForeignKey(Scheme, null=True, related_name='+', on_delete=PROTECT)

    is_etenorm = BooleanField(default=False)
    is_primarynorm = BooleanField(default=False)
    scalelength_ce = CharField(max_length=10, null=True)
    norm_ce = CharField(max_length=10, null=True)
    scalelength_reex = CharField(max_length=10, null=True)
    norm_reex = CharField(max_length=10, null=True)
    scalelength_practex = CharField(max_length=10, null=True)
    norm_practex = CharField(max_length=10, null=True)

    mode = CharField(max_length=1, null=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()


# PR2018-06-06
class PackageScheme(Model):
    package = ForeignKey(Package, related_name='packageschemes', on_delete=PROTECT)
    subjectscheme = ForeignKey(SubjectScheme, related_name='packageschemes', on_delete=PROTECT)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    def __str__(self):
        name = ''
        if self.package:
            name = str(self.package)
        if self.subjectscheme:
            name = name + '-' + str(self.subjectscheme)
        return name


# PR2018-06-06
class PackageScheme_log(Model):
    packagescheme_id = IntegerField(db_index=True)
    package = ForeignKey(Package, null=True, related_name='+', on_delete=PROTECT)
    subjectscheme = ForeignKey(SubjectScheme, null=True, related_name='+', on_delete=PROTECT)
    mode = CharField(max_length=1, null=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()


# PR2018-06-06
class Cluster(Model):
    department = ForeignKey(Department, related_name='clusters', on_delete=PROTECT)
    subject = ForeignKey(Subject, related_name='clusters', on_delete=PROTECT)
    name = CharField(max_length=50)
    abbrev = CharField(max_length=20)
    is_active = BooleanField(default=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    def __str__(self):
        return self.abbrev

# PR2018-06-06
class Cluster_log(Model):
    cluster_id = IntegerField(db_index=True)
    department = ForeignKey(Department, null=True, related_name='+', on_delete=PROTECT)
    subject = ForeignKey(Subject, null=True, related_name='+', on_delete=PROTECT)
    name = CharField(max_length=50, null=True)
    abbrev = CharField(max_length=20, null=True)
    is_active = BooleanField(default=True)
    mode = CharField(max_length=1, null=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    def __str__(self):
        return self.abbrev

# +++++++++++++++++++++   Functions Department, Level, Sector  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def get_dep_list_tuple(dep_list):
    # PR2018-08-28 dep_list_tuple converts self.dep_list string into tuple,
    # e.g.: dep_list='1;2' will be converted to dep_list=(1,2)
    # empty list = (0,), e.g: 'None'

    dep_list_tuple = ()
    if dep_list:
        dep_list_str = str(dep_list)
        # This function converts init_list_str string into init_list_tuple,  e.g.: '1;2' will be converted to (1,2)
        dep_list_list = dep_list_str.split(';')
        dep_list_tuple = tuple(dep_list_list)

    # select 0 (None) in EditForm when no other departments are selected
    if not dep_list_tuple:
        dep_list_tuple = (0,)

    return dep_list_tuple


def get_list_str(list, model):
    # PR2018-08-16 get_list_str displays string of dep_list, level_list or sector_list. e.g.: Vsbo, Havo, Vwo'
    _list_str = '-'
    # logger.debug('def get_list_str list: <' + str(list) + '> type: <' + str(type(list)) + '>')
    if list:
        _list_split = list.split(';')
        if bool(_list_split):
            for _id_str in _list_split:
                if _id_str:
                    try:
                        _id_int = int(_id_str)
                        # logger.debug('def get_list_str _id_int: ' + str(_id_int) + '> type: <' + str(type(_id_int)) + '>')
                        # skip value 0 (None)
                        if _id_int:
                            # logger.debug('def get_list_str _id_int: ' + str(_id_int))
                            if model =='Department':
                                _instance = Department.objects.filter(pk=_id_int).first()
                                _field = _instance.shortname
                            elif model == 'Level':
                                _instance = Level.objects.filter(pk=_id_int).first()
                                _field = _instance.abbrev
                            elif model == 'Sector':
                                _instance = Sector.objects.filter(pk=_id_int).first()
                                _field = _instance.abbrev
                    except:
                        _field = ''
                    if _field:
                        _list_str = _list_str + ', ' + _field
            if _list_str: # means: if not _list_str == '':
                # slice off first 2 characters: ', '
                _list_str = _list_str[2:]
    # logger.debug('def get_list_str _list_str: <' + str(_list_str) + '>')
    return _list_str


def get_list_tupleXXX(list_str):
    # PR2018-08-23 get_list_tuple converts list_str string into tuple,
    # e.g.: level_list='1;2' will be converted to _list_tuple=(1,2)
    # empty list = None. Was: empty list = (0,), e.g: 'None'
    if list_str:
        # logger.debug('get_list_tuple list_str=<' + str(list_str) + '> type: ' + str(type(list_str)))
        try:
            _list_split = list_str.split(';')
            # logger.debug('get_list_tuple _list_split=<' + str(_list_split) + '>')
            _list_tuple = tuple(_list_split)
            # logger.debug('get_list_tuple _list_tuple=<' + str(_list_tuple) + '>')
        except:
            _list_tuple = ('0',)
        if not bool(_list_tuple):
            # _list_tuple = ('0',)
            _list_tuple = None
    else:
        # _list_tuple = ('0',)
        _list_tuple = None
    # logger.debug('get_list_tuple _list_tuple=#' + str(_list_tuple) + '#')
    return _list_tuple

