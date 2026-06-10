<?php
define('WEIGHT_TYPE', 50);
define('WEIGHT_LOCATION_EXACT', 30);
define('WEIGHT_LOCATION_NEAR', 15);
define('WEIGHT_DATE_PROXIMITY', 10);
define('WEIGHT_DESC', 20);

$pdo = new PDO("mysql:host=localhost;dbname=findora_db;charset=utf8", "root", "");

function preprocess_text($text) {
    $text = strtolower($text);
    $text = preg_replace("/[^a-z0-9\s]/","", $text);
    $tokens = explode(" ", $text);
    return array_filter($tokens);
}

function cosine_similarity($vecA, $vecB){
    $dot = 0; $normA = 0; $normB = 0;
    for ($i=0; $i<count($vecA); $i++){
        $dot += $vecA[$i] * $vecB[$i];
        $normA += $vecA[$i] ** 2;
        $normB += $vecB[$i] ** 2;
    }
    if ($normA == 0 || $normB == 0) return 0;
    return $dot / (sqrt($normA) * sqrt($normB));
}

function description_similarity($descA, $descB){
    $tokensA = preprocess_text($descA);
    $tokensB = preprocess_text($descB);

    if (empty($tokensA) || empty($tokensB)) return 0;

    $vocab = array_unique(array_merge($tokensA, $tokensB));
    $tfA = array_count_values($tokensA);
    $tfB = array_count_values($tokensB);

    $vecA = [];
    $vecB = [];
    foreach ($vocab as $term) {
        $vecA[] = isset($tfA[$term]) ? $tfA[$term] : 0;
        $vecB[] = isset($tfB[$term]) ? $tfB[$term] : 0;
    }

    return cosine_similarity($vecA, $vecB);
}

function calculateMatch($lostItem, $foundItem) {
    $score = 0;

    if ($lostItem['type'] === $foundItem['type']) {
        $score += WEIGHT_TYPE;
    }

    if ($lostItem['location'] === $foundItem['location']) {
        $score += WEIGHT_LOCATION_EXACT;
    } elseif (stripos($foundItem['location'], $lostItem['location']) !== false) {
        $score += WEIGHT_LOCATION_NEAR;
    }

    $lostDate = strtotime($lostItem['date']);
    $foundDate = strtotime($foundItem['date']);
    if ($lostDate && $foundDate && abs($lostDate - $foundDate) <= 3 * 24 * 60 * 60) { 
        $score += WEIGHT_DATE_PROXIMITY;
    }

    $sim = description_similarity($lostItem['description'], $foundItem['description']);
    $score += $sim * WEIGHT_DESC;

    return round($score, 2);
}

$lostId = 1; 
$stmtLost = $pdo->prepare("SELECT * FROM lost_items WHERE id = ?");
$stmtLost->execute([$lostId]);
$lostItem = $stmtLost->fetch(PDO::FETCH_ASSOC);

if ($lostItem) {
    $stmtFound = $pdo->query("SELECT * FROM found_items");
    $foundItems = $stmtFound->fetchAll(PDO::FETCH_ASSOC);

    $results = [];
    foreach ($foundItems as $foundItem) {
        $score = calculateMatch($lostItem, $foundItem);
        $results[] = [
            'found_id' => $foundItem['id'],
            'score' => $score,
            'found_item' => $foundItem
        ];
    }

    usort($results, function($a, $b) {
        return $b['score'] <=> $a['score'];
    });

    foreach ($results as $r) {
        echo "Found Item #" . $r['found_id'] . " | Score: " . $r['score'] . "\n";
        echo "Type: " . $r['found_item']['type'] . "\n";
        echo "Location: " . $r['found_item']['location'] . "\n";
        echo "Date: " . $r['found_item']['date'] . "\n";
        echo "Description: " . $r['found_item']['description'] . "\n";
        echo "-----------------------------\n";
    }
} else {
    echo "Lost item not found.";
}
?>
