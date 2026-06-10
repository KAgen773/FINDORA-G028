<?php
include("db_connect.php");

$sql = "SELECT * FROM lost_items";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    while ($row = $result->fetch_assoc()) {
        echo "ID : " . $row["id"] . " - Type: " . $row["type"] . " - Location: " . $row["location"] . " - Date: " . $row["date"] . " - Description: " . $row["description"] . "<br>";
    }
} else {
    echo "No lost items found";
}

$conn->close();
?>