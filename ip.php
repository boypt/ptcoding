<?php
header("Cache-Control: no-store, no-cache, must-revalidate");  // HTTP/1.1
header("Cache-Control: post-check=0, pre-check=0", false);
header("Pragma: no-cache");                                    // HTTP/1.0

$fixed_key = array("REMOTE_ADDR", "REMOTE_PORT", "REQUEST_TIME");

if(!empty($_SERVER['HTTP_X_REQUESTED_WITH']) && strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) == 'xmlhttprequest') {
    header("content-type: application/x-javascript");
    echo json_encode($_SERVER, JSON_PRETTY_PRINT);
} elseif (!empty($_SERVER['HTTP_USER_AGENT']) && strpos(strtolower($_SERVER['HTTP_USER_AGENT']), 'curl') !== FALSE) {
    header("Content-type: text/plain");
    foreach($_SERVER as $k => $v) {
        echo "$k => $v\n";
    }
} else { ?>
<!DOCTYPE html>
<html>
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <style type="text/css">
body {font-size:12px;}
table {margin:20px auto;border-collapse:collapse;}
th,td {padding:5px 10px;border: 1px solid #aaa;}
    </style>    
    </head>
    <body>
    <table>
        <tbody>
        <?php
        foreach($fixed_key as $k) { 
        ?><tr><td><?=$k?></td><td><?=$_SERVER[$k]?></td></tr>
        <?php
        }

        foreach($_SERVER as $k => $v) {
            if(substr($k, 0, 4) === "HTTP") {
            ?><tr><td><?=$k?></td><td><?=$v?></td></tr>
        <?php }
        }?></tbody>
    </table>
    </body>
</html>
<?php 
}?>
