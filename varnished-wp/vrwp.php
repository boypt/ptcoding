<?php
/*
Plugin Name: Varnished-WP
Plugin URI:
Description: Interface for simple managing varnish servers via the admin port. 
Author: Preston M.
Tags: varnish, cache, varnish-cache
License: MIT
License URI: http://opensource.org/licenses/MIT
*/
require_once("VarnishAdminSocket.php");

?><?php

// some definition we will use
define( 'VRWP_PUGIN_NAME', 'Varnished-WP');
define( 'VRWP_PLUGIN_DIRECTORY', 'varnished-wp');
define( 'VRWP_CURRENT_VERSION', '0.1' );
define( 'VRWP_CURRENT_BUILD', '1' );
define( 'VRWP_LOGPATH', str_replace('\\', '/', WP_CONTENT_DIR).'/vrwp-logs/');
define( 'VRWP_DEBUG', false);		# never use debug mode on productive systems
// i18n plugin domain for language files
define( 'EMU2_I18N_DOMAIN', 'vrwp' );

// how to handle log files, don't load them if you don't log
//require_once('vrwp_logfilehandling.php');

// load language files
function vrwp_set_lang_file() {
	# set the language file
	$currentLocale = get_locale();
	if(!empty($currentLocale)) {
		$moFile = dirname(__FILE__) . "/lang/" . $currentLocale . ".mo";
		if (@file_exists($moFile) && is_readable($moFile)) {
			load_textdomain(EMU2_I18N_DOMAIN, $moFile);
		}

	}
}
//vrwp_set_lang_file();

// create custom plugin settings menu
add_action( 'admin_menu', 'vrwp_create_menu' );

//call register settings function
add_action( 'admin_init', 'vrwp_register_settings' );


//register_activation_hook(__FILE__, 'vrwp_activate');
//register_deactivation_hook(__FILE__, 'vrwp_deactivate');
register_uninstall_hook(__FILE__, 'vrwp_uninstall');

// activating the default values
function vrwp_activate() {
	//add_option('vrwp_option_3', 'any_value');
}

// deactivating
function vrwp_deactivate() {
	// needed for proper deletion of every option
	//delete_option('vrwp_option_3');
}

// uninstalling
function vrwp_uninstall() {
	# delete all data stored
	delete_option('vrwp_varnish_servers');
	delete_option('vrwp_ban_urls');
	delete_option('vrwp_ban_re');
	// delete log files and folder only if needed
	if (function_exists('vrwp_deleteLogFolder')) vrwp_deleteLogFolder();
}

function vrwp_create_menu() {
	add_options_page( 'Varnished-WP Options', 'Varnished-WP', 'manage_options', 'varnished_wp_options', 'varnished_wp_options_page' );
}


function vrwp_register_settings() {
	//register settings
	register_setting( 'vrwp-settings-servers', 'vrwp_varnish_servers' );
	register_setting( 'vrwp-settings-rules', 'vrwp_ban_urls' );
	register_setting( 'vrwp-settings-rules', 'vrwp_ban_re' );
}

// check if debug is activated
function vrwp_debug() {
	# only run debug on localhost
	if ($_SERVER["HTTP_HOST"]=="localhost" && defined('EPS_DEBUG') && EPS_DEBUG==true) return true;
}

function varnished_wp_options_page () {
    require_once("vrwp_settings_page.php");
}
?>
