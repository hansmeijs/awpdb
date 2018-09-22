# PR2018-05-08 too be changed

# PR2018-03-27
# This doesnt't work in django 2 any more:
# from django.core.urlresolvers import reverse
# changed to
from django.urls import reverse
from menu import Menu, MenuItem

def profile_title(request):
    """
    Return a personalized title for our profile menu item
    """
    # we don't need to check if the user is authenticated because our menu
    # item will have a check that does that for us
    name = request.user.get_full_name() or request.user

    return "%s's Profile" % name

#Menu.add_item("main", MenuItem("Accounts Index",
#                               reverse('home')))

# this item will be shown to users who are not logged in
#Menu.add_item("user", MenuItem("Log in",
#                               reverse('login'),
#                               check=lambda request: not request.user.is_authenticated))

# this will only be shown to logged in users and also demonstrates how to use
# a callable for the title to return a customized title for each request
#Menu.add_item("user", MenuItem(profile_title,
#                               reverse('user_list_url'),
#                               check=lambda request: request.user.is_authenticated))
#Menu.add_item("user", MenuItem("Logout",
#                               reverse('logout'),
#                               check=lambda request: request.user.is_authenticated))

# this only shows to superusers
#Menu.add_item("user", MenuItem("Admin",
#                               reverse("admin:index"),
##                               separator=True,
#                               check=lambda request: request.user.is_superuser))

# for testing
# Add two items to our main menu
Menu.add_item("user", MenuItem("Countries",
                               reverse("country_list_url"),
                               weight=10,
                               icon='tools',
                               check=lambda request: request.user.is_authenticated))

Menu.add_item("user", MenuItem("Exam years",
                               reverse("examyear_list_url"),
                               separator=True,
                               weight=20,
                               check=lambda request: request.user.is_authenticated))
# TODO request.user.is_role_insp_or_system is not working, must find alternative

Menu.add_item("user", MenuItem("Default subjects",
                               reverse("subjectdefault_list_url"),
                               separator=True,
                               weight=30,
                               icon='tools',
                               check=lambda request: request.user.is_authenticated))

Menu.add_item("user", MenuItem("Subjects",
                               reverse("subject_list_url"),
                               separator=True,
                               weight=30,
                               icon='tools',
                               check=lambda request: request.user.is_authenticated))

Menu.add_item("user", MenuItem("Default schools",
                               reverse("schooldefault_list_url"),
                               separator=True,
                               weight=40,
                               icon='tools',
                               check=lambda request: request.user.is_authenticated))

Menu.add_item("user", MenuItem("Schools",
                               reverse("school_list_url"),
                               separator=True,
                               weight=40,
                               icon='tools',
                               check=lambda request: request.user.is_authenticated))

Menu.add_item("user", MenuItem("Departments",
                               reverse("department_list_url"),
                               separator=True,
                               weight=40,
                               icon='tools',
                               check=lambda request: request.user.is_authenticated))


Menu.add_item("user", MenuItem("Levels",
                               reverse("level_list_url"),
                               separator=True,
                               weight=40,
                               icon='tools',
                               check=lambda request: request.user.is_authenticated))

Menu.add_item("user", MenuItem("Sectors",
                               reverse("sector_list_url"),
                               separator=True,
                               weight=40,
                               icon='tools',
                               check=lambda request: request.user.is_authenticated))


Menu.add_item("user", MenuItem("Schemes",
                               reverse("scheme_list_url"),
                               separator=True,
                               weight=40,
                               icon='tools',
                               check=lambda request: request.user.is_authenticated))

Menu.add_item("user", MenuItem("Students",
                               reverse("student_list_url"),
                               separator=True,
                               weight=40,
                               icon='tools',
                               check=lambda request: request.user.is_authenticated))