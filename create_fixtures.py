import os
import subprocess


def create_fixtures():
    fixtures = [
        ('hotels.Country', 'countries.json'),
        ('hotels.City', 'cities.json'),
        ('hotels.Hotel', 'hotels.json'),
        ('hotels.HotelImage', 'hotel_images.json'),
        ('auth.User', 'users.json'),
        ('hotels.Review', 'reviews.json'),
        ('hotels.Booking', 'bookings.json'),
        ('hotels.Favorite', 'favorites.json'),
    ]

    for model, filename in fixtures:
        print(f"Creating {filename}...")
        cmd = f'docker-compose exec web python manage.py dumpdata {model} --indent 2'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')

        if result.returncode == 0:
            with open(f'fixtures/{filename}', 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            print(f"✅ {filename} created successfully!")
        else:
            print(f"❌ Error creating {filename}: {result.stderr}")


if __name__ == '__main__':
    create_fixtures()