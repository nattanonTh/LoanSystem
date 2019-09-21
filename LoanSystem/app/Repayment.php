<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Repayment extends Model
{
    //
    protected $table = 'repayment';
    protected $primaryKey = 'id';

    protected $fillable = [
        'payment_no', 'date', 'payment_amount', 'principal', 'interest', 'balance', 'loan_id'
    ];
}
