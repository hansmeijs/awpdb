# PR2018-07-20
from django.contrib.auth.decorators import login_required # PR2018-04-01
from django.core.paginator import Paginator # PR2018-07-20
from django.db import connection
from django.db.models.functions import Lower
from django.shortcuts import render, redirect #, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, DeleteView, View, ListView, CreateView

from schools.models import Country, Department, Department_log
from subjects.models import Subjectdefault, Subjectdefault_log, Subject, \
    Level, Level_log, Sector, Sector_log, Scheme, Scheme_log

from subjects.forms import SubjectdefaultAddForm, SubjectdefaultEditForm, SubjectAddForm, \
    LevelAddForm, LevelEditForm, SectorAddForm, SectorEditForm, \
    SchemeAddForm, SchemeEditForm

from awpdb import functions as f

# PR2018-04-27
import logging
logger = logging.getLogger(__name__)

# PR2018-05-06
from django.utils.translation import activate, get_language_info, ugettext_lazy as _

"""

# from https://simpleisbetterthancomplex.com/tips/2016/09/27/django-tip-15-cbv-mixins.html

class GetFormKwargsMixin(object):
    @property
    def form_valid_message(self):
        return NotImplemented

    form_invalid_message = 'Please correct the errors below.'

    def form_valid(self, form):
        messages.success(self.request, self.form_valid_message)
        return super(FormMessageMixin, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, self.form_invalid_message)
        return super(FormMessageMixin, self).form_invalid(form)

"""

# === Level =====================================
@method_decorator([login_required], name='dispatch')
class LevelListView(ListView):  # PR2018-08-11

    def get(self, request):
        _params = f.get_headerbar_param(request, {'select_country': True})
        if request.user.country is not None:
            # filter Levels of request.user.country
            levels = Level.objects.filter(country=request.user.country)
            _params.update({'levels': levels})
        return render(request, 'level_list.html', _params)


@method_decorator([login_required], name='dispatch')
class LevelAddView(CreateView):  # PR2018-08-11
    def get(self, request, *args, **kwargs):
        form = LevelAddForm(request=request)
        _param = f.get_headerbar_param(request, {'form': form, 'display_country': True})
        return render(request, 'level_add.html', _param)

    def post(self, request, *args, **kwargs):
        form = LevelAddForm(request.POST, request=request)

        if form.is_valid():
            level = form.save(commit=False)

            # ======  save field 'dep_list_field'  ============
            _clean_dep_list_field = form.cleaned_data.get('dep_list_field')  # Type: <class 'list'>
            level.dep_list = f.get_dep_list_field_sorted_zerostripped(_clean_dep_list_field)

            level.save(request=self.request)
            return redirect('level_list_url')
        else:
            """If the form is invalid, render the invalid form."""
            _param = f.get_headerbar_param(request, {'form': form, 'display_country': True})
            return render(request, 'level_add.html', _param)

@method_decorator([login_required], name='dispatch')
class LevelEditView(UpdateView):  # PR2018-08-11
    model = Level
    form_class = LevelEditForm
    template_name = 'level_edit.html'
    context_object_name = 'level'

    # from https://stackoverflow.com/questions/7299973/django-how-to-access-current-request-user-in-modelform?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    # PR 2018-05-25 add request to kwargs, so it passes request to the form
    def get_form_kwargs(self):
        kwargs = super(LevelEditView, self).get_form_kwargs()
        # add request to kwargs, so it can be passed to form
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        level = form.save(commit=False)

    # ======  save field 'dep_list_field'  ============
        _clean_dep_list_field = form.cleaned_data.get('dep_list_field')  # Type: <class 'list'>
        level.dep_list = f.get_dep_list_field_sorted_zerostripped(_clean_dep_list_field)
        # logger.debug('LevelEditView form_valid level.dep_list: <' + str(level.dep_list) + '> Type: ' + str(type(level.dep_list)))

        # ======  save field 'field_is_active'  ============
        is_active_field = form.cleaned_data.get('is_active_field')
        level.is_active = bool(int(is_active_field))

        level.save(request=self.request)

        return redirect('level_list_url')


