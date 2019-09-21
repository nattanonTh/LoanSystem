<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class LoanDetails extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        //
        Schema::create('loan_details', function (Blueprint $table) {
            $table->bigIncrements('id');
            $table->integer('payment_no');
            $table->date('date');
            $table->decimal('payment_amount', 21, 6);
            $table->decimal('principal', 21, 6);
            $table->decimal('interest', 21, 6);
            $table->decimal('balance', 21, 6);
            $table->bigInteger('loan_id');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        //
        Schema::dropIfExists('loan_details');
    }
}
