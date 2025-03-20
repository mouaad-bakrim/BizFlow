from django.db import models

class CategorieProduit(models.Model):
    nom = models.CharField(max_length=255, unique=True, verbose_name="Nom de la catégorie")
    description = models.TextField(blank=True, null=True, verbose_name="Description de la catégorie")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Catégorie de produit"
        verbose_name_plural = "Catégories de produits"
        ordering = ['nom']


class Produit(models.Model):
    nom = models.CharField(max_length=255, verbose_name="Nom du produit")
    description = models.TextField(blank=True, null=True, verbose_name="Description du produit")
    categorie = models.ForeignKey('CategorieProduit', on_delete=models.CASCADE, related_name="produits", verbose_name="Catégorie")
    prix_achat = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prix d'achat")
    prix_vente = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prix de vente")
    quantite_en_stock = models.PositiveIntegerField(default=0, verbose_name="Quantité en stock")
    seuil_minimum = models.PositiveIntegerField(default=10, verbose_name="Seuil minimum")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    actif = models.BooleanField(default=True, verbose_name="Produit actif")

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['nom']


class MouvementStock(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name="mouvements", verbose_name="Produit")
    quantite = models.PositiveIntegerField(verbose_name="Quantité")
    type_mouvement = models.CharField(
        max_length=50, choices=[('entree', 'Entrée'), ('sortie', 'Sortie')],
        verbose_name="Type de mouvement"
    )
    date_mouvement = models.DateTimeField(auto_now_add=True, verbose_name="Date du mouvement")
    reference = models.CharField(max_length=100, verbose_name="Référence (facture, bon de commande, etc.)")
    commentaire = models.TextField(blank=True, null=True, verbose_name="Commentaire")

    def __str__(self):
        return f"{self.produit.nom} - {self.type_mouvement} - {self.quantite}"

    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"
        ordering = ['-date_mouvement']


class Approvisionnement(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name="approvisionnements", verbose_name="Produit")
    fournisseur = models.ForeignKey('Fournisseur', on_delete=models.CASCADE, related_name="approvisionnements", verbose_name="Fournisseur")
    quantite = models.PositiveIntegerField(verbose_name="Quantité")
    prix_achat = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prix d'achat")
    date_approvisionnement = models.DateTimeField(auto_now_add=True, verbose_name="Date d'approvisionnement")
    statut = models.CharField(
        max_length=50, choices=[('en_attente', 'En attente'), ('livree', 'Livrée'), ('annulee', 'Annulée')],
        default='en_attente', verbose_name="Statut de l'approvisionnement"
    )

    def __str__(self):
        return f"Approvisionnement {self.produit.nom} - {self.fournisseur.nom}"

    class Meta:
        verbose_name = "Approvisionnement"
        verbose_name_plural = "Approvisionnements"
        ordering = ['-date_approvisionnement']


class Fournisseur(models.Model):
    nom = models.CharField(max_length=255, verbose_name="Nom du fournisseur")
    contact_nom = models.CharField(max_length=255, verbose_name="Nom du contact")
    contact_email = models.EmailField(blank=True, null=True, verbose_name="Email du contact")
    contact_telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone du contact")
    adresse = models.TextField(blank=True, null=True, verbose_name="Adresse")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ['nom']



class Inventaire(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name="inventaires", verbose_name="Produit")
    quantite_initiale = models.PositiveIntegerField(verbose_name="Quantité initiale")
    quantite_finale = models.PositiveIntegerField(verbose_name="Quantité finale")
    date_inventaire = models.DateTimeField(auto_now_add=True, verbose_name="Date de l'inventaire")
    ajustement = models.IntegerField(verbose_name="Ajustement", default=0)
    commentaire = models.TextField(blank=True, null=True, verbose_name="Commentaire")

    def __str__(self):
        return f"Inventaire {self.produit.nom} - {self.date_inventaire}"

    class Meta:
        verbose_name = "Inventaire"
        verbose_name_plural = "Inventaires"
        ordering = ['-date_inventaire']


class CommandeClient(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="commandes")
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name="commandes")
    quantite = models.PositiveIntegerField(verbose_name="Quantité")
    date_commande = models.DateTimeField(auto_now_add=True, verbose_name="Date de la commande")
    statut = models.CharField(
        max_length=50, choices=[('en_attente', 'En attente'), ('livree', 'Livrée'), ('annulee', 'Annulée')],
        default='en_attente', verbose_name="Statut de la commande"
    )

    def __str__(self):
        return f"Commande {self.id} - {self.client.nom}"

    class Meta:
        verbose_name = "Commande Client"
        verbose_name_plural = "Commandes Clients"
        ordering = ['-date_commande']