// stan 2018-08-09


jQuery( function($) {


  $( document ).ajaxError( function(event, xhr, ajaxOptions, thrownError) {
    const jdebug = $( 'div#jdebug' );

    jdebug.html(xhr.responseText);
  } );


} );
