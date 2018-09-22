# PR2018-05-28
from django.contrib import messages
from django.utils.translation import activate, ugettext_lazy as _

from schools.models import Examyear, Department, Schooldefault, Country
from awpdb import constants as c

import datetime
import logging
logger = logging.getLogger(__name__)


def get_headerbar_param(request, params):
    # PR2018-05-28 set values for headerbar

    # params.get() returns an element from a dictionary, second argument is default when not found
    # this is used for arguments that are passed to headerbar

    logger.debug('get_headerbar_param params: ' + str(params))

    # select_country overrides display_country
    _display_country = params.get('display_country', False)
    _select_country = params.get('select_country', False)
    if _select_country:
        _display_country = True

    # select_examyear overrides display_examyear
    _display_examyear = params.get('display_examyear', False)
    _select_examyear = params.get('select_examyear', False)
    if _select_examyear:
        _display_examyear = True


    # select_school overrides display_school
    _display_school = params.get('display_school', False)
    _select_school = params.get('select_school', False)
    if _select_school:
        _display_school = True

    # params.pop() removes and returns an element from a dictionary, second argument is default when not found
    # this is used for arguments that are not passed to headerbar
    _override_school = params.pop('override_school', None)

    # select_department overrides display_department
    _display_dep = params.get('display_dep', False)
    _select_dep = params.get('select_dep', False)
    if _select_dep:
        _display_dep = True



    # These are arguments that are added to headerbar in this function
    _country = ''
    _country_list = ''
    _examyear = ''
    _examyear_list = ''
    _school = ''
    _school_list = ''
    _department = ''
    _dep_list = ''
    _class_examyear_warning = ''

    if request.user.is_authenticated:
        # PR2018-05-11 set language
        if request.user.lang is not None:
            activate(request.user.lang)
        else:
            activate('nl')

# PR2018-08-11 display_country = True when user.is_role_system,
        # _select_country is always True when display_country = True
        if _display_country:
            _country_list = get_country_list(request.user)
            # only system user can change country
            if _select_country:
                if not request.user.is_role_system:
                    _select_country = False
            if request.user.country is None:
                if _select_country:
                    _country = _('<Select country>')
                    messages.warning(request, _('Please select a country.'))
                else:
                    messages.error(request, _('No country selected.'))
            else:
                _country = request.user.country

# PR2018-05-29 select examyear
        if _display_examyear:
            _examyear_list = get_examyear_list(request.user)
            if request.user.examyear is None:
                if _select_examyear:
                    _examyear = _('<Select exam year>')
                    messages.warning(request, _('Please select an exam year.'))
                else:
                    _examyear = _('<No exam year selected>')
            else:
                _examyear = request.user.examyear# .examyear
                # if _select_examyear:
                # PR2018-05-18 check if request.user.examyear equals this examyear
                if not request.user.examyear.equals_this_examyear:
                    # PR2018-08-24 debug: in base.html  href="#" is needed,
                    # because bootstrap line 233: a:not([href]):not([tabindex]) overrides navbar-item-warning
                    _class_examyear_warning = 'navbar-item-warning'
                    messages.warning(request,  _("Please note: selected exam year is different from the current exam year."))

# PR2018-05-11 select school
        if _display_school:
            if _override_school:
                _school = _override_school
            else:
                _school_list = get_schooldefault_list(request.user)
                if request.user.schooldefault is None:
                    if _select_school:
                        _school = _('<Select school>')
                        messages.warning(request, _('Please select a school.'))
                    else:
                        _school = _('<No school selected>')
                else:
                    if request.user.is_role_insp_or_system:
                        _school = request.user.schooldefault.code + ' - ' + request.user.schooldefault.name
                    else:
                        _school = request.user.schooldefault.name

