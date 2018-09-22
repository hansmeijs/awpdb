# PR2018-07-20
from django.db.models import Model, Manager, ForeignKey, PROTECT
from django.db.models import CharField, TextField, IntegerField, PositiveSmallIntegerField, BooleanField, DateField, DateTimeField

from django.utils import timezone

# PR2018-05-05 use AUTH_USER_MODEL
#from django.contrib.auth.models import User
#from accounts.models import User
from awpdb.settings import AUTH_USER_MODEL
from django.utils.translation import ugettext_lazy as _
from awpdb import constants as c

from schools.models import Department, School
from subjects.models import Scheme, Package, SubjectScheme, Cluster

import logging
logger = logging.getLogger(__name__)

# PR2018-04-22: backup: (venv) C:\dev\awpr\awpr>py -3 manage.py dumpdata schools --format json --indent 4 > schools/backup/schools.json
#               restore: (venv) C:\dev\awpr\awpr>py -3 manage.py loaddata schools/backup/schools.json

# clean() method rus to_python(), validate(), and run_validators() and propagates their errors.
# If, at any time, any of the methods raise ValidationError, the validation stops and that error is raised.
# This method returns the clean data, which is then inserted into the cleaned_data dictionary of the form.




# === Birthcountry =====================================
class Birthcountry(Model):
    # PR2018-07-20 from https://stackoverflow.com/questions/3090302/how-do-i-get-the-object-if-it-exists-or-none-if-it-does-not-exist
    name = CharField(max_length=50, unique=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    class Meta:
        ordering = ['name',]

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(Birthcountry, self).__init__(*args, **kwargs)
        self.original_name = self.name

    def save(self, *args, **kwargs):
        logger.debug('Birthcountry(Model) save kwargs: ' + str(kwargs))
        self.request = kwargs.pop('request', None)
        # logger.debug('Birthcountry(Model) save self.request.user: ' + str(self.request.user))
        if self.data_has_changed():
            self.modified_by = self.request.user
            self.modified_at = timezone.now()
            self.mode = ('c', 'u')[self.is_update]
            super(Birthcountry, self).save(force_insert = not self.is_update, force_update = self.is_update, **kwargs)
            self.save_to_log()

    def delete(self, *args, **kwargs):
        self.modified_at = timezone.now()
        self.mode = 'd'
        self.data_has_changed()
        # First save to logfile
        self.save_to_log()
        # then delete record
        super(Birthcountry, self).delete(*args, **kwargs)

    def save_to_log(self):
        Birthcountry_log.objects.create(
            birthcountry_id=self.id,
            name=self.name,
            name_mod=self.name_mod,
            mode=self.mode,
            modified_by=self.modified_by,
            modified_at=self.modified_at
        )

    def data_has_changed(self):  # PR2018-08-31
        self.is_update = self.id is not None # self.id is None before new record is saved
        self.name_mod = self.original_name != self.name
        return not self.is_update or \
               self.name_mod

# PR2018-05-05
class Birthcountry_log(Model):
    birthcountry_id = IntegerField(db_index=True)
    name = CharField(max_length=50, null=True)
    name_mod = BooleanField(default=False)
    mode = CharField(max_length=1, null=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    def __str__(self):
        return self.name

    @property
    def mode_str(self):
        mode_str = '-'
        if self.mode is not None:
            mode_str = c.MODE_DICT.get(str(self.mode))
        return mode_str


# === Birthcity =====================================
class Birthcity(Model):
    birthcountry = ForeignKey(Birthcountry, related_name='birthcities', on_delete=PROTECT)
    name = CharField(max_length=50, unique=False)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    class Meta:
        ordering = ['name',]

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(Birthcity, self).__init__(*args, **kwargs)
        self.original_name = self.name

    def save(self, *args, **kwargs):
        logger.debug('Birthcity(Model) save kwargs: ' + str(kwargs) + ' Type: ' + str(type(kwargs)))
        self.request = kwargs.pop('request', None)
        if self.data_has_changed():
            self.modified_by = self.request.user
            self.modified_at = timezone.now()
            self.mode = ('c', 'u')[self.is_update]
            super(Birthcity, self).save(force_insert = not self.is_update, force_update = self.is_update, **kwargs)
            self.save_to_log()

    def delete(self, *args, **kwargs):
        self.modified_at = timezone.now()
        self.mode = 'd'
        self.data_has_changed()
        # First save to logfile
        self.save_to_log()
        # then delete record
        super(Birthcountry, self).delete(*args, **kwargs)

    def save_to_log(self):
        Birthcity_log.objects.create(
            birthcity_id=self.id,
            name=self.name,
            name_mod=self.name_mod,
            mode=self.mode,
            modified_by=self.modified_by,
            modified_at=self.modified_at
        )

    def data_has_changed(self):  # PR2018-08-31
        self.is_update = self.id is not None # self.id is None before new record is saved
        self.name_mod = self.original_name != self.name

        logger.debug('Birthcity(Model) data_has_changed self.is_update: ' + str(self.is_update) + ' Type: ' + str(type(self.is_update)))
        logger.debug('Birthcity(Model) data_has_changed self.name: ' + str(self.name) + ' Type: ' + str(type(self.name)))
        logger.debug('Birthcity(Model) data_has_changed self.name_mod: ' + str(self.name_mod) + ' Type: ' + str(type(self.name_mod)))

        return not self.is_update or \
               self.name_mod


# PR2018-05-05
class Birthcity_log(Model):
    birthcity_id = IntegerField(db_index=True)
    name = CharField(max_length=50, null=True)
    name_mod = BooleanField(default=False)
    mode = CharField(max_length=1, null=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    def __str__(self):
        return self.name

    @property
    def mode_str(self):
        mode_str = '-'
        if self.mode is not None:
            mode_str = c.MODE_DICT.get(str(self.mode))
        return mode_str


# =================

class Student(Model):# PR2018-06-06, 2018-09-05
    school = ForeignKey(School, related_name='students', on_delete=PROTECT)
    department = ForeignKey(Department, related_name='students', on_delete=PROTECT)
    scheme = ForeignKey(Scheme, null=True, related_name='students', on_delete=PROTECT)
    package = ForeignKey(Package, null=True, related_name='students', on_delete=PROTECT)

    lastname = CharField(db_index=True, max_length=80)
    firstname= CharField(db_index=True, max_length=80)
    prefix= CharField(max_length=10, null=True, blank=True)
    gender= CharField(db_index=True, max_length=1, choices=c.GENDER_CHOICES, default=c.GENDER_NONE)
    idnumber= CharField(db_index=True, max_length=20)
    birthdate= DateField(null=True)

    # birthcountry= CharField(max_length=50, null=True)
    # birthcity= CharField( max_length=50, null=True)
    birthcountry = ForeignKey(Birthcountry, null=True, blank=True, related_name='students', on_delete=PROTECT)
    birthcity = ForeignKey(Birthcity, null=True, blank=True, related_name='students', on_delete=PROTECT)

    classname = CharField(db_index=True, max_length=20, null=True)
    examnumber = CharField(db_index=True, max_length=20, null=True)
    regnumber = CharField(db_index=True, max_length=20, null=True)
    diplomanumber = CharField(db_index=True, max_length=10, null=True)
    gradelistnumber = CharField(db_index=True, max_length=10, null=True)
    notes = TextField(blank=True, null=True)
    status = PositiveSmallIntegerField(default=0)
    locked =  BooleanField(default=False)

    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

    class Meta:
        ordering = ['lastname', 'firstname']

    def __str__(self):
        _lastname = self.lastname
        _firstname = self.firstname
        _fullname = _lastname + ', ' + _firstname
        return _fullname

    def __init__(self, *args, **kwargs):
        super(Student, self).__init__(*args, **kwargs)
        # private variable __original checks if data_has_changed, to prevent update record when no changes are made.
        # Otherwise a logrecord is created every time the save button is clicked without changes
        try:
            self.original_school = self.school
        except:
            self.original_school = None
        try:
            self.original_department = self.department
        except:
            self.original_department = None
        try:
            self.original_scheme = self.scheme
        except:
            self.original_scheme = None
        try:
            self.original_package = self.package
        except:
            self.original_package = None
        self.original_lastname = self.lastname
        self.original_firstname = self.firstname
        self.original_prefix = self.prefix
        self.original_gender = self.gender
        self.original_idnumber = self.idnumber
        self.original_birthdate = self.birthdate
        self.original_birthcountry = self.birthcountry
        self.original_birthcity = self.birthcity
        self.original_classname = self.classname
        self.original_examnumber = self.examnumber
        self.original_regnumber = self.regnumber
        self.original_diplomanumber = self.diplomanumber
        self.original_gradelistnumber = self.gradelistnumber
        self.original_notes = self.notes
        self.original_status = self.status
        self.original_locked = self.locked

    def save(self, *args, **kwargs):  # called by subjectdefault.save(self.request) in SubjectdefaultEditView.form_valid
        self.request = kwargs.pop('request', None)

    # check if data has changed. If so: save object
        if self.data_has_changed():
            self.modified_by = self.request.user
            self.modified_at = timezone.now()
            self.mode = ('c', 'u')[self.is_update]
            super(Student, self).save(force_insert = not self.is_update, force_update = self.is_update, **kwargs)
            self.save_to_log()

    def delete(self, *args, **kwargs):
        self.modified_at = timezone.now()
        self.mode = 'd'
        self.data_has_changed()
        # First save to logfile
        self.save_to_log()
        # then delete record
        super(Student, self).delete(*args, **kwargs)

    def save_to_log(self):
        # Create method also saves record
        Student_log.objects.create(
            student_id=self.id, # self.id gets its value in super(School, self).save

            lastname=self.lastname,
            firstname=self.firstname,
            prefix=self.prefix,
            gender=self.gender,
            idnumber=self.idnumber,
            birthdate=self.birthdate,
            birthcountry=self.birthcountry,
            birthcity=self.birthcity,
            classname=self.classname,
            examnumber=self.examnumber,
            regnumber=self.regnumber,
            diplomanumber=self.diplomanumber,
            gradelistnumber=self.gradelistnumber,
            notes=self.notes,
            status=self.status,
            locked=self.locked,

            lastname_mod = self.lastname_mod,
            firstname_mod = self.firstname_mod,
            prefix_mod = self.prefix_mod,
            gender_mod = self.gender_mod,
            idnumber_mod = self.idnumber_mod,
            birthdate_mod = self.birthdate_mod,
            birthcountry_mod = self.birthcountry_mod,
            birthcity_mod = self.birthcity_mod,
            classname_mod = self.classname_mod,
            examnumber_mod = self.examnumber_mod,
            regnumber_mod = self.regnumber_mod,
            diplomanumber_mod = self.diplomanumber_mod,
            gradelistnumber_mod = self.gradelistnumber_mod,
            notes_mod = self.notes_mod,
            status_mod = self.status_mod,
            locked_mod = self.locked_mod,

            mode=self.mode,
            modified_by=self.modified_by,
            modified_at=self.modified_at
        )

    def data_has_changed(self):  # PR2018-07-21
        # returns True when the value of one or more fields has changed PR2018-08-26
        self.is_update = self.id is not None # self.id is None before new record is saved
        self.school_mod = self.original_school != self.school
        self.department_mod = self.original_department != self.department
        self.scheme_mod = self.original_scheme != self.scheme
        self.package_mod = self.original_package != self.package
        self.lastname_mod = self.original_lastname != self.lastname
        self.firstname_mod = self.original_firstname != self.firstname
        self.prefix_mod = self.original_prefix != self.prefix
        self.gender_mod = self.original_gender != self.gender
        self.idnumber_mod = self.original_idnumber != self.idnumber
        self.birthdate_mod = self.original_birthdate != self.birthdate
        self.birthcountry_mod = self.original_birthcountry != self.birthcountry
        self.birthcity_mod = self.original_birthcity != self.birthcity
        self.classname_mod = self.original_classname != self.classname
        self.examnumber_mod = self.original_examnumber != self.examnumber
        self.regnumber_mod = self.original_regnumber != self.regnumber
        self.diplomanumber_mod = self.original_diplomanumber != self.diplomanumber
        self.gradelistnumber_mod = self.original_gradelistnumber != self.gradelistnumber
        self.notes_mod = self.original_notes != self.notes
        self.status_mod = self.original_status != self.status
        self.locked_mod = self.original_locked != self.locked

        return not self.is_update or \
               self.school_mod or \
               self.department_mod or \
               self.scheme_mod or \
               self.package_mod or \
               self.lastname_mod or \
               self.firstname_mod or \
               self.prefix_mod or \
               self.gender_mod or \
               self.idnumber_mod or \
               self.birthdate_mod or \
               self.birthcountry_mod or \
               self.birthcity_mod or \
               self.classname_mod or \
               self.examnumber_mod or \
               self.regnumber_mod or \
               self.diplomanumber_mod or \
               self.gradelistnumber_mod or \
               self.notes_mod or \
               self.status_mod or \
               self.locked_mod

    @property
    def full_name(self):
        full_name = str(self.lastname)
        full_name = full_name.strip()  # Trim
        if self.prefix: # put prefix at the front
            prefix_str  = str(self.prefix)
            full_name = prefix_str .strip() + ' ' + full_name
        firstname_str = str(self.firstname)
        firstname_str = firstname_str.split()
        full_name = firstname_str.strip() + ' ' + full_name
        return full_name

    @property
    def lastname_firstname_initials(self):
        lastname_str = str(self.lastname)
        full_name = lastname_str.strip()
        firstnames = ''
        if self.firstname:
            firstnames_str = str(self.firstname)
            firstnames_arr = firstnames_str.split()
            if len(firstnames_arr) == 0:
                firstnames = firstnames_str.strip()  # 'PR 13 apr 13 Trim toegevoegd
            else:
                skip = False
                for item in firstnames_arr:
                    if not skip:
                        firstnames = firstnames + item + " " # write first firstname in full
                        skip = True
                    else:
                        if item:
                            #PR2017-02-18 VB debug. bij dubbele spatie in voornaam krijg je lege err(x)
                            firstnames = firstnames + item[:1] + ' ' # write of the next firstnames only the first letter
        if firstnames:
            full_name = full_name + ', ' + firstnames
        if self.prefix: # put prefix at the front
            prefix = str(self.prefix)
            full_name = prefix.strip() + ' ' + full_name
        full_name = full_name.strip()
        return full_name

"""

    GemidCEcijferText = CharField(db_index=True, max_length=10, null=True)
    GemidEindcijferText = CharField(db_index=True, max_length=10, null=True)
    GemidCombicijferText = CharField(db_index=True, max_length=10, null=True)
    CEcijfer_Tv01Gem = DecimalField(max_digits=5, decimal_places=2, default = 0)
    CEcijfer_Tv02Gem = DecimalField(max_digits=5, decimal_places=2, default = 0)
    CEcijfer_Tv03Gem = DecimalField(max_digits=5, decimal_places=2, default = 0)

    Eindcijfer_Tv01Som = PositiveSmallIntegerField(default=0)
    Eindcijfer_Tv02Som = PositiveSmallIntegerField(default=0)
    Eindcijfer_Tv03Som = PositiveSmallIntegerField(default=0)
    Eindcijfer_Count = PositiveSmallIntegerField(default=0)
    ResultaatID = PositiveSmallIntegerField(default=0)
    ResultaatId_Tv01 = PositiveSmallIntegerField(default=0)
    ResultaatId_Tv02 = PositiveSmallIntegerField(default=0)
    ResultaatId_Tv03 = PositiveSmallIntegerField(default=0)

    ResultaatInfo = CharField(db_index=True, max_length=80, null=True)

    IsHerexKand = BooleanField(default=False)
    IsManualResultaat = BooleanField(default=False)
    IsTeruggetrokken = BooleanField(default=False)
    OpmerkingEx5 = CharField(db_index=True, max_length=80, null=True)
    Sectorwerkstuk = CharField(db_index=True, max_length=80, null=True)
    ResSectorwerkstuk = CharField(db_index=True, max_length=8, null=True0)

"""


# PR2018-06-08
class Student_log(Model):
    student_id = IntegerField(db_index=True)

    school = ForeignKey(School, null=True, related_name='+', on_delete=PROTECT)
    department = ForeignKey(Department, null=True, related_name='+', on_delete=PROTECT)
    scheme = ForeignKey(Scheme, null=True, related_name='+', on_delete=PROTECT)
    package = ForeignKey(Package, null=True, related_name='+', on_delete=PROTECT)

    lastname = CharField(max_length=80, null=True)
    firstname = CharField(max_length=80, null=True)
    prefix = CharField(max_length=10, null=True)
    gender = CharField(max_length=1, null=True)
    idnumber = CharField(max_length=20, null=True)
    birthdate = DateField(null=True)

    # birthcountry = CharField(max_length=50, null=True)
    # birthplace = CharField(max_length=50, null=True)
    birthcountry = ForeignKey(Birthcountry, null=True, related_name='+', on_delete=PROTECT)
    birthcity = ForeignKey(Birthcity, null=True, related_name='+', on_delete=PROTECT)

    classname = CharField(db_index=True, max_length=20, null=True)
    examnumber = CharField(db_index=True, max_length=20, null=True)
    regnumber = CharField(db_index=True, max_length=20, null=True)
    diplomanumber = CharField(db_index=True, max_length=10, null=True)
    gradelistnumber = CharField(db_index=True, max_length=10, null=True)
    notes = TextField(blank=True, null=True)
    status = PositiveSmallIntegerField(default=0)
    locked = BooleanField(default=False)

    school_mod = BooleanField(default=False)
    department_mod = BooleanField(default=False)
    scheme_mod = BooleanField(default=False)
    package_mod = BooleanField(default=False)
    lastname_mod = BooleanField(default=False)
    firstname_mod = BooleanField(default=False)
    prefix_mod = BooleanField(default=False)
    gender_mod = BooleanField(default=False)
    idnumber_mod = BooleanField(default=False)
    birthdate_mod = BooleanField(default=False)
    birthcountry_mod = BooleanField(default=False)
    birthcity_mod = BooleanField(default=False)

    classname_mod = BooleanField(default=False)
    examnumber_mod = BooleanField(default=False)
    regnumber_mod = BooleanField(default=False)
    diplomanumber_mod = BooleanField(default=False)
    gradelistnumber_mod = BooleanField(default=False)
    notes_mod = BooleanField(default=False)
    status_mod = BooleanField(default=False)
    locked_mod = BooleanField(default=False)

    mode = CharField(max_length=1, null=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()


# PR2018-06-06
class StudentSubject(Model):
    student = ForeignKey(Student, related_name='studentsubjects', on_delete=PROTECT)
    subjectscheme = ForeignKey(SubjectScheme, related_name='studentsubjects', on_delete=PROTECT)
    cluster = ForeignKey(Cluster, related_name='studentsubjects', on_delete=PROTECT)
    # # #
    is_extra_subject = BooleanField(default=False)
    is_extra_subject_counts = BooleanField(default=False)
    is_choice_combi = BooleanField(default=False)
    has_tv02 = BooleanField(default=False)
    has_tv03 = BooleanField(default=False)
    has_proof_of_knowledge = BooleanField(default=False)
    # # #
    score_pe = CharField(max_length=4, null=True)
    score_ce = CharField(max_length=4, null=True)
    score_ce_tv02 = CharField(max_length=4, null=True)
    score_ce_tv03 = CharField(max_length=4, null=True)
    # # #
    grade_se = CharField(max_length=4, null=True)
    grade_pe = CharField(max_length=4, null=True)
    grade_ce = CharField(max_length=4, null=True)
    grade_ce_tv02 = CharField(max_length=4, null=True)
    grade_ce_tv03 = CharField(max_length=4, null=True)
    # # #
    score_pe_authby = ForeignKey(AUTH_USER_MODEL, null=True, related_name='+', on_delete=PROTECT)
    score_ce_authby = ForeignKey(AUTH_USER_MODEL, null=True, related_name='+', on_delete=PROTECT)
    score_ce_tv02_authby = ForeignKey(AUTH_USER_MODEL, null=True, related_name='+', on_delete=PROTECT)
    score_ce_tv03_authby = ForeignKey(AUTH_USER_MODEL, null=True, related_name='+', on_delete=PROTECT)
    # # #
    score_pe_auth_at = DateTimeField(null=True)
    score_ce_auth_at = DateTimeField(null=True)
    score_ce_tv02_auth_at = DateTimeField(null=True)
    score_ce_tv03_auth_at = DateTimeField(null=True)
    # # #
    grade_se_auth_by = ForeignKey(AUTH_USER_MODEL, null=True, related_name='+', on_delete=PROTECT)
    grade_pe_auth_by = ForeignKey(AUTH_USER_MODEL, null=True, related_name='+', on_delete=PROTECT)
    grade_ce_auth_by = ForeignKey(AUTH_USER_MODEL, null=True, related_name='+', on_delete=PROTECT)
    grade_ce_tv02_auth_by = ForeignKey(AUTH_USER_MODEL, null=True, related_name='+', on_delete=PROTECT)
    grade_ce_tv03_auth_by = ForeignKey(AUTH_USER_MODEL, null=True, related_name='+', on_delete=PROTECT)
    # # #
    grade_se_auth_at = DateTimeField(null=True)
    grade_pe_auth_at = DateTimeField(null=True)
    grade_ce_auth_at = DateTimeField(null=True)
    grade_ce_tv02_auth_at = DateTimeField(null=True)
    grade_ce_tv03_auth_at = DateTimeField(null=True)
    # # #
    grade_se_pe_ce_appr_by = ForeignKey(AUTH_USER_MODEL, null=True, related_name='+', on_delete=PROTECT)
    grade_ce_tv02_appr_by = ForeignKey(AUTH_USER_MODEL, null=True, related_name='+', on_delete=PROTECT)
    grade_ce_tv03_appr_by = ForeignKey(AUTH_USER_MODEL, null=True, related_name='+', on_delete=PROTECT)
    # # #
    grade_se_pe_ce_appr_at = DateTimeField(null=True)
    grade_ce_tv02_appr_at = DateTimeField(null=True)
    grade_ce_tv03_appr_at = DateTimeField(null=True)
    # # #
    grade_pece = CharField(max_length=4, null=True)
    grade_pece_tv02 = CharField(max_length=4, null=True)
    grade_pece_tv03 = CharField(max_length=4, null=True)
    # # #
    endgrade = CharField(max_length=2, null=True)
    endgrade_tv02 = CharField(max_length=2, null=True)
    endgrade_tv03 = CharField(max_length=2, null=True)
    # # #
    info  = CharField(max_length=255, null=True)
    flag_insp = PositiveSmallIntegerField(default=0)
    # put notes in a separate table, per user

    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()


# PR2018-06-06
class StudentSubject_log(Model):
    studentsubject_id = IntegerField(db_index=True)
    # # #
    student = ForeignKey(Student, null=True, related_name='+', on_delete=PROTECT)
    subjectscheme = ForeignKey(SubjectScheme, null=True, related_name='+', on_delete=PROTECT)
    cluster = ForeignKey(Cluster, null=True, related_name='+', on_delete=PROTECT)
    # # #
    is_extra_subject = BooleanField(default=False)
    is_extra_subject_counts = BooleanField(default=False)
    is_choice_combi = BooleanField(default=False)
    has_tv02 = BooleanField(default=False)
    has_tv03 = BooleanField(default=False)
    has_proof_of_knowledge = BooleanField(default=False)
    # # #
    score_pe = CharField(max_length=4, null=True)
    score_ce = CharField(max_length=4, null=True)
    score_ce_tv02 = CharField(max_length=4, null=True)
    score_ce_tv03 = CharField(max_length=4, null=True)
    # # #
    grade_se = CharField(max_length=4, null=True)
    grade_pe = CharField(max_length=4, null=True)
    grade_ce = CharField(max_length=4, null=True)
    grade_ce_tv02 = CharField(max_length=4, null=True)
    grade_ce_tv03 = CharField(max_length=4, null=True)
    # # #
    score_pe_authby = ForeignKey(AUTH_USER_MODEL, null=True, related_name='+', on_delete=PROTECT)
    score_ce_authby = ForeignKey(AUTH_USER_MODEL, null=True, related_name='+', on_delete=PROTECT)
    score_ce_tv02_authby = ForeignKey(AUTH_USER_MODEL, null=True, related_name='+', on_delete=PROTECT)
    score_ce_tv03_authby = ForeignKey(AUTH_USER_MODEL, null=True, related_name='+', on_delete=PROTECT)
    # # #
    score_pe_auth_at = DateTimeField(null=True)
    score_ce_auth_at = DateTimeField(null=True)
    score_ce_tv02_auth_at = DateTimeField(null=True)
    score_ce_tv03_auth_at = DateTimeField(null=True)
    # # #
    grade_se_auth_by = ForeignKey(AUTH_USER_MODEL, null=True, related_name='+', on_delete=PROTECT)
    grade_pe_auth_by = ForeignKey(AUTH_USER_MODEL, null=True, related_name='+', on_delete=PROTECT)
    grade_ce_auth_by = ForeignKey(AUTH_USER_MODEL, null=True, related_name='+', on_delete=PROTECT)
    grade_ce_tv02_auth_by = ForeignKey(AUTH_USER_MODEL, null=True, related_name='+', on_delete=PROTECT)
    grade_ce_tv03_auth_by = ForeignKey(AUTH_USER_MODEL, null=True, related_name='+', on_delete=PROTECT)
    # # #
    grade_se_auth_at = DateTimeField(null=True)
    grade_pe_auth_at = DateTimeField(null=True)
    grade_ce_auth_at = DateTimeField(null=True)
    grade_ce_tv02_auth_at = DateTimeField(null=True)
    grade_ce_tv03_auth_at = DateTimeField(null=True)
    # # #
    grade_se_pe_ce_appr_by = ForeignKey(AUTH_USER_MODEL, null=True, related_name='+', on_delete=PROTECT)
    grade_ce_tv02_appr_by = ForeignKey(AUTH_USER_MODEL, null=True, related_name='+', on_delete=PROTECT)
    grade_ce_tv03_appr_by = ForeignKey(AUTH_USER_MODEL, null=True, related_name='+', on_delete=PROTECT)
    # # #
    grade_se_pe_ce_appr_at = DateTimeField(null=True)
    grade_ce_tv02_appr_at = DateTimeField(null=True)
    grade_ce_tv03_appr_at = DateTimeField(null=True)
    # # #
    grade_pece = CharField(max_length=4, null=True)
    grade_pece_tv02 = CharField(max_length=4, null=True)
    grade_pece_tv03 = CharField(max_length=4, null=True)
    # # #
    endgrade = CharField(max_length=2, null=True)
    endgrade_tv02 = CharField(max_length=2, null=True)
    endgrade_tv03 = CharField(max_length=2, null=True)
    # # #
    info  = CharField(max_length=255, null=True)
    flag_insp = PositiveSmallIntegerField(default=0)
    # put notes in a separate table, per user

    mode = CharField(max_length=1, null=True)
    modified_by = ForeignKey(AUTH_USER_MODEL, related_name='+', on_delete=PROTECT)
    modified_at = DateTimeField()

