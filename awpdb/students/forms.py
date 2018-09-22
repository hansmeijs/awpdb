# PR2018-09-03
from django.forms import Form, ModelForm, CharField, ChoiceField, MultipleChoiceField, SelectMultiple, ModelChoiceField

from django.utils.translation import ugettext_lazy as _

from students.models import Student, Birthcountry, Birthcity

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

# === Student =====================================
class StudentAddForm(ModelForm):  # PR2018-08-09
    class Meta:
        model = Student
        fields = ('school', 'department', 'lastname', 'firstname', 'prefix', 'gender', 'idnumber',
                  'birthdate', 'birthcountry')
        labels = {
            "school": _('School'),
            "department": _('Department'),
            "lastname": _('Last name'),
            "firstname": _('First name'),
            "prefix": _('Prefix'),
            "gender": _('Gender'),
            "idnumber": _('ID number'),
            "birthdate": _('Birthdate'),
            "birthcountry": _('Birth country'),
        }

    # PR2018-06-09 from https://stackoverflow.com/questions/16205908/django-modelform-not-required-field/30403969?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(StudentAddForm, self).__init__(*args, **kwargs)

        # ======= field 'school' ============
        self.initial['school'] = request.user.school.id
        self.fields['school'].disabled = True

        # ======= field 'department' ============
        self.initial['department'] = request.user.department.id
        self.fields['department'].disabled = True

        # ======= field 'lastname' ============
        self.fields['lastname'] = CharField(
            max_length = 80,
            required = True,
            # validators=[validate_unique_subject_name(request.user.country)]
            )
        self.fields['lastname'].widget.attrs.update({'autofocus': 'autofocus'})

        # ======= field 'firstname' ============
        self.fields['firstname'] = CharField(
            max_length = 80,
            required = True,
            # validators=[validate_unique_subject_abbrev(request.user.country)]
            )

        # ======= field 'birthcity_list' ============
        self.choices = [(0, '---')]
        for _item in Birthcity.objects.all():
            self.choices.append((_item.id, _item.name))
        # logger.debug('StudentAddForm __init__  self.choices: ' + str(self.choices))
        self.fields['birthcity_list'] = ChoiceField(
            required=False,
            # choises must be tuple or list, dictionary gives error: 'int' object is not iterable
            # choices=self.choices,
            label=_('birthcity_list'),
            # PR2018-07-31 debug: use schooldefault.id instead of schooldefault.
            # This showed always first item in choices: initial=self.this_instance.schooldefault
            # initial=self.birthcountry
        )

        # self.fields['schooldefault_list'].disabled = self.is_disabled


#  =========== Functions  ===========
def birthcountry_choices():
    _choices = []
    for _item in Birthcountry.objects.all():
        _choices.append((_item.id, _item.name))

    # logger.debug('class User(AbstractUser) schooldefault_choices: ' + str(_choices))
    return _choices