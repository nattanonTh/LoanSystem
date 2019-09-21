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
}
