<?php

namespace App\Http\Controllers;

use App\Http\Requests\CreateLoan;
use App\Http\Requests\EditLoan;
use App\Loan;
use App\Repayment;
use Libraries\LoanCalculation;

class LoanController extends Controller
{
    private $loan;
    private $loanCalculation;

    public function __construct()
    {
        $this->loanCalculation = new LoanCalculation();
    }

    public function index()
    {
        //
        return view('loans.loan_list', ['loans' => Loan::all()]);
    }

    public function create()
    {
        //
        return view('loans.loan_create');
    }

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

        if (!empty($repaymentList)) {
            // insert repayments
            foreach ($repaymentList as $replayment) {
                Repayment::create((array) $replayment);
            }
        }

        return redirect('/loan/' . $loanData->id)->with('success', 'the loan has created successfully.');
    }

    public function show(Loan $loan)
    {
        //
        return view('loans.loan_details', ['loan' => $loan, 'repayments' => $loan->repayments]);
    }

    public function edit(Loan $loan)
    {
        //
        return view('loans.loan_edit', compact('loan'));
    }

    public function update(EditLoan $request, Loan $loan)
    {
        $validated = $request->validated();

        $loan->loan_amount = $validated['input-loan-amount'];
        $loan->loan_term = $validated['input-loan-term'];
        $loan->interest_rate = $validated['input-interest-rate'];
        $loan->start_date = date("Y-m-d", strtotime('1-' . $validated['input-month'] . '-' . $validated['input-year']));

        $loan->save();

        // remove all repayment record 
        Repayment::removeByLoanId($loan->id);

        // set loan for calculation class
        $this->loanCalculation->setLoan($loan);

        // generate repayment list
        $this->loanCalculation->generateReplaymentSchedule();

        // get repayment list
        $repaymentList = $this->loanCalculation->getRepaymentList();

        if (!empty($repaymentList)) {
            // insert repayments
            foreach ($repaymentList as $replayment) {
                Repayment::create((array) $replayment);
            }
        }

        return redirect('/loan/' . $loan->id)->with('success', 'the loan has updated successfully.');
    }

    public function destroy(Loan $loan)
    {
        // remove all repayment record 
        Repayment::removeByLoanId($loan->id);

        // delete loan
        $loan->delete();

        return redirect('/')->with('success', 'the loan has deleted successfully.');
    }

}
