# Запросы для клиентов
INSERT_CLIENT_SQL = """
INSERT INTO clients (last_name, first_name, middle_name, passport_data, comment)
VALUES (%s, %s, %s, %s, %s)
"""

FETCH_CLIENTS_SQL = """SELECT * FROM clients ORDER BY last_name, first_name"""

DELETE_CLIENT_SQL = """DELETE FROM clients WHERE client_id = %s"""

EDIT_CLIENT_SQL = """
UPDATE clients
SET last_name = %s, first_name = %s, middle_name = %s, passport_data = %s, comment = %s
WHERE client_id = %s
"""

# Запросы для номеров
INSERT_ROOM_SQL = """
INSERT INTO rooms (room_number, capacity, comfort_level, price)
VALUES (%s, %s, %s, %s)
"""

FETCH_ROOMS_SQL = """SELECT * FROM rooms ORDER BY room_number"""

DELETE_ROOM_SQL = """DELETE FROM rooms WHERE room_id = %s"""

EDIT_ROOM_SQL = """
UPDATE rooms
SET room_number = %s, capacity = %s, comfort_level = %s, price = %s
WHERE room_id = %s
"""

# Запросы для бронирований
INSERT_BOOKING_SQL = """
INSERT INTO bookings (client_id, room_id, check_in_date, check_out_date, note)
VALUES (%s, %s, %s, %s, %s)
"""

FETCH_BOOKINGS_SQL = """SELECT * FROM bookings ORDER BY check_in_date DESC"""

DELETE_BOOKING_SQL = """DELETE FROM bookings WHERE booking_id = %s"""

EDIT_BOOKING_SQL = """
UPDATE bookings
SET client_id = %s, room_id = %s, check_in_date = %s, check_out_date = %s, note = %s
WHERE booking_id = %s
"""

FETCH_CLIENTS_FOR_BOOKINGS_SQL = """SELECT client_id, last_name, first_name, middle_name FROM clients ORDER BY last_name, first_name"""

FETCH_ROOMS_FOR_BOOKINGS_SQL = """SELECT room_id, room_number, comfort_level FROM rooms ORDER BY room_number"""

# Запросы для фильтрации
LOAD_CLIENTS_FOR_FILTER_SQL = """SELECT client_id, last_name, first_name, middle_name FROM clients ORDER BY last_name, first_name"""

LOAD_ROOMS_FOR_FILTER_SQL = """SELECT room_id, room_number, comfort_level FROM rooms ORDER BY room_number"""

CLIENT_FILTER_SQL = """SELECT client_id FROM clients WHERE CONCAT(last_name, ' ', first_name, ' ', middle_name) = %s"""

ROOM_FILTER_SQL = """SELECT room_id FROM rooms WHERE room_number = %s"""

APPLY_FILTERS_SQL = """
SELECT b.booking_id, 
       c.last_name || ' ' || c.first_name || ' ' || c.middle_name AS client_name,
       r.room_number || ' (' || r.comfort_level || ')' AS room_info,
       b.check_in_date, b.check_out_date, b.note
FROM bookings b
JOIN clients c ON b.client_id = c.client_id
JOIN rooms r ON b.room_id = r.room_id
WHERE (%s IS NULL OR b.client_id = %s)
AND (%s IS NULL OR b.room_id = %s)
AND (%s IS NULL OR b.check_in_date >= %s)
AND (%s IS NULL OR b.check_in_date <= %s)
"""