# PR2018-08-24 select department
        if _display_dep:
            _dep_list = get_department_list(request.user)
            if request.user.department is None:
                if _select_dep:
                    _department = _('<Select department>')
                    messages.warning(request, _('Please select a department.'))
                else:
                    messages.error(request, _('No department selected.'))
            else:
                _department = request.user.department.shortname


    else:
        activate('nl')

    headerbar = {
        'request': request,
        'display_country': _display_country, 'select_country': _select_country, 'country': _country, 'country_list': _country_list,
        'display_examyear': _display_examyear, 'select_examyear': _select_examyear, 'examyear': _examyear, 'examyear_list': _examyear_list,
        'class_examyear_warning': _class_examyear_warning,
        'display_school': _display_school, 'select_school': _select_school, 'school': _school, 'school_list': _school_list,
        'display_dep': _display_dep,'select_dep': _select_dep, 'department': _department, 'dep_list': _dep_list,
    }
    # append the rest of the dict 'params' to the dict 'headerbar'.
    # the rest can be for instance: {'form': form},  {'countries': countries}
    headerbar.update(params)

    logger.debug('get_headerbar_param headerbar: ' + str(headerbar))

    return  headerbar

def get_country_list(request_user):
    # PR2018-08-11   #country_list: [{'pk': '1', 'country': 'Curacao'},
    _country_list = []
    if request_user is not None:
        for country in Country.objects.all():
            # current country cannot be selected in dropdown list
            _is_user_country = False
            if request_user.country is not None:
                if country == request_user.country:
                    _is_user_country = True
            row_dict = {'pk': str(country.id), 'country':country.name, 'is_user_country': _is_user_country}
            _country_list.append(row_dict)
    return _country_list

def get_examyear_list(request_user):
    # PR2018-05-14 objects.order_by('-examyear').all() not necessary, because I added to model: class Meta: ordering = ['-examyear',]

    # PR2018-05-14 create examyear_list
    # NB: if user not authenticated examyear_list is not used in base.html

    #examyear_list: [{'pk': '2', 'examyear': '2019', 'is_user_examyear': False},
    #                  {'pk': '1', 'examyear': '2018', 'is_user_examyear': False}]

    # logger.debug('get_examyear_list request_user: ' + str(request_user.country))
    examyear_list = []
    if request_user is not None:
        # logger.debug('get_examyear_list request_user: ' + str(request_user))
        if request_user.country is not None:
            # logger.debug('get_examyear_list request_user.country: ' + str(request_user.country))
            # show only examyears in request_user.country
            for item in Examyear.objects.filter(country=request_user.country):
                # PR 2018-05-19 current examyear = request.user.examyear, this_examyear = year(now) or 1 + year(now)
                # current examyear cannot be selected in dropdown list
                is_user_examyear = False
                if request_user.examyear is not None:
                    if item == request_user.examyear:
                        is_user_examyear = True
                row_dict = {'pk':str(item.id), 'examyear':item.examyear, 'is_user_examyear':is_user_examyear }
                logger.debug('get_examyear_list row_dict: ' + str(row_dict))
                examyear_list.append(row_dict)
    return examyear_list


def get_schooldefault_list(request_user):
    # PR2018-05-28 school_list: [{'pk': '1', 'school': 'SXM01 -  Milton Peters College', 'is_cur_school': False}
    # PR2018-08-04 omit schoolcoede when user is School
    schooldefault_list = []
    if request_user is not None:
        if request_user.country is not None:
            # show only schools in request_user.country
            for schooldefault in Schooldefault.objects.filter(country=request_user.country):
                _school_name = ''
                # current school cannot be selected in dropdown list
                is_cur_school = False
                if request_user.schooldefault is not None:
                    if schooldefault == request_user.schooldefault:
                        is_cur_school = True

                # TODO: display schoolname of current examyear, if not exists: display schoolname
                #if request_user.examyear is not None:
                #    for school in School.objects.filter(examyear=request_user.examyear and schoolcode=schoolcode):
                #        school_name = schoolcode.schoolcode + ' - ' + schoolcode.schoolname
                #else:

                # PR2018-08-04 omit schoolcode when request_user role=School
                if request_user.is_role_insp_or_system:
                    _school_name = schooldefault.code + ' - ' + schooldefault.name
                else:
                    _school_name = schooldefault.name

                row_dict = {'pk':str(schooldefault.id), 'school':_school_name, 'is_cur_school':is_cur_school }
                # logger.debug('get_schooldefault_list row_dict: ' + str(row_dict))
                schooldefault_list.append(row_dict)

    return schooldefault_list


