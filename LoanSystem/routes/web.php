<?php

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Here is where you can register web routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| contains the "web" middleware group. Now create something great!
|
 */

//  List
Route::get('/', 'LoanController@index');

// Details
Route::get('/loan/{loan}', 'LoanController@show');
// Delete
Route::get('/loan/delete/{loan}', 'LoanController@destroy');


// Edit
Route::get('/loan/edit/{loan}', 'LoanController@edit');
Route::post('/loan/edit/{loan}', 'LoanController@update');

// Create
Route::get('/create-new-loan', 'LoanController@create');
Route::post('/create-new-loan', 'LoanController@store');