@method_decorator([login_required], name='dispatch')
class LevelDeleteView(DeleteView):
    model = Level
    template_name = 'level_delete.html'  # without template_name Django searches for subjectdefault_confirm_delete.html
    success_url = reverse_lazy('level_list_url')


@method_decorator([login_required], name='dispatch')
class LevelLogView(View):
    def get(self, request, pk):
        level_log = Level_log.objects.filter(level_id=pk).order_by('-modified_at')
        level = Level.objects.get(id=pk)
        _param = f.get_headerbar_param(request,  {'level_log': level_log, 'level': level})
        return render(request, 'level_log.html', _param)


# === Sector =====================================
@method_decorator([login_required], name='dispatch')
class SectorListView(ListView):  # PR2018-08-23

    def get(self, request):
        _params = f.get_headerbar_param(request, {'select_country': True})
        if request.user.country is not None:
            # filter Sectors of request.user.country
            sectors = Sector.objects.filter(country=request.user.country)
            _params.update({'sectors': sectors})
        return render(request, 'sector_list.html', _params)


@method_decorator([login_required], name='dispatch')
class SectorAddView(CreateView):  # PR2018-08-24
    def get(self, request, *args, **kwargs):
        form = SectorAddForm(request=request)
        _params = f.get_headerbar_param(request, {'form': form, 'display_country': True})
        return render(request, 'sector_add.html', _params)

    def post(self, request, *args, **kwargs):
        form = SectorAddForm(request.POST, request=request)
        if form.is_valid():
            sector = form.save(commit=False)

            # ======  save field 'dep_list_field'  ============
            _clean_dep_list_field = form.cleaned_data.get('dep_list_field')  # Type: <class 'list'>
            sector.dep_list = f.get_dep_list_field_sorted_zerostripped(_clean_dep_list_field)

            sector.save(request=self.request)
            return redirect('sector_list_url')
        else:
            """If the form is invalid, render the invalid form."""
            _param = f.get_headerbar_param(request, {'form': form, 'display_country': True})
            return render(request, 'sector_add.html', _param)


@method_decorator([login_required], name='dispatch')
class SectorEditView(UpdateView):  #PR2018-09-04
        model = Sector
        form_class = SectorEditForm
        template_name = 'sector_edit.html'
        context_object_name = 'sector'

        # from https://stackoverflow.com/questions/7299973/django-how-to-access-current-request-user-in-modelform?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
        # PR 2018-05-25 add request to kwargs, so it passes request to the form
        def get_form_kwargs(self):
            kwargs = super(SectorEditView, self).get_form_kwargs()
            # add request to kwargs, so it can be passed to form
            kwargs.update({'request': self.request})
            return kwargs

        def form_valid(self, form):
            sector = form.save(commit=False)

            # ======  save field 'dep_list_field'  ============
            _clean_dep_list_field = form.cleaned_data.get('dep_list_field')  # Type: <class 'list'>
            sector.dep_list = f.get_dep_list_field_sorted_zerostripped(_clean_dep_list_field)
            # logger.debug('SectorEditView form_valid sector.dep_list: <' + str(sector.dep_list) + '> Type: ' + str(type(sector.dep_list)))

            # ======  save field 'field_is_active'  ============
            is_active_field = form.cleaned_data.get('is_active_field')
            sector.is_active = bool(int(is_active_field))

            sector.save(request=self.request)

            return redirect('sector_list_url')


@method_decorator([login_required], name='dispatch')
class SectorDeleteView(DeleteView):
    model = Sector
    template_name = 'sector_delete.html'  # without template_name Django searches for subjectdefault_confirm_delete.html
    success_url = reverse_lazy('sector_list_url')


@method_decorator([login_required], name='dispatch')
class SectorLogView(View):
    def get(self, request, pk):
        sector_log = Sector_log.objects.filter(sector_id=pk).order_by('-modified_at')
        sector = Sector.objects.get(id=pk)
        _param = f.get_headerbar_param(request, {'sector_log': sector_log, 'sector': sector})
        return render(request, 'sector_log.html', _param)


# === Scheme =====================================
@method_decorator([login_required], name='dispatch')
class SchemeListView(ListView):  # PR2018-08-23

    def get(self, request):
        _param = f.get_headerbar_param(request, {'display_country': True, 'select_examyear': True, })
        if request.user.country is not None:
            if request.user.examyear is not None:
                schemes = Scheme.objects.filter(examyear=request.user.examyear)
                _param.update({'schemes': schemes})
        return render(request, 'scheme_list.html', _param)


