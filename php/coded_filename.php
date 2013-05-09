<?php

$root = dirname(__FILE__);
$req = $_SERVER["REQUEST_URI"];

error_log("Requested: ".$_SERVER['HTTP_HOST'].$req);

if(strpos($req, "/wp-content/uploads/") !== 0) {
    error_log("Non-content request. Forbided.");
    header("HTTP/1.1 403 Forbbiden.");
    die();
}

if(mb_detect_encoding($req, 'ASCII', true)) {
    error_log("Pure ascii, try urlencoded.");
    $req = rawurldecode($req);
}

$utf8_path = @mb_convert_encoding($req, "utf-8", array("cp936", "gbk", "big5"));

if($utf8_path === null || !is_file($root . $utf8_path)) {
    error_log("can't decode, try forced decode utf8.");
    $utf8_path = @utf8_decode($req);
}

if($utf8_path !== null && is_file($root . $utf8_path)) {
    error_log("File Found: $utf8_path");
    header("Content-Type: ". mime_content_type($root . $utf8_path));
    header("X-Accel-Redirect: " . $utf8_path);
} else {
    error_log("can't decode, not found");
    header("HTTP/1.1 404 Not Found");
    die();
}
?>
