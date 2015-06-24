<?php 

function getapi($url) {

    // Get cURL resource
    $curl = curl_init();
    // Set some options - we are passing in a useragent too here
    curl_setopt_array($curl, array(
        CURLOPT_RETURNTRANSFER => 1,
        CURLOPT_URL => $url,
        CURLOPT_REFERER => 'http://finance.sina.com.cn/stock/jyts/',
        CURLOPT_USERAGENT => 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.65 Safari/537.36',
        CURLOPT_TIMEOUT => 20
    ));

    // Send the request & save response to $resp
    $resp = curl_exec($curl);
    // Close request to clear up some resources
    curl_close($curl);

    return $resp;
}

$sinaurl = 'http://hq.sinajs.cn/ran='.(float)rand()/(float)getrandmax().'&list='.$_GET['list'];
#echo $sinaurl;

header('Content-Type: application/x-javascript; charset=GBK');
echo getapi($sinaurl);
?>
