<?php
header("Cache-Control: no-store, no-cache, must-revalidate");  // HTTP/1.1
header("Cache-Control: post-check=0, pre-check=0", false);
header("Pragma: no-cache");                                    // HTTP/1.0

$fixed_key = array("REMOTE_ADDR", "REMOTE_PORT", "REQUEST_TIME");

if (!empty($_SERVER['HTTP_USER_AGENT']) && strlen($_SERVER['HTTP_USER_AGENT']) < 30) {
    header("Content-type: text/plain");
    echo "IP: {$_SERVER["REMOTE_ADDR"]}\n";
    echo "UA: {$_SERVER["HTTP_USER_AGENT"]}\n";
} else { ?>
<!DOCTYPE html>
<html>
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style type="text/css">
div.container {margin:20px auto;}
table {width:100%;border-collapse:collapse;}
th,td {padding:5px 10px;border: 1px solid #aaa;}
td.value {font-size:10px;}
textarea {width:100%; height: 200px;}
    </style>    
    </head>
    <body>

    <div class="container">
        <table>
            <tbody>
<?php foreach($fixed_key as $k) : ?>
<tr>
    <td><?=$k?></td>
    <td class="value"><?=$_SERVER[$k]?></td>
</tr>
<?php endforeach;

            foreach($_SERVER as $k => $v):
                $pre_key = substr($k, 0, 4);
                if($pre_key === "HTTP" || $pre_key === "GEOI"):
?>
<tr>
    <td><?=$k?></td>
    <td class="value"><?=$v?></td>
</tr>
<?php           endif;
            endforeach;
?>
            </tbody>
        </table>
    </body>
</html>
<?php 
}?>
