from django.views.generic import TemplateView

"""
This view is used to ensure all paths redirect to the SPA index file.
The actual routing is handled by React Router on the frontend.
"""


class ReactView(TemplateView):
    template_name = "index.html"
