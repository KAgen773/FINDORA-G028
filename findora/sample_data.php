<?php
include 'db_connect.php';

$sql = "INSERT INTO lost_items (type, description, location, date) VALUES 
        ('Wallet', 'Black leather wallet with several cards and cash inside.', 'Central Park', '2024-06-01'),
        ('Phone', 'Silver iPhone with a cracked screen.', 'Downtown Library', '2024-06-03'),
        ('Backpack', 'Blue backpack containing a laptop and notebooks.', 'University Campus', '2024-06-05')";

if ($conn->query($sql) === TRUE) {
    echo "New lost item added successfully";
} else {
    echo "Error : " . $sql . "<br>" . $conn->error;
}

$conn->close();
?>