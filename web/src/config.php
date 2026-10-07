<?php
/**
 * Database configuration for the Observ monitoring portal.
 *
 * NOTE (lab): credentials here are intentionally reused elsewhere on the
 * host. This mirrors a common real-world misconfiguration.
 */
$DB_HOST = '127.0.0.1';
$DB_USER = 'observ_app';
$DB_PASS = 'Pr0dDbAcc3ss!2023';
$DB_NAME = 'observ';

function db_connect() {
    global $DB_HOST, $DB_USER, $DB_PASS, $DB_NAME;
    $conn = @mysqli_connect($DB_HOST, $DB_USER, $DB_PASS, $DB_NAME);
    if (!$conn) {
        http_response_code(500);
        die('Database connection failed.');
    }
    return $conn;
}
