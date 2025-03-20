from django.db import models




class Devis(models.Model):
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name="devis", verbose_name="Client")
    numero_devis = models.CharField(max_length=100, unique=True, verbose_name="Numéro du devis")
    date_devis = models.DateTimeField(auto_now_add=True, verbose_name="Date du devis")
    date_expiration = models.DateTimeField(verbose_name="Date d'expiration du devis")
    total_ht = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total HT")
    total_tva = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total TVA")
    total_ttc = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total TTC")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    statut = FSMField(default='en_cours', choices=[('en_cours', 'En cours'), ('livree', 'Livrée'), ('annulee', 'Annulée')], verbose_name="Statut")


    def __str__(self):
        return f"Devis {self.numero_devis} - {self.client.nom}"

    class Meta:
        verbose_name = "Devis"
        verbose_name_plural = "Devis"

class LigneDevis(models.Model):
    devis = models.ForeignKey(Devis, on_delete=models.CASCADE, related_name="lignes_devis", verbose_name="Devis")
    produit = models.ForeignKey('Stock.Produit', on_delete=models.CASCADE, related_name="lignes_devis", verbose_name="Produit")
    quantite = models.PositiveIntegerField(verbose_name="Quantité")
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prix unitaire")
    total_ht = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total HT")
    total_tva = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total TVA")
    total_ttc = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total TTC")

    def __str__(self):
        return f"Ligne Devis {self.id} - {self.produit.nom}"

    class Meta:
        verbose_name = "Ligne de Devis"
        verbose_name_plural = "Lignes de Devis"


class BonCommande(models.Model):
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name="bons_commande", verbose_name="Client")
    numero_commande = models.CharField(max_length=100, unique=True, verbose_name="Numéro du bon de commande")
    date_commande = models.DateTimeField(auto_now_add=True, verbose_name="Date de la commande")
    date_livraison_souhaitee = models.DateTimeField(verbose_name="Date de livraison souhaitée")
    statut = FSMField(default='en_cours', choices=[('en_cours', 'En cours'), ('livree', 'Livrée'), ('annulee', 'Annulée')], verbose_name="Statut")
    total_ht = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total HT")
    total_tva = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total TVA")
    total_ttc = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total TTC")
    description = models.TextField(blank=True, null=True, verbose_name="Description (facultative)")

    def __str__(self):
        return f"Bon de commande {self.numero_commande} - {self.client.nom}"

    class Meta:
        verbose_name = "Bon de commande"
        verbose_name_plural = "Bons de commande"
        ordering = ['-date_commande']

class LigneBonCommande(models.Model):
    bon_commande = models.ForeignKey(BonCommande, on_delete=models.CASCADE, related_name="lignes_bon_commande", verbose_name="Bon de commande")
    produit = models.ForeignKey('Stock.Produit', on_delete=models.CASCADE, related_name="lignes_bon_commande", verbose_name="Produit")
    quantite = models.PositiveIntegerField(verbose_name="Quantité")
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prix unitaire")
    total_ht = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total HT")
    total_tva = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total TVA")
    total_ttc = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total TTC")

    def __str__(self):
        return f"Ligne Bon de Commande {self.id} - {self.produit.nom}"

    class Meta:
        verbose_name = "Ligne de Bon de Commande"
        verbose_name_plural = "Lignes de Bons de Commande"

class BonLivraison(models.Model):
    bon_commande = models.ForeignKey(BonCommande, on_delete=models.CASCADE, related_name="bons_livraison", verbose_name="Bon de commande")
    numero_livraison = models.CharField(max_length=100, unique=True, verbose_name="Numéro du bon de livraison")
    date_livraison = models.DateTimeField(auto_now_add=True, verbose_name="Date de livraison")
    statut = FSMField(default='en_cours',
                      choices=[('en_cours', 'En cours'), ('livree', 'Livrée'), ('annulee', 'Annulée')],
                      verbose_name="Statut")
    transporteur = models.CharField(max_length=100, verbose_name="Transporteur")
    commentaire = models.TextField(blank=True, null=True, verbose_name="Commentaire (facultatif)")

    def __str__(self):
        return f"Bon de livraison {self.numero_livraison} - {self.bon_commande.client.nom}"

    class Meta:
        verbose_name = "Bon de livraison"
        verbose_name_plural = "Bons de livraison"
        ordering = ['-date_livraison']

class LigneBonLivraison(models.Model):
    bon_livraison = models.ForeignKey(BonLivraison, on_delete=models.CASCADE, related_name="lignes_bon_livraison", verbose_name="Bon de livraison")
    produit = models.ForeignKey('Stock.Produit', on_delete=models.CASCADE, related_name="lignes_bon_livraison", verbose_name="Produit")
    quantite_livree = models.PositiveIntegerField(verbose_name="Quantité livrée")
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prix unitaire")
    total_ht = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total HT")
    total_tva = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total TVA")
    total_ttc = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total TTC")

    def __str__(self):
        return f"Ligne Bon de Livraison {self.id} - {self.produit.nom}"

    class Meta:
        verbose_name = "Ligne de Bon de Livraison"
        verbose_name_plural = "Lignes de Bons de Livraison"



class Facture(models.Model):
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name="factures", verbose_name="Client")
    numero_facture = models.CharField(max_length=100, unique=True, verbose_name="Numéro de la facture")
    date_facture = models.DateTimeField(auto_now_add=True, verbose_name="Date de la facture")
    date_echeance = models.DateTimeField(verbose_name="Date d'échéance")
    total_ht = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total HT")
    total_tva = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total TVA")
    total_ttc = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total TTC")
    statut = FSMField(default='en_attente', choices=[('en_attente', 'En attente'), ('payee', 'Payée'), ('partiellement_payee', 'Partiellement payée'), ('annulee', 'Annulée')], verbose_name="Statut")
    montant_remise = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Montant de la remise")

    # Relation avec les bons de livraison
    bons_livraison = models.ManyToManyField('BonLivraison', related_name="factures", verbose_name="Bons de livraison", blank=True)

    def __str__(self):
        return f"Facture {self.numero_facture} - {self.client.nom}"

    @transition(field=statut, source='en_attente', target='payee')
    def mark_as_paid(self):
        pass

    @transition(field=statut, source='*', target='annulee')
    def cancel_invoice(self):
        pass

    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ['-date_facture']
