<?php
namespace Libraries;

use App\Loan;
use Libraries\Object\Repayment;

class LoanCalculation
{
    private $loan;
    private $repaymentList;
    private $PMT;
    private $outstandingBalance;
    private $totalMonth;
    private $month;
    private $year;

    public function __construct()
    {

    }

    public function generateReplaymentSchedule()
    {
        // prepare data before calculation
        $this->prepareData();
        if ($this->hasLoan()) {
            // loop thorough all month of loan
            for ($count = 1; $count <= $this->totalMonth; $count++) {
                // calculate interest
                $tempInterest = $this->getInterestAmount();

                // create Repayment object
                $this->repaymentList[] = new Repayment([
                    'payment_no' => $count,
                    'date' => $this->year . '-' . $this->month . '-1',
                    'payment_amount' => $this->PMT,
                    'interest' => $tempInterest,
                    'principal' => $this->PMT - $tempInterest,
                    'balance' => $this->outstandingBalance - ($this->PMT - $tempInterest),
                    'loan_id' => $this->loan->id,
                ]);

                $this->month += 1;

                // check if end year
                $this->checkEndYear();

                $this->outstandingBalance = round($this->outstandingBalance - ($this->PMT - $tempInterest), 2);
            }
        }
    }

    private function getInterestAmount()
    {
        return round(($this->loan->interest_rate / 12) * $this->outstandingBalance, 2);
    }

    private function checkEndYear()
    {
        // if end year then increse amount of year and set month to 1
        if ($this->month == 13) {
            $this->year += 1;
            $this->month = 1;
        }
    }

    private function prepareData()
    {
        $this->calculatePMT();
        $this->outstandingBalance = $this->loan->loan_amount;
        $this->totalMonth = $this->loan->loan_term * 12;
        $this->month = date('m', strtotime($this->loan->start_date));
        $this->year = date('Y', strtotime($this->loan->start_date));
    }

    private function calculatePMT()
    {
        // PMT calculation
        $this->PMT = ($this->loan->loan_amount * ($this->loan->interest_rate / 12)) / (1 - pow((1 + ($this->loan->interest_rate / 12)), (-12) * $this->loan->loan_term));
        $this->PMT = round($this->PMT, 2);
    }

    private function hasLoan()
    {
        return !empty($this->loan);
    }

    // ------------- Auto gen

    /**
     * Get the value of loan
     */
    public function getLoan()
    {
        return $this->loan;
    }

    /**
     * Set the value of loan
     *
     * @return  self
     */
    public function setLoan(Loan $loan)
    {
        $this->loan = $loan;
        return $this;
    }

    /**
     * Get the value of repaymentList
     */
    public function getRepaymentList()
    {
        return $this->repaymentList;
    }

    /**
     * Set the value of repaymentList
     *
     * @return  self
     */
    public function setRepaymentList($repaymentList)
    {
        $this->repaymentList = $repaymentList;

        return $this;
    }
}
