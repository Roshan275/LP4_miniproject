<?php
declare(strict_types=1);
require __DIR__.'/../../src/bootstrap.php';
function check(string $label,bool $passed): void { if(!$passed){fwrite(STDERR,"FAIL: $label\n");exit(1);} echo "PASS: $label\n"; }
check('valid email accepted',valid_email('qa.user+stqa@example.test'));
check('email without domain rejected',!valid_email('qa@'));
check('10 digit phone accepted',valid_phone('9876543210'));
check('short phone rejected',!valid_phone('987654321'));
check('phone with letters rejected',!valid_phone('98765abc10'));
check('strong password accepted',valid_password('StrongPass1'));
check('password without uppercase rejected',!valid_password('weakpass1'));
$today=new DateTimeImmutable('2026-04-10');
check('tomorrow accepted',valid_slot_date('2026-04-11',$today));
check('today rejected',!valid_slot_date('2026-04-10',$today));
check('invalid calendar date rejected',!valid_slot_date('2026-02-30',$today));
check('malformed date rejected',!valid_slot_date('11/04/2026',$today));
