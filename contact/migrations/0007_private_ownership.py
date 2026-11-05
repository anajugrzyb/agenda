from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations, models
import django.db.models.deletion


LEGACY_USERNAME = '__legacy_contacts__'


def preserve_legacy_data(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    Category = apps.get_model('contact', 'Category')
    Contact = apps.get_model('contact', 'Contact')

    needs_legacy_owner = (
        Contact.objects.filter(owner__isnull=True).exists()
        or Category.objects.filter(owner__isnull=True).exists()
    )

    if needs_legacy_owner:
        username = LEGACY_USERNAME
        suffix = 1
        while User.objects.filter(username=username).exists():
            username = f'{LEGACY_USERNAME}_{suffix}'
            suffix += 1

        legacy_user = User(username=username, is_active=False)
        legacy_user.password = make_password(None)
        legacy_user.save()

        Contact.objects.filter(owner__isnull=True).update(owner=legacy_user)
        Category.objects.filter(owner__isnull=True).update(owner=legacy_user)

    for contact in Contact.objects.exclude(category__isnull=True).iterator():
        category = Category.objects.get(pk=contact.category_id)
        if category.owner_id == contact.owner_id:
            continue

        private_category = Category.objects.filter(
            owner_id=contact.owner_id,
            name=category.name,
        ).order_by('pk').first()
        if private_category is None:
            private_category = Category.objects.create(
                owner_id=contact.owner_id,
                name=category.name,
            )
        contact.category_id = private_category.pk
        contact.save(update_fields=('category',))

    duplicate_groups = (
        Category.objects.values('owner_id', 'name')
        .annotate(total=models.Count('id'))
        .filter(total__gt=1)
    )
    for group in duplicate_groups:
        duplicates = Category.objects.filter(
            owner_id=group['owner_id'],
            name=group['name'],
        ).order_by('pk')
        keeper = duplicates.first()
        duplicate_ids = list(duplicates.values_list('pk', flat=True)[1:])
        Contact.objects.filter(category_id__in=duplicate_ids).update(category=keeper)
        Category.objects.filter(pk__in=duplicate_ids).delete()


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contact', '0006_remove_contact_create_date_contact_created_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='owner',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='categories',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(preserve_legacy_data, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='category',
            name='owner',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='categories',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='contact',
            name='owner',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='contacts',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddConstraint(
            model_name='category',
            constraint=models.UniqueConstraint(
                fields=('owner', 'name'),
                name='unique_category_name_per_owner',
            ),
        ),
    ]