def get_department_list(request_user):
    logger.debug('get_department_list')
    # PR2018-08-24 dep_list: [{'pk': '1', 'department': 'Vsbo', 'is_cur_dep': False}
    dep_list = []
    logger.debug('get_department_list request_user: ' + str(request_user))
    if request_user is not None:
        logger.debug('get_department_list request_user is not None: ')
        if request_user.schooldefault is not None:
            # show only departments in request_user.schooldefault

            # school_departments = request_user.schooldefault
            for item in Department.objects.filter(country=request_user.country):
                _dep_name = ''
                # current department cannot be selected in dropdown list
                _is_cur_dep = False

                logger.debug('get_department_list item: ' + str(item.shortname))

                if request_user.department is not None:
                    if item == request_user.department:
                        _is_cur_dep = True

                # TODO: display schoolname of current examyear, if not exists: display schoolname
                #if request_user.examyear is not None:
                #    for school in School.objects.filter(examyear=request_user.examyear and schoolcode=schoolcode):
                #        school_name = schoolcode.schoolcode + ' - ' + schoolcode.schoolname
                #else:

                # PR2018-08-04 omit schoolcode when request_user role=School
                if item.shortname:
                    _dep_name = item.shortname

                row_dict = {'pk':str(item.id), 'dep_name':_dep_name, 'is_cur_dep':_is_cur_dep }
                # logger.debug('get_schooldefault_list row_dict: ' + str(row_dict))

                logger.debug('get_department_list row_dict: ' + str(row_dict))
                dep_list.append(row_dict)

    return dep_list


# PR2018-07-23
def get_country_choices_all():
    # PR2018-07-20 function creates list of countries, used in SubjectdefaultAddForm and SubjectdefaultEditForm
    # countries_choices: [(1, 'cur'), (2, 'sxm')]
    # choises must be tuple or list, dictionary gives error: 'int' object is not iterable
    choices = []
    countries = Country.objects.all()
    for country in countries:
        if country:
            item = (country.id, country.name)
            choices.append(item)
    return choices


def get_schooldefault_choices_all(request_user):
    # PR2018-08-01  this function is used in UserAddForm, in UserEditForm

    # RequestUser role = School:
        # RequestUser cannot change their own country and school
        # RequestUser Admin: at Add: can only add users with country=RequestUser.country and defaultschool=RequestUser.defaultschool
        #                    at Edit: country and school cannot be modified

    # RequestUser role = Inspection:
        # Inspection users can change their own school, not their own country
        # RequestUser Admin: at Add: can only add Inspection users, country is RequestUser's country, leave school blank
        # RequestUser Admin: at Edit Inspection users: country is locked, RequestUser cannot change school

    # RequestUser role = System:
        # System Users can edit their own country and school
        # RequestUser Admin: at Add: can add school users, set country and school of that country
        #                    at Add: can add Inspection users, set country, leave school blank
        #                    at Add: can add System users, leave country and school blank

        # RequestUser Admin: at Edit School users: country and school cannot be modified
        #                    at Edit Inspection users: country cannot be modified, RequestUser cannot change school
        #                    at Edit System users: RequestUser cannot change country or school

    # PR2018-07-28  Show only schools from selecteduser.country
    # self = request_user, not selected_user when called by UserEditForm
    """
    if is_AddMode:
        if request_user.is_role_school:
            # SelectedUser's country = RequestUser's country
            # SelectedUser's school = RequestUser's school
        elif request_user.is_role_insp:
            if selected_user.is_role_school:
                # SelectedUser's country = RequestUser's country
                # SelectedUser's school can be set by RequestUser, only schools of SelectedUser's country
            if selected_user.is_role_insp:
                # SelectedUser's country = RequestUser's country
                # SelectedUser's school = blank
        elif request_user.is_role_system:
            if selected_user.is_role_school:
                # SelectedUser's country can be set by RequestUser
                # SelectedUser's school can be set by RequestUser, only schools of SelectedUser's country
            if selected_user.is_role_insp:
                # SelectedUser's country can be set by RequestUser
                # SelectedUser's school = blank
            if selected_user.is_role_system:
                # SelectedUser's country = blank
                # SelectedUser's school = blank
    else: # is_EditMode
        if request_user == selected_user:
            # user changes his own country / school
            if selected_user.is_role_school:
                # SelectedUser's country cannot be changed
                # SelectedUser's school cannot be changed
            if selected_user.is_role_insp:
                # SelectedUser's country cannot be changed
                # SelectedUser's school can be set by SelectedUser, only schools of SelectedUser's country
            if selected_user.is_role_system:
                # SelectedUser's country can be set by SelectedUser
                # SelectedUser's school can be set by SelectedUser, only schools of SelectedUser's country
        else:
            # RequestUser changes SelectedUser's country / school
            if request_user.is_role_school:
                # SelectedUser's country cannot be changed
                # SelectedUser's school cannot be changed
            elif request_user.is_role_insp:
                if selected_user.is_role_school:
                    # SelectedUser's country cannot be changed
                    # SelectedUser's school cannot be changed
                if selected_user.is_role_insp:
                    # SelectedUser's country cannot be changed
                    # SelectedUser's school cannot be changed by RequestUser
            elif request_user.is_role_system:
                if selected_user.is_role_school:
                    # SelectedUser's country cannot be changed
                    # SelectedUser's school cannot be changed
                if selected_user.is_role_insp:
                    # SelectedUser's country cannot be changed
                    # SelectedUser's school cannot be changed by RequestUser
                if selected_user.is_role_system:
                    # SelectedUser's country cannot be changed by RequestUser
                    # SelectedUser's school cannot be changed by RequestUser
        """
    choices = [c.CHOICE_NONE] # CHOICE_NONE = (0, _('None'))

    request_user_countryid = 0
    if request_user:
        if request_user.country:
            request_user_countryid = request_user.country.id

    #if request_user.country:
    # logger.debug('class User(AbstractUser) self.selecteduser_countryid: ' + str(selecteduser_countryid))
    schooldefaults = Schooldefault.objects.filter(country=request_user.country)
    for item in schooldefaults:
        item_str = ''
        if item.code is not None:
            item_str = str(item.code) + ' - '
        if item.name is not None:
            item_str = item_str + str(item.name)
        choices.append((item.id, item_str))

    # logger.debug('class User(AbstractUser) schooldefault_choices: ' + str(choices))
    return choices


