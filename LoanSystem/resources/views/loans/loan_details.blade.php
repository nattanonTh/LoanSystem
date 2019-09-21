@extends('layouts.app')

@section('content')
<div class="row">
    <h1>Loan Details</h1>
</div>
<div class="row">
    <div class="col-sm-2">
        ID:
    </div>
    <div class="col-sm-10">
        {{ $loan->id }}
    </div>
</div>
<div class="row">
    <div class="col-sm-2">
        Loan Amount:
    </div>
    <div class="col-sm-10">
        {{ $loan->showLoanAmount }} ฿
    </div>
</div>
<div class="row">
    <div class="col-sm-2">
        Loan Term:
    </div>
    <div class="col-sm-10">
        {{ $loan->showLoanTerm }} {{ $loan->showLoanTerm > 1 ? 'Years' : 'Year' }}
    </div>
</div>
<div class="row">
    <div class="col-sm-2">
        Interest Rate:
    </div>
    <div class="col-sm-10">
        {{ $loan->showInterestRate }} %
    </div>
</div>
<div class="row">
    <div class="col-sm-2">
        Created at:
    </div>
    <div class="col-sm-10">
        {{ $loan->created_at }}
    </div>
</div>
<div class="pt-4">
    <a href="{{ url('/') }}" class="btn btn-secondary btn-sm">Back</a>
</div>
<div class="row pt-4">
    <div class="col-md-12">
        <table id="loan_list" class="table">
            <thead>
                <tr>
                    <th>Payment No</th>
                    <th>Date</th>
                    <th>Payment Amount</th>
                    <th>Principal</th>
                    <th>Interest</th>
                    <th>Balance</th>
                </tr>
            </thead>
            <tbody>
                @if (!empty($repayments))
                @foreach ($repayments->all() as $repayment)
                <tr>
                    <td>{{ $repayment->showPaymentNo }}</td>
                    <td>{{ $repayment->showDate }}</td>
                    <td>{{ $repayment->showPayAmount }}</td>
                    <td>{{ $repayment->showPrincipal }}</td>
                    <td>{{ $repayment->showInterest }}</td>
                    <td>{{ $repayment->showBalance }}</td>
                </tr>
                @endforeach
                @endif
            </tbody>
        </table>
    </div>
</div>
<div class="pt-4">
    <a href="{{ url('/') }}" class="btn btn-secondary btn-sm">Back</a>
</div>
@endsection
