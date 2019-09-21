<?php

namespace App\Http\Controllers;

use App\Http\Requests\CreateLoan;
use App\Loan;
use App\Repayment;
use Illuminate\Http\Request;
use Libraries\LoanCalculation;

class LoanController extends Controller
{
    private $loan;
    private $loanCalculation;

    public function __construct()
    {
        $this->loanCalculation = new LoanCalculation();
    }

    /**
     * Display a listing of the resource.
     *
     * @return \Illuminate\Http\Response
     */
    public function index()
    {
        //
        return view('loans.loan_list');
    }

    /**
     * Show the form for creating a new resource.
     *
     * @return \Illuminate\Http\Response
     */
    public function create()
    {
        //
        return view('loans.loan_create');
    }

    /**
     * Store a newly created resource in storage.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\Response
     */
    public function store(CreateLoan $request)
    {
        $validated = $request->validated();

        $loanData = [
            'loan_amount' => $validated['input-loan-amount'],
            'loan_term' => $validated['input-loan-term'],
            'interest_rate' => $validated['input-interest-rate'],
            'start_date' => date("Y-m-d", strtotime('1-' . $validated['input-month'] . '-' . $validated['input-year'])),
        ];

        // Create new loan and
        $loanData = Loan::create($loanData);

        // set loan for calculation class
        $this->loanCalculation->setLoan($loanData);

        // generate repayment list
        $this->loanCalculation->generateReplaymentSchedule();

        // get repayment list
        $repaymentList = $this->loanCalculation->getRepaymentList();

        foreach ($repaymentList as $replayment) {
            Repayment::create((array) $replayment);
        }
    }

    /**
     * Display the specified resource.
     *
     * @param  \App\Loan  $loan
     * @return \Illuminate\Http\Response
     */
    public function show(Loan $loan)
    {
        //
    }

    /**
     * Show the form for editing the specified resource.
     *
     * @param  \App\Loan  $loan
     * @return \Illuminate\Http\Response
     */
    public function edit(Loan $loan)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  \App\Loan  $loan
     * @return \Illuminate\Http\Response
     */
    public function update(Request $request, Loan $loan)
    {
        //
    }

    /**
     * Remove the specified resource from storage.
     *
     * @param  \App\Loan  $loan
     * @return \Illuminate\Http\Response
     */
    public function destroy(Loan $loan)
    {
        //
    }

    // loan list for datatable
    function list() {
        //
        return Loan::getLoanListDataTable();
    }
}
