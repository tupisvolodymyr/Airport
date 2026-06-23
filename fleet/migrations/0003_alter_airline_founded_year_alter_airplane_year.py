from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('fleet', '0002_alter_airline_iata_code_alter_airport_iata_code'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE fleet_airline 
                ALTER COLUMN founded_year TYPE integer 
                USING EXTRACT(YEAR FROM founded_year)::integer;

                ALTER TABLE fleet_airplane 
                ALTER COLUMN year TYPE integer 
                USING EXTRACT(YEAR FROM year)::integer;
            """,
            reverse_sql="""
                ALTER TABLE fleet_airline 
                ALTER COLUMN founded_year TYPE timestamp with time zone 
                USING to_timestamp(founded_year::text, 'YYYY');

                ALTER TABLE fleet_airplane 
                ALTER COLUMN year TYPE timestamp with time zone 
                USING to_timestamp(year::text, 'YYYY');
            """
        ),
        migrations.AlterField(
            model_name='airline',
            name='founded_year',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='airplane',
            name='year',
            field=models.IntegerField(),
        ),
    ]