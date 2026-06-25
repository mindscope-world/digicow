"""
Script to load farmer data from CSV into Neo4j graph database.
"""
import uuid
import sys
import os
# Add the parent directory to sys.path so that we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
from datetime import datetime
from neomodel import db
from app.models.farmer import Farmer
from app.models.cooperative import Cooperative
from app.models.location.ward import Ward
from app.models.location.subcounty import Subcounty
from app.models.location.county import County
from app.models.trainer.trainer import Trainer
from app.models.training.training_topic import TrainingTopic
from app.models.training import TrainingSession
from app.models.adoption import Adoption
from app.models.input_product.input_product import InputProduct
from app.models.advisory.advisory import AdvisoryRecommendation
from app.models.weather.weather_station import WeatherStation


def get_or_create_county(name, code=None):
    """Get or create a County node."""
    county = County.nodes.get_or_none(name=name)
    if not county:
        county = County(name=name, code=code or name[:3].upper()).save()
    return county


def get_or_create_subcounty(name, code=None, county_name=None):
    """Get or create a Subcounty node and link to County."""
    subcounty = Subcounty.nodes.get_or_none(name=name)
    if not subcounty:
        subcounty = Subcounty(name=name, code=code or name[:3].upper()).save()
    if county_name:
        county = get_or_create_county(county_name)
        # Link subcounty to county (county contains subcounty)
        county.contains_subcounties.connect(subcounty)
    return subcounty


def get_or_create_ward(name, code=None, subcounty_name=None):
    """Get or create a Ward node and link to Subcounty."""
    ward = Ward.nodes.get_or_none(name=name)
    if not ward:
        ward = Ward(name=name, code=code or name[:3].upper()).save()
    if subcounty_name:
        subcounty = get_or_create_subcounty(subcounty_name, county_name="Unknown")  # We'll need to pass county from CSV
        # Link ward to subcounty (subcounty contains ward)
        subcounty.contains_wards.connect(ward)
    return ward


def get_or_create_trainer(name, specialization=None, employee_id=None):
    """Get or create a Trainer node."""
    trainer = Trainer.nodes.get_or_none(name=name)
    if not trainer:
        trainer = Trainer(
            name=name,
            specialization=specialization or "",
            employee_id=employee_id or name.replace(" ", "_")
        ).save()
    return trainer


def get_or_create_training_topic(name, category=None, description=None):
    """Get or create a TrainingTopic node."""
    topic = TrainingTopic.nodes.get_or_none(name=name)
    if not topic:
        topic = TrainingTopic(
            name=name,
            category=category or "",
            description=description or ""
        ).save()
    return topic


def get_or_create_input_product(name, type_="unknown", brand="unknown", cost="0", effectiveness_rating=0):
    """Get or create an InputProduct node."""
    product = InputProduct.nodes.get_or_none(name=name)
    if not product:
        product = InputProduct(
            name=name,
            type=type_,
            brand=brand,
            cost=cost,
            effectiveness_rating=effectiveness_rating
        ).save()
    return product


DEFAULT_INPUT_PRODUCT = get_or_create_input_product("Adopted Practice", type_="practice", brand="Unknown", cost="0", effectiveness_rating=0)


