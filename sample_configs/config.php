$host = $_SERVER['HTTP_HOST'];
define('HTTP_SERVER', 'https://'.$host.'/');
define('HTTP_IMAGE', 'https://'.$host.'/image/');
define('HTTP_ADMIN', 'https://'.$host.'/admin/');

// HTTPS
define('HTTPS_SERVER', 'https://'.$host.'/');
define('HTTPS_IMAGE', 'https://'.$host.'/image/');

// DIR
$dir = dirname(__FILE__);
define('DIR_APPLICATION', $dir . '/catalog/');
define('DIR_SYSTEM', $dir . '/system/');
define('DIR_DATABASE', $dir . '/system/database/');
define('DIR_LANGUAGE', $dir . '/catalog/language/');
define('DIR_TEMPLATE', $dir . '/catalog/view/theme/');
define('DIR_CONFIG', $dir . '/system/config/');
define('DIR_IMAGE', $dir . '/image/');
define('DIR_CACHE', $dir . '/system/cache/');
define('DIR_DOWNLOAD', $dir . '/download/');
define('DIR_LOGS', $dir . '/system/logs/');

// DB
define('DB_DRIVER', 'mysql');
define('DB_HOSTNAME', 'localhost');
define('DB_USERNAME', 'mysql_user');
define('DB_PASSWORD', 'mysql_password');
define('DB_DATABASE', 'mysql_db');
define('DB_PREFIX', 'oc_');

