<?php
include 'db_connect.php';

function matchLocation($lost, $found) {
    $lostLoc = strtolower(trim($lost['location']));
    $foundLoc = strtolower(trim($found['location']));

    if ($lostLoc === $foundLoc) {
        return 30; 
    } elseif (strpos($lostLoc, $foundLoc) !== false || strpos($foundLoc, $lostLoc) !== false) {
        return 20; 
    } elseif (isset($lost['lat'], $lost['lon'], $found['lat'], $found['lon'])) {
        $earthRadius = 6371; 
        $dLat = deg2rad($found['lat'] - $lost['lat']);
        $dLon = deg2rad($found['lon'] - $lost['lon']);
        $a = sin($dLat/2) * sin($dLat/2) +
             cos(deg2rad($lost['lat'])) * cos(deg2rad($found['lat'])) *
             sin($dLon/2) * sin($dLon/2);
        $c = 2 * atan2(sqrt($a), sqrt(1-$a));
        $distance = $earthRadius * $c;

        if ($distance <= 5) return 15; 
    }
    return 0; 
}

function calculateMatch($lost, $found) {
    $score = 0;
    $score += matchLocation($lost, $found);
    return $score;
}

$lostItems = $conn->query("SELECT * FROM lost_items");
$foundItems = $conn->query("SELECT * FROM found_items");

if ($lostItems->num_rows > 0 && $foundItems->num_rows > 0) {
    while ($lost = $lostItems->fetch_assoc()) {
        $bestMatch = null;
        $bestScore = 0;

        $foundItems->data_seek(0);
        while($found = $foundItems->fetch_assoc()) {
            $score = calculateMatch($lost, $found);
            if ($score > $bestScore) {
                $bestScore = $score;
                $bestMatch = $found;
            }
        }

        echo "Lost Item: " . $lost['description'] . "<br>";
        if ($bestMatch) {
            echo "Best Match Found: " . $bestMatch['description'] . " (Score: $bestScore)<br><br>";
        } else {
            echo "No match found.<br><br>";
        }
    }
}
?>
