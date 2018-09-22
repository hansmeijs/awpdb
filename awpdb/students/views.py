# PR2018-09-02
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, DeleteView, View, ListView, CreateView

from schools.models import School
from students.models import Student, Birthcity
from students.forms import StudentAddForm

from awpdb import functions as f

# PR2018-04-27
import logging
logger = logging.getLogger(__name__)



# ========  Student  =====================================
@method_decorator([login_required], name='dispatch')
class StudentListView(ListView):  # PR2018-09-02

    def get(self, request):
        _params = f.get_headerbar_param(request, {'display_examyear': True, 'display_school': True, 'select_dep': True, 'display_user': True})
        # get school from user.examyear and user.schooldefault PR2018-09-03
        if request.user.examyear and request.user.schooldefault and request.user.department:
            school= School.objects.filter(schooldefault=request.user.schooldefault, examyear=request.user.examyear).first()
            if school:
                school= School.objects.filter(schooldefault=request.user.schooldefault, examyear=request.user.examyear).first()
                department = request.user.department
                # filter students of this school and this department
                students = Student.objects.filter(school=school, department=request.user.department)
                _params.update({'school': school})
                _params.update({'students': students})
        return render(request, 'student_list.html', _params)


@method_decorator([login_required], name='dispatch')
class StudentAddView(CreateView): # PR2018-09-03

    def get(self, request, *args, **kwargs):
        # permission: user.is_authenticated AND user.is_role_insp_or_system
        form = StudentAddForm(request=request)

        _param = f.get_headerbar_param(request, {'form': form, 'display_examyear': True, 'display_school': True, 'display_dep': True})
        return render(request, 'student_add.html', _param)

    def post(self, request, *args, **kwargs):
        form = StudentAddForm(request.POST, request=request) # this one doesn't work: form = Subjectdefault(request=request)

        logger.debug('StudentAddView post request.user: ' + str(request.user) + ' type: ' + str(type(request.user)))
        logger.debug('StudentAddView post request.user: ' + str(self.request.user) + ' type: ' + str(type(self.request.user)))
        logger.debug('StudentAddView post request.POST: ' + str(self.request.POST) + ' type: ' + str(type(self.request.POST)))

        if form.is_valid():
            student = form.save(commit=False)

            # ======  save field 'school'  ============
            _school = form.cleaned_data.get('school')
            logger.debug('StudentAddView form.is_valid _school: ' + str(_school) + ' Type: ' + str(type(_school)))
            student.school = _school

            # ======  save field 'department'  ============
            _department = form.cleaned_data.get('department')
            logger.debug('StudentAddView form.is_valid _department: ' + str(_department) + ' Type: ' + str(type(_department)))
            student.department = _department

            # ======  save field 'birthcity_list'  ============
            _birthcity_id = form.cleaned_data.get('birthcity_list')
            logger.debug('StudentAddView form.is_valid birthcity_list: ' + str(_birthcity_id) + ' Type: ' + str(type(_birthcity_id)))
            if _birthcity_id:
                birthcity = Birthcity.objects.get(id=_birthcity_id)
                student.birthcity = birthcity

            student.save(request=self.request)
            return redirect('student_list_url')
        else:
            """If the form is invalid, render the invalid form."""
            _param = f.get_headerbar_param(request, {'form': form, 'display_examyear': True, 'display_school': True})
            return render(request, 'student_add.html', _param)

# PR2018-09-03 from https://simpleisbetterthancomplex.com/tutorial/2018/01/29/how-to-implement-dependent-or-chained-dropdown-list-with-django.html
def load_cities(request):
    logger.debug('load_cities request: ' + str(request) + ' Type: ' + str(type(request)))
    birthcountry_id = request.GET.get('birthcountry_id')
    logger.debug('load_cities country_id ' + str(birthcountry_id) + ' Type: ' + str(type(birthcountry_id)))

    cities = Birthcity.objects.filter(birthcountry_id=birthcountry_id).order_by('name')
    logger.debug('load_cities cities: ' + str(cities) + ' Type: ' + str(type(cities)))

    return render(request, 'dropdown_list_options.html', {'items': cities})


"""

      $(document).ready(function(){
        $("#id_birthcountry").change(function () {
          var url = $("#StudentAddForm").attr("data-cities-url");  // get the url of the `load_cities` view
          var birthcountryId = $(this).val();  // get the selected country ID from the HTML input

          $.ajax({                       // initialize an AJAX request
            url: url,                    // set the url of the request (= localhost:8000/hr/ajax/load-cities/)
            data: {
              'birthcountry': birthcountryId       // add the country id to the GET parameters
            },
            success: function (data) {   // `data` is the return of the `load_cities` view function
              $("#id_birthcity").html(data);  // replace the contents of the city input with the data that came from the server
            }

        });
      });
"""

"""

      $(document).ready(function(){
      // from http://jsfiddle.net/CZcvM/

        var sel = $('#testing'),
            opts =[],
            debug = $('#debug');

      debug.append(typeof sel);
      var opt_array = sel.attr('options');
      //for(var i = 0, len = opt_array.length; i < len; ++i)
      for (var a in opt_array)
      {
          debug.append(a + ':' + opt_array[a] + "<br>");
          //opts.push(opt_array[a]);
      }
      //delete the first option
      function remove()
      {
          $('#testing option:first').remove();
      }

      function restore()
      {
          sel.options.length = 0;
          for(var i = 0, len = opts.length; i < len; ++i)
          {
              //debug.append(a + ':' + opts[a] + '<br>');
              sel.options.add(opts[i]);
          }
      }
      */
      $('#remove').click(remove);
      $('#restore').click(restore);








        $("#testbutton").click(function(){
            $(this).css("background-color", "pink");

            var temp = "myXXValue";

            // Create New Option.
            var newOption = $("<option>");

            newOption.attr("value", temp).text(temp);
            $("#showtext").html(newOption.value);

            // Append that to the DropDownList.
            $('#carselect').append(newOption);

            // Select the Option.
            // $("#carselect" > [value=" + temp + "]").attr("selected", "true");


            $("#showtext").html(temp);

        });
                 // $("p").hover(function(){
                 //        $(this).css("background-color", "yellow");
                 //        }, function(){
                 //        $(this).css("background-color", "pink");
                 //    });
      });
     </script>


"""