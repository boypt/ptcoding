<?php
if (isset($_POST["sync"]) && isset($_POST["code"])) {

    $sync = $_POST["sync"];
    $code = $_POST["code"];
    $dir = dirname(__FILE__) . "/json";

    if(!is_numeric($code)) {
        die(400);
    }

    if(!is_dir($dir)) {
        mkdir($dir);
    }

    $path = $dir . "/${code}.json";
    file_put_contents($path,$sync,LOCK_EX);
}
