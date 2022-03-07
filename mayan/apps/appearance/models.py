import bleach

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.events.classes import EventManagerSave
from mayan.apps.events.decorators import method_event

from .events import event_theme_created, event_theme_edited

#import RGBColorFie to create GUI select color
from colorful.fields import RGBColorField

#import os for read files
from os import listdir
from os.path import isfile, join

from django.utils.safestring import mark_safe

class Theme(ExtraDataModelMixin, models.Model):
    label = models.CharField(
        db_index=True, help_text=_('A short text describing the theme.'),
        max_length=128, unique=True, verbose_name=_('Label')
    )

    #add color code to model

    logoLink = models.CharField(
        db_index=True, help_text=_('Logo Link.'),
        max_length=300, unique=True, verbose_name=_('Logo Link')
    )

    mmColor = RGBColorField(
        help_text=_('The RGB color values for first main menu bar color.'),
        verbose_name=_('First Main menu Color')
    )

    smmColor = RGBColorField(
        help_text=_('The RGB color values for second main menu color.'),
        verbose_name=_('Second Main menu Color')
    )

    hlColor = RGBColorField(
        help_text=_('The RGB color values for Highlight color.'),
        verbose_name=_('Highlight Color')
    )

    bgColor = RGBColorField(
        help_text=_('The RGB color values for background page color.'),
        verbose_name=_('Backgroud pages color.')
    )

    mtColor = RGBColorField(
        help_text=_('The RGB color values for main text color.'),
        verbose_name=_('main text color.')
    )

    htColor = RGBColorField(
        help_text=_('The RGB color values for help text color.'),
        verbose_name=_('Help text color.')
    )

    bdtColor = RGBColorField(
        help_text=_('The RGB color values for Head text color.'),
        verbose_name=_('body text color.')
    )

    frameColor = RGBColorField(
        help_text=_('The RGB color values for frame background color.'),
        verbose_name=_('frame background color.')
    )

    stylesheet = models.TextField(
        blank=True, help_text=_(
            'The CSS stylesheet to change the appearance of the different'
            'user interface elements.'
        ), verbose_name=_('Stylesheet')
    )

    class Meta:
        ordering = ('label',)
        verbose_name = _('Theme')
        verbose_name_plural = _('Themes')

    def __str__(self):
        return force_text(s=self.label)

    def get_absolute_url(self):
        return reverse(
            viewname='appearance:theme_edit', kwargs={
                'theme_id': self.pk
            }
        )

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'event': event_theme_created,
            'target': 'self',
        },
        edited={
            'event': event_theme_edited,
            'target': 'self',
        }
    )
    def save(self, *args, **kwargs):
        mmColor = self.mmColor
        smmColor = self.smmColor
        hlColor = self.hlColor
        mtColor = self.mtColor
        htColor = self.htColor
        bgColor = self.bgColor
        bdtColor = self.bdtColor
        frameColor = self.frameColor
        logoLink = self.logoLink
        
        css = f"""

        /* Logo Link */

        img.web-logo{{
            background-image: url("{logoLink}");
            background-size: 150px;
            background-repeat: no-repeat;
        }}

        /* First Main menu color */
        
        .container-fluid {{
            background-color: {mmColor};
        }}

        .btn-block{{
            background-color: {mmColor};
            border: 1px solid {mmColor};
        }}

        .btn.btn-primary.btn-xs  {{
            background-color: {mmColor};
        }}

        .btn.btn-primary  {{
            background-color: {mmColor};
            border: 1px solid {mmColor};
        }}

        .list-group-item.btn-sm.active {{
            background-color: {mmColor};
        }}

        .list-group-item.btn-sm.active {{
            background-color: {mmColor};
        }}

        #menu-main {{
            background-color: {mmColor};
        }}

        .panel-heading {{
            background-color: {mmColor};
        }}

        .panel-primary>.panel-heading {{
            background-color: {mmColor};
            border-color: {mmColor};
        }}

        .list-group-item.active {{
            background-color: {mmColor};
        }}

        .nav.navbar-nav.navbar-right li.dropdown.open ul.dropdown-menu a:hover {{
            background: {mmColor};
        }} 

        #accordion-sidebar .panel-heading {{
            background-color: {mmColor};
        }}

        #accordion-sidebar  .panel  div  .panel-body {{
            background-color: {mmColor};
            transition: .1s ease;
        }}

        
        /* Second Main menu color */

        #accordion-sidebar a[aria-expanded="true"] {{
            background-color: {smmColor};
        }}

        .navbar-default .navbar-nav>li>a:hover, .navbar-default .navbar-nav>li>a:focus {{
            color: {smmColor};
            background-color: transparent;
        }}

        #accordion-sidebar > .panel > div > .panel-body > ul > li:hover {{
            background-color: {smmColor};
            transition: .1s ease;
        }}

        .btn-block:hover {{
            background: {smmColor};
        }}

        #accordion-sidebar .panel-heading:hover {{
            background-color: {smmColor};
            transition: .1s ease;
        }}

        .dropdown-menu li a {{
            color: {smmColor};
        }}

        .list-group-item.active:hover {{
            background-color: {smmColor};
        }}

        .text-center.link-text-span.menu-user-name {{
            color: {smmColor};
        }}

        .active.a-main-menu-accordion-link {{
            background-color: {smmColor};
        }}

        #accordion-sidebar > .panel > div > .panel-body > ul > li.active {{
            background: {smmColor};
        }}

        .nav.navbar-nav.navbar-right li.dropdown.open a[aria-expanded="true"] {{
            background: {smmColor};
        }}

        h3#content-title {{
            color: {smmColor};
        }}

        div.toast.toast-success {{
            background: {smmColor};
        }}

        .well .panel-primary .panel-heading{{
            background: {smmColor};
        }}


        /* Highlight color */

        .input-group-btn .btn-default {{
            background-color: {hlColor};
            border: 1px solid {hlColor};
        }}

        .btn.btn-default.btn-outline.btn-xs {{
            background-color: {hlColor};
            border: 1px solid {hlColor};
        }}

        .btn.btn-default.btn-sm {{
            background-color: {hlColor};
            border: 1px solid {hlColor};
        }}

        .well table span a, td a {{
            color: {hlColor};
        }}

        .well table span a, td a:hover {{
            color: {hlColor};
        }}

        .well .panel-heading, .well .svg, .well div > i svg{{
            color: {hlColor};
        }}


         /* BG color */

        body {{
            background-color: {bgColor};
        }}
        
        
        /* Help text color */

        .well div.panel-footer {{
            background: {smmColor}; 
            color: {htColor}; 
        }}

        div.form-group p.help-block {{
            color: {htColor};
        }}


        /* Main text color */

        td.last .btn-list a.btn-primary {{
            color: {mtColor};
        }}

        div.form-group {{
            color: {mtColor};
        }}


        
        /* body text color */

        td.last .btn-list a.btn-default {{
            color: {bdtColor};
        }}

        h3#content-title {{
            color: {bdtColor};
        }}

        div.text-center {{
            color: {bdtColor};
        }}

        /* frame background color */

        div.well {{
            background: {frameColor};
        }}

        """
        self.stylesheet = css
        super().save(*args, **kwargs)


class UserThemeSetting(models.Model):
    user = models.OneToOneField(
        on_delete=models.CASCADE, related_name='theme_settings',
        to=settings.AUTH_USER_MODEL, verbose_name=_('User')
    )
    theme = models.ForeignKey(
        blank=True, null=True, on_delete=models.CASCADE,
        related_name='user_setting', to=Theme, verbose_name=_('Theme')
    )

    class Meta:
        verbose_name = _('User theme setting')
        verbose_name_plural = _('User theme settings')

    def __str__(self):
        return force_text(s=self.user)

class CurrentTheme(models.Model):
    theme = models.ForeignKey(
        blank=True, null=True, on_delete=models.CASCADE,
        related_name='CurrentTheme', to=Theme, verbose_name=_('CurrentTheme')
    )

    class Meta:
        verbose_name = _('CurrentTheme')
        verbose_name_plural = _('CurrentTheme')

    def __str__(self): 
        return force_text(s=self.theme)

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super().save(*args, **kwargs)