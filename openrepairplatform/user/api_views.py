import hmac
import hashlib
from openrepairplatform.user.models import CustomUser, Organization, Membership, Fee, WebHook, SourceChoice
from openrepairplatform.user.serializers import CustomUserSerializer, HelloAssoWebhookSerializer, WebHookSerializer
from rest_framework.generics import RetrieveAPIView, CreateAPIView
from rest_framework.permissions import BasePermission, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from rest_framework.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _


class OrganizationOwner(BasePermission):
    def has_permission(self, request, view):
        authenticated = request.user and request.user.is_authenticated
        manager_organizations = (
            request.user.active_organizations.all().union(
                request.user.volunteer_organizations.all(),
                request.user.admin_organizations.all()
            )
        )
        return bool(authenticated and manager_organizations)


class CustomUserAPIView(RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [OrganizationOwner]

class MembershipAPIView(RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class MembershipWebhookView(viewsets.ViewSet):
    """
    ViewSet pour traiter les webhooks entrants de HelloAsso ou TiBillet.
    Cette vue est volontairement verbeuse et explicite pour faciliter la maintenance.
    Elle n'utilise pas les classes génériques de DRF (sucres syntaxiques).

    ViewSet to process incoming webhooks from HelloAsso or TiBillet.
    This view is intentionally verbose and explicit for easier maintenance.
    It does not use DRF generic classes (syntactic sugar).
    """
    permission_classes = [AllowAny]

    def create(self, request, webhook_pk=None):
        """
        Action pour traiter le payload du webhook et créer une adhésion.
        
        Action to process the webhook payload and create a membership.

        Exemple de test avec curl / Example test with curl:
        (Note: x-ha-signature est obligatoire et doit correspondre au HMAC SHA-256 
        du body avec la clé secrète)
        
        curl -X POST http://localhost:8005/api/user/webhook/5f351b5b-9360-4b2a-ad9b-b4ec84b602e8/ \
             -H "Content-Type: application/json" \
             -H "x-ha-signature: ff3ca62addcbf329f74e9abd826fbfd792eefb3c9d1507c02d1aff4e06ddc46c" \
             -d '{"eventType": "Payment", "data": {"date": "2026-02-10T11:50:48Z", "state": "Authorized", "payer": {"email": "test@example.com", "firstName": "John", "lastName": "Doe"}, "items": [{"amount": 1000, "type": "Membership", "name": "Adhésion"}]}, "metadata": {"id": 75698555}}'
        
        Note: Cet exemple fonctionne si la clé de signature enregistrée pour le webhook est :
        AyCM0yTeQd8In2OzdP3R2HGTrYiCA818UCFLhrD9BCnNhTriWLipxEDpsaTbdfec

        Méthode pour générer la signature en Python / Method to generate the signature in Python:
        ```python
        import hmac
        import hashlib
        
        secret_key = "AyCM0yTeQd8In2OzdP3R2HGTrYiCA818UCFLhrD9BCnNhTriWLipxEDpsaTbdfec"
        payload = '{"eventType": "Payment", "data": {"date": "2026-02-10T11:50:48Z", "state": "Authorized", "payer": {"email": "test@example.com", "firstName": "John", "lastName": "Doe"}, "items": [{"amount": 1000, "name": "Adhésion"}]}, "metadata": {"id": 75698555}}' # Corps brut / Raw body
        
        signature = hmac.new(
            secret_key.encode("utf-8"),
            msg=payload.encode("utf-8"),
            digestmod=hashlib.sha256
        ).hexdigest()
        print(signature)
        ```
        """


        # 1. Récupération du WebHook par son UUID (hex) passé dans l'URL
        # 1. Retrieve the WebHook by its UUID (hex) passed in the URL
        webhook = get_object_or_404(WebHook, pk=webhook_pk)
        
        # 2. Vérification de la signature (Authenticité)
        # 2. Signature verification (Authenticity)
        # On récupère la signature reçue dans les en-têtes
        received_signature = request.headers.get("x-ha-signature")
        # On récupère la clé secrète enregistrée pour ce webhook
        secret_key = webhook.signature_public_key


        try :
            # HELLOASSO METHOD
            # Calcul de la signature attendue via HMAC SHA-256 sur le corps brut
            # Computing expected signature via HMAC SHA-256 on raw body
            # request.body contient le corps brut de la requête
            computed_signature = hmac.new(
                secret_key.encode('utf-8'),
                msg=request.body,
                digestmod=hashlib.sha256
            ).hexdigest()

            # Comparaison sécurisée des signatures
            if not received_signature or not hmac.compare_digest(computed_signature, received_signature):
                return Response(
                    {
                        "status": "error",
                        "message": "Invalid signature. Webhook authenticity could not be verified."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            # On en déduit l'organisation et la source HELLOASSO
            source = SourceChoice.SOURCE_HELLOASSO
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": f"An error occurred while verifying webhook authenticity: {e}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        organization = webhook.organization

        # 3. Validation manuelle des données via le Serializer
        # 3. Manual data validation via the Serializer
        serializer = HelloAssoWebhookSerializer(data=request.data)
        
        # On vérifie si les données sont valides (lève une exception 400 en cas d'erreur)
        # Check if data is valid (raises a 400 exception on error)
        serializer.is_valid(raise_exception=True)
        
        # Extraction des données validées
        # Extraction of validated data
        validated_data = serializer.validated_data["data"]
        metadata = serializer.validated_data.get("metadata", {})
        payment_id = metadata.get("id")
        
        # 4. Vérification si le paiement a déjà été traité (id_payment unique)
        # 4. Check if payment has already been processed (unique id_payment)
        # On le fait avant de créer quoi que ce soit pour rester idempotent.
        # We do it before creating anything to remain idempotent.
        if payment_id and Fee.objects.filter(id_payment=str(payment_id)).exists():
            return Response(
                {
                    "status": "error",
                    "message": f"Payment with ID {payment_id} has already been processed."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # 5. Vérification de l'état du paiement (doit être "Authorized")
        # 5. Check payment state (must be "Authorized")
        if validated_data.get("state") != "Authorized":
            return Response(
                {
                    "status": "ignored",
                    "message": f"Payment state '{validated_data.get('state')}' ignored. Only 'Authorized' is processed."
                },
                status=status.HTTP_200_OK
            )


        # 6. Vérification du type du paiement (doit être "Membership")
        # 6. Check payment's type (must be "Membership")
        items = validated_data["items"]

        # Check if any of the items is of type "Membership"
        if not any(item.get("type")=="Membership" for item in items):
            return Response(
                {
                    "status": "ignored",
                    "message": f"Payment type '{items[0].get('type')}' ignored. Only 'Membership' is processed."
                },
                status=status.HTTP_200_OK
            )

        payer_data = validated_data["payer"]
        payment_date = validated_data["date"].date()
        
        # 7. Récupération ou création de l'utilisateur (CustomUser)
        # 7. Retrieve or create the user (CustomUser)
        # On utilise l'email comme identifiant unique
        # We use email as a unique identifier
        user, user_created = CustomUser.objects.get_or_create(
            email=payer_data["email"],
            defaults={
                "first_name": payer_data.get("firstName", ""),
                "last_name": payer_data.get("lastName", ""),
            }
        )
        
        # 8. Récupération ou création de l'adhésion (Membership) pour cet utilisateur et cette organisation
        # 8. Retrieve or create the membership (Membership) for this user and organization
        membership, membership_created = Membership.objects.get_or_create(
            user=user,
            organization=organization,
            defaults={
                "first_payment": payment_date,
                "source": source
            }
        )
        
        # 9. Création de la cotisation (Fee) associée
        # 9. Creation of the associated fee (Fee)
        # On calcule le montant total (HelloAsso fournit les montants en centimes)
        # Calculate the total amount (HelloAsso provides amounts in cents)
        total_amount_cents = sum(item["amount"] for item in items)
        total_amount_unit = total_amount_cents // 100
        
        Fee.objects.create(
            organization=organization,
            membership=membership,
            amount=total_amount_unit,
            date=payment_date,
            payment=Fee.PAYMENT_BANK,  # Paiement en ligne / Online payment
            id_payment=str(payment_id) if payment_id else None
        )
        
        # 10. Retour d'une réponse explicite de succès (201 Created)
        # 10. Return an explicit success response (201 Created)
        return Response(
            {
                "status": "success",
                "message": "Membership and fee processed successfully",
                "user_email": user.email,
                "organization": organization.name
            }, 
            status=status.HTTP_201_CREATED
        )


class WebHookViewSet(viewsets.ViewSet):
    """
    ViewSet pour gérer les WebHooks d'une organisation.
    Permet de lister (list), créer (create) et supprimer (destroy) des webhooks de manière explicite.
    L'organisation est identifiée par son slug passé dans l'URL.
    Seuls les administrateurs de l'organisation peuvent effectuer ces actions.
    
    ViewSet to manage Organization WebHooks.
    Allows listing, creating, and deleting webhooks in an explicit manner.
    The organization is identified by its slug passed in the URL.
    Only organization administrators can perform these actions.
    """
    permission_classes = [IsAuthenticated]

    def get_organization(self, orga_slug):
        """
        Méthode utilitaire explicite pour récupérer l'organisation à partir du slug.
        Elle vérifie également si l'utilisateur actuel fait partie des administrateurs.
        
        Explicit utility method to retrieve the organization from the slug.
        It also checks if the current user is among the administrators.
        """
        # Récupération de l'objet Organization ou erreur 404
        # Retrieving the Organization object or 404 error
        organization = get_object_or_404(Organization, slug=orga_slug)
        
        # Vérification des droits : l'utilisateur doit être dans la liste des admins
        # Rights check: the user must be in the admins list
        if not self.request.user in organization.admins.all():
            raise PermissionDenied(
                _("Accès refusé : Vous n'êtes pas administrateur de cette organisation.")
            )
        
        return organization

    def list(self, request, orga_slug=None):
        """
        Action pour lister les webhooks d'une organisation.
        Tout est explicite : récupération de l'orga, filtrage des webhooks, et sérialisation.
        
        Action to list webhooks of an organization.
        Everything is explicit: organization retrieval, webhook filtering, and serialization.
        """
        # On récupère l'organisation via le slug passé dans l'URL
        # Retrieving the organization via the slug passed in the URL
        organization = self.get_organization(orga_slug)
        
        # Récupération manuelle et explicite des webhooks
        # Manual and explicit retrieval of webhooks
        webhooks = WebHook.objects.filter(organization=organization)
        
        # Sérialisation manuelle
        # Manual serialization
        serializer = WebHookSerializer(webhooks, many=True)
        
        # Retour d'une réponse DRF avec les données sérialisées
        # Returning a DRF response with the serialized data
        return Response(serializer.data)

    def create(self, request, orga_slug=None):
        """
        Action pour créer un nouveau webhook pour une organisation.
        Gère explicitement la validation, la sauvegarde et le support HTMX.
        
        Action to create a new webhook for an organization.
        Explicitly handles validation, saving, and HTMX support.
        """
        # On récupère l'organisation via le slug
        # Retrieving the organization via the slug
        organization = self.get_organization(orga_slug)
        
        # Initialisation du serializer avec les données de la requête
        # Initializing the serializer with the request data
        serializer = WebHookSerializer(data=request.data)
        
        # Validation explicite (si invalide, une exception est levée ou on renvoie 400)
        # Explicit validation (if invalid, an exception is raised or we return 400)
        if serializer.is_valid():
            # Sauvegarde manuelle en injectant l'organisation récupérée
            # Manual save by injecting the retrieved organization
            webhook = serializer.save(organization=organization)
            
            # Détection explicite d'une requête HTMX
            # Explicit detection of an HTMX request
            if "HTTP_HX_REQUEST" in request.META:
                # Si c'est du HTMX, on renvoie un fragment HTML via 'render'
                # If it's HTMX, we return an HTML fragment via 'render'
                return render(
                    request, 
                    "user/webhooks/item.html", 
                    {"webhook": webhook, "organization": organization}
                )
            
            # Sinon on renvoie une réponse JSON standard avec un code 201
            # Otherwise return a standard JSON response with a 201 code
            return Response(
                WebHookSerializer(webhook).data, 
                status=status.HTTP_201_CREATED
            )
        
        # Si le serializer n'est pas valide, on renvoie les erreurs
        # If the serializer is not valid, we return the errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, orga_slug=None, pk=None):
        """
        Action pour supprimer un webhook spécifique.
        Recherche explicite de l'objet et gestion de la réponse HTMX.
        
        Action to delete a specific webhook.
        Explicit object lookup and HTMX response management.
        """
        # On récupère d'abord l'organisation (pour vérification des droits)
        # First retrieve the organization (for rights check)
        organization = self.get_organization(orga_slug)
        
        # Récupération explicite du webhook appartenant à cette organisation
        # Explicit retrieval of the webhook belonging to this organization
        webhook = get_object_or_404(WebHook, pk=pk, organization=organization)
        
        # Suppression manuelle de l'objet
        # Manual deletion of the object
        webhook.delete()
        
        # Détection explicite d'une requête HTMX
        # Explicit detection of an HTMX request
        if "HTTP_HX_REQUEST" in request.META:
            # Pour HTMX, une réponse vide avec succès (200) suffit pour que 
            # hx-swap="outerHTML" supprime l'élément.
            # For HTMX, a successful empty response (200) is enough for 
            # hx-swap="outerHTML" to remove the element.
            return HttpResponse("", status=status.HTTP_200_OK)
            
        # Réponse DRF standard (204 No Content) pour les clients non-HTMX
        # Standard DRF response (204 No Content) for non-HTMX clients
        return Response(status=status.HTTP_204_NO_CONTENT)

