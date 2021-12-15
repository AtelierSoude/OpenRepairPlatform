from copy import deepcopy
from openrepairplatform.user.models import Membership, Fee


rest_memberships_fee = []
rest_memberships = []

Fee.objects.filter(amount=0).delete()
for membership in Membership.objects.all():

    for fee in membership.fees.all():
        fees = membership.fees.filter(date=fee.date, amount=fee.amount)
        if fees.count() > 1:
            for f in fees:
                if f.pk != fee.pk:
                    f.delete()

    if membership.fees.all():
        if membership.fees.count() == 1:
            fee = membership.fees.first()
            fee.date = membership.first_payment
            fee.save()
        else:
            for fee in membership.fees.all():
                if fee.event:
                    fee.date = fee.event.date
                    fee.save()
                else:
                    rest_memberships_fee.append(fee)

        membership.computed_amount()
        membership.save()

for fee in rest_memberships_fee:
    if fee.membership not in rest_memberships:
        rest_memberships.append(fee.membership)

for membership in rest_memberships:
    advised_fee = deepcopy(membership.organization.advised_fee)
    for fee in membership.fees.filter(date__year__gte=2021):
        advised_fee -= fee.amount
        if advised_fee <= 0:
            fee.date = membership.first_payment
            fee.save()
            membership.computed_amount()
            membership.save()
            break
