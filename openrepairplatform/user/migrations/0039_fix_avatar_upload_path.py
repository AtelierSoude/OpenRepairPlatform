# Migration pour corriger le chemin d'upload des avatars.
# Le champ avatar_img avait upload_to="media/avatar/" alors que MEDIA_ROOT
# est déjà /srv/media/, ce qui créait un double préfixe media/media/avatar/.
#
# Migration to fix avatar upload path.
# The avatar_img field had upload_to="media/avatar/" while MEDIA_ROOT
# is already /srv/media/, creating a double prefix media/media/avatar/.

from django.db import migrations, models


def fix_avatar_paths(apps, schema_editor):
    """
    Retire le préfixe 'media/' des chemins avatar_img existants en BDD.
    Remove the 'media/' prefix from existing avatar_img paths in DB.
    """
    CustomUser = apps.get_model("user", "CustomUser")
    users_with_avatar = CustomUser.objects.filter(
        avatar_img__startswith="media/avatar/"
    )
    for user in users_with_avatar:
        user.avatar_img = user.avatar_img.name.replace(
            "media/avatar/", "avatar/", 1
        )
        user.save(update_fields=["avatar_img"])


def reverse_avatar_paths(apps, schema_editor):
    """
    Remet le préfixe 'media/' pour revenir à l'ancien comportement.
    Re-add the 'media/' prefix to revert to old behavior.
    """
    CustomUser = apps.get_model("user", "CustomUser")
    users_with_avatar = CustomUser.objects.filter(
        avatar_img__startswith="avatar/"
    )
    for user in users_with_avatar:
        user.avatar_img = "media/" + user.avatar_img.name
        user.save(update_fields=["avatar_img"])


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0038_remove_signature_add_source_webhook"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="avatar_img",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="avatar/",
                verbose_name="Avatar",
            ),
        ),
        migrations.RunPython(
            fix_avatar_paths,
            reverse_avatar_paths,
        ),
    ]
