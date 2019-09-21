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

Route::get('/', 'LoanController@index');
Route::post('/create-new-loan', 'LoanController@store');
Route::get('/create-new-loan', 'LoanController@create');

Route::post('/loan-list', 'LoanController@list');
