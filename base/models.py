from django.db import models
from simple_history.models import HistoricalRecords
from simple_history import register
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime
from django.core.validators import RegexValidator
from simple_history.signals import pre_create_historical_record
from django.dispatch import receiver
from django.conf import settings
from tree_queries.models import TreeNode
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone


class AbstractBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    # objects = BaseModelManager()

    class Meta:
        abstract = True
        default_permissions = ['add', 'change', 'view', "soft_delete"]

    def soft_delete(self):
        # Get the classes that reference self that are instances of BaseModel and are not soft deleted
        for f in self._meta.get_fields():
            if f.one_to_many or f.one_to_one:
                if issubclass(f.related_model, AbstractBaseModel) and \
                        f.related_model.objects.filter(**{f.field.name: self}, deleted=False).exists():
                    raise ValidationError(
                        "Vous ne pouvez pas supprimer cet élément car il est référencé par au moins un élément de type {0}".format(
                            f.related_model._meta.verbose_name))
        self.deleted = True
        self.save()

    def delete(self):
        return self.soft_delete()

    def save(self, *args, **kwargs):
        if self.deleted and not self.pk:
            raise ValidationError("Vous ne pouvez pas supprimer un objet qui n'est pas encore enregistré.")
        super(AbstractBaseModel, self).save(*args, **kwargs)


# MinValueValidator and MaxValueValidator are used to validate the longitude
if hasattr(settings, "LONGITUDE_MIN_MAX"):
    min_long, max_long = settings.LONGITUDE_MIN_MAX
    longitude_validators = [
        MinValueValidator(min_long),
        MaxValueValidator(max_long)
    ]
else:
    longitude_validators = [
        MinValueValidator(-180),
        MaxValueValidator(180)
    ]
if hasattr(settings, "LATITUDE_MIN_MAX"):
    min_lat, max_lat = settings.LATITUDE_MIN_MAX
    latitude_validators = [
        MinValueValidator(min_lat),
        MaxValueValidator(max_lat)
    ]
else:
    latitude_validators = [
        MinValueValidator(-90),
        MaxValueValidator(90)
    ]


@receiver(pre_create_historical_record)
def pre_create_historical_record_callback(sender, **kwargs):
    instance = kwargs['instance']
    if hasattr(instance, "deleted") and instance.deleted:
        kwargs['history_instance'].history_type = "-"


class Company(AbstractBaseModel):
    class CompanyForms(models.TextChoices):
        SARL = 'sarl', 'SARL'
        SARLAU = 'sarlau', 'SARL AU'
        SA = 'sa', 'SA'

    name = models.CharField(max_length=30, verbose_name="Raison sociale")
    phone = models.CharField(max_length=16, verbose_name="Téléphone", null=True, blank=True)
    address1 = models.CharField(max_length=30, verbose_name="Adresse", null=True, blank=True)
    address2 = models.CharField(max_length=30, verbose_name="Suite", null=True, blank=True)
    city = models.CharField(max_length=15, verbose_name="Ville")
    licence = models.CharField(max_length=15, verbose_name="Patente", null=True, blank=True)
    registration_id = models.CharField(max_length=15, verbose_name="Registre de commerce", null=True, blank=True)
    social_id = models.CharField(max_length=15, verbose_name="Num CNSS", null=True, blank=True)
    tax_id = models.CharField(max_length=15, verbose_name="Identifiant fiscal", null=True, blank=True)
    company_id = models.CharField(max_length=15, verbose_name="ICE", null=True, blank=True)
    company_form = models.CharField(max_length=10, verbose_name="Forme juridique", choices=CompanyForms.choices,
                                    null=True, blank=True)
    logo = models.ImageField(upload_to='logo', blank=True, null=True, verbose_name="Logo")
    history = HistoricalRecords(table_name="base_company_history")

    class Meta(AbstractBaseModel.Meta):
        ordering = ["name"]
        verbose_name = "Société"
        verbose_name_plural = "Sociétés"
        permissions = ()
        db_table = "base_company"

    def __str__(self):
        if self.company_form:
            return "{0} {1}".format(self.name, self.get_company_form_display())
        else:
            return self.name


