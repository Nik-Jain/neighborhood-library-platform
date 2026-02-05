# Generated migration for adding database constraints

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_apitoken'),
    ]

    operations = [
        # Add constraints to Book model
        migrations.AddConstraint(
            model_name='book',
            constraint=models.CheckConstraint(
                check=models.Q(total_copies__gte=0),
                name='book_total_copies_non_negative'
            ),
        ),
        migrations.AddConstraint(
            model_name='book',
            constraint=models.CheckConstraint(
                check=models.Q(available_copies__gte=0),
                name='book_available_copies_non_negative'
            ),
        ),
        migrations.AddConstraint(
            model_name='book',
            constraint=models.CheckConstraint(
                check=models.Q(available_copies__lte=models.F('total_copies')),
                name='book_available_lte_total'
            ),
        ),
        
        # Add unique constraint to Borrowing model for active borrowings
        migrations.AddIndex(
            model_name='borrowing',
            index=models.Index(
                fields=['member', 'book', 'returned_at'],
                name='core_borrow_member_book_returned_idx'
            ),
        ),
        migrations.AddConstraint(
            model_name='borrowing',
            constraint=models.UniqueConstraint(
                fields=['member', 'book'],
                condition=models.Q(returned_at__isnull=True),
                name='unique_active_borrowing_per_member_book'
            ),
        ),
        
        # Add constraint to Fine model
        migrations.AddConstraint(
            model_name='fine',
            constraint=models.CheckConstraint(
                check=models.Q(amount__gte=0),
                name='fine_amount_non_negative'
            ),
        ),
    ]
