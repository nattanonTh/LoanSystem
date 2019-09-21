<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Repayment extends Model
{
    //
    protected $table = 'repayment';
    protected $primaryKey = 'id';

    protected $fillable = [
        'payment_no', 'date', 'payment_amount', 'principal', 'interest', 'balance', 'loan_id',
    ];

    public function getShowPaymentNoAttribute()
    {
        return $this->payment_no;
    }

    public function getShowDateAttribute()
    {
        return Date('F Y', strtotime($this->date));
    }

    public function getShowPayAmountAttribute()
    {
        return number_format($this->payment_amount, '2');
    }

    public function getShowPrincipalAttribute()
    {
        return number_format($this->principal, '2');
    }

    public function getShowInterestAttribute()
    {
        return number_format($this->interest, '2');
    }

    public function getShowBalanceAttribute()
    {
        return number_format($this->balance, '2');
    }

    public static function removeByLoanId($loanId = 0)
    {
        return static::where('loan_id', $loanId)->delete();
    }

}
