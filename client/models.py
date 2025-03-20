from django.db import models

class CategorieClient(models.Model):
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom de la catégorie")
    description = models.TextField(blank=True, null=True, verbose_name="Description de la catégorie")

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = 'Catégorie Client'
        verbose_name_plural = 'Catégories Clients'
        ordering = ['nom']


class Client(models.Model):
    # Informations de base du client
    nom = models.CharField(max_length=200, verbose_name="Nom du client")
    email = models.EmailField(unique=True, verbose_name="Email")
    telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Numéro de téléphone")
    adresse = models.TextField(blank=True, null=True, verbose_name="Adresse")
    ville = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ville")
    pays = models.CharField(max_length=100, blank=True, null=True, verbose_name="Pays")

    # Informations légales et administratives
    ice = models.CharField(max_length=20, unique=True, blank=True, null=True,
                           verbose_name="ICE (Identifiant Commun d'Entreprise)")
    rc = models.CharField(max_length=50, blank=True, null=True,
                          verbose_name="Registre du Commerce (RC)")  # Le registre du commerce de l'entreprise
    if_numero = models.CharField(max_length=30, blank=True, null=True,
                                 verbose_name="Numéro IF (Identifiant Fiscal)")  # Identifiant fiscal
    cnss = models.CharField(max_length=30, blank=True, null=True,
                            verbose_name="Numéro CNSS (si applicable)")  # Pour les entreprises ayant un numéro CNSS

    # Référence unique du client (pour une identification rapide)
    reference_client = models.CharField(
        max_length=50, unique=True, blank=False, verbose_name="Référence Client"
    )  # Cela permet de générer une référence unique pour chaque client

    # Statut du client (actif ou inactif)
    statut = models.CharField(
        max_length=20,
        choices=[('actif', 'Actif'), ('inactif', 'Inactif')],
        default='actif',
        verbose_name="Statut du client"
    )

    # Informations financières
    limite_credit = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, blank=True, null=True,
        verbose_name="Limite de crédit"
    )  # Le crédit maximal du client
    solde = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00,
        verbose_name="Solde actuel"
    )  # Le solde actuel (montant dû ou crédit disponible)

    # Date de création du client
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")

    # Relation avec les commandes du client
    commandes = models.ManyToManyField('Commande', related_name='clients', blank=True, verbose_name="Commandes passées")

    # Relation avec les contacts du client
    contacts = models.ManyToManyField('Contact', related_name='clients', blank=True, verbose_name="Contacts")

    def __str__(self):
        return self.nom

    def montant_total_commandes(self):
        """
        Méthode pour calculer le montant total des commandes passées par ce client.
        Retourne la somme des montants des commandes du client.
        """
        total = sum(commande.total() for commande in self.commandes.all())
        return total

    def update_solde(self, montant):
        """
        Mise à jour du solde du client, en fonction du montant ajouté ou soustrait.
        Exemple : après un paiement, ou après la validation d'une commande.
        """
        self.solde += montant
        self.save()

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ['-date_creation']  # Par défaut, les clients sont classés par date de création décroissante
        unique_together = ['email']  # Assurer l'unicité de l'email
        indexes = [
            models.Index(fields=['email']),  # Créer un index sur l'email pour améliorer les recherches
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(limite_credit__gte=0),
                name='limite_credit_positive'
            )
        ]

class HistoriqueCommande(models.Model):
    commande = models.ForeignKey('Commande', on_delete=models.CASCADE, related_name="historiques")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="historiques")
    statut = models.CharField(max_length=100, verbose_name="Statut de la commande")
    date_modification = models.DateTimeField(auto_now_add=True, verbose_name="Date de modification")
    commentaires = models.TextField(blank=True, null=True, verbose_name="Commentaires")

    def __str__(self):
        return f"{self.commande} - {self.statut}"

    class Meta:
        verbose_name = "Historique de Commande"
        verbose_name_plural = "Historiques de Commandes"
        ordering = ['-date_modification']
