<?php
require_once('Log.php');
//$logger = Log::factory('syslog', '', 'APC-Checker');
$logger = Log::factory('error_log', PEAR_LOG_TYPE_SYSTEM, 'Coded');

$ROOT = "/srv/http/public_html/appgame";

$fn = $_SERVER["REQUEST_URI"];

$logger->log("Requested: ".$_SERVER['HTTP_HOST'].$fn);

if(mb_detect_encoding($fn, 'ASCII', true)) {
    $logger->log("pure ascii, may urlencoded.");
    $fn = urldecode($fn);
}


$utf8_path = @mb_convert_encoding($fn, "utf-8", array("cp936", "gbk", "big5"));

if($utf8_path === null || !is_file($ROOT . $utf8_path)) {
    $logger->log("can't decode, try forced decode utf8.");
    $utf8_path = @utf8_decode($fn);
}

if($utf8_path !== null && is_file($ROOT . $utf8_path)) {
    $logger->log("File Found: $utf8_path");
    header("Content-Type: ". mime_content_type($ROOT . $utf8_path));
    header("X-Accel-Redirect: " . $utf8_path);
} else {
    $logger->log("can't decode, not found");
    header("HTTP/1.0 404 Not Found");
    die();
}
?>
