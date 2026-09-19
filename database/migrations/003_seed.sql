-- Deterministic portfolio/demo data.
-- Demo passwords are documented in database/README.md and are never suitable
-- for a real deployment.

INSERT INTO roles (role_id, role_name) VALUES
    (1, 'ADMIN'),
    (2, 'HOST'),
    (3, 'GUEST');

INSERT INTO users (user_id, full_name, email, password_hash, phone) VALUES
    (
        1,
        'StayEase Admin',
        'admin@stayease.local',
        'scrypt$16384$8$1$c3RheWVhc2UtYWRtaW4tMjAyNg$OJHOQxBQ52s93Mj8_zekhEqJlf-XbzrBv7l44ynXbdg',
        '+919000000001'
    ),
    (
        2,
        'Aarav Sharma',
        'host@stayease.local',
        'scrypt$16384$8$1$c3RheWVhc2UtaG9zdC0yMDI2$0NQ2iTpZZaM_y_tsEQ-_EjoGzBo7_0XexeQtsJBCcR4',
        '+919000000002'
    ),
    (
        3,
        'Meera Kapoor',
        'guest@stayease.local',
        'scrypt$16384$8$1$c3RheWVhc2UtZ3Vlc3QtMjAyNg$r8gYKInS46DRRcWJXrCs7vUgv-Ogkf-ccZGjN94-d6A',
        '+919000000003'
    );

INSERT INTO user_roles (user_id, role_id) VALUES
    (1, 1),
    (2, 2),
    (3, 3);

INSERT INTO amenities (amenity_id, amenity_name) VALUES
    (1, 'Wi-Fi'),
    (2, 'Air conditioning'),
    (3, 'Kitchen'),
    (4, 'Parking'),
    (5, 'Workspace'),
    (6, 'Pool'),
    (7, 'Mountain view'),
    (8, 'Beach access');

INSERT INTO properties (
    property_id,
    host_id,
    title,
    slug,
    description,
    address_line,
    city,
    capacity,
    bedrooms,
    bathrooms,
    base_price
) VALUES
    (
        1,
        2,
        'Sunset Courtyard Villa',
        'sunset-courtyard-villa-goa',
        'A bright Portuguese-inspired villa with a private courtyard near the coast.',
        '12 Fontainhas Lane',
        'Goa',
        6,
        3,
        2.5,
        6200.00
    ),
    (
        2,
        2,
        'Pine Ridge Cabin',
        'pine-ridge-cabin-manali',
        'A quiet timber cabin with mountain views, a fireplace, and a dedicated workspace.',
        '44 Old Manali Road',
        'Manali',
        4,
        2,
        2.0,
        4800.00
    ),
    (
        3,
        2,
        'Pink City Heritage Loft',
        'pink-city-heritage-loft-jaipur',
        'A restored city loft within walking distance of Jaipur landmarks and local markets.',
        '8 Badi Chaupar',
        'Jaipur',
        3,
        1,
        1.0,
        3400.00
    ),
    (
        4,
        2,
        'Lakeside Studio Retreat',
        'lakeside-studio-retreat-udaipur',
        'A calm studio overlooking the lake, designed for couples and solo travellers.',
        '19 Ambrai Ghat',
        'Udaipur',
        2,
        1,
        1.0,
        3900.00
    );

INSERT INTO property_amenities (property_id, amenity_id) VALUES
    (1, 1), (1, 2), (1, 3), (1, 4), (1, 6), (1, 8),
    (2, 1), (2, 3), (2, 4), (2, 5), (2, 7),
    (3, 1), (3, 2), (3, 3), (3, 5),
    (4, 1), (4, 2), (4, 3), (4, 5);

INSERT INTO property_images (property_id, image_url, alt_text, display_order) VALUES
    (1, '/images/goa-villa.svg', 'Courtyard and pool at Sunset Courtyard Villa', 0),
    (2, '/images/manali-cabin.svg', 'Pine Ridge Cabin against the mountains', 0),
    (3, '/images/jaipur-loft.svg', 'Interior of Pink City Heritage Loft', 0),
    (4, '/images/udaipur-studio.svg', 'Lake view from Lakeside Studio Retreat', 0);

INSERT INTO availability_windows (
    property_id,
    start_date,
    end_date,
    price_per_night,
    note
) VALUES
    (1, DATE_SUB(CURDATE(), INTERVAL 365 DAY), DATE_ADD(CURDATE(), INTERVAL 365 DAY), 6200.00, 'Standard rate'),
    (2, DATE_SUB(CURDATE(), INTERVAL 365 DAY), DATE_ADD(CURDATE(), INTERVAL 365 DAY), 4800.00, 'Standard rate'),
    (3, DATE_SUB(CURDATE(), INTERVAL 365 DAY), DATE_ADD(CURDATE(), INTERVAL 365 DAY), 3400.00, 'Standard rate'),
    (4, DATE_SUB(CURDATE(), INTERVAL 365 DAY), DATE_ADD(CURDATE(), INTERVAL 365 DAY), 3900.00, 'Standard rate');

-- A completed historical stay makes the seeded review workflow visible.
INSERT INTO bookings (
    booking_id,
    guest_id,
    property_id,
    check_in,
    check_out,
    guest_count,
    nightly_rate,
    total_nights,
    total_amount,
    status
) VALUES (
    1,
    3,
    1,
    DATE_SUB(CURDATE(), INTERVAL 40 DAY),
    DATE_SUB(CURDATE(), INTERVAL 37 DAY),
    2,
    6200.00,
    3,
    18600.00,
    'PENDING'
);

INSERT INTO payments (
    booking_id,
    amount,
    status,
    provider_reference,
    paid_at
) VALUES (
    1,
    18600.00,
    'PENDING',
    'DEMO-SEED-0001',
    NULL
);

UPDATE payments
   SET status = 'PAID',
       paid_at = DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 45 DAY)
 WHERE booking_id = 1;

UPDATE bookings
   SET status = 'COMPLETED'
 WHERE booking_id = 1;

INSERT INTO reviews (booking_id, guest_id, property_id, rating, comment)
VALUES (
    1,
    3,
    1,
    5,
    'Thoughtful host, spotless rooms, and a peaceful courtyard.'
);
