<?php
declare(strict_types=1);
session_start();
$envFile=dirname(__DIR__).'/.env';
if(is_readable($envFile)){foreach(file($envFile,FILE_IGNORE_NEW_LINES|FILE_SKIP_EMPTY_LINES) as $line){$line=trim($line);if($line===''||str_starts_with($line,'#')||!str_contains($line,'='))continue;[$key,$value]=explode('=',$line,2);$key=trim($key);$value=trim($value);if($key!==''&&getenv($key)===false){$value=trim($value," \"'");putenv($key.'='.$value);$_ENV[$key]=$value;}}}
function env_value(string $key,string $default=''): string { $v=getenv($key); return $v===false?$default:$v; }
function db(): PDO { static $pdo=null; if($pdo instanceof PDO)return $pdo; $dsn=sprintf('mysql:host=%s;port=%s;dbname=%s;charset=utf8mb4',env_value('DB_HOST','127.0.0.1'),env_value('DB_PORT','3306'),env_value('DB_NAME','covid_portal')); return $pdo=new PDO($dsn,env_value('DB_USER','root'),env_value('DB_PASSWORD',''),[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION,PDO::ATTR_DEFAULT_FETCH_MODE=>PDO::FETCH_ASSOC]); }
function h(string $s): string { return htmlspecialchars($s,ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8'); }
function csrf_token(): string { return $_SESSION['csrf']??=bin2hex(random_bytes(32)); }
function csrf_check(): void { if(!hash_equals($_SESSION['csrf']??'',(string)($_POST['_csrf']??''))){http_response_code(419);exit('Session expired. Reload and try again.');} }
function flash(string $m,string $kind='success'): void { $_SESSION['flash']=[$m,$kind]; }
function redirect(string $path='/'): never { header('Location: '.$path); exit; }
function require_login(): void { if(empty($_SESSION['user'])){flash('Please sign in to continue.','error');redirect('/?page=login');} }
function require_admin(): void { require_login(); if(($_SESSION['user']['role']??'')!=='admin'){http_response_code(403);exit('Administrator access required.');} }
function valid_email(string $s): bool { $pattern=<<<'REGEX'
/^[A-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?(?:\.[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?)+$/i
REGEX; return preg_match($pattern,$s)===1; }
function valid_phone(string $s): bool { return (bool)preg_match('/^[0-9]{10}$/',$s); }
function valid_password(string $s): bool { return strlen($s)>=8&&preg_match('/[A-Z]/',$s)&&preg_match('/[a-z]/',$s)&&preg_match('/[0-9]/',$s); }

function valid_slot_date(string $value, ?DateTimeImmutable $today=null): bool {
    if(!preg_match('/^\d{4}-\d{2}-\d{2}$/',$value)) return false;
    $date=DateTimeImmutable::createFromFormat('!Y-m-d',$value);
    $errors=DateTimeImmutable::getLastErrors();
    if(!$date || ($errors!==false && ($errors['warning_count']>0 || $errors['error_count']>0)) || $date->format('Y-m-d')!==$value) return false;
    $today=($today??new DateTimeImmutable('today'))->setTime(0,0);
    return $date >= $today->modify('+1 day');
}