def get_dep_list_field_sorted_zerostripped(dep_list):  # PR2018-08-23
    # sort dep_list. List ['16', '15', '0', '18'] becomes ['0', '15', '16', '18']. Necessary, otherwise is_updated will not work properly
    # PR2018-08-27 debug. ALso remove value '0'
    # function will store dep_list as: [;15;16;18;] with delimiters at the beginning and end, zo it can filter  dep_list__contains =";15;"

    dep_list_sorted = sorted(dep_list)
    #logger.debug('get_dep_list_field_sorted_zerostripped dep_list_sorted: <' + str(dep_list_sorted) + '> Type: ' + str(type(dep_list_sorted)))

    sorted_dep_list = ''
    if dep_list_sorted:
        for dep in dep_list_sorted:
            logger.debug('get_dep_list_field_sorted_zerostripped dep: <' + str(dep) + '> Type: ' + str(type(dep)))
            # skip zero
            if dep != '0':
                sorted_dep_list = sorted_dep_list + ';' + str(dep)
    if sorted_dep_list:
        # PR2018-08-30 Was: slice off the first character ';'
        # sorted_dep_list = sorted_dep_list[1:]
        # PR2018-08-30 add delimiter ';' at the end
        sorted_dep_list += ';'

        #logger.debug('get_dep_list_field_sorted_zerostripped sorted_dep_list: <' + str(sorted_dep_list) + '> Type: ' + str(type(sorted_dep_list)))
        return sorted_dep_list
    else:
        return None

def get_tuple_from_list_str(list_str):  # PR2018-08-28
    # get_tuple_from_list_str converts list_str string into tuple,
    # e.g.: list_str='1;2' will be converted to list_tuple=(1,2)
    # empty list = (0,), e.g: 'None'
    dep_list_str = str(list_str)
    list_tuple = tuple()
    if dep_list_str:
        try:
            dep_list_split = dep_list_str.split(';')
            list_tuple = tuple(dep_list_split)
        except:
            pass
    # logger.debug('get_tuple_from_list_str tuple list_tuple <' + str(list_tuple) + '> Type: " + str(list_tuple))
    return list_tuple


