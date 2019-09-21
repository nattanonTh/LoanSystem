<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!-- CSRF Token -->
    <meta name="csrf-token" content="{{ csrf_token() }}">

    <title>Loan System</title>

    <!-- Scripts -->
    <script src="{{ mix('js/app.js') }}"></script>

    <!-- Styles -->
    <link href="{{ mix('css/app.css') }}" rel="stylesheet">
</head>

<body>

    <div id="app" class="container pt-4">

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

        @if ($errors->any())
            <div class="alert alert-danger">
                <ul>
                    @foreach ($errors->all() as $error)
                        <li>{{ $error }}</li>
                    @endforeach
                </ul>
            </div>
        @endif

        <main class="py-4">
            @yield('content')
        </main>
    </div>
</body>

</html>
