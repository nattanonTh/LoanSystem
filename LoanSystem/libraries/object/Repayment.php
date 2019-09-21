<?php
namespace Libraries\Object;

class Repayment
{
    public $payment_no;
    public $date;
    public $payment_amount;
    public $principal;
    public $interest;
    public $balance;
    public $loan_id;

    public function __construct($param = [])
    {
        if (!empty($param)) {
            foreach ($param as $key => $value) {
                $this->$key = $value;
            }
        }
    }

    /**
     * Get the value of interest
     */
    public function getInterest()
    {
        return $this->interest;
    }

    /**
     * Set the value of interest
     *
     * @return  self
     */
    public function setInterest($interest)
    {
        $this->interest = $interest;

        return $this;
    }

    /**
     * Get the value of payment_no
     */
    public function getPayment_no()
    {
        return $this->payment_no;
    }

    /**
     * Set the value of payment_no
     *
     * @return  self
     */
    public function setPayment_no($payment_no)
    {
        $this->payment_no = $payment_no;

        return $this;
    }

    /**
     * Get the value of date
     */
    public function getDate()
    {
        return $this->date;
    }

    /**
     * Set the value of date
     *
     * @return  self
     */
    public function setDate($date)
    {
        $this->date = $date;

        return $this;
    }

    /**
     * Get the value of payment_amount
     */
    public function getPayment_amount()
    {
        return $this->payment_amount;
    }

    /**
     * Set the value of payment_amount
     *
     * @return  self
     */
    public function setPayment_amount($payment_amount)
    {
        $this->payment_amount = $payment_amount;

        return $this;
    }

    /**
     * Get the value of principal
     */
    public function getPrincipal()
    {
        return $this->principal;
    }

    /**
     * Set the value of principal
     *
     * @return  self
     */
    public function setPrincipal($principal)
    {
        $this->principal = $principal;

        return $this;
    }

    /**
     * Get the value of balance
     */
    public function getBalance()
    {
        return $this->balance;
    }

    /**
     * Set the value of balance
     *
     * @return  self
     */
    public function setBalance($balance)
    {
        $this->balance = $balance;

        return $this;
    }

    /**
     * Get the value of loan_id
     */
    public function getLoan_id()
    {
        return $this->loan_id;
    }

    /**
     * Set the value of loan_id
     *
     * @return  self
     */
    public function setLoan_id($loan_id)
    {
        $this->loan_id = $loan_id;

        return $this;
    }
}