# Remplace les placeholders lors de la constitution des numéros de commande, BL,...
def replace_sequence_placeholders(s, site):
    if not s:
        return ""

    aujourdhui = datetime.date.today()
    s = s.replace("$(YYYY)", aujourdhui.strftime('%Y'))
    s = s.replace("$(YY)", aujourdhui.strftime('%y'))
    s = s.replace("$(MM)", aujourdhui.strftime('%m'))
    s = s.replace("$(DD)", aujourdhui.strftime("%d"))
    s = s.replace("$(SITE)", site.reference)
    return s


class Regions(models.TextChoices):
    MA01 = "MA01", "Tanger-Tétouan-Al Hoceïma"
    MA02 = "MA02", "L'Oriental"
    MA03 = "MA03", "Fès-Meknès"
    MA04 = "MA04", "Rabat-Salé-Kénitra"
    MA05 = "MA05", "Béni Mellal-Khénifra"
    MA06 = "MA06", "Casablanca-Settat"
    MA07 = "MA07", "Marrakech-Safi"
    MA08 = "MA08", "Drâa-Tafilalet"
    MA09 = "MA09", "Souss-Massa"
    MA10 = "MA10", "Guelmim-Oued Noun"
    MA11 = "MA11", "Laâyoune-Sakia El Hamra"
    MA12 = "MA12", "Dakhla-Oued Ed-Dahab"
    ATRE = "ATRE", "Autre / Etranger"


class Site(AbstractBaseModel):
    name = models.CharField(max_length=30, verbose_name="Nom")
    phone = models.CharField(max_length=16, verbose_name="Téléphone", null=True, blank=True)
    address1 = models.CharField(max_length=30, verbose_name="Adresse", null=True, blank=True)
    address2 = models.CharField(max_length=30, verbose_name="Suite", null=True, blank=True)
    city = models.CharField(max_length=15, verbose_name="Ville", null=True, blank=True)
    reference = models.CharField(max_length=5, verbose_name="Ref", unique=True)
    longitude = models.FloatField(verbose_name="Longitude", validators=longitude_validators)
    latitude = models.FloatField(verbose_name="Latitude", validators=latitude_validators)
    stamp_rate = models.DecimalField(verbose_name="Taux de droits de timbre (%)", default=0,
                                     validators=[MinValueValidator(0), MaxValueValidator(100)],
                                     help_text="Entre 0 et 100", max_digits=6, decimal_places=3)
    company = models.ForeignKey(Company, verbose_name="Société", related_name="sites", on_delete=models.PROTECT)
    region = models.CharField(max_length=6, verbose_name="Région", choices=Regions.choices)
    history = HistoricalRecords(table_name="base_site_history")

    class Meta(AbstractBaseModel.Meta):
        ordering = ["name"]
        verbose_name = "Site"
        verbose_name_plural = "Sites"
        permissions = ()
        db_table = "base_site"

    def __str__(self):
        return self.name

    def invoice_footer(self, *args, **kwargs):
        first_line = self.company.name
        if self.company.phone:
            first_line += " - Tél: " + self.company.phone
        elif self.phone:
            first_line += " - Tél: " + self.phone

        second_line = ""
        if self.company.company_id:
            second_line += " - ICE: " + self.company.company_id

        if self.company.tax_id:
            second_line += " Identifiant Fiscal: " + self.company.tax_id

        if self.company.licence:
            second_line += " - Patente: " + self.company.licence

        if self.company.registration_id:
            second_line += " - RC: " + self.company.registration_id

        if self.company.social_id:
            second_line += " - CNSS: " + self.company.social_id

        if not second_line:
            return "", first_line

        return first_line, second_line

    def save(self, *args, **kwargs):

        resave = False
        if not self.pk:
            resave = True
        super(Site, self).save(*args, **kwargs)
        # Si le site vient d'être créé, on crée l'objet site_sequences qui contient les numéros de séquences des commandes, bls,...
        if resave:
            site_sequences = SiteSequences(site=self)
            site_sequences.save()
            self.save()

    @property
    def ice(self):
        return self.company.ice

    @property
    def rc(self):
        return self.company.rc

    @property
    def cnss(self):
        return self.company.cnss

    @property
    def societe(self):
        return str(self.company)

    @property
    def idf(self):
        return self.company.idf

    @property
    def logo(self):
        return self.company.logo

    def get_so_serial(self):
        if not self.sequences:
            site_sequences = SiteSequences(site=self)
            site_sequences.save()

        prefix = replace_sequence_placeholders(self.sequences.so_prefix, self)
        suffix = replace_sequence_placeholders(self.sequences.so_suffix, self)

        external_id = prefix + str(self.sequences.so_last_sequence + 1).zfill(self.sequences.so_nb_digits) + suffix
        self.sequences.so_last_sequence = self.sequences.so_last_sequence + 1
        self.sequences.save()

        return external_id


