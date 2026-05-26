from django.db import migrations, models
import django.db.models.deletion


def seed_airports(apps, schema_editor):
    AirportLookup = apps.get_model("ingestion", "AirportLookup")
    airports = [
        ("JFK", "New York", "US", "40.641300", "-73.778100"),
        ("LHR", "London", "GB", "51.470000", "-0.454300"),
        ("FRA", "Frankfurt", "DE", "50.037900", "8.562200"),
        ("SFO", "San Francisco", "US", "37.621300", "-122.379000"),
        ("ORD", "Chicago", "US", "41.974200", "-87.907300"),
        ("AMS", "Amsterdam", "NL", "52.310500", "4.768300"),
    ]
    for code, city, country, latitude, longitude in airports:
        AirportLookup.objects.update_or_create(
            code=code,
            defaults={
                "city": city,
                "country": country,
                "latitude": latitude,
                "longitude": longitude,
            },
        )


def unseed_airports(apps, schema_editor):
    AirportLookup = apps.get_model("ingestion", "AirportLookup")
    AirportLookup.objects.filter(code__in=["JFK", "LHR", "FRA", "SFO", "ORD", "AMS"]).delete()


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Tenant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="RawRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("raw_json", models.JSONField()),
                ("processing_status", models.CharField(choices=[("pending", "Pending"), ("processed", "Processed"), ("failed", "Failed")], default="pending", max_length=20)),
                ("error_message", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="AirportLookup",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=10, unique=True)),
                ("city", models.CharField(max_length=255)),
                ("country", models.CharField(blank=True, max_length=255)),
                ("latitude", models.DecimalField(decimal_places=6, max_digits=9)),
                ("longitude", models.DecimalField(decimal_places=6, max_digits=9)),
            ],
        ),
        migrations.CreateModel(
            name="DataSource",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_type", models.CharField(choices=[("sap", "SAP"), ("utility", "Utility"), ("travel", "Travel")], max_length=20)),
                ("filename", models.CharField(max_length=255)),
                ("uploaded_by", models.CharField(max_length=255)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="data_sources", to="ingestion.tenant")),
            ],
        ),
        migrations.CreateModel(
            name="ActivityRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("activity_type", models.CharField(choices=[("fuel", "Fuel"), ("electricity", "Electricity"), ("flight", "Flight"), ("hotel", "Hotel"), ("taxi", "Taxi"), ("procurement", "Procurement")], max_length=20)),
                ("scope", models.PositiveSmallIntegerField()),
                ("activity_date", models.DateField()),
                ("original_quantity", models.DecimalField(decimal_places=4, max_digits=18)),
                ("original_unit", models.CharField(max_length=32)),
                ("normalized_quantity", models.DecimalField(decimal_places=4, max_digits=18)),
                ("normalized_unit", models.CharField(max_length=32)),
                ("emission_factor", models.DecimalField(decimal_places=6, max_digits=18)),
                ("co2e_kg", models.DecimalField(decimal_places=4, max_digits=18)),
                ("facility", models.CharField(blank=True, max_length=255)),
                ("vendor", models.CharField(blank=True, max_length=255)),
                ("cost_center", models.CharField(blank=True, max_length=255)),
                ("review_status", models.CharField(default="pending", max_length=20)),
                ("anomaly_flag", models.BooleanField(default=False)),
                ("anomaly_reason", models.TextField(blank=True)),
                ("source_reference", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("raw_record", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="activity_records", to="ingestion.rawrecord")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="activity_records", to="ingestion.tenant")),
            ],
        ),
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(max_length=100)),
                ("old_value", models.JSONField(default=dict)),
                ("new_value", models.JSONField(default=dict)),
                ("changed_by", models.CharField(max_length=255)),
                ("changed_at", models.DateTimeField(auto_now_add=True)),
                ("activity_record", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="audit_logs", to="ingestion.activityrecord")),
            ],
        ),
        migrations.RunPython(seed_airports, unseed_airports),
    ]
