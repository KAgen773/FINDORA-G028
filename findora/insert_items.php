<?php
include 'db_connect.php';

$lost_sql = "INSERT INTO lost_items (type, description, location, date) VALUES
    ('Wallet', 'Black leather wallet with several cards and cash inside.', 'Central Park', '2024-06-01'),
    ('Phone', 'Silver iPhone with a cracked screen.', 'Downtown Library', '2024-06-03'),
    ('Backpack', 'Blue backpack containing a laptop and notebooks.', 'University Campus', '2024-06-05')";

if ($conn->query($lost_sql) === TRUE) {
    echo "Lost items inserted successfully.<br>";
} else {
    echo "Error inserting lost items: " . $conn->error . "<br>";
}

$found_sql = "INSERT INTO found_items (type, description, location, date) VALUES
    ('Wallet', 'Brown wallet with ID cards inside.', 'Central Park', '2024-06-02'),
    ('Phone', 'Silver smartphone found near library entrance.', 'Downtown Library', '2024-06-04'),
    ('Backpack', 'Blue bag with books and charger.', 'University Campus', '2024-06-06')";

if ($conn->query($found_sql) === TRUE) {
    echo "Found items inserted successfully.<br>";
} else {
    echo "Error inserting found items: " . $conn->error . "<br>";
}

$conn->close();
?>
