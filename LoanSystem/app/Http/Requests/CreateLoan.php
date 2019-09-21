<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class CreateLoan extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     *
     * @return bool
     */
    public function authorize()
    {
        return true;
    }

    /**
     * Get the validation rules that apply to the request.
     *
     * @return array
     */
    public function rules()
    {
        return [
            'input-loan-amount' => ['required', 'integer', 'between:1000,100000000'],
            'input-loan-term' => ['required', 'integer', 'between:1,50'],
            'input-interest-rate' => ['required', 'numeric', 'between:00.00,36.00'],
            'input-month' => ['required', 'integer', 'between:1,12'],
            'input-year' => ['required', 'integer', 'between:2017,2050'],
        ];
    }

    public function attributes()
    {
        return [
            'input-loan-amount.required' => 'Loan Amount',
            'input-loan-term' => 'Loan Term',
            'input-interest-rate' => 'Interest Rate',
            'input-month' => 'Month',
            'input-year' => 'Year',
        ];
    }
}
