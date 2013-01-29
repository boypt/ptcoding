<?php


require_once("VarnishAdminSocket.php");
$s = new VarnishAdminSocket('127.0.0.1', 6082, '3.0');
$s->set_auth("123456");
echo $s->connect();
echo $s->connect();
echo $s->connect();
echo $s->connect();
echo $s->status();
echo $s->status();
echo $s->status();
echo $s->status();



?>
