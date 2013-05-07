# -*- coding: utf-8 -*_
"""
Views for creating, editing, deleting and listing projects.
"""
from flask import Blueprint

projects = Blueprint('projects', __name__, template_folder='templates')

# Must be imported after projects Blueprint is contructed
# due to circular dependency.
from notifico.views.projects.hook import *
from notifico.views.projects.project import *
