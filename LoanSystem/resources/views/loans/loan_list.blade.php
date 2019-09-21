@extends('layouts.app')

@section('content')
<div class="row">
    <h1>All Loans</h1>
</div>
<div class="row pt-1">
    <a class="btn btn-primary" href="{{ url('create-new-loan') }}">Add new Loan</a>
</div>
<div class="row pt-4">
    <div class="col-md-12">
        <table id="loan_list" class="table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Loan Amount</th>
                    <th>Loan Term</th>
                    <th>Interest Rate</th>
                    <th>Created at</th>
                    <th>Edit</th>
                </tr>
            </thead>
        </table>
    </div>
</div>

<script>
    $('#loan_list').DataTable({
        searching: false,
        info: false,
        ajax: {
            "url": "{{ url('loan-list') }}",
            "type": "POST",
            headers: {
                'X-CSRF-TOKEN': $('meta[name="csrf-token"]').attr('content')
            }
        },
        lengthChange: false,
        processing: true,
        serverSide: true,
        columns: [
            { data: 'id', name: 'id' },
            { data: 'loan_amount', name: 'loan_amount' },
            { data: 'loan_term', name: 'loan_term' },
            { data: 'interest_rate', name: 'interest_rate' },
            { data: 'created_at', name: 'created_at' },
            {
                data: "id",
                name: "id",
                "render": function (data, type, row, meta) {
                    return '<div class="btn-group"><button type="button" class="btn btn-primary">View</button><button type="button" class="btn btn-success">Edit</button><button type="button" class="btn btn-danger">Delete</button></div>'
                }
            }
        ],
    });
</script>

@endsection