class SiteSequences(models.Model):
    site = models.OneToOneField("Site", verbose_name="Site", on_delete=models.PROTECT, related_name='sequences')
    so_last_sequence = models.IntegerField(default=0, verbose_name="Commandes - Dernière seq",
                                           validators=[MinValueValidator(0)])
    so_prefix = models.CharField(max_length=20, verbose_name="Commandes - Préfixe", blank=True, default="SO/$(SITE)/",
                                 help_text="$(YYYY): Année sur 4 chiffres, $(YY): Année sur 2 chiffres, $(MM): Mois,  $(DD): Jour, $(SITE): Référence du site.")
    so_suffix = models.CharField(max_length=20, verbose_name="Commandes - Suffixe", blank=True, default="",
                                 help_text="$(YYYY): Année sur 4 chiffres, $(YY): Année sur 2 chiffres, $(MM): Mois,  $(DD): Jour, $(SITE): Référence du site.")
    so_nb_digits = models.IntegerField(default=7, verbose_name="Commandes - Nombre de chiffres",
                                       validators=[MinValueValidator(3), MaxValueValidator(10)])

    def clean(self):
        if len(replace_sequence_placeholders(self.so_prefix, self.site)) > 10:
            raise ValidationError(
                {'so_prefix': ('Ce champ peut produire des chaines de plus de 10 caractère. Ce qui est interdit')})
        if len(replace_sequence_placeholders(self.so_suffix, self.site)) > 10:
            raise ValidationError(
                {'so_suffix': ('Ce champ peut produire des chaines de plus de 10 caractère. Ce qui est interdit')})

    class Meta:
        default_permissions = []
        db_table = "base_site_sequence"
        verbose_name = "Séquences"


phone_regex = RegexValidator(
    regex=r'^0(|.| |-)(5|6|7|8)((|.| |-)[0-9]){8}$',
    message='Le numéro de téléphone est incorrect.'
)




class Notification(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Lu le")
    title = models.CharField(max_length=100, verbose_name="Titre")
    message = models.CharField(verbose_name="Message")
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.PROTECT,
                                     verbose_name="Type de contenu")
    object_id = models.PositiveIntegerField(verbose_name="ID de l'objet")
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        db_table = "base_notification"
        verbose_name = ('Notification')
        verbose_name_plural = ('Notifications')

    def __str__(self):
        return self.message[:50] + "..." if len(self.message) > 50 else self.message

    @property
    def get_object_url(self):
        print(self.content_object.get_path)
        return self.content_object.get_path

    @property
    def cropped_message(self):
        return self.message[:100] + "..." if len(self.message) > 100 else self.message

    @property
    def is_read(self):
        return self.read_at is not None

    @property
    def short_timesince(self):
        now = timezone.now()

        diff = now - self.created_at
        periods = [
            (diff.days // 365, 'an', 'ans'),
            (diff.days // 30, 'mois', 'mois'),
            (diff.days // 7, 'sem', 'sem'),
            (diff.days, 'j', 'j'),
            (diff.seconds // 3600, 'h', 'h'),
            (diff.seconds // 60 % 60, 'min', 'min'),
            (diff.seconds % 60, 's', 's'),
        ]

        for period, singular, plural in periods:
            if period:
                return f"{period} {singular}" if period == 1 else f"{period} {plural}"
        return "0 s"