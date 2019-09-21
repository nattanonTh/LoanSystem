<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>Loan System</title>

    <!-- Scripts -->
    <script src="{{ asset('js/app.js') }}" defer></script>

    <!-- Styles -->
    <link href="{{ asset('css/app.css') }}" rel="stylesheet">
</head>
<body>
    <div id="app">
        <nav class="navbar navbar-expand-md navbar-dark bg-dark shadow-sm">
            <div class="container">

            </div>
        </nav>

        @if(\Session::has('success'))
        <div class="container pt-4">
                <div class="alert alert-success">
                    {{\Session::get('success')}}
                </div>
        </div>
        @endif
        @if(\Session::has('error'))
        <div class="container pt-4">
                <div class="alert alert-danger">
                    {{\Session::get('error')}}
                </div>
        </div>
        @endif

        <main class="py-4">
            @yield('content')
        </main>
    </div>
</body>
</html>
