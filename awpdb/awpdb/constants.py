#PR2018-05-25
from django.utils.translation import ugettext_lazy as _

USERNAME_MAX_LENGTH = 30

# PR2018-05-07
ROLE_00_SCHOOL = 0
ROLE_01_INSP = 1
ROLE_02_SYSTEM = 2

# PR2018-05-21
PERMIT_00_NONE = 0
PERMIT_01_READ = 1
PERMIT_02_WRITE = 2
PERMIT_04_AUTH = 4
PERMIT_08_ADMIN = 8

GENDER_NONE = '-'  # PR2018-09-05
GENDER_MALE = 'm'
GENDER_FEMALE = 'f'

GRADETYPE_00_NONE = 0
GRADETYPE_01_NUMBER = 1
GRADETYPE_02_CHARACTER = 2 # goed / voldoende / onvoldoende



# PR2018-08-01
CHOICES_ROLE = (
    (ROLE_00_SCHOOL, _('School')),
    (ROLE_01_INSP, _('Inspection')),
    (ROLE_02_SYSTEM, _('System'))
)

# PR2018-08-07
CHOICES_ROLE_DICT = {
    ROLE_00_SCHOOL: _('School'),
    ROLE_01_INSP: _('Inspection'),
    ROLE_02_SYSTEM: _('System')
}

MODE_DICT = {
    'c': _('Created'),
    'u': _('Updated'),
    'a': _('Authorized'),
    'p': _('Approved'),
    'd': _('Deleted'),
    's': _('System')
}

# choises must be tuple or list, dictionary gives error: 'int' object is not iterable
CHOICES_NO_YES = (
    (False, _('No')),
    (True, _('Yes'))
)

# choises must be tuple or list, dictionary gives error: 'int' object is not iterable
CHOICES_NO_YES_DICT = {
    False: _('No'),
    True: _('Yes')
}

# choises must be tuple or list, dictionary gives error: 'int' object is not iterable
CHOICES_LOCKED = (
    (0, _('Unlocked')),
    (1, _('Locked'))
)
LOCKED_DICT = {
    0: _('Unlocked'),
    1: _('Locked')
}

IS_ACTIVE_DICT = {
    0: _('Inactive'),
    1: _('Active')
}
# choises must be tuple or list, dictionary gives error: 'int' object is not iterable
IS_ACTIVE_CHOICES = (
    (0, _('Inactive')),
    (1, _('Active'))
)

INACTIVE_DICT = {
    0: _('Active'),
    1: _('Inactive')
}

# PR2018-07-19 choises must be tuple or list, dictionary gives error: 'int' object is not iterable
INACTIVE_CHOICES = (
    (0, _('Active')),
    (1, _('Inactive'))
)

# PR2018-07-31 choise 0 = 'None' for empty choice
CHOICE_NONE = (0, _('None'))

# PR2018-08-04 for Examyear.publishes
PUBLISHED_CHOICES = (
    (0, _('Not published')),
    (1, _('Published'))
)
PUBLISHED_DICT = {
    0: _('Not published'),
    1: _('Published')
}

GRADETYPE_CHOICES = (
    (GRADETYPE_00_NONE, _('None')),
    (GRADETYPE_01_NUMBER, _('Number')),
    (GRADETYPE_02_CHARACTER, _('Good/Sufficient/Insufficient'))
)

# PR2018-09-05
GENDER_CHOICES = (
    (GENDER_NONE, '-'),
    (GENDER_MALE, _('M')),
    (GENDER_FEMALE, _('F')),
)
