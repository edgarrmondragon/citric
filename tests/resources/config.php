<?php

$db_type = getenv('DB_TYPE');
$db_host = getenv('DB_HOST');
$db_port = getenv('DB_PORT');
$db_name = getenv('DB_NAME');
$db_username = getenv('DB_USERNAME');
$db_password = getenv('DB_PASSWORD');
$db_charset = getenv('DB_CHARSET') ?: 'utf8';

return array(
    'components' => array(
        'db' => array(
            'connectionString' => "$db_type:host=$db_host;port=$db_port;dbname=$db_name;",
            'emulatePrepare' => true,
            'username' => $db_username,
            'password' => $db_password,
            'charset' => $db_charset,
            'tablePrefix' => 'lime_',
        ),
        'urlManager' => array(
            'urlFormat' => 'path',
            'rules' => array(),
            'showScriptName' => true,
        ),
        'request' => array(
            'baseUrl' => '',
        ),
    ),
    'config' => array(
        'publicurl' => '',
        'debug' => 0,
        'debugsql' => 0,
        'RPCInterface' => 'json',
    )
);