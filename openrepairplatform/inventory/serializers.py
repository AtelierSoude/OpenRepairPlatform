from rest_framework import serializers

from openrepairplatform.inventory.models import (
    Stuff, Device, Category, RepairFolder, Intervention
)
from openrepairplatform.location.models import (
    Place
)
from openrepairplatform.user.models import (
    CustomUser, Organization
)

class AncestorCategory(serializers.ListField):

    def to_representation(self, data):
        return [self.child.to_representation(item) if item is not None else None for item in data]


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name"]

class PlaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Place
        fields = "__all__"

class OrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = "__all__"

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"

class DeviceSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Device
        fields = ['id', "slug", 'category', 'brand', 'model', 'description', 'picture']

class StuffSerializer(serializers.ModelSerializer):
    place_name = serializers.ReadOnlyField(source='place.name')
    organization_owner_name = serializers.ReadOnlyField(source='organization_owner.name')
    device_name = serializers.ReadOnlyField(source='device.slug')
    category_name = serializers.ReadOnlyField(source='device.category.name')

    class Meta:
        model = Stuff
        fields = "__all__"

class InterventionSerializer(serializers.ModelSerializer):
    observation = serializers.ReadOnlyField(source='observation.name')
    reasoning = serializers.ReadOnlyField(source='reasoning.name')
    action = serializers.ReadOnlyField(source='action.name')
    status = serializers.ReadOnlyField(source='status.name')

    class Meta:
        model = Intervention
        fields = "__all__"

class InterventionPOSTSerializer(serializers.ModelSerializer):

    class Meta:
        model = Intervention
        fields = "__all__"

class RepairFolderSerializer(serializers.ModelSerializer):
    interventions = InterventionSerializer(read_only=True, many=True)
    class Meta:
        model = RepairFolder 
        fields = ['id', 'interventions', 'open_date', 'ongoing', 'stuff']
