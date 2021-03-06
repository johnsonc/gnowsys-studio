# Copyright (c) 2011,  2012 Free Software Foundation

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as
#     published by the Free Software Foundation, either version 3 of the
#     License, or (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.

#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.


# This project incorporates work covered by the following copyright and permission notice:  

#    Copyright (c) 2009, Julien Fache
#    All rights reserved.

#    Redistribution and use in source and binary forms, with or without
#    modification, are permitted provided that the following conditions
#    are met:

#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in
#      the documentation and/or other materials provided with the
#      distribution.
#    * Neither the name of the author nor the names of other
#      contributors may be used to endorse or promote products derived
#      from this software without specific prior written permission.

#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
#    FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
#    COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
#    INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#    HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
#    STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
#    OF THE POSSIBILITY OF SUCH DAMAGE.

# Copyright (c) 2011,  2012 Free Software Foundation

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as
#     published by the Free Software Foundation, either version 3 of the
#     License, or (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.

#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
Module where admin tools dashboard classes are defined.
"""

from django.template.defaultfilters import slugify
from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from grappelli.dashboard import modules
from grappelli.dashboard.utils import get_admin_site_name
from django import forms

class Dashboard(object):
    """
    Base class for dashboards.
    The Dashboard class is a simple python list that has three additional
    properties:
    
    ``title``
        The dashboard title, by default, it is displayed above the dashboard
        in a ``h2`` tag. Default value: 'Dashboard'.
    
    ``template``
        The template to use to render the dashboard.
        Default value: 'admin_tools/dashboard/dashboard.html'
    
    ``columns``
        An integer that represents the number of columns for the dashboard.
        Default value: 2.
    
    If you want to customize the look of your dashboard and it's modules, you
    can declare css stylesheets and/or javascript files to include when
    rendering the dashboard (these files should be placed in your
    media path), for example::
    
        from admin_tools.dashboard import Dashboard
        
        class MyDashboard(Dashboard):
            class Media:
                css = {
                    'all': (
                        'css/mydashboard.css',
                        'css/mystyles.css',
                    ),
                }
                js = (
                    'js/mydashboard.js',
                    'js/myscript.js',
                )
                
    Here's an example of a custom dashboard::
    
        from django.core.urlresolvers import reverse
        from django.utils.translation import ugettext_lazy as _
        from admin_tools.dashboard import modules, Dashboard
        
        class MyDashboard(Dashboard):
            
            # we want a 3 columns layout
            columns = 3
            
            def __init__(self, **kwargs):
                
                # append an app list module for "Applications"
                self.children.append(modules.AppList(
                    title=_('Applications'),
                    exclude=('django.contrib.*',),
                ))
                
                # append an app list module for "Administration"
                self.children.append(modules.AppList(
                    title=_('Administration'),
                    models=('django.contrib.*',),
                ))
                
                # append a recent actions module
                self.children.append(modules.RecentActions(
                    title=_('Recent Actions'),
                    limit=5
                ))
    
    """

    # Using Django's Media meta class
    __metaclass__ = forms.MediaDefiningClass
    def _media(self):
        return forms.Media()
    media = property(_media)

    title = _('Dashboard')
    template = 'grappelli/dashboard/dashboard.html'
    columns = 2
    children = None
    
    def __init__(self, **kwargs):
        for key in kwargs:
            if hasattr(self.__class__, key):
                setattr(self, key, kwargs[key])
        self.children = self.children or []
    
    def init_with_context(self, context):
        """
        Sometimes you may need to access context or request variables to build
        your dashboard, this is what the ``init_with_context()`` method is for.
        This method is called just before the display with a
        ``django.template.RequestContext`` as unique argument, so you can
        access to all context variables and to the ``django.http.HttpRequest``.
        """
        pass
    
    def get_id(self):
        """
        Internal method used to distinguish different dashboards in js code.
        """
        return 'dashboard'


class DefaultIndexDashboard(Dashboard):
    """
    The default dashboard displayed on the admin index page.
    To change the default dashboard you'll have to type the following from the
    commandline in your project root directory::
    
        python manage.py customdashboard
    
    And then set the `GRAPPELLI_INDEX_DASHBOARD`` settings variable to
    point to your custom index dashboard class.
    """
    
    def init_with_context(self, context):
        site_name = get_admin_site_name(context)
        # append a link list module for "quick links"
        self.children.append(modules.LinkList(
            _('Quick links'),
            layout='inline',
            draggable=False,
            deletable=False,
            collapsible=False,
            children=[
                [_('Return to site'), '/'],
                [_('Change password'),
                 reverse('%s:password_change' % site_name)],
                [_('Log out'), reverse('%s:logout' % site_name)],
            ]
        ))
        
        # append an app list module for "Applications"
        self.children.append(modules.AppList(
            _('Applications'),
            exclude=('django.contrib.*',),
        ))
        
        # append an app list module for "Administration"
        self.children.append(modules.AppList(
            _('Administration'),
            models=('django.contrib.*',),
        ))
        
        # append a recent actions module
        self.children.append(modules.RecentActions(_('Recent Actions'), 5))
        
        # append a feed module
        self.children.append(modules.Feed(
            _('Latest Django News'),
            feed_url='http://www.djangoproject.com/rss/weblog/',
            limit=5
        ))
        
        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _('Support'),
            children=[
                {
                    'title': _('Django documentation'),
                    'url': 'http://docs.djangoproject.com/',
                    'external': True,
                },
                {
                    'title': _('Django "django-users" mailing list'),
                    'url': 'http://groups.google.com/group/django-users',
                    'external': True,
                },
                {
                    'title': _('Django irc channel'),
                    'url': 'irc://irc.freenode.net/django',
                    'external': True,
                },
            ]
        ))


