from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import ContextMixin
from edc_locator.action_items import SUBJECT_LOCATOR_ACTION


class SubjectLocatorViewMixinError(Exception):
    pass


class SubjectLocatorViewMixin(ContextMixin):

    """Adds subject locator to the context.

    Declare with SubjectIdentifierViewMixin.
    """

    subject_locator_model_wrapper_cls = None
    subject_locator_model = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.subject_locator_model_wrapper_cls:
            raise SubjectLocatorViewMixinError(
                'subject_locator_model_wrapper_cls must be a valid ModelWrapper. Got None')
        if not self.subject_locator_model:
            raise SubjectLocatorViewMixinError(
                'subject_locator_model must be a model (label_lower). Got None')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wrapper = self.subject_locator_model_wrapper_cls(
            model_obj=self.subject_locator)
        context.update(subject_locator=wrapper)
        self.get_subject_locator_or_message()
        return context

    def get_subject_locator_or_message(self):
        obj = None
        subject_identifier = self.kwargs.get('subject_identifier')
        try:
            obj = self.subject_locator_model_cls.objects.get(
                subject_identifier=subject_identifier)
        except ObjectDoesNotExist:
            action_item_model_cls = (
                self.subject_locator_model_cls.action_cls.action_item_model_cls())
            try:
                action_item_model_cls.objects.get(
                    subject_identifier=subject_identifier,
                    action_type__name=SUBJECT_LOCATOR_ACTION)
            except ObjectDoesNotExist:
                self.subject_locator_model_cls.action_cls(
                    subject_identifier=subject_identifier)
#             try:
#                 ActionItem.objects.get(
#                     subject_identifier=subject_identifier,
#                     name=action_name)
#             except ObjectDoesNotExist:
#                 add_url = self.subject_locator_model_cls().get_absolute_url()
#                 verbose_name = self.subject_locator_model_cls._meta.verbose_name
#                 next_querystring = (f'next=subject_dashboard_url,subject_identifier&'
#                                     f'subject_identifier={subject_identifier}')
#                 messages.warning(self.request, mark_safe(
#                     f'Please complete the <a href="{add_url}?{next_querystring}" '
#                     f'title="Add {verbose_name}">{verbose_name}</a> form.'))
        return obj

    @property
    def subject_locator_model_cls(self):
        try:
            model_cls = django_apps.get_model(self.subject_locator_model)
        except LookupError as e:
            raise SubjectLocatorViewMixinError(
                f'Unable to lookup subject locator model. '
                f'model={self.subject_locator_model}. Got {e}')
        return model_cls

    @property
    def subject_locator(self):
        """Returns a model instance either saved or unsaved.

        If a save instance does not exits, returns a new unsaved instance.
        """
        model_cls = self.subject_locator_model_cls
        try:
            subject_locator = model_cls.objects.get(
                subject_identifier=self.kwargs.get('subject_identifier'))
        except ObjectDoesNotExist:
            subject_locator = model_cls(
                subject_identifier=self.kwargs.get('subject_identifier'))
        return subject_locator
