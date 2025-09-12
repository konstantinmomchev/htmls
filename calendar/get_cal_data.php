<?php
/**
 * Orthodox Calendar Data API
 * Reads feast data from CSV file and returns JSON for specified month
 * 
 * Usage: /get_cal_data.php?month=01
 * Returns: JSON array of feasts for the specified month
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET');
header('Access-Control-Allow-Headers: Content-Type');

// Configuration
define('CSV_FILE_PATH', 'orthodox_feasts.csv');
define('DEFAULT_MONTH', '01');

/**
 * Sanitize and validate month parameter
 */
function getValidatedMonth() {
    $month = isset($_GET['month']) ? trim($_GET['month']) : DEFAULT_MONTH;
    
    // Ensure month is 2 digits
    $month = str_pad($month, 2, '0', STR_PAD_LEFT);
    
    // Validate month range
    if (!preg_match('/^(0[1-9]|1[0-2])$/', $month)) {
        $month = DEFAULT_MONTH;
    }
    
    return $month;
}

/**
 * Parse CSV file and return array of feast data
 */
function readFeastsFromCSV($csvPath) {
    if (!file_exists($csvPath)) {
        error_log("CSV file not found: " . $csvPath);
        return [];
    }
    
    if (!is_readable($csvPath)) {
        error_log("CSV file not readable: " . $csvPath);
        return [];
    }
    
    $feasts = [];
    
    try {
        $handle = fopen($csvPath, 'r');
        if ($handle === false) {
            throw new Exception("Cannot open CSV file");
        }
        
        // Read header row to get column positions
        $headers = fgetcsv($handle);
        if ($headers === false) {
            throw new Exception("Cannot read CSV headers");
        }
        
        // Normalize headers (remove BOM, trim whitespace, lowercase)
        $headers = array_map(function($header) {
            return strtolower(trim($header, " \t\n\r\0\x0B\xEF\xBB\xBF"));
        }, $headers);
        
        // Find column indices
        $dateIndex = array_search('date', $headers);
        $feastNameIndex = array_search('feast_name', $headers);
        $descriptionIndex = array_search('description', $headers);
        $showFishIndex = array_search('show_fish', $headers);
        $showOilIndex = array_search('show_oil', $headers);
        $showStrictFastIndex = array_search('show_strict_fast', $headers);
        
        // Alternative column names
        if ($feastNameIndex === false) {
            $feastNameIndex = array_search('name', $headers);
        }
        
        if ($dateIndex === false) {
            throw new Exception("Required 'date' column not found in CSV");
        }
        
        // Read data rows
        $rowNumber = 1;
        while (($row = fgetcsv($handle)) !== false) {
            $rowNumber++;
            
            // Skip empty rows
            if (empty(array_filter($row))) {
                continue;
            }
            
            // Ensure we have enough columns
            if (count($row) <= $dateIndex) {
                error_log("Row $rowNumber: Not enough columns");
                continue;
            }
            
            $date = trim($row[$dateIndex]);
            
            // Validate date format
            if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $date)) {
                error_log("Row $rowNumber: Invalid date format: $date");
                continue;
            }
            
            // Validate date
            $dateTime = DateTime::createFromFormat('Y-m-d', $date);
            if (!$dateTime || $dateTime->format('Y-m-d') !== $date) {
                error_log("Row $rowNumber: Invalid date: $date");
                continue;
            }
            
            $feast = [
                'date' => $date,
                'feast_name' => $feastNameIndex !== false && isset($row[$feastNameIndex]) ? trim($row[$feastNameIndex]) : '',
                'description' => $descriptionIndex !== false && isset($row[$descriptionIndex]) ? trim($row[$descriptionIndex]) : '',
                'show_fish' => $showFishIndex !== false && isset($row[$showFishIndex]) ? parseBooleanValue($row[$showFishIndex]) : true,
                'show_oil' => $showOilIndex !== false && isset($row[$showOilIndex]) ? parseBooleanValue($row[$showOilIndex]) : true,
                'show_strict_fast' => $showStrictFastIndex !== false && isset($row[$showStrictFastIndex]) ? parseBooleanValue($row[$showStrictFastIndex]) : true
            ];
            
            $feasts[] = $feast;
        }
        
        fclose($handle);
        
    } catch (Exception $e) {
        error_log("Error reading CSV: " . $e->getMessage());
        return [];
    }
    
    return $feasts;
}

/**
 * Parse boolean values from CSV
 */
function parseBooleanValue($value) {
    $value = strtolower(trim($value));
    
    // Handle various boolean representations
    switch ($value) {
        case 'true':
        case '1':
        case 'yes':
        case 'да':
        case 'y':
            return true;
        case 'false':
        case '0':
        case 'no':
        case 'не':
        case 'n':
        case '':
            return false;
        default:
            // If it's not clearly false, default to true
            return true;
    }
}

/**
 * Filter feasts by month
 */
function filterFeastsByMonth($feasts, $targetMonth) {
    return array_filter($feasts, function($feast) use ($targetMonth) {
        $feastDate = $feast['date'];
        $feastMonth = substr($feastDate, 5, 2); // Extract MM from YYYY-MM-DD
        return $feastMonth === $targetMonth;
    });
}

/**
 * Sort feasts by date
 */
function sortFeastsByDate($feasts) {
    usort($feasts, function($a, $b) {
        return strcmp($a['date'], $b['date']);
    });
    return $feasts;
}

/**
 * Main execution
 */
try {
    // Get and validate month parameter
    $requestedMonth = getValidatedMonth();
    
    // Read all feasts from CSV
    $allFeasts = readFeastsFromCSV(CSV_FILE_PATH);
    
    if (empty($allFeasts)) {
        // Return empty array if no data available
        echo json_encode([]);
        exit;
    }
    
    // Filter by requested month
    $monthFeasts = filterFeastsByMonth($allFeasts, $requestedMonth);
    
    // Sort by date
    $monthFeasts = sortFeastsByDate($monthFeasts);
    
    // Re-index array to ensure clean JSON output
    $monthFeasts = array_values($monthFeasts);
    
    // Return JSON response
    echo json_encode($monthFeasts, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    
} catch (Exception $e) {
    // Log error and return error response
    error_log("API Error: " . $e->getMessage());
    
    http_response_code(500);
    echo json_encode([
        'error' => 'Internal server error',
        'message' => 'Unable to process request'
    ], JSON_UNESCAPED_UNICODE);
}

/**
 * Example CSV format (save as orthodox_feasts.csv):
 * 
 * date,feast_name,description,show_fish,show_oil,show_strict_fast
 * 2025-01-01,Нова година,Празник на новата година,true,true,false
 * 2025-01-06,Богоявление,Кръщение Господне,false,false,true
 * 2025-01-07,Рождество Христово,Рождение на Иисус Христос,true,true,false
 * 2025-01-18,Свети Атанасий Велики,Архиепископ Александрийски,true,true,true
 * 2025-02-14,Свети Валентин,Ден на влюбените,true,true,true
 * 2025-03-25,Благовещение,Благовещение на Пресвета Богородица,true,true,false
 * 2025-04-20,Цветница,Връбница,true,true,false
 * 2025-04-27,Великден,Възкресение Христово,true,true,false
 * 2025-05-06,Гергьовден,Свети Георги Победоносец,true,true,false
 * 2025-09-14,Кръстовден,Въздвижение на Честния Кръст,false,false,true
 * 2025-12-25,Рождество Христово,Рождение на Иисус Христос,true,true,false
 */
?>