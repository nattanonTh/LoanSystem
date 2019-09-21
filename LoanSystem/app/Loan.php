<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Loan extends Model
{
    //
    protected $table = 'loans';
    protected $primaryKey = 'id';

    protected $fillable = [
        'loan_amount', 'loan_term', 'interest_rate', 'start_date', 'created_at',
    ];

    public static function getLoanListDataTable()
    {
        $list = Loan::all();
        return datatables()->of($list)->make(true);
    }

    public function repayments()
    {
        return $this->hasMany('App\Repayment');
    }

    public function getIntegerLoanAmountAttribute()
    {
        return (int) $this->loan_amount;
    }

    public function getShowLoanAmountAttribute()
    {
        return number_format($this->loan_amount, '2');
    }

    public function getShowLoanTermAttribute()
    {
        return number_format($this->loan_term);
    }

    public function getShowInterestRateAttribute()
    {
        return number_format($this->interest_rate, 2);
    }

    public function getMonthAttribute()
    {
        return date('m', strtotime($this->start_date));
    }

    public function getYearAttribute()
    {
        return date('Y', strtotime($this->start_date));
    }
}
