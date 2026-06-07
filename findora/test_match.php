<?php
include 'db_connect.php';
include 'match_items.php'; 

$lost_sql = "SELECT * FROM lost_items";
$lost_result = $conn->query($lost_sql);

$found_sql = "SELECT * FROM found_items";
$found_result = $conn->query($found_sql);

$found_items = [];
while ($row = $found_result->fetch_assoc()) {
    $found_items[] = $row;
}

echo "<h2>Match Results</h2>";
echo "<table border='1' cellpadding='8'>";
echo "<tr><th>Lost Item</th><th>Best Match</th><th>Score</th></tr>";

while ($lost = $lost_result->fetch_assoc()) {
    $bestScore = 0;
    $bestMatch = null;

    foreach ($found_items as $found) {
        $score = calculateMatch($lost, $found);
        if ($score > $bestScore) {
            $bestScore = $score;
            $bestMatch = $found;
        }
    }

    echo "<tr>";
    echo "<td>{$lost['type']} - {$lost['description']}</td>";
    if ($bestMatch) {
        echo "<td>{$bestMatch['type']} - {$bestMatch['description']}</td>";
        echo "<td>{$bestScore}</td>";
    } else {
        echo "<td>No match</td><td>0</td>";
    }
    echo "</tr>";
}

echo "</table>";

$conn->close();
?>
