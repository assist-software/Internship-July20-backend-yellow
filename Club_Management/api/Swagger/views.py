from urllib import request

from rest_framework import schemas, permissions
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.schemas import get_schema_view, openapi
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer

schema_view_docs = get_schema_view(title="Club Management API",
                              public=True,
                              permission_classes=(permissions.AllowAny,),
                              )