import factory
from factory.django import DjangoModelFactory

from openrepairplatform.inventory.models import (
    Brand,
    Category,
    Device,
    Stuff,
    Observation,
    Reasoning,
    Action,
    Status,
    RepairFolder,
    Intervention,
)
from openrepairplatform.user.factories import CustomUserFactory


class BrandFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Marque #{n}")

    class Meta:
        model = Brand


class CategoryFactory(DjangoModelFactory):
    """
    Category utilise treebeard MP_Node : on ne peut pas faire Category(name=...).save().
    Il faut passer par add_root() pour creer un noeud racine.
    ---
    Category uses treebeard MP_Node: cannot use Category(name=...).save().
    Must use add_root() to create a root node.
    """
    name = factory.Sequence(lambda n: f"Categorie #{n}")

    class Meta:
        model = Category

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return model_class.add_root(**kwargs)


class DeviceFactory(DjangoModelFactory):
    category = factory.SubFactory(CategoryFactory)
    brand = factory.SubFactory(BrandFactory)
    model = factory.Sequence(lambda n: f"Modele-{n}")

    class Meta:
        model = Device


class StuffFactory(DjangoModelFactory):
    device = factory.SubFactory(DeviceFactory)
    member_owner = factory.SubFactory(CustomUserFactory)
    state = "B"
    is_visible = False

    class Meta:
        model = Stuff


class ObservationFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Observation #{n}")

    class Meta:
        model = Observation


class ReasoningFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Cause #{n}")

    class Meta:
        model = Reasoning


class ActionFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Action #{n}")

    class Meta:
        model = Action


class StatusFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Statut #{n}")

    class Meta:
        model = Status


class RepairFolderFactory(DjangoModelFactory):
    stuff = factory.SubFactory(StuffFactory)
    ongoing = True

    class Meta:
        model = RepairFolder


class InterventionFactory(DjangoModelFactory):
    folder = factory.SubFactory(RepairFolderFactory)
    observation = factory.SubFactory(ObservationFactory)
    reasoning = factory.SubFactory(ReasoningFactory)
    action = factory.SubFactory(ActionFactory)
    status = factory.SubFactory(StatusFactory)

    class Meta:
        model = Intervention
