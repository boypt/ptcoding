<?php require_once("VarnishAdminSocket.php"); ?>
<div class="wrap">
<h1><?php print VRWP_PUGIN_NAME ." ". VRWP_CURRENT_VERSION. "<sub>(Build ".VRWP_CURRENT_BUILD.")</sub>"; ?></h1>

<h2>Varnish Servers</h2>
<form method="post" action="options.php">
    <?php settings_fields( 'vrwp-settings-servers' ); ?>
    <table class="form-table">
        <tr valign="top">
        <th scope="row"><code>ADDR:PORT:SECRET</code>s, each for a line. Example: 
<code>192.168.67.11:6082:PassC0D38vers
192.168.67.12:6082:SecR3t0fAn0ther</code></th>
        <td><textarea style="width:250px;height:8em;" type="text" name="vrwp_varnish_servers"><?php echo get_option('vrwp_varnish_servers'); ?></textarea></td>
        </tr>
    </table>
    
    <p class="submit">
    <input type="submit" class="button-primary" value="<?php _e('Save Servers') ?>" />
    </p>
</form>


<h2>Ban/Flush Rules</h2>

<form method="post" action="options.php">
    <?php settings_fields( 'vrwp-settings-rules' ); ?>
    <table class="form-table">
        <tr valign="top">
        <th scope="row">URLs: <code>http://xxxxxxxxxxxxxxx</code></th>
        <td><textarea style="width:250px;height:8em;" type="text" name="vrwp_ban_urls"><?php echo get_option('vrwp_ban_urls'); ?></textarea></td>
        </tr>
         
        <tr valign="top">
        <th scope="row">Regular Expressions:</th>
        <td><textarea style="width:250px;height:8em;" type="text" name="vrwp_ban_re"><?php echo get_option('vrwp_ban_re'); ?></textarea></td>
        </tr>
    </table>
    
    <p class="submit">
    <input type="submit" class="button-primary" value="<?php _e('Save Rules') ?>" />
    </p>
</form>


</div>
<div>

<?php

if ( isset( $_GET['settings-updated'] ) ) {
    echo "<div class='updated'><p>Theme settings updated successfully.</p></div>";
    //print_r(explode("\n", get_option('vrwp_varnish_servers'))); 
}

?>
<pre>
<?php


foreach(explode("\n", get_option('vrwp_varnish_servers')) as $svrstr) {
    $sinf = explode(":", trim($svrstr));
    $server_ip = $sinf[0];
    $server_port = $sinf[1];
    $server_secret = $sinf[2];

    $svr = new VarnishAdminSocket($server_ip, $server_port, '3.0');
    $svr->set_auth("$server_secret\n");
    try {
        //print_r($sinf);
        echo $svr->connect();
    } catch (Exception $Ex) {
        echo $Ex->getMessage();
        echo "\nfailed\n";
    }
    $svr->close();
    echo "==========================....=====================\n";
}

?>
</pre>

</div>
