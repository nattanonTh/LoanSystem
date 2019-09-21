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
            <tbody>
                @if (!empty($loans))
                @foreach ($loans->all() as $loan)
                <tr>
                    <td>{{ $loan->id }}</td>
                    <td>{{ $loan->showLoanAmount }} ฿</td>
                    <td>{{ $loan->showLoanTerm }} Years</td>
                    <td>{{ $loan->showInterestRate }}%</td>
                    <td>{{ $loan->created_at }}</td>
                    <td>{{ $loan->id }}</td>
                </tr>
                @endforeach
                @endif
            </tbody>
        </table>
    </div>
</div>

<script>
    $(function () {
        $('#loan_list').DataTable({
            searching: false,
            info: false,
            lengthChange: false,
            "order": [[0, "desc"]],
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
                        return '<div class="btn-group"><a class="btn btn-primary" href="loan/' + data + '">View</a><a href="loan/edit/' + data + '" class="btn btn-success">Edit</a><a href="loan/delete/' + data + '"  class="btn btn-danger deleteBtn">Delete</a></div>'
                    }
                }
            ],
        });

        $(document).on('click', '.deleteBtn', function(e) {
            e.preventDefault();
            if (confirm('Please confirm to delete loan')) {
                location = $(this).attr('href');
            }
        });
    });

</script>

@endsection
