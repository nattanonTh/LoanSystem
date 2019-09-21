@extends('layouts.app')

@section('content')
<div class="row">
    <h1>Edit Loan</h1>
</div>
<div class="row pt-4">
    <div class="col-sm-8 offset-sm-2">
        <form autocomplete="off" method="post" action="{{ url('loan/edit/' . $loan->id) }}">
            {{ csrf_field() }}
            <div class="form-group row">
                <label for="" class="col-sm-2 col-form-label">Loan Amount:</label>
                <div class="col-sm-10">
                    <div class="input-group mb-2">
                        <input type="number" class="form-control" name="input-loan-amount" id="input-loan-amount"
                            placeholder="Loan Amount" min="1" value="{{ $loan->loan_amount }}" required>
                        <div class="input-group-prepend">
                            <div class="input-group-text">฿</div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="form-group row">
                <label for="" class="col-sm-2 col-form-label">Loan Term:</label>
                <div class="col-sm-10">
                    <div class="input-group mb-2">
                        <input type="number" class="form-control" name="input-loan-term" id="input-loan-term"
                            placeholder="Loan Term" min="1" value="{{ $loan->loan_term }}" required>
                        <div class="input-group-prepend">
                            <div class="input-group-text">Years</div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="form-group row">
                <label for="" class="col-sm-2 col-form-label">Interest Rate:</label>
                <div class="col-sm-10">
                    <div class="input-group mb-2">
                        <input type="text" class="form-control" name="input-interest-rate" id="input-interest-rate"
                            placeholder="Interest Rate" value="{{ $loan->interest_rate }}" required>
                        <div class="input-group-prepend">
                            <div class="input-group-text">%</div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="form-inline form-group row">
                <label for="" class="col-sm-2 col-form-label">Start Date</label>
                <div class="col-sm-5">
                    <select name="input-month" id="input-month" class="form-control">
                        <option value="1">January</option>
                        <option value="2">February</option>
                        <option value="3">March</option>
                        <option value="4">April</option>
                        <option value="5">May</option>
                        <option value="6">June</option>
                        <option value="7">July</option>
                        <option value="8">August</option>
                        <option value="9">September</option>
                        <option value="10">October</option>
                        <option value="11">November</option>
                        <option value="12">December</option>
                    </select>
                </div>
                <div class="col-sm-5">
                    <input type="number" min="0" max="9999" class="form-control" id="input-year" name="input-year"
                        placeholder="Year" value="{{ $loan->year }}" required>
                </div>
            </div>
            <div class="form-group row">
                <div class="col-sm-10 offset-sm-2">
                    <button type="submit" class="btn btn-primary">Update</button>
                    <a class="btn btn-secondary" href="{{ url('/') }}">Back</a>
                </div>
            </div>
        </form>
    </div>
</div>

<script>
    $(function() {
        $('#input-month').val({{ $loan->month }});
    });
</script>

@endsection