def load_farmers_from_csv(csv_path):
    """Load farmers from CSV file and create graph nodes and relationships."""
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return

    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Skip empty rows
            if not row.get('ID'):
                continue

            print(f"Processing farmer {row['ID']}")

            # 1. Location hierarchy: County -> Subcounty -> Ward
            county_name = row['county']
            subcounty_name = row['subcounty']
            ward_name = row['ward']

            county = get_or_create_county(county_name)
            subcounty = get_or_create_subcounty(
                subcounty_name,
                county_name=county_name
            )
            ward = get_or_create_ward(
                ward_name,
                subcounty_name=subcounty_name
            )

            # 2. Trainer(s)
            trainer_names = []
            trainer_field = row['trainer']
            # Trainer field is a string representation of a list, e.g., "[""James Kariuki""]"
            # We'll parse it naively by removing brackets and quotes
            if trainer_field:
                # Remove the outer brackets and split by ','
                # Format: [""name1"", ""name2""]
                cleaned = trainer_field.strip('[]')
                if cleaned:
                    # Split by '","' but careful with spaces
                    parts = cleaned.split('","')
                    for part in parts:
                        name = part.strip('" ')
                        if name:
                            trainer_names.append(name)
            trainers = []
            for t_name in trainer_names:
                trainer = get_or_create_trainer(t_name)
                trainers.append(trainer)

            # 3. Training Topic(s)
            topic_names = []
            topic_field = row['topics']
            if topic_field:
                cleaned = topic_field.strip('[]')
                if cleaned:
                    parts = cleaned.split('","')
                    for part in parts:
                        name = part.strip('" ')
                        if name:
                            topic_names.append(name)
            topics = []
            for t_name in topic_names:
                topic = get_or_create_training_topic(t_name)
                topics.append(topic)

            # 4. Create TrainingSession (if there is a first_training_date and topics)
            training_session = None
            first_training_date = row.get('first_training_date')
            has_topic_trained_on = row.get('has_topic_trained_on', 'False').lower() == 'true'
            if first_training_date and has_topic_trained_on and topics:
                try:
                    session_date = datetime.strptime(first_training_date, '%Y-%m-%d')
                except ValueError:
                    # Try another format if needed
                    try:
                        session_date = datetime.strptime(first_training_date, '%d/%m/%Y')
                    except ValueError:
                        session_date = datetime.now()  # fallback

                # Create a training session
                training_session = TrainingSession(
                    title=f"Training for {row['ID']}",
                    description=f"Training on {', '.join(topic_names)}",
                    session_date=session_date,
                    location=ward_name,  # or use ward code
                    duration=2,  # default 2 hours
                    attendance_count=1  # at least this farmer
                ).save()

                # Link session to topics
                for topic in topics:
                    training_session.has_topic.connect(topic)

                # Link session to trainers (conducted_by)
                # We'll assign the first trainer as conductor for simplicity
                if trainers:
                    training_session.conducted_by.connect(trainers[0])

            # 5. Create Farmer node
            farmer = Farmer(
                farmer_id=row['ID'],
                gender=row['gender'],
                age_bracket=row['age'],  # CSV 'age' column is actually age bracket
                registration_method=row['registration'],
                belongs_to_cooperative=row['belong_to_cooperative'] == '1',
                phone=None,  # not in CSV
                herd_size=0,
                acres_under_cultivation=0.0,
                primary_enterprise=None
            ).save()

            # 6. Link Farmer to Ward
            farmer.located_in.connect(ward)

            # 7. Link Farmer to Trainers (trained_by)
            for trainer in trainers:
                farmer.trained_by.connect(trainer)

            # 8. Link Farmer to TrainingSession (attended_by)
            if training_session:
                farmer.attended_by.connect(training_session)

            # 9. Adoption: Check if the farmer has adopted any practice
            adopted_07 = row.get('adopted_within_07_days', '0') == '1'
            adopted_90 = row.get('adopted_within_90_days', '0') == '1'
            adopted_120 = row.get('adopted_within_120_days', '0') == '1'
            if adopted_07 or adopted_90 or adopted_120:
                # Determine adoption date: use first_training_date if available, else now
                adop_date = None
                if first_training_date:
                    try:
                        adop_date = datetime.strptime(first_training_date, '%Y-%m-%d')
                    except ValueError:
                        try:
                            adop_date = datetime.strptime(first_training_date, '%d/%m/%Y')
                        except ValueError:
                            adop_date = datetime.now()
                else:
                    adop_date = datetime.now()

                # Create adoption record
                adoption_uid = f"{farmer.farmer_id}_{adop_date.strftime('%Y%m%d%H%M%S')}"
                adoption = Adoption(
                    uid=adoption_uid,
                    date_adopted=adop_date
                ).save()

                # Link adoption to farmer and default input product
                adoption.farmer.connect(farmer)
                adoption.input_product.connect(DEFAULT_INPUT_PRODUCT)

            # 10. Cooperative membership (optional)
            if farmer.belongs_to_cooperative:
                # We don't have cooperative name in CSV, so we'll create a generic one
                coop_name = f"{county_name} Cooperative"
                coop = Cooperative.nodes.get_or_none(name=coop_name)
                if not coop:
                    coop = Cooperative(name=coop_name, location_details=f"Located in {county_name}").save()
                farmer.member_of.connect(coop)

            print(f"  -> Created farmer {farmer.farmer_id}")

    print("CSV loading completed.")


if __name__ == "__main__":
    CSV_PATH = "/home/mindscope/Lab/hackathons/backend/data/Prior_digicow.csv"
    load_farmers_from_csv(CSV_PATH)