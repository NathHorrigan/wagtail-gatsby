from django.conf import settings

from wagtail.contrib.modeladmin.helpers import PermissionHelper
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core.signals import page_published, page_unpublished

from .models import Deployment


class GatsbyPermissions(PermissionHelper):
    def user_can_create(self, user):
        return True

    def user_can_list(self, user):
        return True

    def user_can_edit_obj(self, user, obj):
        return False

    def user_can_delete_obj(self, user, obj):
        return False


class GatsbyDeploymentAdmin(ModelAdmin):
    model = Deployment
    permission_helper_class = GatsbyPermissions
    menu_label = "Gatsby Deployments"
    menu_icon = "collapse-up"
    menu_order = 1000

    list_display = ("deployment_created", "deployment_time", "deployment_created_by")
    form_fields_exclude = ("deployment_created_by", "deployment_time")


modeladmin_register(GatsbyDeploymentAdmin)


def trigger_deployment(**kwargs):
    if hasattr(settings, "GATSBY_AUTO_DEPLOY"):
        if settings.GATSBY_AUTO_DEPLOY:
            user = ""
            if kwargs.get("revision") is not None:
                user = kwargs.get("revision").user

            deployment = Deployment(deployment_created_by=user)
            deployment.save()


page_published.connect(trigger_deployment)
page_unpublished.connect(trigger_deployment)