@method_decorator([login_required], name='dispatch')
class SchemeAddView(CreateView):  # PR2018-08-24
    def get(self, request, *args, **kwargs):
        form = SchemeAddForm(request=request)
        _param = f.get_headerbar_param(request, {'form': form, 'display_country': True, 'display_examyear': True, })
        return render(request, 'scheme_add.html', _param)

    def post(self, request, *args, **kwargs):
        form = SchemeAddForm(request.POST, request=request)
        if form.is_valid():
            scheme = form.save(commit=False)

            # ======  save field 'dep_list_field'  ============
            _clean_dep_list_field = form.cleaned_data.get('dep_list_field')  # Type: <class 'list'>
            scheme.dep_list = f.get_dep_list_field_sorted_zerostripped(_clean_dep_list_field)

            scheme.save(request=self.request)
            return redirect('scheme_list_url')
        else:
            """If the form is invalid, render the invalid form."""
            _param = f.get_headerbar_param(request, {'form': form, 'display_country': True, 'display_examyear': True, })
            return render(request, 'scheme_add.html', _param)


@method_decorator([login_required], name='dispatch')
class SchemeEditView(UpdateView):  # PR2018-08-24
    model = Scheme
    form_class = SchemeEditForm
    template_name = 'scheme_edit.html'
    context_object_name = 'scheme'

    def get_form_kwargs(self):
        kwargs = super(SchemeEditView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        scheme = form.save(commit=False)

        # ======  save field 'dep_list_field'  ============
        _clean_dep_list_field = form.cleaned_data.get('dep_list_field')  # Type: <class 'list'>
        scheme.dep_list = f.get_dep_list_field_sorted_zerostripped(_clean_dep_list_field)

        scheme.save(request=self.request)
        return redirect('scheme_list_url')


# === Subjectdefault =====================================
@method_decorator([login_required], name='dispatch')
class SubjectdefaultListView(ListView):
    # PR 2018-07-18 template_name is not necessary, Django looks for <appname>/<model>_list.html
    # template_name = 'subjectdefault_list.html'
    # Django sets context_object_name to the lower cased version of the model class’ name.
    # context_object_name = 'subjectdefaults'

    #queryset = Subjectdefault.objects.all()
    #paginate_by = 10  # After this /country_list/?page=1 will return first 10 countries.

    def get(self, request):
        _params = f.get_headerbar_param(request, {'select_country': True})
        # filter subjectdefaults of request.user.country
        if request.user.country is not None:
            subjectdefaults = Subjectdefault.objects.filter(country=request.user.country).order_by('sequence')
            # add subjectdefaults to headerbar parameters PR2018-08-12
            _params.update({'subjectdefaults': subjectdefaults})
        # render(request object, template name, [dictionary optional]) returns an HttpResponse of the template rendered with the given context.
        return render(request, 'subjectdefault_list.html', _params)

@method_decorator([login_required], name='dispatch')
class SubjectdefaultAddView(CreateView):
    # PR2018-07-20
    def get(self, request, *args, **kwargs):
        # permission: user.is_authenticated AND user.is_role_insp_or_system
        form = SubjectdefaultAddForm(request=request)

        # set headerbar parameters PR 2018-08-06
        param = {'form': form, 'display_school': True}
        headerbar_param = f.get_headerbar_param(request, param)
        # logger.debug('def home(request) headerbar_param: ' + str(headerbar_param))

        # render(request, template_name, context=None (A dictionary of values to add to the template context), content_type=None, status=None, using=None)
        return render(request, 'subjectdefault_add.html', headerbar_param)

    def post(self, request, *args, **kwargs):
        form = SubjectdefaultAddForm(request.POST, request=request) # this one doesn't work: form = Subjectdefault(request=request)

        if form.is_valid():
            subjectdefault = form.save(commit=False)

        # ======  save field 'dep_list_field'  ============
            # get list of department_id's from dep_list_field, save it in subjectdefault.dep_list
            _dep_list_field_str = form.cleaned_data.get('dep_list_field')  # Type: <class 'list'>
            _dep_list_field_sorted = sorted(_dep_list_field_str)
            # logger.debug('SubjectdefaultAddView post form.is_valid _dep_list_field_str: ' + str(_dep_list_field_sorted) + ' Type: ' + str(type(_dep_list_field_sorted)))
            _dep_list = ''
            if _dep_list_field_sorted:
                for dep in _dep_list_field_sorted:
                    _dep_list = _dep_list + ';' + str(dep)
            if _dep_list:
                # slice off the first character ';'
                _dep_list = _dep_list[1:]
                subjectdefault.dep_list = _dep_list
            else:
                subjectdefault.dep_list = None
            # logger.debug('SubjectdefaultAddView _dep_list: ' + str(_dep_list) + ' Type: ' + str(type(_dep_list)))

        # ======  save field 'Country'  ============
            country_list = form.cleaned_data.get('country_list')
            if country_list:
                country_id = int(country_list)
            else:
                country_id = request.user.country.id

            # PR2018-06-08 objects.get gives error: 'matching query does not exist' when record not found (should not be possible)
            # use Country.objects.filter instead
            try:
                country = Country.objects.get(id=country_id)
                if country:
                    subjectdefault.country = request.user.country
            except:
                pass

            subjectdefault.save(request=self.request)

            return redirect('subjectdefault_list_url')
        else:
            logger.debug('SubjectdefaultAddView post form.is NOT_valid: ' + str(form))
            """If the form is invalid, render the invalid form."""
            # set headerbar parameters PR 2018-08-06
            headerbar_param = f.get_headerbar_param(request, {'form': form, 'display_school': True})

            return render(request, 'subjectdefault_add.html', headerbar_param)

@method_decorator([login_required], name='dispatch')
class SubjectdefaultEditView(UpdateView):
    # PR2018-04-17 debug: Specifying both 'fields' and 'form_class' is not permitted.
    model = Subjectdefault
    form_class = SubjectdefaultEditForm
    template_name = 'subjectdefault_edit.html'
    context_object_name = 'subjectdefault'

    # from https://stackoverflow.com/questions/7299973/django-how-to-access-current-request-user-in-modelform?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    # PR 2018-05-25 add request to kwargs, so it passes request to the form
    def get_form_kwargs(self):
        kwargs = super(SubjectdefaultEditView, self).get_form_kwargs()
        # add request to kwargs, so it can be passed to form
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        # PR2018-06-10
        subjectdefault = form.save(commit=False)


    # ======  save field 'dep_list_field'  ============
        # get list of department_id's from dep_list_field, save it in subjectdefault.dep_list
        _dep_list_field_str = form.cleaned_data.get('dep_list_field')  # Type: <class 'list'>
        _dep_list_field_sorted = sorted(_dep_list_field_str)
        # logger.debug('SubjectdefaultEditView _dep_list_field_str: ' + str(_dep_list_field_sorted) + ' Type: ' + str(type(_dep_list_field_sorted)))
        _dep_list = None
        if _dep_list_field_sorted:
            _dep_list = ''
            for dep in _dep_list_field_sorted:
                _dep_list = _dep_list + ';' + str(dep)
            if _dep_list:
                # slice off the first character ';'
                _dep_list = _dep_list[1:]
            else:
                _dep_list = None
        subjectdefault.dep_list = _dep_list
        # logger.debug('SubjectdefaultEditView _dep_list: ' + str(_dep_list) + ' Type: ' + str(type(_dep_list)))

    # get selected countries from field_countrylist, convert it to string, save it in subjectdefault.countrylist
        # value in field_countrylist is tuple: (1,2), value in countrylist is stored as str: '1;2'
        # value '-1' (None) will be removed
        field_countrylist = form.cleaned_data.get('field_countrylist')
        logger.debug('SubjectdefaultEditView >form_valid>field_countrylist = ' + str(field_countrylist) + ' type : ' + str(type(field_countrylist)))

        try:
            delim = ';'
            countrylist_str = delim.join(field_countrylist)
            # wrap countrylist_str in delimiter ';' and check if ';-1;' (None) is in the string
            countrylist_wrap = ';' + countrylist_str + ';'
            if ';-1;' in countrylist_wrap:
                # remove '-1;' from string
                countrylist_str = countrylist_wrap.replace('-1;', '')
                # remove first delimiter
                if countrylist_str[0:1] == ';':
                    countrylist_str = countrylist_str[1:]
                # remove last delimiter
                if countrylist_str[-1:] == ';':
                    countrylist_len = len(countrylist_str)
                    # logger.debug('CountryEditView>form_valid>countrylist_len = ' + str(countrylist_len))
                    countrylist_str = countrylist_str[0:countrylist_len -1]
        except:
            countrylist_str = ''
        #logger.debug('CountryEditView form_valid countrylist_str = ' + str(countrylist_str))

        subjectdefault.countrylist = countrylist_str

    # ======  save field 'field_is_active'  ============
        # PR2018-08-09 get value from field 'field_is_active', save it in user.is_active
        # value in field_is_active is stored as str: '0'=False, '1'=True
        _is_active_field = form.cleaned_data.get('is_active_field')
        # logger.debug('UserEditView form_valid field_is_active: ' +  str(field_is_active) + ' Type: ' + str(type(field_is_active)))
        _is_active = bool(int(_is_active_field))
        subjectdefault.is_active = _is_active

        subjectdefault.save(request=self.request)

        return redirect('subjectdefault_list_url')


@method_decorator([login_required], name='dispatch')
class SubjectdefaultDeleteView(DeleteView):
    model = Subjectdefault
    template_name = 'subjectdefault_delete.html'  # without template_name Django searches for subjectdefault_confirm_delete.html
    success_url = reverse_lazy('subjectdefault_list_url')



@method_decorator([login_required], name='dispatch')
class SubjectdefaultLogView(View):
    # PR 2018-04-22 template_name is not necessary, Django looks for <appname>/<model>_list.html
    # template_name = 'country_list.html'
    # context_object_name = 'countries'
    # paginate_by = 10  After this /country_list/?page=1 will return first 10 countries.

    def get(self, request, pk):
        subjectdefault_log = Subjectdefault_log.objects.filter(subjectdefault_id=pk).order_by('-modified_at')
        subjectdefault = Subjectdefault.objects.get(id=pk)
        _param = {'subjectdefault_log': subjectdefault_log, 'subjectdefault': subjectdefault, 'display_school': True}
        _headerbar_param = f.get_headerbar_param(request, _param)
        # headerbar_param['subjectdefault_log'] = subjectdefault_log
        # headerbar_param['subjectdefault'] = subjectdefault
        # render(request object, template name, [dictionary optional]) returns an HttpResponse of the template rendered with the given context.
        return render(request, 'subjectdefault_log.html', _headerbar_param)

# ========  Subject  =====================================
@method_decorator([login_required], name='dispatch')
class SubjectListView(ListView):
    # PR2018-08-08

    def get(self, request):
        _params = f.get_headerbar_param(request,{'display_country': True, 'display_examyear': True})

        # filter subjects of request.user.examyear
        if request.user.examyear is not None:
            subjects = Subject.objects.filter(examyear=request.user.examyear).order_by('sequence')
            # add subjectdefaults to headerbar parameters PR2018-08-12
            _params.update({'subjects': subjects})

        return render(request, 'subject_list.html', _params)



@method_decorator([login_required], name='dispatch')
class SubjectAddView(CreateView):  # PR2018-08-09

    def get(self, request, *args, **kwargs):
        # permission: user.is_authenticated AND user.is_role_insp_or_system
        form = SubjectAddForm(request=request)

        headerbar_param = f.get_headerbar_param(request, {'form': form, 'display_examyear': True, 'display_school': True})
        return render(request, 'subject_add.html', headerbar_param)

    def post(self, request, *args, **kwargs):
        form = SubjectAddForm(request.POST, request=request) # this one doesn't work: form = Subjectdefault(request=request)

        if form.is_valid():
            subject = form.save(commit=False)
            subject.save(request=self.request)
            return redirect('subject_list_url')
        else:
            """If the form is invalid, render the invalid form."""
            headerbar_param = f.get_headerbar_param(request, {'form': form, 'display_examyear': True, 'display_school': True})
            return render(request, 'subject_add.html', headerbar_param)





