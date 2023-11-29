<?php

$db_type = getenv('DB_TYPE');
$db_host = getenv('DB_HOST');
$db_port = getenv('DB_PORT');
$db_name = getenv('DB_NAME');
$db_username = getenv('DB_USERNAME');
$db_password = getenv('DB_PASSWORD');
$db_charset = getenv('DB_CHARSET') ?: 'utf8';

$email_smtphost = getenv('EMAIL_SMTPHOST');
$email_smtpuser = getenv('EMAIL_SMTPUSER');
$email_smtppassword = getenv('EMAIL_SMTPPASSWORD');

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
        'debug' => 2,
        'debugsql' => 1,
        'RPCInterface' => 'json',
        'sitename' => 'Citric - Test',
        'defaultlang' => 'en',
        'defaulttheme' => 'vanilla',
        'emailsmtphost' => $email_smtphost,
        'emailsmtpuser' => $email_smtpuser,
        'emailsmtppassword' => $email_smtppassword,
        'emailmethod' => 'smtp',
    )
);
