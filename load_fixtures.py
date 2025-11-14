import os
import subprocess


def load_fixtures():
    fixtures = [
        'countries.json',
        'cities.json',
        'users.json',
        'hotels.json',
        'hotel_images.json',
        'reviews.json',
        'bookings.json',
        'favorites.json',
    ]

    for fixture in fixtures:
        print(f"Loading {fixture}...")
        cmd = f'docker-compose exec web python manage.py loaddata {fixture}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')

        if result.returncode == 0:
            print(f"✅ {fixture} loaded successfully!")
        else:
            print(f"❌ Error loading {fixture}: {result.stderr}")


if __name__ == '__main__':
    load_fixtures()